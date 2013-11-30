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
ser = serial.Serial(port=device, baudrate=baud, bytesize=8,parity='N',stopbits=1,timeout=0.1)
#ser = serial.Serial(port=device, baudrate=baud, timeout=1, xonxoff=False, rtscts=False, dsrdtr=True)

#ser.write(unicode("A\n"))
#set right diagnostic mode
ser.write("\x1A\n")
while ser.inWaiting()!=0:
    print ser.readline(ser.inWaiting())

ser.write("/T\n")
while ser.inWaiting()!=0:
    print ser.readline(ser.inWaiting())
ser.write("B115200\n")
while ser.inWaiting()!=0:
    print ser.readline(ser.inWaiting())
baud=115200
ser = serial.Serial(port=device, baudrate=baud, bytesize=8,parity='N',stopbits=1,timeout=0.1)


print 'FLUUUUSHHHHH'
ser.write(unicode("/1\n"))
#ser.write(unicode("^E\n"))
print 'Waiting for '+str(ser.inWaiting())
ser.readline(ser.inWaiting())
print 'Waiting for '+str(ser.inWaiting())+' foos in output to be flushed'
full=ser.inWaiting()
while ser.inWaiting()!=0:
    sys.stdout.write('\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b')
    sys.stdout.write('Flushing '+str((100/full)*(full-ser.inWaiting()))+'%')
    sys.stdout.flush()
    ser.readline(ser.inWaiting())
print ''
print 'Done Flushing :)'
print str(ser.inWaiting())+' remaining'
#ser.write("A\n")
#ser.setBreak()
i=0
dumpf=""
zeit=time.time()
zz=zeit
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
            speed=256/(zz-time.time())
            ser.write("D0,"+str(hex(512*i)[2:])+"\n")
            zz=time.time()
            i=i+1
            print 'Dumping address '+str(hex(512*i)[2:])+' '+str(256*i/1000)+'kB '+str(len(dumpf))+' mit einer Geschwindigkeit von '+speed+'byte/sek'
#            if len(dumpf)%36!=0:
#                print 'Dumping error'
#                print dumpf
#                break
    except:
        print 'Saving this shit right where it belongs!'
#        mem.close()
        break

print time.time()-zeit
fooR=re.compile('\d\d\d\d\d\d\d\d\s+(.+)\r')
foo=fooR.findall(dumpf)
for line in foo:
    mem.write(re.sub(' ','',line).decode("hex"))
mem.close
print 'Succesfully dumped file'
