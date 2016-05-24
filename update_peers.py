#!/usr/bin/python
import glob
import os
import psutil
import signal
import git
import argparse
import json
import socket
import time
def test():
    before = getAllKeys("/etc/fastd/peers-ffs")
    after = getAllKeys("/etc/fastd/peers-ffs")
    after["vpn04"].pop()
    #shrinkedSegments = getShrinkedSegments(before, after)
    segmentPids = getProcesses()
    sockets = getSockets(segmentPids)
    activeKeys = getAllActiveKeys(sockets)
    shrinkedSegments = getShrinkedSegments(activeKeys,after)
    for segment in segmentPids:
        pid = segmentPids[segment] 
        print "Would send SIGHUP to %i"%(pid)
        #os.kill(pid,signal.SIGHUP)
    for segment in shrinkedSegments:
        pid = segmentPids[segment]
        print "Would send SIGUSR2 to %i"%(pid)
        #os.kill(pid,signal.SIGUSR2)

def readFromSocket(f):
    s = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
    s.connect(f)
    result = ""
    while(True):
        tmp = s.recv(1024*1024)
        if tmp == "":
            break
        result += tmp
    s.close()
    return result

def getActiveKeys(f):
    data = readFromSocket(f)
    status = json.loads(data)
    keys = []
    for p in status["peers"]:
        if  status["peers"][p]["connection"] != None:
            keys.append(p)
    return keys

def getProcesses():
    pids = {}
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name',"cmdline"])
        except psutil.NoSuchProcess:
            pass
        else:
            if pinfo["name"] == "fastd":
                socket = ""
                config = pinfo["cmdline"][pinfo["cmdline"].index("--config")+1]
                segment = os.path.dirname(config).rsplit("/",1)[1]
                pids[segment] = pinfo["pid"]
                p = psutil.Process(pinfo["pid"])
                for f in p.get_connections(kind="unix")[0].laddr:
                    if "sock" in f:
                        socket = f
    return pids

def getSockets(pids):
    sockets = {}
    for segment in pids:
        pid = pids[segment]
        p = psutil.Process(pid)
        for f in p.get_connections(kind="unix"):
            if "sock" in f.laddr:
                sockets[segment] = f.laddr
    return sockets

def getSegments(basedir):
    segments = []
    segmentDirs = glob.glob("%s/vpn*"%(basedir))
    for s in segmentDirs:
        segments.append(s.rsplit("/",1)[1])
    return segments

def getPeers(basedir,segment):
    peers = glob.glob("%s/%s/peers/*"%(basedir,segment))
    return peers

def getKeys(peers):
    keys = []
    for p in peers:
        with open(p, 'r') as f:
            data = f.read()
        for line in data.split("\n"):
            if line.startswith("key "):
                try:
                    key = line.split(" ")[1][1:-2]
                    keys.append(key)
                except:
                    print "Could not read key from %s"%(p)
    return keys            

def printSegmentkeys(segmentkeys):
    for sk in segmentkeys:
        print sk
        keys = segmentkeys[sk]
        for k in keys:
            print "\t%s"%(k)

def getAllActiveKeys(sockets):
    activeKeys = {}
    for s in sockets:
        activeKeys[s] = getActiveKeys(sockets[s])
    return activeKeys

def getAllKeys(basedir):
    segments =  getSegments(basedir)
    segmentkeys = {}
    for s in segments:
        peers = getPeers(basedir,s)
        segmentkeys[s] = getKeys(peers)
    return segmentkeys

def getShrinkedSegments(before,after):
    shrinkedSegments = {}
    for s in after:
        for key in before[s]:
            if not key in after[s]:
                shrinkedSegments[s] = True
    return shrinkedSegments.keys()

def gitPull(basedir):
    repo = git.Repo(basedir)
    o = repo.remotes.origin
    try:
        time.sleep(1)
        o.pull()
    except:
        print "Error during pull!"
        return False
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Updates peer files and sends signals to fastd')
    parser.add_argument('--repo',dest='basedir',action='store',required=True,help='path to repo')

    args = parser.parse_args()

    basedir = args.basedir

    result = False
    retries = 3
    while not result:
        result = gitPull(basedir)
        retries -=1
        if retries == 0:
            break

    segmentkeys_after = getAllKeys(basedir)

    segmentPids = getProcesses()
    sockets = getSockets(segmentPids)
    activeKeys = getAllActiveKeys(sockets)
    shrinkedSegments = getShrinkedSegments(activeKeys,segmentkeys_after)

    for segment in segmentPids:
        pid = segmentPids[segment] 
        #print "Sending SIGHUP to %i"%(pid)
        os.kill(pid,signal.SIGHUP)
    for segment in shrinkedSegments:
        pid = segmentPids[segment]
        print "Will send SIGUSR2 to %i"%(pid)
        os.kill(pid,signal.SIGUSR2)

