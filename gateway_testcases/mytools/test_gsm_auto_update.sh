#!/usr/bin/env bash
# Author: ZouHualong

ipaddr='192.168.250.1'
ipaddr+=' 192.168.250.2'
ipaddr+=' 192.168.250.3'
ipaddr+=' 192.168.250.4'
ipaddr+=' 192.168.250.5'
ipaddr+=' 192.168.250.6'
#ipaddr+=' 192.168.250.7'
ipaddr+=' 192.168.250.8'
ipaddr+=' 192.168.250.9'
ipaddr+=' 192.168.250.10'
for ip in ${ipaddr}; do
    sed -i "/^env.hosts/cenv.hosts = ['root@${ip}:12345',]" test_gsm_auto_update.py
    while true; do
        #fab -f test_gsm_auto_update.py config
        #fab -f test_gsm_auto_update.py test
        fab -f test_gsm_auto_update.py clean
        [ "$?" -eq "0" ] && break
    done
done
