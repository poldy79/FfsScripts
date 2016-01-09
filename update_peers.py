#!/usr/bin/python
import glob
import os
import psutil
import signal
import git

def _testRemoveKey(segmentkeys):
    import copy
    import random
    segmentkeys = copy.deepcopy(segmentkeys)
    k = segmentkeys.keys()
    segment = k[random.randint(0,len(k)-1)]
    removedKey = segmentkeys[segment].pop(random.randint(0,len(segmentkeys[segment])-1))
    print "Removed %s from %s"%(removedKey,segment)
    return segmentkeys

def getProcesses():
    pids = {}
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name',"cmdline"])
        except psutil.NoSuchProcess:
            pass
        else:
            if pinfo["name"] == "fastd":
                #print(pinfo)
                config = pinfo["cmdline"][pinfo["cmdline"].index("--config")+1]
                segment = "/".join(config.split("/")[0:4])
                #print "%s: %i"%(segment,pinfo["pid"])
                pids[segment] = pinfo["pid"]
    return pids

def getSegments(basedir):
    segments = glob.glob("%s/vpn*"%(basedir))
    return segments

def getPeers(segment):
    peers = glob.glob("%s/peers/*"%segment)
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

def getAllKeys(basedir):
    segments =  getSegments(basedir)
    segmentkeys = {}
    for s in segments:
        peers = getPeers(s)
        segmentkeys[s] = getKeys(peers)
    return segmentkeys

def getShrinkedSegments(before,after):
    shrinkedSegments = {}
    for s in before:
        for key in before[s]:
            if not key in after[s]:
                shrinkedSegments[s] = True
    return shrinkedSegments.keys()

def gitPull(basedir):
    repo = git.Repo(basedir)
    o = repo.remotes.origin
    o.pull()

basedir = "/etc/fastd"
segmentkeys_before = getAllKeys(basedir)

gitPull(basedir)

segmentkeys_after = getAllKeys(basedir)
#segmentkeys_after = _testRemoveKey(segmentkeys_after)

#printSegmentkeys(segmentkeys_before)
#printSegmentkeys(segmentkeys_after)
shrinkedSegments = getShrinkedSegments(segmentkeys_before, segmentkeys_after)
segmentPids = getProcesses()
for segment in segmentPids:
    pid = segmentPids[segment] 
    print "Sending SIGHUP to %i"%(pid)
    os.kill(pid,signal.SIGHUP)
for segment in shrinkedSegments:
    pid = segmentPids[segment]
    print "Will send SIGUSR2 to %i"%(pid)
    os.kill(pid,signal.SIGUSR2)


