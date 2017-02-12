#!/usr/bin/python
import socket
import argparse
import json
import os
import sys
parser = argparse.ArgumentParser(description='Clean fastd output - remove public IP addresses')
parser.add_argument('-o', dest='output', action='store', required=True, help='Output file')
parser.add_argument('-i', dest='input', action='store', required=True, help='Input file')
parser.add_argument('-q',dest='quiet', action='store_true', required=False, help='Do not warn if input file does not exist')
args = parser.parse_args()

if not os.path.exists(args.input):
    if not args.quiet: 
        print ("Input file does not exist")
    sys.exit(-1)


s = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
s.connect(args.input)
result = ""
while(True):
    tmp = s.recv(1024*1024) 
    if tmp == "":
        break
    result += tmp
s.close()
status = json.loads(result)

for p in  status["peers"]:
        if status["peers"][p]["address"] != "any":
                status["peers"][p]["address"] = "available"

try:
    fp = open(args.output,"wb")
except:
    print "Output file could not be created"
    sys.exit(-1)


fp.write( json.dumps(status,sort_keys=True, indent=4, separators=(',', ': ')))          
fp.close()

