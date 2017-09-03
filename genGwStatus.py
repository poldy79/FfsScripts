#!/usr/bin/python3
# encoding: utf-8
'''
genGwStatus -- generator for gwstatus.json
'''

import sys
import os
import time
import json
import subprocess

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2017-09-03'
__updated__ = '2017-09-03'

DEBUG = 1
TESTRUN = 0
PROFILE = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def getPeak24h():
    vnstat = json.loads(subprocess.check_output(["/usr/bin/vnstat", "-h", "--json"]).decode('utf-8'))
    #with open("/home/leonard/freifunk/FfsScripts/vnstat.json","r") as fp:
    #    vnstat = json.load(fp)
    hours = vnstat["interfaces"][0]["traffic"]["hours"]
    peak  = 0
    for h in hours:
        if h["tx"] > peak:
            peak = h["tx"]
    return peak/1024/3600*8
    
def getPreference():
    preference = int((300-getPeak24h()) / 3) # max 300mbit
    return preference
    
def genData(preference = 80, active = 1):
    data = {}
    data["version"] = "1"
    data["timestamp"] = int(time.time())
    segment = {}
    segment["preference"] = preference
    segment["dnsactive"] = active
    
    segments = {}
    for s in range(1,18):
        segments[s] = segment
    
    data["segments"] = segments 
    return data

def genJson(data,output):
    with open(output,"w") as fp:
        json.dump(data,fp ,indent=4,separators=(',', ': ')) 
    

#def main(argv=None): # IGNORE:C0111
if __name__ == "__main__":

    # Setup argument parser
    parser = ArgumentParser(description="Generator for gwstats.json", formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("-o", "--output", dest="output", action="store", required=True, help="output filename")

    # Process arguments
    args = parser.parse_args()

    preference = getPreference()
    data = genData(preference=preference)
    genJson(data,args.output)
