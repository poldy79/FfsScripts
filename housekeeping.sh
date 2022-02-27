#!/bin/bash
cd ~/freifunk
for seg in {01..32}; do
./FfsScripts/fastd-status.py -q -i /var/run/fastd-vpn$seg.sock -o /var/www/html/data/vpn$seg.json
./FfsScripts/fastd-status.py -q -i /var/run/fastd-bb${seg}.sock -o /var/www/html/data/bb${seg}.json
done

~/freifunk/FfsScripts/update_peers.sh /etc/fastd/peers-ffs > /dev/null
git -C /etc/tinc/ffsbb/tinc-ffsbb fetch -q > /dev/null
git -C /etc/tinc/ffsbb/tinc-ffsbb pull -q > /dev/null
git -C /etc/tinc/ffsl3/tinc fetch -q > /dev/null
git -C /etc/tinc/ffsl3/tinc pull -q > /dev/null
#killall -HUP tincd

# replaced by extra cron job !!  ~/freifunk/FfsScripts/genGwStatus.py -o /var/www/html/data/gwstatus.json
# -> new script is "/var/lib/ffs/loadbalancer/genGwStatus.py"

