#!/usr/bin/python3
import argparse
import subprocess
import time
import os
import dns.resolver
import sys

#key = "/home/leonard/freifunk/Kgw.freifunk-stuttgart.de.+165+50977.key"

key_basename = "Kgw.freifunk-stuttgart.de.+165+50977.key"
server = "dns2.lihas.de"

parser = argparse.ArgumentParser()
parser.add_argument("--gw", help="gw to update", type=int)
parser.add_argument("--segment", help="segment to be updated", type=int)
parser.add_argument("--instance", help="instances to be enabled", type=int)
parser.add_argument("--remove",help="enirely remove gw from segment",action="store_true")
parser.add_argument("--verbose",help="be verbose",action="store_true")
parser.add_argument("--key",help="path to key",type=str)


args = parser.parse_args()

options = ["./","../","../../"]
if args.key != None:
    key = args.key
else:
    key = None
    for o in options:
        if os.path.isfile("%s%s"%(o,key_basename)):
            key = "%s%s"%(o,key_basename)
            break

if key == None:
    print("ERROR: Key was not found")
    sys.exit(1)
cmd = []
cmd.append("server %s"%server)

if args.remove:
    if args.verbose:
        print("Will remove gw %i from semgent %i"%(args.gw,args.segment))
    for t in ["a","aaaa"]:
        if args.segment == 0:
            cmd.append("update delete gw%02i.gw.freifunk-stuttgart.de %s"%(args.gw,t))
        else:
            cmd.append("update delete gw%02is%02i.gw.freifunk-stuttgart.de %s"%(args.gw,args.segment,t))
else:
    resolver = dns.resolver.Resolver()
    server_ip = resolver.resolve("%s."%(server),"a")[0].to_text()
    resolver.nameservers = [server_ip]
    ip = {}
    for t in ["a","aaaa"]:
        try:
            ip[t] = resolver.resolve("gw%02in%02i.gw.freifunk-stuttgart.de."%(args.gw,args.instance),t)[0]
        except:
            if args.verbose:
                print("No %s record found for gw%02in%02i.gw.freifunk-stuttgart.de"%(t,args.gw,args.instance))
    
    if len(ip.keys()) == 0:
        print("ERROR: No IPs given for this instance")
        sys.exit(1)
    if args.verbose:
        print("Will enable gw %i instance %i in segment %i"%(args.gw,args.instance,args.segment))
    for t in ip.keys():
        if args.segment == 0:
            cmd.append("update add gw%02i.gw.freifunk-stuttgart.de 300 %s %s"%(args.gw,t,ip[t]))
        else:
            cmd.append("update add gw%02is%02i.gw.freifunk-stuttgart.de 300 %s %s"%(args.gw,args.segment,t,ip[t]))

cmd.append("send")

if args.verbose:
    print("\n".join(cmd))

fp = open("/tmp/dnsupdate.txt","w")
fp.write("\n".join(cmd))
fp.close()

cmdline = '/usr/bin/nsupdate -k %s -t 300 /tmp/dnsupdate.txt'%(key)
result = subprocess.call(cmdline.split(" "),shell=False)

if result != 0:
    print("ERROR: update was not successfully")
    sys.exit(1)
else:
    os.remove("/tmp/dnsupdate.txt")


