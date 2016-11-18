#!/usr/bin/python
import sys
import time
import socket
import pickle
import struct
import random
import json
import fastd
CARBON_SERVER = '10.191.255.253'
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
    fastd_data  = fastd.getSocketData()
    for interface in fastd_data:
        f = fastd_data[interface]
        print f
        break
    data = []
    prefix =  "gw01n00.freifunk-stuttgart.de.fastd."
    data.append((prefix+"clients",0))
    #submit(data,timestamp)

def main():
    timestamp = int(time.time())
    commitData(timestamp)

if __name__ == "__main__":
    main()
