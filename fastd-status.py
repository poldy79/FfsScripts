#!/usr/bin/python
import socket
import argparse
import json
import os
import sys
parser = argparse.ArgumentParser(description='Clean fastd output - remove public IP addresses')
parser.add_argument('-o', dest='output', action='store', required=False, help='Output file')
parser.add_argument('-i', dest='input', action='store', required=True, help='Input file')
parser.add_argument('-q',dest='quiet', action='store_true', required=False, help='Do not warn if input file does not exist')
parser.add_argument('--show-address',dest='showAddress', action='store_true', required=False, help='show ip adresses in output')
parser.add_argument('--show-unconnected',dest='showUnconnected', action='store_true', required=False, help='show also unconnected')
args = parser.parse_args()

dslite = ["46.5.254.26",]

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
unconnected = []

for p in  status["peers"]:
    if status["peers"][p]["address"] != "any":
        if status["peers"][p]["address"].split(":")[0] in dslite:
            status["peers"][p]["protocol"] = "IPv4 ds-lite"
        elif "." in status["peers"][p]["address"]:
            status["peers"][p]["protocol"] = "IPv4"
        elif ":" in status["peers"][p]["address"]:
            status["peers"][p]["protocol"] = "IPv6"
        if not args.showAddress:
            status["peers"][p]["address"] = "available"
    else:
        unconnected.append(p)

if not args.showUnconnected:
    for u in unconnected:
        del status["peers"][u]

jsons = json.dumps(status,sort_keys=True, indent=4, separators=(',', ': '))

if args.output == None:
    print(jsons)
else:
    if args.showAddress and args.output != None:
        print("Output to file not allowed if addresses are shown!")
        sys.exit(-1)
    try:
        with open(args.output,"w") as fp:
            fp.write(jsons)
    except:
        print("Output file could not be created")
        sys.exit(-1)



