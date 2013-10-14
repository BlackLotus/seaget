import sys
import re

fooR=re.compile('\d\d\d\d\d\d\d\d\s+(.+)\r')
mem=open(sys.argv[1],'r')
mfile=mem.read()
mem.close()
foo=fooR.findall(mfile)
for line in foo:
    print re.sub(' ','',line)
