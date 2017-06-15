#!/bin/bash
cd ~/freifunk
for seg in {00..63}; do
./FfsScripts/fastd-status.py -q -i /var/run/fastd-vpn$seg.sock -o /var/www/html/data/vpn$seg.json
./FfsScripts/fastd-status.py -q -i /var/run/fastd-vpn${seg}bb.sock -o /var/www/html/data/vpn${seg}bb.json
done

~/freifunk/FfsScripts/update_peers.sh /etc/fastd/peers-ffs > /dev/null
git -C /etc/tinc/ffsbb/tinc-ffsbb pull > /dev/null
git -C /etc/tinc/ffsl3/tinc pull > /dev/null
killall -HUP tincd

