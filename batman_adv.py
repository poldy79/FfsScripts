#!/usr/bin/python
import glob

def getGateways():
    gateways = []
    files = glob.glob("/sys/kernel/debug/batman_adv/bat*/gateways")
    for f in files:
        fp = open(f,"rb")
        data = fp.read()
        fp.close()
        for line in data.strip().split("\n")[1:]:
            line = line.strip()
            gateways.append(line.split(" ")[0])
    return gateways

def getTranstableGlobal():
    t = {}
    files = glob.glob("/sys/kernel/debug/batman_adv/bat*/transtable_global")
    for f in files:
        fp = open(f,"rb")
        data = fp.read().strip().split("\n")
        status = data[0]
        header = data[1]
        for line in data[2:]:
            line = line.replace("*","").replace("(","").replace(")","")
            while "  " in line:
                line = line.replace("  "," ")
            el = line.split(" ")
            try:
                client = el[0]
                vid = el[1]
                ttvn = el[2]
                originator = el[3]
                t[client] = {"vid":vid,"ttvn":ttvn,"originator":originator}
            except:
                print line
    return t

def getOriginators():
    o = {}
    files = glob.glob("/sys/kernel/debug/batman_adv/bat*/originators")
    for f in files:
        fp = open(f,"rb")

        data = fp.read().strip().split("\n")
        status = data[0]
        header = data[1]
        for line in data[2:]:
            line = line.replace("]:","").replace("[","").replace("(","").replace(")","")
            while "  " in line:
                line = line.replace("  "," ")
            el = line.split(" ")
            try:
                originator = el[0]
                lastSeen = el[1]
                quality = el[2]
                nexthop = el[3]
                interface = el[4]
                o[originator] = {"lastSeen": lastSeen,"quality":quality,"nexthop":nexthop, "interface":interface}
            except:
                print line
    return o


#o = getOriginators()
#t = getTranstableGlobal()

