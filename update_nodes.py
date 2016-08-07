#!/usr/bin/python
import ujson as json
import time
import sys
import traceback
from georeference import getRegion

import email
import smtplib
from email.mime.text import MIMEText
import batman_adv
import argparse

def send(sender,to,subject, message):

    # Open a plain text file for reading.  For this example, assume that
    # the text file contains only ASCII characters.
    # Create a text/plain message
    msg = MIMEText(message)

    # me == the sender's email address
    # you == the recipient's email address
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP('localhost')
    s.sendmail(sender, [to], msg.as_string())
    s.quit()


parser = argparse.ArgumentParser(description='Update nodes json file')

parser.add_argument('--mesh', dest='mesh', action='store',
            required=True,
           help='batadv-vis preparsed mesh info')

parser.add_argument('--alfred-158', dest='alfred158', action='store',
            required=True,
           help='Aldred 158 channel data')

parser.add_argument('--alfred-159', dest='alfred159', action='store',
            required=True,
           help='Alfred 159 channel data')

parser.add_argument('--alfred-160', dest='alfred160', action='store',
            required=True,
           help='Alfred 160 channel data')

parser.add_argument('--nodes', dest='nodes', action='store',
            required=True,
           help='nodes file')

parser.add_argument('--nodes_map', dest='nodes_map', action='store',
            required=True,
           help='nodes_map file')

parser.add_argument('--mailto', dest='mailto', action='store',
            required=True,
           help='mail to')

parser.add_argument('--mailfrom', dest='mailfrom', action='store',
            required=True,
           help='mail from')


args = parser.parse_args()
transtable = batman_adv.getTranstableGlobal()

def getFastdConnections(node,gk):
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

def getSegment(gateway):
    try:
        if gateway.split(":")[2] == "0a":
            return int(gateway.split(":")[4])
        else:
            return int(gateway.split(":")[3])
    except:
        print "Exception with GW %s"%gateway
        return None

def getNodeConnections():
    node_connections = {}
    for n in nodes_mesh:
        neighbours = []
        if "batadv" in nodes_mesh[n]:
            for iface in nodes_mesh[n]["batadv"]:
                neighbours+= nodes_mesh[n]["batadv"][iface]["neighbours"].keys()
        #print  nm[n]["batadv"]
        gws = []
        for g in neighbours:
            if g.startswith("02:00:3") or g.startswith("02:00:0a:3"):
                gws.append(g)

        nodes = [x for x in neighbours if x not in gws]
        #gws = [x for x in neighbours if x in gk]
        node_connections[n] ={"nodes": nodes, "gws":gws}
    return node_connections

fp158 = open(args.alfred158,"rb")
fp159 = open(args.alfred159,"rb")
fp160 = open(args.alfred160,"rb")
fp_nodes_all = open(args.nodes,"rb")
nodes_info = json.load(fp158)
nodes_status = json.load(fp159)
nodes_mesh = json.load(fp160)
nodes_all = json.load(fp_nodes_all)
fp_nodes_all.close()

#build up gateway list
gk = batman_adv.getGateways()
gk.append("02:00:38:03:07:02")
gk.sort()

node_connections = getNodeConnections()

for mac in nodes_info:
    n = nodes_info[mac]
    if not n.has_key("owner"):
        n["owner"] = ""
    if not nodes_all.has_key(mac):
        #totaly new node
        nodes_all[mac] = {}        
        name = None
        try:
            name = "unknown"
            if mac in nodes_info and "hostname" in nodes_info[mac]:
                name = nodes_info[mac]["hostname"]
            no = nodes_info[mac]
            region = "Unknown"
            if no.has_key("location"):
                if "longitude" in no["location"] and "latitude" in no["location"]:
                    (region,desiredSegment) = getRegion(no["location"]["latitude"],no["location"]["longitude"])
            send(args.mailfrom,args.mailto,"New Node anounced","MAC: %s\nName: %s\nregion %s\nSegment: %s"%(mac,name,region,desiredSegment))
        except:
            print "Error sending mail for mac %s"%(mac)
            print name
            traceback.print_exc(file=sys.stdout)
            pass

hiddenNodes = []
alfred = 0
tt = 0

for mac in nodes_all:
    n = nodes_all[mac]
    if n.has_key("owner"):
        n.pop("owner")
    if nodes_info.has_key(mac) and nodes_status.has_key(mac):
        alfred+=1   
        no = nodes_info[mac]
        nos = nodes_status[mac]
        n["status"] = "online"
        n["hostname"] = no["hostname"]
        n["hardware"] = no["hardware"]
        n["network"] = no["network"]
        n["loadavg"] = nos["loadavg"]
        if mac in node_connections:
            n["neighbours"] = node_connections[mac]["nodes"]
        if nos.has_key("gateway"):
            n["gateway"] = nos["gateway"]
            n["segment"] = getSegment(nos["gateway"])
        else:
            n["gateway"] = ""
        if no.has_key("location"):
            n["location"] = no["location"]        
            if "longitude" in n["location"] and "latitude" in n["location"]:
                (n["region"],n["desiredSegment"]) = getRegion(n["location"]["latitude"],n["location"]["longitude"])
        else:
            if n.has_key("location"):
                n.pop("location")
                n["region"] = "No Location"
        n["software"] = no["software"]
        n["last_online"] = int(time.time())
        n["last_alfred"] = int(time.time())
        if nodes_status[mac].has_key("clients"):
            n["clients"] = nodes_status[mac]["clients"]
        n["fastd"] = getFastdConnections(mac,gk)
    elif transtable.has_key(mac):
        tt+=1
        print "target: %s"%(mac)
        n["last_online"] = int(time.time())
        n["status"] = "online"
    #elif n["last_online"] > int(time.time())-60*15:
    #    #has been seen 15minutes ago
    #    print "node has been online last 15 min: %s"%(mac)
    else:
        n["status"] = "offline"
        n["clients"]["total"] = 0
        n["clients"]["wifi"] = 0
        n["gateway"] = ""
        n["fastd"] = []
        n["neighbours"] = []
        deltaWeek = 7*24*60*60
        if n["last_online"] < int(time.time())-deltaWeek:
            hiddenNodes.append(mac)

fp_nodes_all = open(args.nodes,"wb")
#fp_nodes_all.write( json.dumps(nodes_all,sort_keys=True, indent=4, separators=(',', ': ')))
fp_nodes_all.write( json.dumps(nodes_all,sort_keys=True))
fp_nodes_all.close()

for hidden in hiddenNodes:
    del nodes_all[hidden]

fp_nodes_all = open(args.nodes_map,"wb")
#fp_nodes_all.write( json.dumps(nodes_all,sort_keys=True, indent=4, separators=(',', ': ')))
fp_nodes_all.write( json.dumps(nodes_all,sort_keys=True))
fp_nodes_all.close()



