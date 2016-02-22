#!/usr/bin/env bash
# Author: ZouHualong
# Usage: multi_gw_sip.sh init count
#   The first gw_sip is init+1

[ $# -ne '2' ] && echo "Usage: $0 <init> <count>" && exit 0
init=$1
count=$2

gw_sip="gw_sip = "
for num in `seq 1 ${count}`; do
    gw_sip+="gw_sip_${num}"
    [ ${num} -ne ${count} ] && gw_sip+=";"
done
echo ${gw_sip}
for num in `seq 1 ${count}`; do
    account=$[${init} + ${num}]
    echo "gw_sip_${num} = server;${account};${account};123456;;"
done
