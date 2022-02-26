#!/usr/bin/python3
import sys
import time
import socket
import pickle
import struct
import random
import json
from pathlib import Path
CARBON_SERVER = '10.191.255.243'
CARBON_PICKLE_PORT = 2004

def submit(data,timestamp):
    sock = socket.socket()
    sock.connect( (CARBON_SERVER, CARBON_PICKLE_PORT) )

    tuples = []
    for d in data:
        tuples.append((d[0],(timestamp,d[1])))

    package = pickle.dumps(tuples, 1)
    size = struct.pack('!L', len(package))
    sock.sendall(size)
    sock.sendall(package)

def commitData(timestamp):
    fn = "/root/freifunk/data/raw.json"
    try:
        raw = json.load(open(fn,"r",encoding='utf-8'))
    except Exception as e:
        size = Path(fn).stat().st_size
        print(f"Size of {fn} is {size}")
        raise
    nodes = raw["nodes"]
    for node in nodes:
        try:
            data = []
            hostname = node["nodeinfo"]["hostname"]
            if hostname.startswith("ffs-nbhfstr163") or hostname.startswith("ffs-es-altstadt") or hostname.startswith("71522-") or hostname.startswith("71546-"):
                n = node["statistics"]
                host =  "alfred."+hostname+"."
                data.append((host+"clients",n["clients"]["total"]))
                if "loadavg" in n:
                    data.append((host+"loadavg",n["loadavg"]))
                data.append((host+"memory.buffers",n["memory"]["buffers"]))
                data.append((host+"memory.cached",n["memory"]["cached"]))
                data.append((host+"memory.free",n["memory"]["free"]))
                data.append((host+"memory.total",n["memory"]["total"]))
                data.append((host+"processes.running",n["processes"]["running"]))
                data.append((host+"processes.total",n["processes"]["total"]))
                data.append((host+"traffic.forward.bytes",n["traffic"]["forward"]["bytes"]))
                data.append((host+"traffic.forward.packets",n["traffic"]["forward"]["packets"]))
                data.append((host+"traffic.mgmt_rx.bytes",n["traffic"]["mgmt_rx"]["bytes"]))
                data.append((host+"traffic.mgmt_rx.packets",n["traffic"]["mgmt_rx"]["packets"]))
                data.append((host+"traffic.mgmt_tx.bytes",n["traffic"]["mgmt_tx"]["bytes"]))
                data.append((host+"traffic.mgmt_tx.packets",n["traffic"]["mgmt_tx"]["packets"]))
                data.append((host+"traffic.rx.bytes",n["traffic"]["rx"]["bytes"]))
                data.append((host+"traffic.rx.packets",n["traffic"]["rx"]["packets"]))
                data.append((host+"traffic.tx.bytes",n["traffic"]["tx"]["bytes"]))
                data.append((host+"traffic.tx.packets",n["traffic"]["tx"]["packets"]))
                data.append((host+"uptime",n["uptime"]))
                #print(data)
                submit(data,timestamp)
                #print("wrote data for %s"%(hostname))
        except Exception as e:
            pass

def main():
    timestamp = int(time.time())

    commitData(timestamp)

if __name__ == "__main__":
    main()
