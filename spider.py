import scrapy
from ivdiff import checkDiff
from urllib.parse import urlparse
from multiprocessing import Pool
from scrapy.crawler import CrawlerProcess
import argparse
from scrapy.utils.project import get_project_settings
import os
from urllib.parse import urljoin


class IvSpider(scrapy.Spider):
    name = 'IvSpider'
    dupl = []
    total = 0
    parsed = 0

    def __init__(self, domain="", cookies="cookies.txt", poolsize=5, **kwargs):
        if not domain.startswith("http"):
            domain = "http://" + domain
        self.start_urls = [domain]

        d = urlparse(domain).netloc
        if domain.startswith("www."):
            d = domain[4:]

        self.allowed_domains = [d]

        self.pool = Pool(poolsize)

        self.cookies = cookies
        fn = "gen/{}/parsed.txt".format(d)
        try:
            os.makedirs(os.path.dirname(fn))
        except Exception:
            pass

        try:
            self.dupl = list(open(fn, "r"))
        except Exception:
            pass
        self.dupl = list(map(lambda s: s.strip(), self.dupl))
        print(self.dupl)
        self.file = open(fn, "a")
        super().__init__(**kwargs)

    def callback(self, roflan):
        self.parsed += 1
        print("{0:.2f}% [{1} / {2}] {3}".format(self.parsed / self.total * 100, self.parsed, self.total, roflan))
        self.file.write("{}\n".format(roflan))

    def addToPool(self, url):
        self.total += 1
        self.pool.apply_async(checkDiff, [self.cookies, url, self.t1, self.t2], callback=self.callback)
        pass

    def parse(self, response):
        for i in response.xpath("//a/@href"):
            z = i.extract()
            if z.endswith(".jpg") or z.endswith(".png") or z.endswith(".gif") or z.endswith(".jpeg"):
                continue
            z = urljoin(response.url, z.strip())
            domain = urlparse(z).netloc
            if domain.startswith("www."):
                domain = domain[4:]
            if not domain.startswith(self.allowed_domains[0]):
                continue
            yield response.follow(z, self.parse)
            if z in self.dupl:
                continue
            self.dupl.append(z)
            self.addToPool(z)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Crawl whole website and diff it')
    parser.add_argument('t1', metavar='first_template', type=str, help='first template number OR template file path')
    parser.add_argument('t2', metavar='second_template', type=str, help='second template number OR template file path')
    parser.add_argument('domain', metavar='domain', type=str, help='domain to crawl')
    parser.add_argument('--cookies', '-c', help='path to file with cookies (default is cookies.txt)', nargs='?', default="cookies.txt")
    parser.add_argument('--poolsize', '-p', help='concurrent connections count(default=5)', type=int, nargs='?', default=5)

    args = parser.parse_args()

    settings = get_project_settings()
    settings['LOG_LEVEL'] = 'INFO'
    settings["USER_AGENT"] = "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36"

    process = CrawlerProcess(settings)

    process.crawl(IvSpider, domain=args.domain, t1=args.t1, t2=args.t2, poolsize=args.poolsize)
    process.start()
