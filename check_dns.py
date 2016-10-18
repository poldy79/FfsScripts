#!/usr/bin/python
import argparse
import time
import dns.resolver
import sys
import socket

lookupTable = {}
lookupTable["gw01.freifunk-stuttgart.de"] = "gw01n00"
lookupTable["gw05.freifunk-stuttgart.de"] = "gw05n00"
lookupTable["gw09.freifunk-stuttgart.de"] = "gw09n00"
lookupTable["gw10.nul1.net"] = "gw10n00"
lookupTable["ms132.moonshot.fastwebserver.de"] = "gw05n02"
lookupTable["f338.fuchsia.servdiscount-customer.com"] = "gw05n03"

seg = {}
seg[0] = ""
seg[1] = "s01"
seg[2] = "s02"
seg[3] = "s03"
seg[4] = "s04"

def reverseLookup(ip):
    try:
        host = socket.gethostbyaddr(ip)[0]
        if host in lookupTable:
            return lookupTable[host]
        else:
            return host
    except:
        return ip

server = "dns1.lihas.de"

parser = argparse.ArgumentParser()
parser.add_argument("--dump",help="print as much information as available",action="store_true")
args = parser.parse_args()

peers = {}

resolver = dns.resolver.Resolver()
server_ip = resolver.query("%s."%(server),"a")[0].to_text()
resolver.nameservers = [server_ip]

#for s in seg.keys():
for s in [01]:
    peers[s] = []
    #for gw in range(1,11):
    for gw in [8,]:
        hostname = "gw%02i%s.freifunk-stuttgart.de."%(gw,seg[s])
        #for t in ["a","cname"]:
        for t in ["cname"]:
            try:
                if t == "cname":
                    cnames = resolver.query(hostname,t)[0]
                    ips  = resolver.query(cnames,"a")
                else:
                    ips  = resolver.query(hostname,t)
                for ip in ips:
                    try:
                        peers[s].append((hostname.split(".")[0],reverseLookup(ip.to_text())))
                    except:
                        print("No reverseloopup for %s"%(ip))
            except:
                raise
                pass

orphanedSegments = []

for s in seg:
    count = len(peers[s])
    if count <1:
        orphanedSegments.append(s)
    if args.dump:
        print("Segment %02d has %i peers"%(s,count))
        for p in peers[s]:
            print("\t%s : %s"%(p[0],p[1]))

if len(orphanedSegments) >0:
    print("Not all Segments are currently connectable:")
    for s in orphanedSegments:
        print("\tSegment %02i "%(s),)
    print("")
    sys.exit(1)
    
