#!/usr/bin/python
import munin
import socket
import json
import os
import sys
import glob

def getData():
    sockets = glob.glob("/var/run/fastd-vpn??.sock")
    connections = {}
    
    for f in sockets:
        field = os.path.basename(f).split("-")[1].split(".")[0]
        connections[field] = 0
        s = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        s.connect(f)
        result = ""
        while(True):
            tmp = s.recv(1024*1024)
            if tmp == "":
                break
            result += tmp
        s.close()
        status = json.loads(result)

        for p in  status["peers"]:
                if status["peers"][p]["address"] != "any":
                        connections[field] += 1
    return connections


category = 'network'
vlabel = 'connections'

def values():
    global connections
    return connections


connections = getData()
fields = connections.keys()

if __name__ == '__main__':
    munin.main()
