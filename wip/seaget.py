#!/usr/bin/python2
# clean rewrite and combination of all my old python scripts
# TODO:
# - get basic functions []
# - add advances functions like:
#       looking for password at address $foo []
#       write to buffer/memory []
#       search for password without dumping []
#       add devices with known address []

from __future__ import print_function

from argparse import ArgumentParser
import math
import re
import sys
import time
from wgetstyle import progress_bar

try:
    from serial import Serial
except ImportError:
    sys.exit('You have to install pyserial')


def main():
    args = get_arguments()
    see = SeaGet(args.baud, args.cont, args.filename, args.device, args.new_baud)
    see.dump_memory(args.filename, args.cont)


def get_arguments():
    parser = ArgumentParser(description='Dump memory/buffer of a seagate hd using a serial connection.')
    parser.add_argument('--dumptype', metavar='memory/buffer', nargs=1, default='memory', help='What gets dumped')
    parser.add_argument('--baud', metavar=38400, default=38400, help='current baud rate [38400,115200]')
    parser.add_argument('--new-baud', metavar=115200, default=False, help='set new baud rate [38400,115200]')
    parser.add_argument('-c', dest='cont', action='store_const', const=True, help='Continue dump')
    parser.add_argument('--device', metavar='/dev/ttyUSB0', default='/dev/ttyUSB0', help='the serial device you use')
    parser.add_argument('filename', metavar='dumpfile', help='the name of the dump file, duh')
    return parser.parse_args()


class SeaGet():
    debug = 0
    timeout = 0.004
    benchmark = 0

    def __init__(self, baud, cont, filename, device, new_baud):
        self.ser = Serial(port=device, baudrate=baud, bytesize=8, parity='N', stopbits=1, timeout=self.timeout)
        debug = self.debug
        #start diagnostic mode
        if debug > 0:
            print('Start diagnostic mode')
        resp = self.send("\x1A")
        if resp[1] != "T" and resp[1] != "1":
            sys.exit("Something has gone wrong. Modus is %s" % resp[1])

        #if you want a different baud rate you get it!
        if new_baud:
            if debug > 0:
                print('Set new baud rate')
            self.set_baud(new_baud)
            baud = new_baud
        #set the right mode to access memory and buffer
        if debug > 0:
            print('Set mode /1')
        resp = self.send("/1")
        if resp[1] != "1":
            exit_msgs = ["Couldn't set modus to 1. Failed with %s" % resp[0], ]
            if re.match('Input Command Error', resp[0]) and baud != 38400:
                exit_msgs.append('You probably set a higher baud rate, on a hd that has a bug.')
                exit_msgs.append('Turn the hd off and on again and try the default baud rate 38400.')
            sys.exit('\n'.join(exit_msgs))

    def send(self, command):
        #if this doesn't work for you try setting a greater timeout (to be on the safe side try 1)
        #zc is the zerocounter and used to prevent it from going forever
        incom = [""]
        line = True
        zc = 0
        self.ser.write(command + "\n")
        while 1:
            try:
                line = self.ser.readline()
                if line == "":
                    zc += 1
                else:
                    zc = 0
                if zc == 500:
                    break
                incom.append(line)
            except:
                sys.exit('Failed to read line. Maybe the timeout is too low.')

        incom = "".join(incom)
        #You can (and have to) set different modi for the hd.
        #a different modus means you get a different set of commands
        #checking the modi after every command can be used for debugging and/or to verify that a command got executed correctly
        try:
            modus = re.findall('F3 (.)>', incom)
            modus = modus[len(modus)-1]
        except:
            exit_msgs = ["Failed to execute regex.",
                         "This usually means that you didn't get the whole message or nothing at all.",
                         "Check your baud rate and timeout/zc.",
                         incom, ]
            sys.exit(exit_msgs)

        return incom, modus

    def get_modus(self):
        return self.send("")[1]

    def set_baud(self, newbaud):
        modus = self.get_modus()
        print('Setting baud to %s' % newbaud)
        if modus != "T":
            print('Changing mode to T')
            self.send("/T")
        self.send("B"+str(newbaud))
        self.ser = Serial(port=device, baudrate=newbaud, bytesize=8, parity='N', stopbits=1, timeout=self.timeout)
        newmodus = self.send("/"+modus)[1]

        return modus == newmodus

    def parse(self, buff):
        hex = ""
        fooR = re.compile('[0-9A-F][0-9A-F][0-9A-F][0-9A-F][0-9A-F][0-9A-F][0-9A-F][0-9A-F]\s+(.+)\r')
        parsed = fooR.findall(buff)
#        for line in parsed:
#            hex=hex+re.sub(' ','',line)
        hex = re.sub(' ', '', ''.join(parsed))
        bin = hex.decode("hex")
        return hex, bin

    def read_buffer(self, hexa):
        #hexa xxxx
        #hexa is the address you want to read in hex
        res, modus = self.send('B'+str(hexa))
        return self.parse(res)
        
    def read_memory(self, hexa, hexb):
        #hexa xx
        #hexb yyyy
        #it always gives you 256bytes
        resp, modus = self.send('D'+str(hexa)+','+str(hexb))
        parsed = self.parse(resp)
        if len(parsed[1]) != 512:
            #should never happen,but could if timeout is too low
            return False, False
        return parsed

    def dump_memory(self, filename, cont):
        if cont:
            memf = open(filename, 'r+')
            fsize = len(memf.read())
            if fsize % 512 != 0:
                sys.exit('%s seems to be corrupted (wrong file size)' % filename)

            sj = math.trunc(fsize/512/64)
            si = fsize/512-64*sj
            if self.debug > 0:
                print('Starting from %s %s' % (sj, si))
        else:
            memf = open(filename, 'w')
            fsize = 0
            sj, si = 0, 0
        k = fsize/512
        total = (64*128*512)/1000.0
        stime = time.time()  # start time
        mem = []
        
        print('Starting memory dump')
        for j in range(sj, 64):
            for i in range(si, 128):
                k += 1
                zz = time.time()
                memf.write(self.read_memory(hex(j)[2:], hex(i*0x200)[2:])[1])
                size = (k*512)/1000.0
                if self.benchmark == 1:
                    speed = round(512/(time.time()-zz), 2)
                    percentage = round(100.0/total*size, 2)
                    minleft = round((time.time()-stime)/k*(247*128-k)/60, 2)
                progress_bar(time.time()-stime, size*1000, total*1000)
        memf.close()
        
    def dump_buffer(self):
        pass


if __name__ == '__main__':
    main()
