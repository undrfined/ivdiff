import requests
import argparse


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
    print("success!")

    with open(file, 'wb') as f:
        for i, v in cookies.items():
            f.write("{}={}; ".format(i, v).encode("utf-8"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Auth to IV and get cookies.txt file')
    parser.add_argument('phone', type=str, help='phone number')
    parser.add_argument('--cookies', '-c', help='path to file to write cookies to (default is cookies.txt)', nargs='?', default="cookies.txt")

    args = parser.parse_args()
    auth(args.phone, args.cookies)
