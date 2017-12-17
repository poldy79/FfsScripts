#!/usr/bin/python
import json
import time
import datetime


import argparse

parser = argparse.ArgumentParser(description='Generate JSON for Freifunk App')
parser.add_argument('-o', dest='output', action='store',
                        required=True,
                   help='Output file')

parser.add_argument('--nodes', dest='nodes', action='store',
                                        required=True,
                                                                                           help='nodes file')


args = parser.parse_args()



ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%dT%H:%M:%S')
fp = open(args.nodes,"rb")

nodes = json.load(fp)
fp.close()


m = {}


m["meta"] = { "timestamp": st }
m["links"] = []
m["nodes"] = []


for node in nodes:
	n = nodes[node]
	if n["status"] == "offline":
		status = False
	else:
		status = True
	current =  {"id":node,"name":n["hostname"],"flags": { "online": status, "gateway":False} ,"clientcount":n["clients"]["total"],"firmware": n["software"]["firmware"]["base"] }
	if n.has_key("location") and "latitude" in n["location"] and "longitude" in n["location"]:
		pos = [ n["location"]["latitude"], n["location"]["longitude"] ]
		current["geo"] = pos
	else:
		current["geo"] = None
	m["nodes"].append( current )

map = open(args.output,"wb")

map.write( json.dumps(m,sort_keys=True, indent=4, separators=(',', ': ')))

map.close()

