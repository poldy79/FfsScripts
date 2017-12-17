#!/usr/bin/python

import time
import json

import argparse

parser = argparse.ArgumentParser(description='Generate json for stats')
parser.add_argument('--stats', dest='data', action='store',
                        required=True,
                   help='Output file')

parser.add_argument('--nodes-', dest='nodes', action='store',
                                        required=True,
                                                     help='nodes file')

args = parser.parse_args()



nodes_fp = open(args.nodes,"rb")
nodes = json.load(nodes_fp)
nodes_fp.close()
clients = 0
online = 0
total = len(nodes)
for node in nodes:
	n = nodes[node]
	clients+=int(n['clients']['total'])
	hostname = n['hostname']
	if n.has_key("status"):
		status = n["status"]
		if status!="offline":
			online+=1
#print clients
try:
	stats_fp = open(args.data,"rb")
	stats = json.load(stats_fp)
	stats_fp.close()
except:
	raise
	stats = {}
	stats["hourly"] = {}
	stats["daily"] = {}

lt = time.localtime()
minute = lt.tm_min
hour = str(lt.tm_hour).zfill(2)
day = "%s-%s-%s"%(str(lt.tm_year),str(lt.tm_mon).zfill(2),str(lt.tm_mday).zfill(2))


for (span,index) in [("hourly",hour),("daily",day)]:
#stats["hourly"][hour]["..."] = ...
#stats["daily"][day]["..."] = ...
	if not stats[span].has_key(index) or (span=="hourly" and minute ==0):
		stats[span][index] = {}
		stats[span][index]["clients"] = 0
		stats[span][index]["nodes_online"] = 0
		stats[span][index]["nodes_total"] = 0

	if stats[span][index]["clients"] < clients:
		stats[span][index]["clients"] = clients
	 
	if stats[span][index]["nodes_online"] < online:
		stats[span][index]["nodes_online"] = online
	 
	if stats[span][index]["nodes_total"] < total:
		stats[span][index]["nodes_total"] = total


#print stats
fp_stats = open(args.data,"wb")
fp_stats.write( json.dumps(stats,sort_keys=True, indent=4, separators=(',', ': ')))
fp_stats.close()

