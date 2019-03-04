import requests
import argparse
import ivdiff
import time


def auth(phone, file):
    d = "https://instantview.telegram.org/"
    r = requests.get(d)
    cookies = r.cookies

    r = requests.post(d + "auth/request", cookies=cookies, data={"phone": phone}, headers={"X-Requested-With": "XMLHttpRequest"})
    try:
        temp_session = r.json()["temp_session"]
    except Exception:
        print("Error: {}".format(r.content.decode("utf-8")))
        return

    print("waiting for request approval...")
    while r.content != b"true":
        r = requests.post(d + "auth/login", cookies=cookies, data={"temp_session": temp_session}, headers={"X-Requested-With": "XMLHttpRequest"})
    cookies = requests.cookies.merge_cookies(cookies, r.cookies).get_dict()
    print("success! getting stel_ivs...")

    stel_ivs = None
    while stel_ivs is None:
        print("getting stel_ivs...")
        # Domain and url can be actually anything, just make sure it exists in the contest
        r = ivdiff.getHtml("5minutes.rtl.lu", cookies, "5minutes.rtl.lu", 1)
        if r is not None and "stel_ivs" in r[3]:
            stel_ivs = r[3]
        else:
            time.sleep(10)
    print(f"success! {stel_ivs}")
    cookies = stel_ivs

    with open(file, 'wb') as f:
        for i, v in cookies.items():
            f.write("{}={}; ".format(i, v).encode("utf-8"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Auth to IV and get cookies.txt file')
    parser.add_argument('phone', type=str, help='phone number')
    parser.add_argument('--cookies', '-c', help='path to file to write cookies to (default is cookies.txt)', nargs='?', default="cookies.txt")

    args = parser.parse_args()
    auth(args.phone, args.cookies)
