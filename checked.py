import requests
import ivdiff
import re
from lxml import etree
from io import StringIO
import argparse
import urllib3
from functools import partial
import json


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


def getHashAndRules(domain, cookies):
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

    r = requests.get(d, headers=headers, verify=verify, cookies=cookies, params=dict(url=domain))
    hash = re.search("my\\?hash=(.*?)\",", str(r.content)).group(1)
    rules = json.loads(re.search("initWorkspace\\(\".*?\",(.*?)\\);", str(r.content.decode("utf8"))).group(1))
    return (rules["rules"], hash)


def checkAll(domain, cookies):
    rules, hash = getHashAndRules(domain, cookies)
    r = requests.post("https://instantview.telegram.org/api/my", headers=headers, verify=verify, cookies=cookies, params=dict(hash=hash), data=dict(url=domain, section=domain, method="processByRules", rules_id="", rules=rules, random_id=""))
    rid = r.json()["random_id"]
    r = requests.post("https://instantview.telegram.org/api/my", headers=headers, verify=verify, cookies=cookies, params=dict(hash=hash), data=dict(url=domain, section=domain, method="getSectionData"))
    tree = etree.parse(StringIO(r.json()["items"]), htmlparser)
    list(map(partial(check, domain, cookies, rid, hash), tree.xpath("//h4/text()")))


def check(domain, cookies, rid, hash, url):
    print(url)
    headers["X-Requested-With"] = "XMLHttpRequest"
    headers["Accept"] = "application/json, text/javascript, */*; q=0.01"
    r = []
    while r is False or "contest_ready" not in r:
        r = requests.post("https://instantview.telegram.org/api/my", headers=headers, verify=verify, cookies=cookies, params=dict(hash=hash), data=dict(random_id=rid, url=url, section=domain, method="markUrlAsChecked")).json()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Mark all the IV templates as checked.')
    parser.add_argument('domain', metavar='domain', type=str, help='domain where script should check all the pages')
    parser.add_argument('--cookies', '-c', help='path to file with cookies (default is cookies.txt)', nargs='?', default="cookies.txt")

    args = parser.parse_args()
    cookies = ivdiff.parseCookies(args.cookies)
    checkAll(args.domain, cookies)
