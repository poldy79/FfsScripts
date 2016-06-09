
#!/usr/bin/python
import sys
import json
import psutil
import socket
import os

def readFromSocket(f):
    s = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
    s.connect(f)
    result = ""
    while(True):
        tmp = s.recv(1024*1024)
        if tmp == "":
            break
        result += tmp
    s.close()
    return result

def getPids():
    pids = {}
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name',"cmdline"])
        except psutil.NoSuchProcess:
            pass
        else:
            if pinfo["name"] == "fastd":
                socket = ""
                config = pinfo["cmdline"][pinfo["cmdline"].index("--config")+1]
                segment = os.path.dirname(config).rsplit("/",1)[1]
                pids[segment] = pinfo["pid"]
                p = psutil.Process(pinfo["pid"])
                for f in p.get_connections(kind="unix")[0].laddr:
                    if "sock" in f:
                        socket = f
    return pids

def getSocket(pid):
    p = psutil.Process(pid)
    for f in p.get_connections(kind="unix"):
        if "sock" in f.laddr:
            return f.laddr

def getSocketData():
    pids = getPids()
    interfaces = {}
    for pid in pids:
        socket = getSocket(pids[pid])
        data = readFromSocket(socket)
        interfaces[pid] = data
    return interfaces



    
