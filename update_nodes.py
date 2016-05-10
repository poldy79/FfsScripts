#!/usr/bin/python
import ujson as json
import time

from georeference import getRegion, getRegions

import email
import smtplib
from email.mime.text import MIMEText
import batman_adv

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

import argparse

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
#originators = batman_adv.o
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

fp158 = open(args.alfred158,"rb")
fp159 = open(args.alfred159,"rb")
fp_nodes_all = open(args.nodes,"rb")
nodes_online_info = json.load(fp158)
nodes_online_status = json.load(fp159)
nodes_all = json.load(fp_nodes_all)
fp_nodes_all.close()

gk = []
for node in nodes_all:
    n = nodes_all[node]
    if n["gateway"] != "" and not n["gateway"] in gk:
        gk.append(n["gateway"])
gk.sort()


for mac in nodes_online_info:
    n = nodes_online_info[mac]
    if not n.has_key("owner"):
        n["owner"] = ""
    if not nodes_all.has_key(mac):
        #totaly new node
        nodes_all[mac] = {}        
        name = None
        try:
            name = nodes_online_info[mac]["hostname"]
            mail.send(args.mailfrom,args.mailto,"New Node anounced","MAC: %s\nName: %s\n"%(mac,name))
        except:
            print "Error sending mail for mac %s"%(mac)
            print name
            pass
hiddenNodes = []
alfred = 0
tt = 0

for mac in nodes_all:
    n = nodes_all[mac]
    if n.has_key("owner"):
        n.pop("owner")
    if nodes_online_info.has_key(mac) and nodes_online_status.has_key(mac):
        alfred+=1   
        no = nodes_online_info[mac]
        nos = nodes_online_status[mac]
        n["status"] = "online"
        n["hostname"] = no["hostname"]
        n["hardware"] = no["hardware"]
        n["network"] = no["network"]
        n["loadavg"] = nos["loadavg"]
        if nos.has_key("gateway"):
            n["gateway"] = nos["gateway"]
            n["segment"] = getSegment(nos["gateway"])
        else:
            n["gateway"] = ""
        if no.has_key("location"):
            n["location"] = no["location"]        
            if "longitude" in n["location"] and "latitude" in n["location"]:
                n["region"] = getRegion(n["location"]["latitude"],n["location"]["longitude"])
        else:
            if n.has_key("location"):
                n.pop("location")
                n["region"] = "No Location"
        n["software"] = no["software"]
        n["last_online"] = int(time.time())
        n["last_alfred"] = int(time.time())
        if nodes_online_status[mac].has_key("clients"):
            n["clients"] = nodes_online_status[mac]["clients"]
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



