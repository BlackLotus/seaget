#!/usr/bin/python2
import re
import sys
import binascii

f=binascii.hexlify(open(sys.argv[1],'r').read())
pwsR=re.compile('00000000edfe0d90ffff.+?00000c54.{8}(.{64})(.{64})')
pws=pwsR.findall(f)
for pw in pws[0]:
    print pw
    print pw.decode("hex")
