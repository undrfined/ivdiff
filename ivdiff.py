import logging
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
from hashlib import md5
import time
import copy
import urllib3

logging.basicConfig(filename="ivdiff.log", level=logging.INFO)
htmlparser = etree.HTMLParser(remove_blank_text=True)
verify = True
if not verify:
    urllib3.disable_warnings()


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
    logging.info("-- Getting html for {} --".format(url.encode("ascii")))
    # print("-- Getting html for {} --".format(url.encode("ascii")))

    r = requests.get(d, headers=headers, verify=verify, cookies=cookies, params=dict(url=url))
    cookies = dict(list(cookies.items()) + list(r.cookies.get_dict().items()))

    hash = re.search("{}\\?hash=(.*?)\",".format(contest), str(r.content)).group(1)
    # logging.info("hash={}".format(hash))
    # print(f"got hash {hash}")

    rules = rules.encode('utf-8')
    headers["X-Requested-With"] = "XMLHttpRequest"
    headers["Accept"] = "application/json, text/javascript, */*; q=0.01"
    r = requests.post("https://instantview.telegram.org/api/{}".format(contest), headers=headers, verify=verify, cookies=cookies, params=dict(hash=hash), data=dict(url=url, section=domain, method="processByRules", rules_id=templNumber, rules=rules, random_id=""))
    random_id = r.json()["random_id"]
    # logging.info("random_id={}".format(random_id))
    # print(f"got random id {random_id}")

    final = ""
    fail = time.time()
    lastTry = False
    # total_fail = 0
    while "result_doc_url" not in final:
        logging.info("trying again... {}".format(final))

        r = requests.post("https://instantview.telegram.org/api/{}".format(contest), headers=headers, verify=verify, cookies=cookies, params=dict(hash=hash), data=dict(url=url, section=domain, method="processByRules", rules_id=templNumber, rules=rules, random_id=random_id))
        final = r.json()
        random_id = final["random_id"]

        if "status" not in final:
            if "result_doc_url" not in final:
                # print(time.time() - fail)
                if time.time() - fail >= 5:
                    if lastTry:
                        print(f"struggling on page for more than 10 seconds, trying from start in 45s {url}")
                        return None

                    print(f"struggling on page for more than 5 seconds, trying without random_id {url}")
                    random_id = ""
                    lastTry = True
                    fail = time.time()

                # time.sleep(5)

                # r = requests.get(d, cookies=cookies, params=dict(url=url), verify=verify)
                # hash = re.search("{}\\?hash=(.*?)\",".format(contest), str(r.content)).group(1)
                # logging.info("new hash={}".format(hash))

                # r = requests.post("https://instantview.telegram.org/api/{}".format(contest), verify=verify, cookies=cookies, params=dict(hash=hash), data=dict(url=url, section=domain, method="processByRules", rules_id=templNumber, rules=rules, random_id=""))
                # random_id = r.json()["random_id"]
                # logging.info("new random_id={}".format(random_id))
        else:
            pass
            # This is only available for templates from "my" section
            # print(final)
            # tree = etree.parse(final["status"], htmlparser)
            # print("Status: " + tree.xpath("//text()")[0])

    random_id = final["random_id"]
    u = final["result_doc_url"]
    preview_html = final["preview_html"]

    logging.info("loading page {}".format(u))
    r = requests.get(u, verify=verify, cookies=cookies)
    if r.status_code != 200:
        print(f"{r.status_code}, trying again {url}")
        return None

    if "NESTED_ELEMENT_NOT_SUPPORTED" in str(r.content):
        logging.error("NESTED_ELEMENT_NOT_SUPPORTED in {}".format(url))

    tree = etree.parse(StringIO(str(r.content.decode("utf-8"))), htmlparser)
    if preview_html is not False:
        preview_html_tree = etree.parse(StringIO(preview_html), htmlparser)
    else:
        preview_html_tree = None

    logging.info("-- FINISHED --")
    return (d + "?url=" + url, tree, preview_html_tree, cookies)


def compare(f, s):
    # You can remove elements before diff if you want to

    # for bad in s.xpath("//h6[@data-block=\"Kicker\"]"):
    #     bad.getparent().remove(bad)
    # for bad in f.xpath("//footer[last()]"):
    #    bad.getparent().remove(bad)

    # for img in f.xpath("//img"):
    #    del img.attrib["src"]
    # for img in s.xpath("//img"):
    #    del img.attrib["src"]

    pass


def checkDiff(nobrowser, cookies, url, t1, t2, browser=""):
    # print(f"checkDiff {cookies}")
    if not url.startswith("http"):
        url = "http://" + url

    domain = urlparse(url).netloc
    if domain.startswith("www."):
        domain = domain[4:]

    f1 = None
    s1 = None

    # TODO switch to next cookie if this fails too much
    # For now just start over with the same cookie
    cookies = [cookies]
    cookie = -1
    while f1 is None:
        cookie += 1
        if cookie >= len(cookies):
            cookie = 0
            time.sleep(45)
        f1 = getHtml(domain, cookies[cookie], url, t1)

    cookie = -1
    while s1 is None:
        cookie += 1
        if cookie >= len(cookies):
            cookie = 0
            time.sleep(45)
        s1 = getHtml(domain, cookies[cookie], url, t2)

    if f1 is None or s1 is None:
        return (url, -1, cookies)
    f = f1[1]
    s = s1[1]
    preview_html_first = f1[2]
    preview_html_second = s1[2]

    compare(f, s)

    a1 = f.xpath("//article")

    if len(a1) == 0:
        a1 = f.xpath("//section[@class=\"message\"]")
        copy1 = copy.deepcopy(a1)
    else:
        copy1 = copy.deepcopy(a1)
        for img in copy1[0].xpath("//img"):
            del img.attrib["src"]
        if preview_html_first is not None:
            copy1[0].append(copy.deepcopy(preview_html_first).xpath("//div[@class='page-preview']")[0])

    a2 = s.xpath("//article")
    if len(a2) == 0:
        a2 = s.xpath("//section[@class=\"message\"]")
        copy2 = copy.deepcopy(a2)
    else:
        copy2 = copy.deepcopy(a2)
        for img in copy2[0].xpath("//img"):
            del img.attrib["src"]
        if preview_html_second is not None:
            copy2[0].append(copy.deepcopy(preview_html_second).xpath("//div[@class='page-preview']")[0])

    diff = difflib.HtmlDiff(wrapcolumn=90).make_file(etree.tostring(copy1[0], pretty_print=True, encoding='UTF-8').decode("utf-8").split("\n"), etree.tostring(copy2[0], pretty_print=True, encoding='UTF-8').decode("utf-8").split("\n"))
    htmlparser = etree.HTMLParser(remove_blank_text=True)
    tree = etree.parse(StringIO(str(diff)), htmlparser)

    frame1_link = f.xpath("//head/link")
    frame1_link[0].attrib["href"] = "https://ivwebcontent.telegram.org{}".format(frame1_link[0].attrib["href"])
    frame1_script = f.xpath("//head/script[@src]")
    frame1_script[0].attrib["src"] = "../../instantview-frame.js"

    tree.xpath("//head")[0].append(frame1_link[0])
    tree.xpath("//head")[0].append(frame1_script[0])

    htmlparser = etree.HTMLParser(remove_blank_text=True, encoding='utf-8')
    append = etree.parse(open("append.html", "r", encoding='utf8'), htmlparser)

    frames = append.xpath("//div[contains(@id, 'frame')]")
    frames[0].append(a1[0])
    frames[1].append(a2[0])

    previews = append.xpath("//div[contains(@id, 'preview')]")
    if preview_html_first is not None:
        previews[0].append(preview_html_first.xpath("//div[@class='page-preview']")[0])
    if preview_html_second is not None:
        previews[1].append(preview_html_second.xpath("//div[@class='page-preview']")[0])

    first_link = append.xpath("//a[@id='first_template']")[0]
    first_link.attrib["href"] = f1[0]
    first_link.text = "Template {}\n".format(t1)

    second_link = append.xpath("//a[@id='second_template']")[0]
    second_link.attrib["href"] = s1[0]
    second_link.text = "Template {}\n".format(t2)

    append.xpath("//input")[0].attrib["value"] = url

    tree.xpath("//body//table")[0].addprevious(append.xpath("//main/div[1]")[0])
    tree.xpath("//body//table")[0].addnext(append.xpath("//main/div[1]")[0])

    for bad in tree.xpath("//table[@summary='Legends']"):
        bad.getparent().remove(bad)
    final = etree.tostring(tree, pretty_print=True).decode("utf-8")

    # ДУМОТЬ ВСО ЕСЧО ВПАДЛУ
    # ХТО ЗАРЖАВ СТАВ РОФЛАН ЇБАЛО
    if "class=\"diff_add\"" in final or "class=\"diff_chg\"" in final or "class=\"diff_sub\"" in final:
        md = md5()
        md.update(url.encode('utf-8'))

        fn = "gen/{}/{}_{}_{}.html".format(domain, t1, t2, str(md.hexdigest()))
        try:
            os.makedirs(os.path.dirname(fn))
        except Exception:
            pass
        file = open(fn, "w")
        file.write(final)
        file.close()
        if not nobrowser:
            browser = webbrowser if browser == "" else webbrowser.get(browser)
            browser.open_new_tab("file:///{}/{}".format(os.getcwd(), fn))
        return (url, 1, cookies)
    else:
        return (url, 0, cookies)


def parseCookies(cookiesFile):
    c = open(cookiesFile, "r")
    cl = c.read()
    c.close()

    cookie = SimpleCookie()
    cookie.load(cl)

    cookies = {}
    for key, morsel in cookie.items():
        cookies[key] = morsel.value
    return cookies


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get pretty HTML diff between two IV templates.')
    parser.add_argument('t1', metavar='first_template', type=str, help='first template number OR template file path')
    parser.add_argument('t2', metavar='second_template', type=str, help='second template number OR template file path')
    parser.add_argument('url', metavar='url', nargs='+', type=str, help='original page url to diff')
    parser.add_argument('--cookies', '-c', help='path to file with cookies (default is cookies.txt)', nargs='?', default="cookies.txt")
    parser.add_argument('--nobrowser', '-n', help='do not open browser when diff is found', action='store_true')
    parser.add_argument('--browser', '-b', help='browser or path to program to open diff', nargs='?', default="")

    args = parser.parse_args()
    for i in args.url:
        cookies = parseCookies(args.cookies)
        checkDiff(args.nobrowser, cookies, i, args.t1, args.t2, args.browser)
