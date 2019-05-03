from flask import Flask
from flask import jsonify
from flask import current_app
from flask import request
import threading
import requests
from lxml import html
import datetime
import ivdiff
import re
import json as js
import webbrowser
import time as tt
from hashlib import md5
import os
from time import sleep

app = Flask(__name__)
verify = True
webhook = "https://integram.org/webhook/yourwebhook"  # t.me/bullhorn_bot
fail_retry = 5
fail_wait_time = 20


def notify(message):
    requests.post(webhook, json={"text": message})


@app.route("/download", methods=["POST"])
def download():
    try:
        json = request.get_json()
        r = requests.get(json["url"])
        md = md5()
        md.update(json["url"].encode("utf8"))

        fn = "download/{}.html".format(str(md.hexdigest()))

        file = open(fn, "w", errors="ignore")
        file.write(r.text)
        file.close()
        path = os.path.dirname(os.path.realpath(__file__))
        os.system("\"E:\\Sublime Text 3\\subl.exe\" {}/{}".format(path, fn))
        sleep(1)
        os.system("\"E:\\Sublime Text 3\\subl.exe\" --command htmlprettify")
        sleep(1)
        os.system("\"E:\\Sublime Text 3\\subl.exe\" --command save")
        return jsonify({
            "status": "ok"
        })
    except Exception as ex:
        return jsonify({
            "status": "not ok",
            "error": str(ex)
        })


@app.route("/remove", methods=["POST"])
def remove():
    json = request.get_json()
    with app.app_context():
        if json["section"] not in current_app.delayed or str(json["rules_id"]) not in current_app.delayed[json["section"]] or json not in current_app.delayed[json["section"]][str(json["rules_id"])]:
            return jsonify({
                "status": "not ok",
                "error": "not found"
            })
        current_app.delayed[json["section"]][str(json["rules_id"])].remove(json)
        file = open("issues.json", "w")
        file.write(js.dumps(current_app.delayed))
        file.close()
    return jsonify({
        "status": "ok"
    })


@app.route("/remove_all", methods=["POST"])
def remove_all():
    json = request.get_json()
    with app.app_context():
        if json["section"] not in current_app.all or str(json["rules_id"]) not in current_app.all[json["section"]] or json not in current_app.all[json["section"]][str(json["rules_id"])]:
            return jsonify({
                "status": "not ok",
                "error": "not found"
            })
        current_app.all[json["section"]][str(json["rules_id"])].remove(json)
        file = open("issues_all.json", "w")
        file.write(js.dumps(current_app.all))
        file.close()
    return jsonify({
        "status": "ok"
    })


@app.route("/post_now", methods=["POST"])
def post_now():
    json = request.get_json()
    with app.app_context():
        if json["section"] not in current_app.delayed or str(json["rules_id"]) not in current_app.delayed[json["section"]] or json not in current_app.delayed[json["section"]][str(json["rules_id"])]:
            return jsonify({
                "status": "not ok",
                "error": "not found"
            })
        if not send_issue(json):
            return jsonify({
                "status": "not ok",
                "error": "issue failed to send"
            })
    return jsonify({
        "status": "ok"
    })


@app.route("/diff", methods=["POST"])
def diff():
    cookies = ivdiff.parseCookies("cookies.txt")
    json = request.get_json()
    print(json)
    result = ivdiff.checkDiff(False, cookies, json["url"], json["rules_id"], "~")
    if result is None or result[1] < 0:
        return jsonify({
            "status": "not ok",
            "error": result[1]
        })
    return jsonify({
        "status": "ok",
        "has_diff": result[1] == 1
    })


@app.route("/undiff", methods=["POST"])
def undiff():
    cookies = ivdiff.parseCookies("cookies.txt")
    json = request.get_json()
    print(json)
    if ivdiff.getHtml(json["section"], cookies, json["section"], "~", "~") is None:
        return jsonify({
            "status": "not ok"
        })
    return jsonify({
        "status": "ok"
    })


@app.route("/snippets", methods=["GET"])
def snippets():
    file = open("snippets.json", "r")
    ls = js.loads(file.read())
    file.close()
    return jsonify({
        "status": "ok",
        "snippets": ls
    })


@app.route("/list", methods=["GET"])
def list():
    return jsonify({
        "status": "ok",
        "list": current_app.delayed
    })


@app.route("/get_issues", methods=["POST"])
def get_issues():
    json = request.get_json()
    section = json["section"]
    rules_id = json["rules"]

    if section not in current_app.all:
        return jsonify({
            "status": "not ok",
            "error": "no such section " + section
        })
    ok = []
    for i in rules_id:
        if str(i) in current_app.all[section]:
            for j in current_app.all[section][str(i)]:
                ok.append(j)
    if len(ok) == 0:
        return jsonify({
            "status": "not ok",
            "error": "no issues for candidate"
        })

    return jsonify({
        "status": "ok",
        "list": ok
    })


def report_to_string(json):
    return f"{json['comment']}"


def send_issue(json):
    error = ""
    data = "DATA"
    report_url = f"https://instantview.telegram.org/contest/{json['section']}/template{json['rules_id']}/?url={json['url']}"
    try:
        with app.app_context():
            if json["section"] not in current_app.delayed or str(json["rules_id"]) not in current_app.delayed[json["section"]] or json not in current_app.delayed[json["section"]][str(json["rules_id"])]:
                print(f"issue {json} not found")
                return
        print("Posting issue", json)
        cookies = ivdiff.parseCookies("cookies.txt")

        d = "https://instantview.telegram.org/contest/{}/template{}".format(json["section"], json["rules_id"])

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
        random_id = ""
        for retry in range(0, fail_retry):
            try:
                r = requests.get(d, headers=headers, verify=verify, cookies=cookies, params=dict(url=json["url"]))

                hash = re.search("contest\\?hash=(.*?)\",", str(r.content)).group(1)
                print(hash)

                jj = json.copy()
                del jj["random_id"]

                headers["X-Requested-With"] = "XMLHttpRequest"
                headers["Accept"] = "application/json, text/javascript, */*; q=0.01"

                # r = requests.post("https://instantview.telegram.org/api/contest", headers=headers, verify=verify, cookies=cookies, params=dict(hash=hash), data=data)
                final = ""
                fail = tt.time()
                lastTry = False
                # total_fail = 0
                while "result_doc_url" not in final:
                    data = {**jj, "method": "processByRules", "rules": "", "random_id": random_id}
                    r = requests.post("https://instantview.telegram.org/api/contest", headers=headers, verify=verify, cookies=cookies, params=dict(hash=hash), data=data)
                    final = r.json()
                    try:
                        random_id = final["random_id"]

                        # if "status" not in final:
                        if "result_doc_url" not in final:
                            # print(time.time() - fail)
                            if tt.time() - fail >= fail_wait_time:
                                if lastTry:
                                    print(f"struggling on page for more than {fail_wait_time * 2} seconds, trying from start")
                                    return None

                                print(f"struggling on page for more than {fail_wait_time} seconds, trying without random_id")
                                random_id = ""
                                lastTry = True
                                fail = tt.time()

                    except Exception as ex:
                        print(f"{ex} {final}")
                # random_id = r.json()["random_id"]

                data = {**jj, "method": "sendIssue", "random_id": random_id}
                data["type"] = int(data["type"])
                r = requests.post("https://instantview.telegram.org/api/contest", headers=headers, verify=verify, cookies=cookies, params=dict(hash=hash), data=data)
                error = r.content

                reply = r.json()
                if "error" in reply:
                    print(f"Telegram-side error for {report_url}\n{report_to_string(json)}\n`{reply['error']}`")
                    notify(f"Telegram-side error for {report_url}\n{report_to_string(json)}\n`{reply['error']}`")
                    return False
                issue_url = "https://instantview.telegram.org/" + reply["redirect_to"]
                webbrowser.open_new_tab(issue_url)

                with app.app_context():
                    current_app.delayed[json["section"]][str(json["rules_id"])].remove(json)
                    file = open("issues.json", "w")
                    file.write(js.dumps(current_app.delayed))
                    file.close()
                    notify(f"Issue successfully sent {issue_url}")
                return True
            except Exception as ex:
                print(f"ERROR while posting issue {data} {hash}, retry {retry}, {ex}")
                notify(f"Failed to send issue `{report_to_string(json)}`\n{error}\nReport it NOW!\n{report_url}")
        return False
    except Exception as ex:
        print(ex)
        error = str(ex)
        notify(f"Failed to send issue `{json}`\n{error}\nReport it NOW!\n{report_url}\n\n{json['comment']}")
        return False


@app.route("/report", methods=["POST"])
def report():
    json = request.get_json()

    r = requests.get(f"https://instantview.telegram.org/contest/{json['section']}/template{json['rules_id']}/")
    tree = html.fromstring(r.content).xpath("//p[contains(@class, \"about-text\")]/text()")
    date = datetime.datetime.strptime(tree[1], " at %I:%M %p, %b %d.").replace(year=2019)
    reportTime = date + datetime.timedelta(days=3) - datetime.timedelta(minutes=25)
    time = reportTime - datetime.datetime.utcnow()

    print("Delaying issue", json)
    t = threading.Timer(time.total_seconds(), send_issue, [json])
    t.start()

    json["reportTime"] = str(reportTime)

    if json["section"] not in current_app.delayed:
        current_app.delayed[json["section"]] = {}
    if str(json["rules_id"]) not in current_app.delayed[json["section"]]:
        current_app.delayed[json["section"]][str(json["rules_id"])] = []
    current_app.delayed[json["section"]][str(json["rules_id"])].append(json)
    file = open("issues.json", "w")
    file.write(js.dumps(current_app.delayed))
    file.close()

    return jsonify({
        "status": "ok",
        "date": str(time)
    })


@app.route("/add_issue", methods=["POST"])
def add_issue():
    json = request.get_json()

    # r = requests.get(f"https://instantview.telegram.org/contest/{json['section']}/candidate{json['rules_id']}/")

    print("Adding issue", json)

    if json["section"] not in current_app.all:
        current_app.all[json["section"]] = {}
    if str(json["rules_id"]) not in current_app.all[json["section"]]:
        current_app.all[json["section"]][str(json["rules_id"])] = []
    current_app.all[json["section"]][str(json["rules_id"])].append(json)
    file = open("issues_all.json", "w")
    file.write(js.dumps(current_app.all))
    file.close()

    return jsonify({
        "status": "ok"
    })


if __name__ == "__main__":
    with app.app_context():
        try:
            file = open("issues.json", "r")
            current_app.delayed = js.loads(file.read())
            for domain in current_app.delayed:
                data = current_app.delayed[domain]
                for rule in data:
                    issues = data[rule]
                    for issue in issues:
                        reportTime = datetime.datetime.strptime(issue["reportTime"], "%Y-%m-%d %H:%M:%S")
                        time = reportTime - datetime.datetime.utcnow()

                        print("Delaying issue", issue)
                        t = threading.Timer(time.total_seconds(), send_issue, [issue])
                        t.start()
        except Exception as ex:
            current_app.delayed = {}

        try:
            file = open("issues_all.json", "r")
            current_app.all = js.loads(file.read())
        except Exception as ex:
            current_app.all = {}
    app.run(host="0.0.0.0", port=5000)
