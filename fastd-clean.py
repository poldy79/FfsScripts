#!/usr/bin/python
import json
import argparse

parser = argparse.ArgumentParser(description='Clean fastd output - remove public IP addresses')
parser.add_argument('-o', dest='output', action='store',
                        required=True,
                   help='Output file')

parser.add_argument('-i', dest='input', action='store',
                        required=True,
                   help='Input file')

args = parser.parse_args()

fp = open(args.input,"rb")

status = json.load(fp)
fp.close()
for p in  status["peers"]:
	if status["peers"][p]["address"] != "any":
		status["peers"][p]["address"] = "available"

fp = open(args.output,"wb")

fp.write( json.dumps(status,sort_keys=True, indent=4, separators=(',', ': ')))		
fp.close()
