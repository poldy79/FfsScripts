#!/usr/bin/python
import json
import argparse

parser = argparse.ArgumentParser(description='Generate JSON for Freifunk App')

parser.add_argument('--input', dest='input', action='store',
                        required=True,
                   help='Input file')

parser.add_argument('--output', dest='output', action='store',
                        required=True,
                   help='Output file')

parser.add_argument('--nodes', dest='nodes', action='store',
                        required=True,
                   help='nodes file')

args = parser.parse_args()


fp = open(args.nodes,"rb")
nodes = json.load(fp)
fp.close()

nodecount = 0
for node in nodes:
	n = nodes[node]
	if n["status"] == "online":
		nodecount+=1

fd = open(args.input,"rb")
map = json.load(fd)
fd.close()

map["state"]["nodes"] = nodecount 

fd = open(args.output,"wb")
fd.write( json.dumps(map,sort_keys=True, indent=4, separators=(',', ': ')))
fd.close()
