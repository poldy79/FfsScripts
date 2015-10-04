#!/usr/bin/python

import json



import argparse

parser = argparse.ArgumentParser(description='Update nodes json file')

parser.add_argument('--mesh', dest='mesh', action='store',
                                required=True,
                                                   help='batadv-vis preparsed mesh info')

parser.add_argument('--batadv-vis', dest='batadvvis', action='store',
                                required=True,
                                                   help='batman-vis json')

parser.add_argument('--nodes', dest='nodes', action='store',
                                required=True,
                                                   help='nodes file')

args = parser.parse_args()



fp_nodes = open(args.nodes,"rb")
nodes = json.load(fp_nodes)
fp_nodes.close()

fp_mesh = open(args.batadvvis,"rb")
mesh = fp_mesh.read().strip().split("\n")
fp_mesh.close()

primary = {}
secondary = {}
gateway = {}
alias = {}
for line in mesh:
	j = json.loads(line)
	if j.has_key("primary"):
		if primary.has_key(j["primary"]):
			print "Double primary"
			print 1/0 #occures often
		primary[j["primary"]] = {}
		alias[j["primary"]] = j["primary"]

for line in mesh:
	j = json.loads(line)
	if j.has_key("secondary"):
		if secondary.has_key(j["secondary"]):
			print "Double secondary"
			print 1/0
		secondary[j["secondary"]] = j["of"]
		alias[j["secondary"]] = j["of"]

for line in mesh:
	j = json.loads(line)
	if j.has_key("gateway"):
		if gateway.has_key(j["gateway"]) and gateway[j["gateway"]] !=  j["router"]:
			#print "Double gateway"
			#print "%s vs. %s"%(gateway[j["gateway"]], j["router"])
			pass
		gateway[j["gateway"]] = j["router"]
		alias[j["gateway"]] = j["router"]

for line in mesh:
	j = json.loads(line)
	if j.has_key("neighbor"):
		mac = alias[j["router"]]
		if not primary.has_key(mac):
			print "Finally not resolved"	
			print 1/0
		else:
			primary[mac][j["neighbor"]] = j["label"]


out = {}
out["primary"] = primary
#out["secondary"] = secondary
#out["gateway"] = gateway
out["alias"] = alias

fp_out = open(args.mesh,"wb")
fp_out.write( json.dumps(out,sort_keys=True, indent=4, separators=(',', ': ')))
fp_out.close()

