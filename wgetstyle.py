import os,sys,re
from math import ceil
#wget style progress bar library :) 0.1
#rows, columns = os.popen('stty size', 'r').read().split()
stypes=['byte','KB','MB','GB','TB']
ttypes=[['ms',1000],['s',60],['m',60],['h',24],['d',365],['y','10']]

def correctsize(num,stype):
    if num>=1024:
        num=num/1024.0
        stype=stype+1
    if num>=1024:
        num,stype=correctsize(num,stype)
    return num,stype

def correcttime(num,ttype=1):
    if num>ttypes[ttype][1]:
        num=num/1.0/ttypes[ttype][1]
        ttype=ttype+1
    if num>ttypes[ttype][1]:
        num,ttype=correcttime(num,ttype)
    else:
        num=round(num,0)+float(round(ttypes[ttype-1][1]/100.0*((num-ceil(num)+1)*100.0),0)/100.0)
    return num,ttype

def foo_to_byte(num,stype):
    if stype>1:
        num=num/1024
        stype=stype-1
    elif stype<1:
        num=num*1024
        stype=stype+1
    if stype!=1:
        num,stype=foo_to_byte(num,stype)
    return num

def dotit(num):
    addnull=(3-len(str(num))%3)%3
    newnum=""
    if addnull!=3:
        for i in range(0,addnull):
            num='0'+str(num)
    for i in re.findall('(.?.?.)',str(num)):
        newnum=newnum+'.'+i
    return newnum[addnull+1:]


def progress_bar(dtime,nfile,total=0,k=0,stype=1):
    rows, columns = os.popen('stty size', 'r').read().split()
    columns=int(columns)
    for i in range(0,columns):
        sys.stdout.write("\b")
    perc=100*int(nfile)/int(total)
    #stype 0=bit,1=byte,2=kbyte,3=mbyte,4=gbyte - shouldn't be changed (time is in seconds)
    if dtime==0:
        dtime=0.0001
    speed=float(nfile)/float(dtime)
    speed,sptype=correctsize(speed,stype)
    space=columns-42
    eq=int(round(space/100.0*perc,0))
    #penis
    if perc<10:
        line=' '+str(perc)+'% ['
    elif perc>99:
        line='100%['
    else:
        line=str(perc)+'% ['
    for i in range(0,eq):
        line=line+"="
    line=line+">"
    for i in range(0,space-eq):
        line=line+" "
    #bytesize
    bytes=foo_to_byte(nfile,stype)
    line=line+"] "
    foo=" "+dotit(nfile)
#    print type(len(dotit(total))+3-len(foo))
    for i in range(0,len(dotit(total))+3-len(foo)):
        foo=foo+" "
    line=line+foo
    #speed
    if int(nfile)==0:
        nfile=0.0001
    eta=float(dtime)/float(nfile)*(int(total)-int(nfile))
    eta,ttype=correcttime(eta)
    speed=str(round(speed,3-len(str(int(ceil(speed)-1)))))
#    if len(speed)==2:
#        speed=speed+'0'
#    elif len(speed)==1:
#        speed=speed+'00'

    line=line+str(speed)+stypes[stype]+'/s  ETA '+str(round(eta,2))+ttypes[ttype][0]
    for i in range(0,columns-len(line)):
        line=line+" "
    sys.stdout.write(line)
    sys.stdout.flush()
    
    
#progress_bar(int(sys.argv[1]),sys.argv[2],sys.argv[3])

