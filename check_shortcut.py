#!/usr/bin/python
import batman_adv
import sys
import subprocess
import argparse
import json
import psutil
import socket
import os
import fastd


def check_output(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output = process.communicate()[0].strip()
    return (output,process.returncode)

def resolveMac(mac):
    fp = open("/root/freifunk/data/alfred-json-158-merged.json","rb")
    nodes = json.load(fp)
    fp.close()
    if mac in nodes:
        return "ffs-%s"%(mac.replace(":",""))
    for node in nodes:
        for interface in nodes[node]["network"]["mesh"]["bat0"]["interfaces"]:
            macs = nodes[node]["network"]["mesh"]["bat0"]["interfaces"][interface]
            try:
                for t in macs:
                    if t == mac:
                        return "ffs-%s"%(node.replace(":",""))
            except:
                pass
    return mac
def getKeyForNode(node):
    data = fastd.getSocketData()
    for interface in data:
        peers = json.loads(data[interface])["peers"]
        for peer in peers:
            name = peers[peer]["name"]
            if name == node:
                return (peer,interface)
    return ("?","?")

def parseTr(route):
    route = route.strip().split("\n")
    macs = []
    for line in route[1:]:
        if line.startswith(" "):
            mac = line.strip().split(" ")[1]    
            macs.append(mac)
        else:
            mac =  line.rsplit(":",1)[0]
            macs.append(mac)
    return macs


batmanMacs = batman_adv.getMacs()
gateways = batman_adv.getGatewaysPerInterface()

parser = argparse.ArgumentParser()
parser.add_argument("--sim", help="simulate shortcut",action="store_true")
parser.add_argument("--out", type=str, help="output file")
parser.add_argument("--shortcut", type=str, help="last shortcut file")
args = parser.parse_args()

test = False
if args.sim:
    test = True
    gateways["bat00"].append(batmanMacs["bat01"])

shortcut = False
output = ""
for interface in gateways:
    for mac in batmanMacs:
        if batmanMacs[mac] in gateways[interface]:
            output+= "shortcut between %s and %s\n"%(interface,mac)

            if test == False:
                params = ["/usr/local/sbin/batctl","-m",interface,"tr",batmanMacs[mac]]
            else:
                params = ["/usr/local/sbin/batctl","-m",interface,"tr","30:b5:c2:88:60:9a"]
                #params = ["/usr/local/sbin/batctl","-m",interface,"tr","02:00:38:00:10:00"]
            (result,status) = check_output(params)
            output+= "-"*20 + "trace" + "-"*20+"\n"
            output+= result + "\n"
            output+= "-"*20 + "trace" + "-"*20+"\n"
            route = parseTr(result)
            for r in route:
                (key,segment) = getKeyForNode(resolveMac(r))
                output+= "%s: %s: %s (%s)\n"%(r,resolveMac(r),key,segment)
            shortcut = True

if not shortcut:
    output+= "No shortcut detected"

if not args.out == None:
    fp = open(args.out,"wb")
    fp.write(output)
    fp.close()
else:
    print output

if args.shortcut != None and shortcut:
    fp = open(args.shortcut,"wb")
    fp.write(output)
    fp.close()

if shortcut:
    sys.exit(1)
else:
    sys.exit(0)


