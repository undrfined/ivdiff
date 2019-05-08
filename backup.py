import requests
import ivdiff
import re
from lxml import etree
import argparse
import urllib3
import json
from lxml import html
import os

htmlparser = etree.HTMLParser(remove_blank_text=True)
verify = True
if not verify:
    urllib3.disable_warnings()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0"
}


def getHashAndRules(domain, url, cookies):
    d = "https://instantview.telegram.org/my/{}".format(domain)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": d,
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0"
    }

    while True:
        r = requests.get(d, headers=headers, verify=verify, cookies=cookies, params=dict(url=url))
        cookies = dict(list(cookies.items()) + list(r.cookies.get_dict().items()))

        hash = re.search("my\\?hash=(.*?)\",", str(r.content)).group(1)
        tree = html.fromstring(r.content.decode("utf8"))

        rules = json.loads(re.search("initWorkspace\\(\".*?\",(.*)\\);", tree.xpath("//script[last()]/text()")[0]).group(1))

        try:
            return (rules["rules"], hash, cookies)
        except Exception:
            print("retry")
            pass


def getAll(cookies):
    r = requests.get("https://instantview.telegram.org/my", headers=headers, cookies=cookies)
    h = html.fromstring(r.content)
    fn = "backup/"
    try:
        os.makedirs(os.path.dirname(fn))
    except Exception:
        pass
    for i in h.xpath("//h3/a[@class=\"section-header\"]/text()"):
        print(i)
        rules, hash, cc = getHashAndRules(i, i, cookies)
        f = open(fn + i + ".xpath", "w", encoding='utf8')
        f.write(rules)
        f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Backup all templates')
    parser.add_argument('--cookies', '-c', help='path to file with cookies (default is cookies.txt)', nargs='?', default="cookies.txt")

    args = parser.parse_args()
    cookies = ivdiff.parseCookies(args.cookies)
    getAll(cookies)
