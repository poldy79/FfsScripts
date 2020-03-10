#!/usr/bin/python
import json
import time
import datetime
import argparse
from time import strftime

parser = argparse.ArgumentParser(description='Generate json for freifunk-karte.de')
parser.add_argument('-o', dest='output', action='store',
                        required=True,
                   help='Output file')
parser.add_argument('--nodes', dest='nodes', action='store',
                                        required=True,
                                                                                           help='nodes file')
args = parser.parse_args()




ts = time.time()
st = datetime.datetime.now().isoformat()

fp = open(args.nodes,"rb")

nodes = json.load(fp)
fp.close()


m = {}

m["version"] = "1.0"
m["updated_at"] = st
m["comunity"] ={ "href":"http://netinfo.freifunk-stuttgart.de/FreifunkStuttgart-api.json","name":"Freifunk Stuttgart"}

m["nodes"] = []


for node in nodes:
	n = nodes[node]
	if n["status"] == "offline":
		status = False
	else:
		status = True
	#pos = {"lat": 
	current =  {"id":node,"name":n["hostname"],"node_type":"AccessPoint","status":{"online":status,"clients":n["clients"]["total"]} }
	if n.has_key("location") and "latitude" in n["location"] and "longitude" in n["location"]:
		pos = { "lat": n["location"]["latitude"], "long":n["location"]["longitude"] }
		current["position"] = pos
	m["nodes"].append( current )

global_map = open(args.output,"wb")

global_map.write( json.dumps(m,sort_keys=True, indent=4, separators=(',', ': ')))

global_map.close()

