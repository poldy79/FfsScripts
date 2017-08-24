#!/usr/bin/python
import ujson as json
import time
import datetime
fp158 = open("data/alfred-json-158-merged.json","rb")
fp159 = open("data/alfred-json-159-merged.json","rb")
fpnodes = open("data/nodes.json","rb")
try:
    fpuptime = open("uptime.json","rb")
    uptime = json.load(fpuptime)
    fpuptime.close()
except:
    uptime = {}

logToJson = False

if logToJson:
    try:
        fpreboots = open("reboots.json","rb")
        reboots = json.load(fpreboots)
        fpreboots.close()
    except:
        reboots = []
else:
    reboots = []

nodes = json.load(fpnodes)
fpnodes.close()
info = json.load(fp158)
fp158.close()
status = json.load(fp159)
fp159.close()

try:
    fplog = open("reboots.log","rb")
    log = "\n".join(fplog.read().split("\n")[0:10000])
    fplog.close()
except:
    log = ""
ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

for mac in status:
    if not mac in info:
        #print "monotor_uptime: Skipped %s"%(mac)
        continue
    if uptime.has_key(mac) and status[mac]["uptime"] < uptime[mac]["uptime"]:
        #this is a reboot
        if uptime[mac].has_key("firmware") and ( info[mac]["software"]["firmware"]["base"] != uptime[mac]["firmware"]["base"] or info[mac]["software"]["firmware"]["release"] != uptime[mac]["firmware"]["release"]):
            pass
            #print "%s has rebooted with update"%(nodes[mac]["hostname"])
        else:
            try:
                reboot = {"mac": "?", "hostname": "?", "uptime": "?", "firmware": {"release": "?", "base": "?"} , "model": "?"}
                reboot["mac"] = mac
                reboot["hostname"] = nodes[mac]["hostname"]
                reboot["epoch"] = time.time()
                reboot["iso"] = st
                reboot["uptime"] = uptime[mac]["uptime"]
                reboot["gateway"] = uptime[mac]["gateway"]
                try:    
                    reboot["firmware"] = uptime[mac]["firmware"]
                    reboot["model"] = info[mac]["hardware"]["model"]
                except:
                    print "no info about %s"%(mac)
                    pass
                if logToJson:
                    reboots.append(reboot)
                msg = "%s : %s after %i (%s, %s)\n"%(st,nodes[mac]["hostname"],uptime[mac]["uptime"],  reboot["model"],reboot["gateway"] )
                log = msg + log
            except:
                print "Exception with mac %s"%(mac)
                raise

    if not uptime.has_key(mac):
        if mac in info:
            msg =  "%s : %s has joined\n"%(st,info[mac]["hostname"])
        else:
            msg =  "%s : %s has joined\n"%(st,mac)


    current = {}
    current["firmware"] = info[mac]["software"]["firmware"]    
    current["uptime"] = status[mac]["uptime"]
    current["name"] = nodes[mac]["hostname"]
    current["last_update"] = time.time()
    current["gateway"] = nodes[mac]["gateway"]
    uptime[mac] = current
    
for u in uptime.keys():
    if (time.time() - uptime[u]["last_update"]) > 60*120: # 120 Minutes not seen 
        try:
            hostname = nodes[u]["hostname"]
        except:
            hostname = u
            pass

        msg =  "%s : %s not online for 120 min - removed\n"%(st,hostname)
        log = msg + log
        del uptime[u]

fp_uptime = open("uptime.json","wb")
fp_uptime.write( json.dumps(uptime,sort_keys=True))
fp_uptime.close()
if logToJson:
    fp_reboots = open("reboots.json","wb")
    fp_reboots.write( json.dumps(reboots,sort_keys=True, indent=4, separators=(',', ': ')))
    fp_reboots.close()

fplog = open("reboots.log","wb")
fplog.write(log)
fplog.close()

