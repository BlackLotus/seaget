#!/usr/bin/python2
# clean rewrite and combination of all my old python scripts
# TODO:
# - get basic functions []
# - add advances functions like:
#       looking for password at address $foo
#       write to buffer/memory
#       search for password without dumping
#       add devices with known address

import argparse
try:
    import serial
except:
    print 'You have to install pyserial'
    quit()
import sys,os,re,time

class SeaGet():
    debug=0

    def send(self,command):
    #I'm not sure how to safely break this
    #I have added a ZeroCounter (zc) so that it won't run forever
        incom=[""]
        line=True
        self.ser.write(command+"\n")
        zc=0
        while 1:
            try:
                line=self.ser.readline()
                line=self.ser.read(1000)
                if line=="":
                    zc+=1
                else:
                    zc=0
                incom.append(line)
                if zc==300:
                    break
            except:
                print 'Failed to read line.Maybe the timeout is too low'
                break
        incom="".join(incom)
        #You can (and have to) set different modi for the hd.
        #a different modus means you get a different set of commands
        #checking the modi after every command can be used for debugging and/or to verify that a command got executed correctly
        try:
            modus=re.findall('F3 (.)>',incom)
            modus=modus[len(modus)-1]
        except:
            print 'Failed to execute regex.This usually means that you didn\'t get the whole message or nothing at all'
            print 'Check your baud rate and timeout/zc'
            quit()
        return incom,modus


    def __init__(self,baud, cont, dumptype, filename, device, new_baud=False):
        self.ser = serial.Serial(port=device, baudrate=baud, bytesize=8,parity='N',stopbits=1,timeout=0)
        resp=self.send("\x1A")
        if resp[1]!="T" and resp[1]!="1":
            print "Something went probably wrong"
            print "Modus is "+resp[1]
            quit()
        #set the right mode to access memory and buffer
        resp=self.send("/1")
        if resp[1]!="1":
            print 'Couldn\'t set modus to 1'
            quit()

    def read_buffer():
        pass
        
    def read_memory():
        pass

    def dump_buffer():
        pass
        
    def dump_memory():
        pass

def main():
    parser = argparse.ArgumentParser(description='Dump memory/buffer of a seagate hd using a serial connection.')
    parser.add_argument('--dumptype', metavar='memory/buffer', nargs=1, default='memory', help='What gets dumped')
    parser.add_argument('--baud', metavar=38400, default=38400, help='current baud rate [38400,115200]')
    parser.add_argument('--new-baud', metavar=115200, default=115200, help='set new baud rate [38400,115200]')
    parser.add_argument('-c', dest='cont', action='store_const', const=True, help='Continue dump')
    parser.add_argument('--device', metavar='/dev/ttyUSB0', default='/dev/ttyUSB0', help='the serial device you use')
    parser.add_argument('filename', metavar='dumpfile', help='the name of the dump file, duh')
    args = parser.parse_args()
    see = SeaGet(args.baud, args.cont, args.dumptype, args.filename, args.device, args.new_baud)

if __name__ == '__main__':
    main()
