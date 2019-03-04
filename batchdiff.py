import ivdiff
from multiprocessing import Pool
import argparse
from functools import partial


def check(nobrowser, browser, cookies, t1, t2, i):
    n = i.rstrip("\n\r").rstrip("\n")
    print("Trying {0}".format(n))
    ivdiff.checkDiff(nobrowser, cookies, n, t1, t2, browser)


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

    p = Pool(args.poolsize)
    cookies = ivdiff.parseCookies(args.cookies)

    f = list(open(args.file, "r"))
    func = partial(check, args.nobrowser, args.browser, cookies, args.t1, args.t2)
    print("Total: {}".format(len(f)))
    z = 0
    p.map(func, f)
