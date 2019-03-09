import scrapy
import ivdiff
from urllib.parse import urlparse
from multiprocessing import Pool
from scrapy.crawler import CrawlerProcess
import argparse
from scrapy.utils.project import get_project_settings
import os
import json
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor


class IvSpider(scrapy.spiders.CrawlSpider):
    name = 'IvSpider'
    dupl = []
    url_list = {}
    crawled = 0
    parsed = 0
    have_diff = 0

    def __init__(self, ignore="", nobrowser=False, browser="", domain="", cookies="cookies.txt", poolsize=5, **kwargs):
        if not domain.startswith("http"):
            domain = "http://" + domain
        self.start_urls = [domain]

        d = urlparse(domain).netloc
        if domain.startswith("www."):
            d = domain[4:]

        self.allowed_domains = [d]
        self.browser = browser
        self.nobrowser = nobrowser
        self.ignore = ignore

        self.pool = Pool(poolsize)
        self.rules = [Rule(LinkExtractor(allow=(), allow_domains=self.allowed_domains, deny=(ignore), deny_domains=()), callback='parse_item', follow=True)]

        print(cookies)
        self.cookies = ivdiff.parseCookies(cookies)
        fn = "gen/{}/url_list.json".format(d)
        try:
            os.makedirs(os.path.dirname(fn))
        except Exception:
            pass

        self.file = open(fn, "a+", buffering=1)
        self.file.seek(0)
        try:
            self.url_list = json.loads(self.file.read())
        except Exception as ex:
            print(ex)
            pass
        self.file.seek(0)

        super().__init__(**kwargs)

    def callback(self, roflan):
        self.parsed += 1
        if roflan[1] == -1:
            print(f"an error occured for url {roflan[0]}")
            return
        if roflan[1] == 1:
            self.have_diff += 1
        print("{0:.2f}% [{1} / crawled {2}] (w/ diff {3}) {4}".format(self.parsed / self.crawled * 100, self.parsed, self.crawled, self.have_diff, roflan[0]))
        self.url_list[roflan[0]] = True
        self.file.seek(0)
        self.file.truncate(0)
        self.file.seek(0)
        self.file.write(json.dumps(self.url_list))
        self.file.seek(0)

    def addToPool(self, url):
        if url in self.url_list:
            if not self.url_list[url]:
                self.pool.apply_async(ivdiff.checkDiff, [self.nobrowser, self.cookies, url, self.t1, self.t2, self.browser], callback=self.callback)
            return
        self.crawled += 1
        self.url_list[url] = False
        self.pool.apply_async(ivdiff.checkDiff, [self.nobrowser, self.cookies, url, self.t1, self.t2, self.browser], callback=self.callback)

    def parse_item(self, response):
        self.addToPool(response.url)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Crawl whole website and diff it')
    parser.add_argument('t1', metavar='first_template', type=str, help='first template number OR template file path')
    parser.add_argument('t2', metavar='second_template', type=str, help='second template number OR template file path')
    parser.add_argument('domain', metavar='domain', type=str, help='domain to crawl')
    parser.add_argument('--cookies', '-c', help='path to file with cookies (default is cookies.txt)', nargs='?', default="cookies.txt")
    parser.add_argument('--poolsize', '-p', help='concurrent connections count(default=5)', type=int, nargs='?', default=5)
    parser.add_argument('--nobrowser', '-n', help='do not open browser when diff is found', action='store_true')
    parser.add_argument('--browser', '-b', help='browser or path to program to open diff', nargs='?', default="")
    parser.add_argument('--ignore', '-i', help='regex with links to ignore (file or string)', nargs='+')

    args = parser.parse_args()

    settings = get_project_settings()
    settings['LOG_LEVEL'] = 'INFO'
    settings["USER_AGENT"] = "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36"

    process = CrawlerProcess(settings)

    ignore = ""
    try:
        c = open(args.ignore[0], "r")
        ignore = c.read()
        ignore = ignore.split("\n")
        c.close()
    except Exception as ex:
        ignore = args.ignore
    print(args.cookies)
    print(f"ignore: {ignore}")
    process.crawl(IvSpider, ignore=ignore, cookies=args.cookies, nobrowser=args.nobrowser, browser=args.browser, domain=args.domain, t1=args.t1, t2=args.t2, poolsize=args.poolsize)
    process.start()
