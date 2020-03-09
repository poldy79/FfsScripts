#!/usr/bin/python
import json
import argparse
import datetime

parser = argparse.ArgumentParser(description='Generate JSON for Freifunk App')

parser.add_argument('--input', dest='input', action='store',
                        required=True,
                   help='Input file')

parser.add_argument('--output', dest='output', action='store',
                        required=True,
                   help='Output file')

parser.add_argument('--raw', dest='raw', action='store',
                        required=True,
                   help='raw.json file')

args = parser.parse_args()


fp = open(args.raw,"rb")
raw = json.load(fp)
fp.close()
nodes = raw["nodes"]
nodecount = 0
for node in nodes:
    if node["online"] == True:
		nodecount+=1

with open(args.input,"rb") as fd:
    map = json.load(fd)

timestamp = "%sZ"%(datetime.datetime.utcnow().isoformat())

map["state"]["nodes"] = nodecount 
map["state"]["lastchange"] = timestamp



with  open(args.output,"wb") as fd:
    fd.write( json.dumps(map,sort_keys=True, indent=4, separators=(',', ': ')))
