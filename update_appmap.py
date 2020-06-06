#!/usr/bin/python
import json
import time
import datetime
import argparse

parser = argparse.ArgumentParser(description='Generate JSON for Freifunk App')
parser.add_argument('-o', dest='output', action='store',
                        required=True,
                   help='Output file')

parser.add_argument('--raw', dest='raw', action='store',
                                        required=True,
                                                                                           help='nodes file')


args = parser.parse_args()
ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%dT%H:%M:%S')
fp = open(args.raw,"rb")

raw = json.load(fp)
fp.close()

m = {}
m["meta"] = { "timestamp": st }
m["links"] = []
m["nodes"] = []

nodes = raw["nodes"]

for node in nodes:
	n = node["statistics"]
        nodeinfo = node["nodeinfo"]
        status = node["online"]
	current =  {"id":node["nodeinfo"]["network"]["mac"],"name":node["nodeinfo"]["hostname"],"flags": { "online": status, "gateway":False} ,"clientcount":n["clients"]["total"],"firmware": node["nodeinfo"]["software"]["firmware"]["base"] }
	if nodeinfo.has_key("location") and "latitude" in nodeinfo["location"] and "longitude" in nodeinfo["location"]:
		pos = [ nodeinfo["location"]["latitude"], nodeinfo["location"]["longitude"] ]
		current["geo"] = pos
	else:
		current["geo"] = None
	m["nodes"].append( current )

map = open(args.output,"wb")
map.write( json.dumps(m,sort_keys=True, indent=4, separators=(',', ': ')))
map.close()

