#!/usr/bin/python3
import subprocess
import os
import sys
import json
from netaddr import *
import time

def getSubnetFromRange(ipRangeStr):
    ffsNet = IPNetwork("10.190.0.0/15")
    tmp =  ipRangeStr.split(" - ")
    r = IPRange(tmp[0],tmp[1])
    segment = 0
    if r in IPNetwork("10.191.0.0/19"): # seg 33
        return ("10.191.0.0/19", 33)
    for subnet in ffsNet.subnet(21):
        segment+=1
        if r in subnet:
            return (subnet,segment)
    return (None,None)
def putval(cmd,hostname):
    params = ("defined","used","free","touched")

    output = subprocess.check_output(cmd.split(" "),shell=False).decode('utf-8')
    data = json.loads(output)
    dhcpSubnets = data["subnets"]

    for param in params:
        print('PUTVAL "%s/dhcp/gauge-dhcp_%s" N:%i'%(hostname,param,data["summary"][param]))

    for dhcpSubnet in dhcpSubnets:
        dhcpRange = dhcpSubnet["range"]
        (subnet,segment) =  getSubnetFromRange(dhcpRange)
        if segment == None:
            continue
        for param in params:
            print('PUTVAL "%s/dhcp-%.2i/gauge-dhcp_%s" N:%i'%(hostname,segment,param,dhcpSubnet[param]))
    sys.stdout.flush()

def loop():
    executable = "/usr/bin/dhcpd-pools"
    if not os.path.isfile(executable):
        executable = "dhcpd-pools"
    if not os.path.isfile(executable):
        sys.exit("dhcpd-pools not found!")
    conf = "/etc/dhcp/dhcpd.conf"
    if not os.path.isfile(conf):
        sys.exit("dhcpd.conf not found")
    cmd = "%s -c %s -f j"%(executable,conf)
    hostname = os.getenv("COLLECTD_HOSTNAME")

    while True:
        putval(cmd,hostname)
        time.sleep(60)

if __name__ == "__main__":
        loop()

