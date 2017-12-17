#!/usr/bin/python
import os
import glob


def gwl(gateways):
    fp = open(gateways)
    data = fp.read()
    fp.close()
    return data

def temp():
    segment = gateways.split("/")[5][3:]
    print "Segment: %s"%(segment)
    for line in data.strip().split("\n")[1:]:
        print "x: %s"%(line) 

def getLocalGwMac(gw_raw):
    return gw_raw.split("\n")[0].split(" ")[-2].split("/")[1]

def getOtherGwMacs(gw_raw):
    gws = []
    for line in gw_raw.strip().split("\n")[1:]:
        gw = line.strip().split(" ")[0]
        gws.append(gw)
    return gws

gwlFiles = glob.glob("/sys/kernel/debug/batman_adv/*/gateways")
gws_raw = {}
localGws = []
segments = {}
for gwlFile in gwlFiles:
    segment = gwlFile.split("/")[5][3:]
    gws_raw[segment] = gwl(gwlFile)
    localGws.append(getLocalGwMac(gws_raw[segment]))
    segments[segment] = getOtherGwMacs(gws_raw[segment])

for segment in segments:
    otherGws = segments[segment] 
    for localGw in localGws:
        if localGw in otherGws:
            print "GW %s present in segment %s"%(localGw,segment)

