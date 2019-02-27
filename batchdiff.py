from ivdiff import checkDiff
from multiprocessing import Pool
import argparse
from functools import partial
import signal


def check(cookies, t1, t2, i):
    n = i.rstrip("\n\r").rstrip("\n")
    print("Trying {0}".format(n))
    checkDiff(cookies, n, t1, t2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Diff the whole file full of links D:')
    parser.add_argument('t1', metavar='first_template', type=str, help='first template number OR template file path')
    parser.add_argument('t2', metavar='second_template', type=str, help='second template number OR template file path')
    parser.add_argument('file', type=str, help='file with links to diff')
    parser.add_argument('--cookies', '-c', help='path to file with cookies (default is cookies.txt)', nargs='?', default="cookies.txt")
    parser.add_argument('--poolsize', '-p', help='concurrent connections count(default=5)', type=int, nargs='?', default=5)

    args = parser.parse_args()

    original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
    p = Pool(args.poolsize)
    signal.signal(signal.SIGINT, original_sigint_handler)

    f = list(open(args.file, "r"))
    func = partial(check, args.cookies, args.t1, args.t2)
    print("Total: {}".format(len(f)))
    z = 0
    p.map(func, f)
