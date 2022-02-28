#!/usr/bin/python3
import time
import socket
import pickle
import struct
import json
from pathlib import Path
import argparse

CARBON_SERVER = '10.191.255.243'
CARBON_PICKLE_PORT = 2004
INTERVAL = 60

class Carbon():
    def __init__(self, timestamp, input, carbon, collectd, dump, verbose):
        self.timestamp = timestamp
        self.carbon = carbon
        self.input = input
        self.dump = dump
        self.verbose = verbose
        self.collectd = collectd

    def mac2met(self, mac):
        s = mac.split(":")
        if s[2] == "0a":
            return "gw%sn01.s%s" % (s[5], s[4])
        else:
            return "gw%sn%s.s%s" % (s[4], s[5], s[3])

    def convert_mac(self, mac):
        s = mac.split(":")
        if s[2] == "0a":
            return f"gw{s[5]}n01", s[4]
        else:
            return f"gw{s[4]}n{s[5]}", s[3]

    def submit_to_carbon(self, data):
        sock = socket.socket()
        sock.connect((CARBON_SERVER, CARBON_PICKLE_PORT))
        tuples = []
        for d in data:
            tuples.append((d[0], (self.timestamp, d[1])))

        package = pickle.dumps(tuples, 1)
        size = struct.pack('!L', len(package))
        sock.sendall(size)
        sock.sendall(package)

    def commitDataGwStats(self):
        errors = []
        raw = self.raw
        gw = {}
        nodes = raw["nodes"]
        for n in nodes:
            if n["online"] == False:
                continue
            node = n["nodeinfo"]["network"]["mac"]
            try:
                clients = n["statistics"]["clients"]["total"]
                gateway = n["statistics"]["gateway"]
                has_uplink = False
                if "mesh_vpn" in n["statistics"]:
                    peers = n["statistics"]["mesh_vpn"]["groups"]["backbone"]["peers"]
                    for p in peers:
                        if peers[p] != None:
                            has_uplink = True
                            break

                if gateway not in gw:
                    gw[gateway] = {}
                    gw[gateway]["fastd"] = 0
                    gw[gateway]["nodes"] = 0
                    gw[gateway]["clients"] = 0

                if has_uplink:
                    gw[gateway]["fastd"] += 1

                gw[gateway]["nodes"] += 1
                gw[gateway]["clients"] += clients
            except:
                print("Error with node %s" % (node))
                errors.append(node)
                pass
        for mac in gw:
            # print(mac2met(mac))
            g = gw[mac]
            carbon_data = []
            prometheus_data = []
            gw_name, segment = self.convert_mac(mac)
            prefix = "alfred_gw.%s." % (self.mac2met(mac))
            carbon_data.append((prefix + "clients", g["clients"]))
            carbon_data.append((prefix + "nodes", g["nodes"]))
            carbon_data.append((prefix + "fastd", g["fastd"]))
            prometheus_data.append(f'PUTVAL "{gw_name}/respondd_segment-{segment}/gauge-clients" N:{g["clients"]}')
            prometheus_data.append(f'PUTVAL "{gw_name}/respondd_segment-{segment}/gauge-nodes" N:{g["nodes"]}')
            prometheus_data.append(f'PUTVAL "{gw_name}/respondd_segment-{segment}/gauge-fastd" N:{g["fastd"]}')

            # print(carbon_data)
            if self.carbon:
                self.submit_to_carbon(carbon_data)
            if self.collectd:
                # print(carbon_data)
                print("\n".join(prometheus_data))
        if len(errors) > 0:
            print("Eroors with nodes: %s" % (" ".join(errors)))

    def commitDataNodeStats(self):
        raw = self.raw
        nodes = raw["nodes"]
        for node in nodes:
            try:
                data = []
                hostname = node["nodeinfo"]["hostname"]
                if hostname.startswith("ffs-nbhfstr163") or hostname.startswith(
                        "ffs-es-altstadt") or hostname.startswith(
                    "71522-") or hostname.startswith("71546-"):
                    n = node["statistics"]
                    host = "alfred." + hostname + "."
                    data.append((host + "clients", n["clients"]["total"]))
                    if "loadavg" in n:
                        data.append((host + "loadavg", n["loadavg"]))
                    data.append((host + "memory.buffers", n["memory"]["buffers"]))
                    data.append((host + "memory.cached", n["memory"]["cached"]))
                    data.append((host + "memory.free", n["memory"]["free"]))
                    data.append((host + "memory.total", n["memory"]["total"]))
                    data.append((host + "processes.running", n["processes"]["running"]))
                    data.append((host + "processes.total", n["processes"]["total"]))
                    data.append((host + "traffic.forward.bytes", n["traffic"]["forward"]["bytes"]))
                    data.append((host + "traffic.forward.packets", n["traffic"]["forward"]["packets"]))
                    data.append((host + "traffic.mgmt_rx.bytes", n["traffic"]["mgmt_rx"]["bytes"]))
                    data.append((host + "traffic.mgmt_rx.packets", n["traffic"]["mgmt_rx"]["packets"]))
                    data.append((host + "traffic.mgmt_tx.bytes", n["traffic"]["mgmt_tx"]["bytes"]))
                    data.append((host + "traffic.mgmt_tx.packets", n["traffic"]["mgmt_tx"]["packets"]))
                    data.append((host + "traffic.rx.bytes", n["traffic"]["rx"]["bytes"]))
                    data.append((host + "traffic.rx.packets", n["traffic"]["rx"]["packets"]))
                    data.append((host + "traffic.tx.bytes", n["traffic"]["tx"]["bytes"]))
                    data.append((host + "traffic.tx.packets", n["traffic"]["tx"]["packets"]))
                    data.append((host + "uptime", n["uptime"]))
                    if self.carbon:
                        self.submit_to_carbon(data)
                    if self.dump:
                        print(data)
                    # print("wrote data for %s"%(hostname))
            except KeyError as e:
                pass
            except Exception as e:
                raise

    def load_json(self):
        fn = self.input
        try:
            self.raw = json.load(open(fn, "r", encoding='utf-8'))
        except Exception as e:
            size = Path(fn).stat().st_size
            print(f"Size of {fn} is {size}")
            raise

    def run(self):
        while(True):
            self.load_json()
            self.commitDataNodeStats()
            self.commitDataGwStats()
            if not self.collectd:
                break
            time.sleep(INTERVAL)

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--carbon', action='store_true',
                        help='push data to carbon')
    parser.add_argument('--collectd', action='store_true',
                        help='print collectd text format')
    parser.add_argument('--verbose', action='store_true',
                        help='print verbose')
    parser.add_argument('--dump', action='store_true',
                        help='dump data')
    parser.add_argument('-i', '--input', required=True,
                        help='input file raw.json')
    args = parser.parse_args()
    timestamp = int(time.time())
    carbon = Carbon(timestamp, input=args.input, carbon=args.carbon, collectd=args.collectd, dump=args.dump, verbose=args.verbose)
    carbon.run()


if __name__ == "__main__":
    main()
