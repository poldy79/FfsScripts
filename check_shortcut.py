#!/usr/bin/python
import batman_adv
import sys
macs = batman_adv.getMacs()
gateways = batman_adv.getGatewaysPerInterface()

test = False
if test:
    gateways["bat00"].append(macs["bat01"])

shortcut = False

for interface in gateways:
    for mac in macs:
        if macs[mac] in gateways[interface]:
            print "shortcut between %s and %s"%(interface,mac)
            shortcut = True

if shortcut:
    sys.exit(1)
else:
    sys.exit(0)

