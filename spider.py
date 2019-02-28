import scrapy
from ivdiff import checkDiff
from urllib.parse import urlparse
from multiprocessing import Pool
from scrapy.crawler import CrawlerProcess
import argparse


class IvSpider(scrapy.Spider):
    name = 'IvSpider'
    dupl = []

    def __init__(self, domain="", cookies="cookies.txt", poolsize=5, **kwargs):
        if not domain.startswith("http"):
            domain = "http://" + domain
        self.start_urls = [domain]

        d = urlparse(domain).netloc
        if domain.startswith("www."):
            d = domain[4:]

        self.allowed_domains = [d]

        self.pool = Pool(5)

        self.cookies = cookies

        super().__init__(**kwargs)

    def addToPool(self, url):
        self.pool.apply_async(checkDiff, [self.cookies, url, self.t1, self.t2])
        pass

    def parse(self, response):
        for i in response.xpath("//a/@href"):
            z = i.extract()
            yield response.follow(i.extract(), self.parse)

            if z.startswith("//"):
                z = "http://" + self.allowed_domains[0] + z
            if z.startswith("/"):
                z = "http://" + self.allowed_domains[0] + z
            if not z.startswith("http"):
                continue
            if self.allowed_domains[0] not in i.extract():
                continue
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

    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })

    process.crawl(IvSpider, domain=args.domain, t1=args.t1, t2=args.t2, poolsize=args.poolsize)
    process.start()
