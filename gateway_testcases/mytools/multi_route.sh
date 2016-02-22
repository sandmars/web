#!/usr/bin/env bash
# Author: ZouHualong

from=$1
to=$2
init=$3
count=$4

gw_route="gw_route = "
for num in `seq 1 ${count}`; do
    gw_route+="gw_route_${num}"
    [ ${num} -ne ${count} ] && gw_route+=";"
done
for num in `seq 1 ${count}`; do
    account=$[${init} + ${num}]
    gw_route_all+="gw_route_${num} = test_${num};${from};${to};;;manipulation_sec_${num}"
    manipulation_sec_all+="manipulation_sec_${num} = manipulation_field_${num}"
    manipulation_field_all+="manipulation_field_${num} = ${account}::${account}::::::.::::"
    if [ ${num} -ne ${count} ]; then
        gw_route_all+="\n"
        manipulation_sec_all+="\n"
        manipulation_field_all+="\n"
    fi
done

echo "tw_type = dgw"
echo ${gw_route}
echo -e ${gw_route_all}
echo -e ${manipulation_sec_all}
echo -e ${manipulation_field_all}
