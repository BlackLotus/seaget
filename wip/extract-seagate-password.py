#!/usr/bin/python3
#
# Extract user and master passwords from Seagate hard drive ROM dumps
#
# Author: Derrick Karpo
# Date:   February 26, 2014
#

import argparse
from binascii import hexlify, unhexlify
from re import findall
import sys


def findPassword(romdump):
    # define the password regex
    PATTERN = b'00000000edfe0d90ffff.+?0c54.{8}(.{64})(.{64})'

    # open the ROM dump and attempt to locate the user and master passwords
    try:
        rom = hexlify(romdump.read())
        password = findall(PATTERN, rom)

        if len(password) == 0:
            sys.exit('No user or master passwords found.')

        for master, user in password:
            print('{0:>15}: {1:}'.format("master HEX pw", master))
            print('{0:>15}: {1:}'.format("master ASCII pw", unhexlify(master)))
            print('{0:>15}: {1:}'.format("user HEX pw", user))
            print('{0:>15}: {1:}'.format("user ASCII pw", unhexlify(user)))
    except IOError:
        sys.exit("Erroring processing file: %s" % romdump)


def main():
    # setup the argument parser for the command line arguments
    parser = argparse.ArgumentParser(
        prog='extract-seagate-password.py',
        description='Find the user and master passwords in Seagate hard drive ROM dumps.')
    parser.add_argument('romdump',
                        type=argparse.FileType('rb'),
                        help='Seagate hard drive ROM dump file')
    parser.add_argument('-v', action='version',
                        version='%(prog)s 0.1', help='Version')
    args = parser.parse_args()

    # output help and exit when no arguments are given
    if len(sys.argv) == 1:
        parser.print_help()
        return

    # attempt to locate the user and master passwords
    findPassword(args.romdump)


if __name__ == "__main__":
    main()
