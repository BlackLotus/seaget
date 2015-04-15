#!/usr/bin/python3
#
# Extract user and master passwords from Seagate hard drive ROM dumps
#
# Author: Derrick Karpo
# Date:   February 26, 2014
#

import argparse
from binascii import hexlify, unhexlify
from re import search
import sys


def findPassword(romdump):
    # define the password regex
    PATTERN = b'00000000edfe0d90ffff.+?0c54.{8}(.{64})(.{64})'

    # open the ROM dump and attempt to locate the user and master passwords
    try:
        rom = hexlify(romdump.read())
        password = search(PATTERN, rom)

        if not password:
            sys.exit("No user or master passwords found in '%s'" % romdump.name)

        # dump out the found passwords
        master = password.group(1)
        user = password.group(2)
        print('{0:>15}: {1:}'.format("File name", romdump.name))
        print('{0:>15}: {1:.0f}'.format("Byte offset", password.start()/2))
        print('{0:>15}: {1:}'.format("master HEX pw", master))
        print('{0:>15}: {1:}'.format("master ASCII pw", unhexlify(master)))
        print('{0:>15}: {1:}'.format("user HEX pw", user))
        print('{0:>15}: {1:}'.format("user ASCII pw", unhexlify(user)))
        print()
    except IOError:
        sys.exit("Erroring processing file: %s" % romdump)


def main():
    # setup the argument parser for the command line arguments
    parser = argparse.ArgumentParser(
        prog='extract-seagate-password.py',
        description='Extract user and master passwords from Seagate hard drive ROM dumps.')
    parser.add_argument('romdump', nargs='+',
                        type=argparse.FileType('rb'),
                        help='Seagate hard drive ROM dump file(s)')
    parser.add_argument('-v', action='version',
                        version='%(prog)s 0.2', help='Version')
    args = parser.parse_args()

    # output help and exit when no arguments are given
    if len(sys.argv) == 1:
        parser.print_help()
        return

    # attempt to locate the user and master passwords
    for fn in args.romdump:
        findPassword(fn)


if __name__ == "__main__":
    main()
