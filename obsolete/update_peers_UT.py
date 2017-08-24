#!/usr/bin/python
from update_peers import *

def test01():
    after = getAllKeys("/etc/fastd/peers-ffs")
    #after["vpn04"].pop()
    segmentPids = getProcesses()
    sockets = getSockets(segmentPids)
    activeKeys = getAllActiveKeys(sockets)

    after["vpn00"].remove(activeKeys["vpn00"][0])
    shrinkedSegments = getShrinkedSegments(activeKeys,after)
    for segment in segmentPids:
        pid = segmentPids[segment]
        #print "Would send SIGHUP to %i"%(pid)
        #os.kill(pid,signal.SIGHUP)
    for segment in shrinkedSegments:
        pid = segmentPids[segment]
        print "Would send SIGUSR2 to %i"%(pid)
        #os.kill(pid,signal.SIGUSR2)

def test02():
    before = {}
    after = {}

    before["vpn00"] = ["a","b","c"]
    after["vpn00"] = ["b","c","d"]

    before["vpn01"] = ["a","b","c"]
    after["vpn01"] = ["a","b","c","d"]

    before["vpn02"] = ["a","b","c"]
    after["vpn02"] = ["a","b","c"]

    shrinkedSegments = getShrinkedSegments(before,after)

    if shrinkedSegments == ["vpn00"]:
        print "OK - test02"
    else:
        print "FAILED - test02"

test01()
test02()

