import scrapy
import ivdiff
from urllib.parse import urlparse
from multiprocessing import Pool, Event, Process
from scrapy.crawler import CrawlerProcess, CrawlerRunner
import argparse
from scrapy.utils.project import get_project_settings
import os
import json
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
import ctypes
from twisted.internet import reactor
from threading import Thread
import readchar
from lxml import etree
import re


class IvSpider(scrapy.spiders.CrawlSpider):
    name = 'IvSpider'
    dupl = []
    url_list = {}
    crawled = 0
    parsed = 0
    olds = 0
    have_diff = 0

    def __init__(self, pool, event=None, whitelist=[], ignore="", restrict_xpaths="", nobrowser=False, browser="", domain="", cookies="cookies.txt", poolsize=5, **kwargs):
        if not domain.startswith("http"):
            domain = "http://" + domain
        self.start_urls = [domain]

        d = urlparse(domain).netloc
        if domain.startswith("www."):
            d = domain[4:]

        self.allowed_domains = [d, d + ":443"]
        self.browser = browser
        self.whitelist = whitelist
        self.nobrowser = nobrowser
        self.ignore = ignore

        self.restrict_xpaths = restrict_xpaths
        self.pool = pool
        self.rules = [Rule(LinkExtractor(allow=(), allow_domains=self.allowed_domains, deny=(ignore), deny_domains=("reklama.oblast45.ru")), callback='parse_item', follow=True)]

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
        if roflan is None or roflan[1] == -1:
            print(f"an error occured for url {roflan[0]}")
            return
        if roflan[1] == 1:
            self.have_diff += 1
        ctypes.windll.kernel32.SetConsoleTitleW(f"{(self.parsed / self.crawled * 100):.2f}% [{self.parsed} / crawled {self.crawled}] (w/ diff {self.have_diff}, old {self.olds}) | diffed {roflan[0]}")
        # print("{0:.2f}% [{1} / crawled {2}] (w/ diff {3}) {4}".format(self.parsed / self.crawled * 100, self.parsed, self.crawled, self.have_diff, roflan[0]))
        self.url_list[roflan[0]] = True
        self.file.seek(0)
        self.file.truncate(0)
        self.file.seek(0)
        self.file.write(json.dumps(self.url_list))
        self.file.seek(0)

    def addToPool(self, url):
        if url in self.url_list:
            if not self.url_list[url]:
                pass
                self.pool.apply_async(ivdiff.checkDiff, [self.nobrowser, self.cookies, url, self.t1, self.t2, self.browser], callback=self.callback)
            return
        self.crawled += 1
        self.url_list[url] = False
        ctypes.windll.kernel32.SetConsoleTitleW(f"{(self.parsed / self.crawled * 100):.2f}% [{self.parsed} / crawled {self.crawled}] (w/ diff {self.have_diff}, old {self.olds}) | added {url} to pool")
        self.pool.apply_async(ivdiff.checkDiff, [self.nobrowser, self.cookies, url, self.t1, self.t2, self.browser], callback=self.callback)

    def parse_item(self, response):
        for i in self.restrict_xpaths:
            if len(response.xpath(i)) > 0:
                # print(f"restrict {etree.tostring(response.xpath(i)[0], pretty_print=True)}")
                self.olds += 1
                return
        for i in self.whitelist:
            if len(response.xpath(i)) > 0:
                self.addToPool(response.url)
        if len(self.whitelist) == 0:
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
    parser.add_argument('--restrict_xpaths', '-r', help='xpath to ignore', nargs='+')
    parser.add_argument('--whitelist', '-w', help='xpath of what pages should be crawled', nargs='+')

    args = parser.parse_args()

    settings = get_project_settings()
    settings['LOG_LEVEL'] = 'INFO'
    settings["QUERYCLEANER_REMOVE"] = ".*"
    settings['SPIDER_MIDDLEWARES'] = {
        'scrapy_querycleaner.QueryCleanerMiddleware': 100
    }
    settings["USER_AGENT"] = "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36"

    # process = CrawlerProcess(settings)
    event = Event()
    pool = Pool(args.poolsize, ivdiff.setup, (event,))
    event.set()

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

    # spider = IvSpider(ignore=ignore, cookies=args.cookies, nobrowser=args.nobrowser, browser=args.browser, domain=args.domain, t1=args.t1, t2=args.t2, poolsize=args.poolsize)
    # crawler = CrawlerProcess(get_project_settings())
    # process = Process(target=crawler.start, stop_after_crawl=False)

    # crawler = CrawlerScript(spider)
    print(args.restrict_xpaths)
    if args.restrict_xpaths is None:
        args.restrict_xpaths = []
    if args.whitelist is None:
        args.whitelist = []
    whitelist = [re.sub(r"has-class\((\".*?\")\)", "contains(concat(' ', normalize-space(@class), ' '), \\1)", i) for i in args.whitelist]
    restrict_xpaths = [re.sub(r"has-class\((\".*?\")\)", "contains(concat(' ', normalize-space(@class), ' '), \\1)", i) for i in args.restrict_xpaths]

    crawler = CrawlerProcess(settings)
    d = crawler.crawl(IvSpider, pool=pool, event=event, restrict_xpaths=args.restrict_xpaths, ignore=ignore, cookies=args.cookies, nobrowser=args.nobrowser, browser=args.browser, domain=args.domain, t1=args.t1, t2=args.t2, poolsize=args.poolsize)
    d.addBoth(lambda _: reactor.stop())
    pause = False
    Thread(target=reactor.run, args=(False,)).start()
    crawl_paused = False

    while True:
        e = readchar.readchar()
        if e == b'r':
            reactor.stop()
            print("Killed reactor")

        if e == b'q':
            print("quit")
            break

        if e == b'k':
            pool.terminate()
            print("Killed pool")

        if e == b' ':
            pause = not pause
            if pause:
                event.clear()
            else:
                event.set()
            print(f"pause = {pause}")

    # process.crawl(IvSpider, event=event, ignore=ignore, cookies=args.cookies, nobrowser=args.nobrowser, browser=args.browser, domain=args.domain, t1=args.t1, t2=args.t2, poolsize=args.poolsize)
    # process.start()

    # while True:
    #     i = input()
    #     print(i)
