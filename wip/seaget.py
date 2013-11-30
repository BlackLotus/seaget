#!/usr/bin/python2
#clean rewrite and combination of all my old python scripts
import argparse

class SeaGet:
    pass

def main():
    parser = argparse.ArgumentParser(description='Dump memory/buffer of a seagate hd using a serial connection.')
    parser.add_argument('--dump', metavar='memory/buffer', nargs=1, default=['memory'], help='What gets dumped')
    parser.add_argument('--baud', metavar=38400, default=38400, help='current baud rate [38400,115200]')
    parser.add_argument('--new-baud', metavar=115200, default=115200, help='set new baud rate [38400,115200]')
    parser.add_argument('-c', dest='cont', action='store_const', const=True, help='Continue dump')
    parser.add_argument('filename', metavar='dumpfile', help='the name of the dump file, duh')
    args = parser.parse_args()
    print args

if __name__ == '__main__':
    main()

