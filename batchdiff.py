import ivdiff
from multiprocessing import Pool
from multiprocessing import Event
import argparse
import json
import ctypes
import readchar


parsed = 0
crawled = 0
have_diff = 0
olds = 0


def callback(roflan):
    global parsed, have_diff
    parsed += 1
    if roflan is None or roflan[1] == -1:
        print(f"an error occured for url {roflan[0]}")
        return
    if roflan[1] == 1:
        have_diff += 1
    ctypes.windll.kernel32.SetConsoleTitleW(f"{(parsed / crawled * 100):.2f}% [{parsed} / crawled {crawled}] (w/ diff {have_diff}, old {olds}) | diffed {roflan[0]}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Diff the whole file full of links D:')
    parser.add_argument('t1', metavar='first_template', type=str, help='first template number OR template file path')
    parser.add_argument('t2', metavar='second_template', type=str, help='second template number OR template file path')
    parser.add_argument('file', type=str, help='file with links to diff')
    parser.add_argument('--cookies', '-c', help='path to file with cookies (default is cookies.txt)', nargs='?', default="cookies.txt")
    parser.add_argument('--poolsize', '-p', help='concurrent connections count(default=5)', type=int, nargs='?', default=5)
    parser.add_argument('--nobrowser', '-n', help='do not open browser when diff is found', action='store_true')
    parser.add_argument('--browser', '-b', help='browser or path to program to open diff', nargs='?', default="")

    args = parser.parse_args()

    event = Event()
    p = Pool(args.poolsize, ivdiff.setup, (event,))
    event.set()
    cookies = ivdiff.parseCookies(args.cookies)

    f = list(json.loads(open(args.file, "r").read()).values())[::-1]
    print("Total: {}".format(len(f)))
    crawled = len(f)
    z = 0
    for i in f:
        p.apply_async(ivdiff.checkDiff, [args.nobrowser, cookies, i, args.t1, args.t2, args.browser], callback=callback)
    pause = False
    while True:
        e = readchar.readchar()
        if e == b'q':
            print("quit")
            break

        if e == b'k':
            p.terminate()
            print("Killed pool")

        if e == b' ':
            pause = not pause
            if pause:
                event.clear()
            else:
                event.set()
            print(f"pause = {pause}")
