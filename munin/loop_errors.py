#!/usr/bin/python
import datetime
import munin

def getLoopCount():
    fp = open("/var/log/syslog","rb")
    data = fp.read()
    fp.close()
    first = None
    result = {}
    for iface in ["bat00","bat01","bat02","bat03","bat04"]:
        result[iface] = 0

    for l in data.strip().split("\n"):

        ls = l.split(" ")
        if ls[4] != "kernel:":
            continue
        if not ls[6].startswith("br"):
            continue
        interface  = ls[10]
        if interface not in result:
            result[interface] = 0

        if not " ".join(ls[11:]) == "with own address as source address":
            continue
        d = datetime.datetime.strptime(str(datetime.datetime.now().year)+" "+" ".join(ls[0:3]), "%Y %b %d %H:%M:%S")
        delta = datetime.datetime.now() - d
        if delta.seconds > 60*5: #last hour - or 5 min
            continue
        if first == None:
            first = l
        #print "%i: %s"%(delta.seconds,interface)
        result[interface]+=1
        #print l

    #print "First:"
    #print first
    #print "Count: %i"%(count)
    return result

category = 'network'
vlabel = 'loop_errors'

def values():
    global loop_errors
    return loop_errors


loop_errors = getLoopCount()
fields = loop_errors.keys()

if __name__ == '__main__':
    munin.main()

