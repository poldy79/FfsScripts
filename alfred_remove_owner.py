#!/usr/bin/python
import json
import argparse

parser = argparse.ArgumentParser(description='Remove personal information from alfred data')
parser.add_argument('-o', dest='output', action='store',
			required=True,
                   help='Output file')

parser.add_argument('--alfred-158', dest='alfred158', action='store',
                                required=True,
                                                   help='Aldred 158 channel data')

args = parser.parse_args()


fp158 = open(args.alfred158,"rb")
nodes = json.load(fp158)
for node in nodes:
	if nodes[node].has_key("owner"):
		nodes[node].pop("owner")

#print json.dumps(nodes,sort_keys=True, indent=4, separators=(',', ': '))


fpOut = open(args.output,"wb")
fpOut.write(json.dumps(nodes,sort_keys=True, indent=4, separators=(',', ': ')))
fpOut.close()

