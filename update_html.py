#!/usr/bin/python
import codecs
import json
import argparse
import time
from time import strftime

parser = argparse.ArgumentParser(description='Generate HTML nodelist')
parser.add_argument('-o', dest='output', action='store',
                        required=True,
                   help='Output file')

parser.add_argument('--mesh', dest='mesh', action='store',
                                required=True,
                                                   help='batadv-vis preparsed mesh info')

parser.add_argument('--nodes-', dest='nodes', action='store',
                                required=True,
                                                   help='nodes file')

parser.add_argument('--alfred-158', dest='alfred158', action='store',
                                required=True,
                                                   help='Aldred 158 channel data')

parser.add_argument('--alfred-159', dest='alfred159', action='store',
                                required=True,
                                                   help='Alfred 159 channel data')

args = parser.parse_args()

regions = {"No Location":{ "nodes":0,"clients":0} , "Unknown Region":  { "nodes":0, "clients":0 }}

def getFastdConnections(node):
	mesh_fp = open(args.mesh,"rb")
	mesh = json.load(mesh_fp)
	mesh_fp.close()
        alias = mesh["alias"]
        fastd = []
        if mesh["alias"].has_key(node):
                primary = mesh["alias"][node]
                for neigh in mesh["primary"][primary]:
                        if neigh in gk:
                                fastd.append(neigh[-1:])
        fastd.sort()
	return fastd

def getGwInstance(mac):
    m = mac.split(":")
    if len(m) <6:
        print "Len: %i: %s"%(len(mac),mac)
        return "gw??n??"
    if m[2] == "0a":
        return "gw%sn%s"%(m[5],"00")
    else:
        return "gw%sn%s"%(m[4],m[5])
    return "gw??n??"

mesh_fp = open(args.mesh,"rb")
mesh = json.load(mesh_fp)
mesh_fp.close()
nodes_fp = open(args.nodes,"rb")
nodes_info = json.load(nodes_fp)

fp158 = open(args.alfred158,"rb")
fp159 = open(args.alfred159,"rb")
fp_nodes_all = open(args.nodes,"rb")
nodes_online_info = json.load(fp158)
nodes_online_status = json.load(fp159)
fp158.close()
fp159.close()

nodesPerSegment = {}
clientsPerSegment = {}
nodesPerGw = {}
clientsPerGw = {}
nodesInWrongSegment = 0
nodesInWrongSegmentAndOnline = 0
locationcount = 0
clients = 0
alfredErrors = []
nodesTotal = 0
html = ""
html2 = ""
head= '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">'
head+= "<html>"
head+= '<head><script type="text/javascript" language="javascript" src="tablefilter/tablefilter.js"></script></head>'
head+= "<body>"
html+=head
html2+=head



table= '<table id="table1" cellspacing="0" class="mytable filterable"><tr><th>Node</th><th>Mac</th><th>Status</th><th>Load</th><th>Seg</th><th>DestSeg</th><th>Clients</th><th>mesh</th><th>GW</th><th>fastd</th><th>Model</th><th>location</th><th>update</th><th>gluon</th><th>release</th><th>IP</th></tr>'
online = 0
gateways= {}
nodes = {}
nodes_list = []
gk = []
for node in nodes_info:
	n = nodes_info[node]
	if n["gateway"] != "" and not n["gateway"] in gk:
		gk.append(n["gateway"])
gk.sort()
		
	
for node in nodes_info:
	n = nodes_info[node]
        if n["status"] == "offline":
            currentTime = int(time.time())
            deltaWeek = 7*24*60*60
            if n["last_online"] < currentTime - deltaWeek:
                #node ist more than one week offline
                continue
	nodesTotal+=1
        nos = {}
        if node in nodes_online_status:
            nos = nodes_online_status[node]

        if n.has_key('location') and n["location"].has_key("latitude") and n["location"].has_key("longitude"):
		location='yes'
		locationcount+=1
                if "region" in n:
    		    location = n["region"]
                else:
                    location = "Outside"
		if location == "Outside":
			location = "Raw: %f,%f"%(n["location"]["latitude"],n["location"]["longitude"])
			if n["status"] == "online":
				regions["Unknown Region"]["nodes"] +=1 
				regions["Unknown Region"]["clients"] += int(n['clients']['total'])
		else:
			if n["status"] == "online":
                                if not location in regions:
                                    regions[location] = {"nodes":0, "clients":0}
				regions[location]["nodes"] +=1
				regions[location]["clients"] += int(n['clients']['total'])
	else:
                if "location" in n:
                    location='<font color="#FF0000">incomplete</font>'	
                else:
                    location='<font color="#FF0000">no location</font>'	
		if n["status"] == "online":
			regions["No Location"]["nodes"] +=1
			regions["No Location"]["clients"] += int(n['clients']['total'])
	if n.has_key('hardware'):
		model = nodes_info[node]['hardware']['model']
	else:
		model = "Unknown"
	clients+=int(n['clients']['total'])
	branch = n['software']['autoupdater']['branch']
	
	if n['software']['autoupdater']['enabled'] == False:
		update = '<font color="#FF0000">disabled</font>'
	else:
		update = "enabled"
	branch += " (%s)"%(update)
	base = n['software']['firmware']['base']
	release = n['software']['firmware']['release']
	hostname = n['hostname']
	gateway = n['gateway']
	nodes_list.append((hostname,node))
	wificlients = n['clients']['wifi']
	totalclients = n['clients']['total']
        segment = "?"
	if not gateway == "":
		if not gateways.has_key(gateway):
			gateways[gateway] = {"nodes":0, "clients":0}
		gateways[gateway]["nodes"] +=1
		gateways[gateway]["clients"] += totalclients
        if n.has_key("segment") and n["segment"] != None:
            segment = "%02i"%(n["segment"])
        if not segment in clientsPerSegment:
            clientsPerSegment[segment] = 0
        clientsPerSegment[segment] += totalclients
        desiredSegment = "?"
        if "desiredSegment" in n:
            desiredSegment = n["desiredSegment"]
            if desiredSegment != segment:
                desiredSegment="<font color=#FF0000>%s</font>"%(n["desiredSegment"])
                nodesInWrongSegment+=1
                if n["status"] == "online":
                    nodesInWrongSegmentAndOnline+=1
            if n["desiredSegment"] == "undefined":
                desiredSegment = "?"
        if len(gateway) > 0:
            if not getGwInstance(gateway) in clientsPerGw:
                clientsPerGw[getGwInstance(gateway)] = 0
            clientsPerGw[getGwInstance(gateway)] += totalclients
	ip = ""
	status = "unknown"
	if n.has_key("network"):
		for ip in n['network']['addresses']:
                    if ip.startswith("fd21:b4dc"):
			break
        ip = "<a href='http://[%s]/'>%s</a>"%(ip,ip)
        mesh_status = "no"
	alias = mesh["alias"]
	if alias.has_key(node):
		if n["status"] == "offline":
			alfredErrors.append(node)
			mesh_status = "<font color='#FF0000'>yes</font>"
		else:
			mesh_status = "yes"
	fastd = []
	if mesh["alias"].has_key(node):
		primary = mesh["alias"][node]
		for neigh in mesh["primary"][primary]:
			if neigh in gk:
				fastd.append("GW0%s"%(neigh[-1:]))
	fastd.sort()
	fastd = ",".join(fastd)	
	if n.has_key("status"):
		status = n["status"]
                if status=="offline":
                    if mesh_status != "no":
                        status='<font color="#FF0000">alfred error</font>'
                    else:    
                        status='<font color="#FF0000">offline</font>'
		else:
			online+=1
                        if segment not in nodesPerSegment:
                            nodesPerSegment[segment] = 0
                        nodesPerSegment[segment] += 1
                        if gateway != "":
                            if not getGwInstance(gateway) in nodesPerGw:
                                nodesPerGw[getGwInstance(gateway)] = 0
                            nodesPerGw[getGwInstance(gateway)] += 1
	mesh_status = "no"
        loadavg = "?"
        if "loadavg" in n:
            loadavg = n["loadavg"]
        
        fastd = []
        if "mesh_vpn" in nos:
            peers = nos["mesh_vpn"]["groups"]["backbone"]["peers"]
            for peer in peers:
                if peers[peer] != None:
                    fastd.append(peer)
	fastd = ",".join(fastd)	
        neighbours = 0
        if "neighbours" in n:
            neighbours = len(n["neighbours"])

        nodes[node] = {"neighbours": neighbours , "segment": segment, "desiredSegment":desiredSegment , "hostname": hostname, "mac": node, "status": status,"mesh_status": mesh_status,"fastd": fastd,  "wificlients": wificlients, "totalclients": totalclients, "model": model, "location":location, "update": branch ,"gluon": base , "release": release, "ip":ip, "gateway": gateway, "loadavg":loadavg }

nodes_list.sort()
for hostname,node in nodes_list:
	node_data = nodes[node]
	table+="<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%i</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"%(node_data["hostname"],node_data['mac'],node_data['status'],node_data["loadavg"], node_data["segment"] , node_data["desiredSegment"],node_data['totalclients'],node_data["neighbours"], node_data['gateway'],node_data["fastd"],node_data['model'],node_data['location'],node_data['update'],node_data['gluon'],node_data['release'],node_data ['ip'])

table +="</table>"

table += '''
<script language="javascript" type="text/javascript">  
    //<![CDATA[
    var filtersConfig = {
        base_path: 'tablefilter/',
        auto_filter: true,
        auto_filter_delay: 1100, //milliseconds
        filters_row_index: 1,
        state: true,
        alternate_rows: true,
        rows_counter: true,
        rows_counter_text: "Rows: ",
        btn_reset: true,
        status_bar: true,
        msg_filter: 'Filtering...'
    };
    var tf = new TableFilter('table1', filtersConfig);
    tf.init();
    //]]>
</script> 
'''

html2 += "Generated: %s"%(strftime("%Y-%m-%d %H:%M:%S"))
html2 += "<p/>Nodes total: %i<br/>"%(nodesTotal)
html2 +="Nodes online: %i<br/>"%(online)
html2 += "Nodes with location: %i<br/>"%(locationcount)
html2+= "Wifi-Clients: %i<br/>"%(clients)
html2+="Alfred Errors %i (%s)<br/>"%(len(alfredErrors),",".join(alfredErrors))
html2 += "Nodes in wrong segment: %i<br/>"%(nodesInWrongSegment)
html2 += "Nodes in wrong segment and online: %i<br/>"%(nodesInWrongSegmentAndOnline)
segmentTable = "<table id='table2' border=1>\n"
segmentTable += "<tr><th>Segment</th><th>Nodes</th><th>Clients</th></tr>\n"
nodesPerSegmentArray = nodesPerSegment.keys()
nodesPerSegmentArray.sort()
for s in nodesPerSegmentArray:
    segmentTable+= "<tr><td>%s</td><td>%i</td><td>%i</td></tr>"%(s,nodesPerSegment[s],clientsPerSegment[s])
segmentTable+="</table><p/>"
html2+=segmentTable

gatewayTable = "<table id='table3' border=1>\n"
gatewayTable += "<tr><th>Gateway</th><th>Nodes</th><th>Clients</th></tr>\n"
nodesPerGwSorted = nodesPerGw.keys()
nodesPerGwSorted.sort()
for s in nodesPerGwSorted:
    gatewayTable += "<tr><td>%s</td><td>%i</td><td>%i</td></tr>"%(s,nodesPerGw[s],clientsPerGw[s])
gatewayTable += "</table><p/>"
html2+=gatewayTable

import operator
#sorted_regions = sorted(regions.items(), key=operator.itemgetter(1), reverse=True)
#for r in sorted_regions:
#	html += "%s: %i<br/>"%(r[0],r[1])
html2+="<table id='table4' border='1'>\n\t<tr><th>Region</th><th>Nodes</th><th>Clients</th></tr>\n"
regionsArray = regions.keys()
regionsArray.sort()
for r in regionsArray:
        nodes = regions[r]["nodes"]
        clients = regions[r]["clients"]
	html2 += "\t<tr><td>%s</td><td>%i</td><td>%i</td></tr>\n"%(r,nodes,clients)
html2 += "</table>"
for g in gk:
	html2+="%s: Nodes: %i Clients: %i<br/>"%(g,gateways[g]["nodes"],gateways[g]["clients"])
fp = codecs.open(args.output.replace("nodes.html","status.html"),"w","utf-8")
fp.write(html2+"</body></html>")
fp.close()


html +=table
html += "</body></html>"
fp = codecs.open(args.output, "w", "utf-8")
fp.write(html)
fp.close()
