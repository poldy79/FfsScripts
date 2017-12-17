#!/usr/bin/python
import os
import sys
import glob
import argparse
import json

def getKey():
    if not os.environ.has_key("PEER_KEY"):
        return ""
    return os.environ["PEER_KEY"]

def checkKey(peer_key):
    if len(peer_key) != 64:
        print "Key has wrong length"
        return False
    for c in peer_key:
        if not c in "abcdef01234567890":
            print "Wrong chars in key %s"%(c)
            return False
    return True

def checkPeerDir(peerDir):
    if not os.path.isdir(peerDir):
        print "Dir not found"
        sys.exit(1)
    return peerDir

def importBatadvVis(batadvvis):
    vis = []
    with open(batadvvis,"rb") as f:
        data = f.read()
    
    for d in data.strip().split("\n"):
        j = json.loads(d)
        vis.append(j)
    return vis

def getGwConnections(vis,mac):
    conn = {}
    print mac[:-2]
    for v in vis:
        if "router" in v and "neighbor" in v and v["neighbor"].startswith("02:00"):
            if v["neighbor"] in conn:
                conn[v["neighbor"]] +=1
            else:
                conn[v["neighbor"]] = 1 
    return conn

def decideToAccept(conn,mac):
    v = conn.values()
    v.sort()
    v.reverse()
    print conn
    if conn[mac] == v[0] and len(v) > 1:
        print "We are full"
        return False
    else:
        print "We can accept more"
        return True

def getKeyFromFile(data):
    for d in data.split("\n"):
        if d.startswith("key ") and d.endswith(";"):
            key = d.split(" ")[1][1:-2]
            if len(key) == 64:
                return key

def authenticate(peer_dir,peer_key):
    for fn in glob.glob(peer_dir+"/*"):
        with open(fn, 'rb') as f:
            data = f.read()
            f.closed
        key = getKeyFromFile(data)
        if key == peer_key:
            return True
    return False

def getOriginatorConnections(interface,mac):
    fp = open("/sys/kernel/debug/batman_adv/%s/originators"%(interface),"rb")
    data = fp.read()
    fp.close()

    conn = {}

    for line in data.split("\n")[2:]:
        org = line[0:17]
        next = line[36:53]
        if next.startswith(mac[:-2]):
            #print "%s %s"%(org,next)
            if not next in conn:
                conn[next] = 1
            else:
                conn[next] +=1
    return conn

def printConnections(conn):
    print "Connections:"
    for c in conn:
        print "%s : %i"%(c,conn[c])


parser = argparse.ArgumentParser(description='auth fastd key')
parser.add_argument('--batadv-vis', dest='batadvvis', action='store',required=True, help='batman-vis json')
parser.add_argument('--peers',dest='peer_dir',action='store',required=True,help='dir with peer files')
parser.add_argument('--mac',dest='mac',action='store',required=True,help='mac of this gw')
parser.add_argument('--interface',dest='interface',action='store',required=True,help='batadv interface')

args = parser.parse_args()
#/sys/kernel/debug/batman_adv/bat00/originators
try:
    vis = importBatadvVis(args.batadvvis)
    conn = getGwConnections(vis,args.mac)
except:
    print "Error loadbalancing"

if not decideToAccept(conn,args.mac):
    sys.exit(1)

conn2 = getOriginatorConnections(args.interface,args.mac)

printConnections(conn)
printConnections(conn2)


peer_dir = checkPeerDir(args.peer_dir)
peer_key = getKey()
if not checkKey(peer_key):
    print "Check of key failed"
    sys.exit(1)
if authenticate(peer_dir,peer_key):
    print "key ok"
    sys.exit(0)

print "key not ok"
sys.exit(1)

