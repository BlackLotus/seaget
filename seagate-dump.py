#!/usr/bin/python2
#Dumps the memory of a seagate hd using the jumper pin serial interface
import serial
import sys,os,re
import time

try:
    device=sys.argv[1]
    dumpfile=sys.argv[2]
except:
    print 'Usage:'
    print sys.argv[0]+' device dumpfile'
    quit()
baud=38400
mem=open(dumpfile,'w')
ser = serial.Serial(port=device, baudrate=baud, bytesize=8,parity='N',stopbits=1,timeout=1)
#ser = serial.Serial(port=device, baudrate=baud, timeout=1, xonxoff=False, rtscts=False, dsrdtr=True)

#ser.write(unicode("A\n"))
#set right diagnostic mode
ser.write(unicode("/1\n"))
i=0
dumpf=""
while 1:
#    print ser.isOpen()
#    ser.write(unicode("A\n"))
    try:
        arr = ser.readline()
        if arr!="":
#            sys.stdout.write(arr)
#            sys.stdout.flush()
#            mem.write(arr)
            dumpf=dumpf+arr
        else:
            ser.write("D0,"+str(hex(512*i)[2:])+"\n")
            i=i+1
            print 'Dumping address '+str(hex(512*i)[2:])+' '+str(320*i/1000)+'kB'
    except:
        print 'Saving this shit right where it belongs!'
#        mem.close()
        break

fooR=re.compile('\d\d\d\d\d\d\d\d\s+(.+)\r')
foo=fooR.findall(dumpf)
for line in foo:
    mem.write(re.sub(' ','',line).decode("hex"))
mem.close
print 'Succesfully dumped file'
