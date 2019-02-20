import requests
import re
from lxml import etree
from io import StringIO
import difflib
import webbrowser
import os
import argparse
from urllib.parse import urlparse
from http.cookies import SimpleCookie


def getHtml(domain, cookies, url, template):
    rules = ""
    try:
        templNumber = str(int(template))
        contest = "contest"
    except ValueError:
        la = open(template, "r", encoding='utf8')
        rules = str(la.read())
        la.close()
        contest = "my"
        templNumber = ""

    if contest == "my":
        d = "https://instantview.telegram.org/{}/{}".format(contest, domain)
    else:
        d = "https://instantview.telegram.org/{}/{}/template{}".format(contest, domain, templNumber)
    r = requests.get(d, cookies=cookies, params=dict(url=url))

    hash = re.search("{}\\?hash=(.*?)\",".format(contest), str(r.content)).group(1)

    rules = rules.encode('utf-8')

    r = requests.post("https://instantview.telegram.org/api/{}".format(contest), cookies=cookies, params=dict(hash=hash), data=dict(url=url, section=domain, method="processByRules", rules_id=templNumber, rules=rules, random_id=""))
    random_id = r.json()["random_id"]

    final = ""
    while "result_doc_url" not in final:
        r = requests.post("https://instantview.telegram.org/api/{}".format(contest), cookies=cookies, params=dict(hash=hash), data=dict(url=url, section=domain, method="processByRules", rules_id=templNumber, rules=rules, random_id=random_id))
        final = r.json()

    random_id = final["random_id"]
    u = final["result_doc_url"]

    r = requests.get(u, cookies=cookies)

    htmlparser = etree.HTMLParser(remove_blank_text=True)
    tree = etree.parse(StringIO(str(r.content)), htmlparser)
    return tree


def checkDiff(cookies, url, t1, t2):
    domain = urlparse(url).netloc
    if domain.startswith("www."):
        domain = domain[4:]

    c = open(cookies, "r")
    cl = c.read()
    c.close()

    cookie = SimpleCookie()
    cookie.load(cl)

    cookies = {}
    for key, morsel in cookie.items():
        cookies[key] = morsel.value

    f = getHtml(domain, cookies, url, t1)
    s = getHtml(domain, cookies, url, t2)

    a1 = f.xpath("//article")
    if len(a1) == 0:
        a1 = f.xpath("//section[@class=\"message\"]")
    a2 = s.xpath("//article")
    if len(a2) == 0:
        a2 = f.xpath("//section[@class=\"message\"]")
    diff = difflib.HtmlDiff(wrapcolumn=120).make_file(etree.tostring(a1[0], pretty_print=True).decode("utf-8").split("\n"), etree.tostring(a2[0], pretty_print=True).decode("utf-8").split("\n"))

    # ДУМОТЬ БЫЛО ВПАДЛУ
    # ХТО ПОСМЕЯВСЯ СТАВЬ ЛАЙК
    if "class=\"diff" in diff:
        fn = "diff_{}_{}_{}.html".format(domain, t1, t2)
        file = open(fn, "w")
        file.write(diff)
        file.close()
        webbrowser.open_new_tab("file:///{}/{}".format(os.getcwd(), fn))


parser = argparse.ArgumentParser(description='Get pretty HTML diff between two IV templates.')
parser.add_argument('url', metavar='url', type=str, help='original page url to diff')
parser.add_argument('t1', metavar='first_template', type=str, help='first template number OR template file path')
parser.add_argument('t2', metavar='second_template', type=str, help='second template number OR template file path')
parser.add_argument('--cookies', '-c', help='path to file with cookies (default is cookies.txt)', nargs='?', default="cookies.txt")

args = parser.parse_args()
checkDiff(args.cookies, args.url, args.t1, args.t2)
