#!/usr/bin/python2
#Dumps the memory of a seagate hd using the jumper pin serial interface
import serial
import sys,os,re,argparse
import time
from wgetstyle import *

debug=0
#automagicly set to 115200 baud
fast=1
#1 is slow 0 is fastest 0.1 is the sweetspot
timeout=0.2
benchmark=1
writing=0

try:
    device=sys.argv[1]
    dumpfile=sys.argv[2]
    baud=sys.argv[3]
    memf=open(dumpfile,'r+')
    fileend=len(memf.read())
except:
    print 'Usage:'
    print sys.argv[0]+' device dumpfile baud\n'
    print 'Default baud should be 38400 maximum is 115200\n'
    quit()

def send(ser,command):
    ser.write(command+"\n")
    inco=""
    while 1:
        try:
            arr=ser.readline()
            if arr!="":
                inco=inco+arr
            else:
                if debug>=2:
                    print inco
                modus=re.findall('F3 (.)>',inco)
                break
                #print 'Next command'
        except:
            print 'Exception! (in send)'
            if writing==1:
                memf.close()
            break
    return inco,modus

def get_modus(ser):
    inco,modus=send(ser,"")
    return modus[0]

def set_baud(ser,baud):
    modus=get_modus(ser)
    print 'Setting baud to '+str(baud)
    if modus!="T":
        print 'Changing mode to T'
        send(ser,"/T")
    send(ser,"B"+str(baud))
    ser = serial.Serial(port=device, baudrate=baud, bytesize=8,parity='N',stopbits=1,timeout=timeout)
    send(ser,"/"+modus)
    return ser

def init(device,baud,fast=fast):
    ser = serial.Serial(port=device, baudrate=baud, bytesize=8,parity='N',stopbits=1,timeout=timeout)
    #Initialize the command line
#    print ser.inWaiting()
#    print dir(ser)
#    if send(ser,"\n")[1]==[]:
#        print 'Got no modus bad'
#        quit()
    print send(ser,"\n")
    print send(ser,"\x1A")[1]
    if baud=="38400" and fast==1:
        baud=115200
        try:
            set_baud(ser,baud)
            ser = serial.Serial(port=device, baudrate=baud, bytesize=8,parity='N',stopbits=1,timeout=timeout)
        except:
            print 'You probably already are on 11500 baud'
    send(ser,"/1")
    return ser

def parse(buff):
    hex=""
    bin=""
    fooR=re.compile('[0-9A-F][0-9A-F][0-9A-F][0-9A-F][0-9A-F][0-9A-F][0-9A-F][0-9A-F]\s+(.+)\r')
    parsed=fooR.findall(buff)
    for line in parsed:
        hex=hex+re.sub(' ','',line)
    try:
        bin=hex.decode("hex")
    except:
        print 'Parse failed'
    return hex,bin

def display_buffer(ser,num):
    #num xxxx
    foo,bar=send(ser,'B'+str(num))
    return parse(foo)

def display_memory(ser,num1,num2):
    #num1 xx, num2 yyyy
    looped=0
    if debug>=1:
        print 'D'+str(num1)+","+str(num2)+" - "
    foo,bar=send(ser,'D'+str(num1)+","+str(num2))
    parsed=parse(foo)
    if len(parsed[1])==0:
        print 'Got nothing trying again :/'
        if looped>10:
            print "Seems like we're stuck - quitting"
            memf.close()
            quit()
        looped=looped+1
        parsed=display_memory(ser,num1,num2)        
    if len(parsed[1])!=512:
        print 'Got the wrong size!!!!!!1111'
        parsed=display_memory(ser,num1,num2)
    return parsed

def dump_memory(ser,dumpfile):
    writing=1
    k=0
    total=(64*128*512)/1024.0
    stime=time.time() #start time
    print 'Continuing memory dump'
    for j in range(0,64):
        for i in range(0,128):
            k=k+1
            zz=time.time()
            if k>fileend/0x200:
                mem=display_memory(ser,hex(j)[2:],hex(i*0x200)[2:])[1]
            if benchmark==1:
                size=(k*512)/1024.0
#                speed=round(512/(time.time()-zz),2)
                percentage=round(100.0/total*size,2)
                minleft=round((time.time()-stime)/k*(247*128-k)/60,2)
		if debug==0:
                    progress_bar(time.time()-stime,size*1024,total*1024)
		elif debug>0:
                    print 'time:'+str(time.time()-stime)
                    print 'size:'+str(size)
                    print 'total:'+str(total)
            if k>fileend/0x200:
                memf.write(mem)
    memf.close()
    writing=0

def dump_buffer(ser,dumpfile):
    writing=1
    k=0
    total=(65535*512)/1024.0
    stime=time.time() #start time
    for i in range(0,65535):
         k=k+1  
         zz=time.time()
         if k>fileend/0x200:
             mem=display_buffer(ser,hex(i)[2:])[1]
         size=(k*512)/1024.0
         if benchmark==1:
             progress_bar(time.time()-stime,size*1024,total*1024)
         if k>fileend/0x200:
             memf.write(mem)
    memf.close()
    writing=0

ser=init(device,baud)
#print send(ser,'')
#print display_buffer(ser,00)[0]
try:
    modus=get_modus(ser)
except:
    print "Couldn't even get the modus - quitting"
    if debug<2:
        print 'Try it using debug=2'
    quit()
if modus!="1":
     print 'Somethings not right here'
     quit()
#print display_memory(ser,'15','C000')
dump_buffer(ser,dumpfile)
#dump_buffer(ser,dumpfile)
print 
