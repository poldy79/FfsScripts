#!/usr/bin/python3
import time
import json
from pathlib import Path
from prometheus_client import start_http_server, Gauge
import argparse

# Prometheus Metriken definieren
class PrometheusExporter:
    def __init__(self, input_file, port=9100):
        self.input_file = input_file
        self.port = port
        self.gauge = Gauge('collectd_respondd_segment_gauge', 
                           'Etwas überladene metrik für clients, tunnel und nodes pro GW',
                           ['respondd_segment', 'type','instance', ])


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

    def update_metrics(self):
        try:
            with open(self.input_file, "r", encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            size = Path(self.input_file).stat().st_size
            print(f"Fehler beim Lesen von {self.input_file} (Größe: {size}): {e}")
            return

        # Gateway Statistiken
        gw = {}
        nodes = data["nodes"]
        for n in nodes:
            if n.get("online", False) == False:
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
            except Exception:
                print("Error with node %s" % (node))
                print(n)
        
        for mac in gw:
            g = gw[mac]
            gw_name, segment = self.convert_mac(mac)
            self.gauge.labels(respondd_segment=segment, type="clients", instance=gw_name).set(g["clients"])
            self.gauge.labels(respondd_segment=segment, type="nodes", instance=gw_name).set(g["nodes"])
            self.gauge.labels(respondd_segment=segment, type="fastd", instance=gw_name).set(g["fastd"])


def main():
    parser = argparse.ArgumentParser(description='Freifunk Prometheus Exporter')
    parser.add_argument('-i', '--input', required=True,
                      help='Eingabedatei raw.json')
    parser.add_argument('-p', '--port', type=int, default=9104,
                      help='Port für den Prometheus Exporter (Standard: 9104)')
    parser.add_argument('--interval', type=int, default=60,
                      help='Update Interval in Sekunden (Standard: 60)')
    parser.add_argument('--bind', type=str, default="0.0.0.0",
                        help='Address to listen on')
    args = parser.parse_args()

    exporter = PrometheusExporter(args.input, args.port)
    
    # Prometheus HTTP Server starten
    start_http_server(args.port, addr = args.bind)
    print(f"Prometheus Exporter läuft auf Port {args.port}")
    
    while True:
        exporter.update_metrics()
        time.sleep(args.interval)

if __name__ == "__main__":
    main()
