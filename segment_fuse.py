#!/usr/bin/python
import json
import glob
import os


def getSegmentFromName(name):
    start = name.find("0") 
    segStr = name[start:start+2]
    seg = int(segStr)
    return seg 

def isGwMac(mac):
    if mac.startswith("02:00:0a:38:"):
        return True
    return False

def isForeginGwMac(mac,currentSeg):
    if isGwMac(mac) and not mac.startswith("02:00:0a:38:0%i"%(currentSeg)):
       return True
    return False

def getForeginRouters(data):
    for d in data:
        seg = data[d]
        for line in seg:
            if line.has_key("router") and line.has_key("neighbor") and isForeginGwMac(line["router"],d) and not isGwMac(line["neighbor"]):
                node = getNodeFromRouter(data,line["neighbor"])
                print "ALERT: Segment %i: Router %s (%s) is connected to gw %s"%(d,line["neighbor"],node,line["router"])

def getNodeFromRouter(data,mac):
    for d in data:
        seg = data[d]
        for line in seg:
            if line.has_key("router") and line.has_key("gateway") and line["router"] == mac:
                return line["gateway"]

    for d in data:
        seg = data[d]
        for line in seg:
            if line.has_key("secondary") and line.has_key("of") and line["secondary"] == mac:
                return getNodeFromRouter(data,line["of"])


def importData():
    g = glob.glob("/home/www/html/map/json/batman-vis-bat*.json")
    data = {}
    for f in g:
        bn = getSegmentFromName(os.path.basename(f))
        data[bn] = []
        fp = open(f,"rb")
        fc = fp.read().strip()
        fp.close()
        for l in fc.split("\n"):
            j = json.loads(l)
            data[bn].append(j)
    return data

data = importData()
getForeginRouters(data)

