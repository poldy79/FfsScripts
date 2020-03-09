#!/usr/bin/python
import sys
import time
import socket
import pickle
import struct
import random
import json
CARBON_SERVER = '10.191.255.243'
CARBON_PICKLE_PORT = 2004

def mac2met(mac):
    s = mac.split(":")
    if s[2] == "0a":
        return "gw%sn01.s%s"%(s[5],s[4])
    else:
        return "gw%sn%s.s%s"%(s[4],s[5],s[3])



def submit(data,timestamp):
    sock = socket.socket()
    sock.connect( (CARBON_SERVER, CARBON_PICKLE_PORT) )

    tuples = []
    for d in data:
        tuples.append((d[0],(timestamp,d[1])))

    package = pickle.dumps(tuples, 1)
    size = struct.pack('!L', len(package))
    sock.sendall(size)
    sock.sendall(package)

def commitData(timestamp):
    errors = []
    raw = json.load(open("/root/freifunk/data/raw.json","r"))
    gw = {}
    nodes = raw["nodes"]
    for n in nodes:
        node =  n["nodeinfo"]["network"]["mac"]
        try:
            clients = n["statistics"]["clients"]["total"]
            gateway = n["statistics"]["gateway"]
            has_uplink = False
            if "mesh_vpn" in n["statistics"]:
                peers = n["statistics"]["mesh_vpn"]["groups"]["backbone"]["peers"]
                for p in peers:
                    if peers[p] != None:
                        has_uplink = True
                        break
                
            if gateway not in gw:
                gw[gateway] = {}
                gw[gateway]["fastd"] = 0
                gw[gateway]["nodes"] = 0
                gw[gateway]["clients"] = 0

            if has_uplink: 
                gw[gateway]["fastd"] += 1

            gw[gateway]["nodes"] += 1
            gw[gateway]["clients"] += clients
        except:
            print "Error with node %s"%(n)
            print nodes[node]
            errors.append(node)
            pass
    for mac in gw:
        #print mac2met(mac)
        g = gw[mac]
        data = []
        prefix =  "alfred_gw.%s."%(mac2met(mac))
        data.append((prefix+"clients",g["clients"]))
        data.append((prefix+"nodes",g["nodes"]))
        data.append((prefix+"fastd",g["fastd"]))
        #print(data)
        submit(data,timestamp)
    if len(errors)>0:
        print "Eroors with nodes: %s"%(" ".join(errors))

def main():
    timestamp = int(time.time())
    commitData(timestamp)

if __name__ == "__main__":
    main()
