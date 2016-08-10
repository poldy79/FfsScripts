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

def getGatewaysPerInterface():
    gateways = {}
    files = glob.glob("/sys/kernel/debug/batman_adv/bat*/gateways")
    for f in files:
        fp = open(f,"rb")
        data = fp.read()
        fp.close()
        line = data.split("\n")[0]
        test = "[B.A.T.M.A.N. adv 2016.2-127-g4f47cce, MainIF/MAC: vpn01/02:00:38:01:01:00 (bat01 BATMAN_IV)]"
        interface = line.split("MainIF/MAC: ")[1].split(" ")[1][1:]
        gateways[interface] = []
        for line in data.strip().split("\n")[1:]:
            line = line.strip()
            gateways[interface].append(line.split(" ")[0])
    return gateways

def getMacs():
    macs = {}
    files = glob.glob("/sys/kernel/debug/batman_adv/bat*/gateways")
    for f in files:
        fp = open(f,"rb")
        data = fp.read()
        fp.close()
        line = data.split("\n")[0]
        mac = line.split("MainIF/MAC: ")[1].split(" ")[0].split("/")[1]
        interface = line.split("MainIF/MAC: ")[1].split(" ")[1][1:]
        macs[interface] = mac
    return macs


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

