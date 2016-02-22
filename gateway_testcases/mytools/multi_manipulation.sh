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
manipulation_sec_all="manipulation_sec_1 = "
for num in `seq 1 ${count}`; do
    account=$[${init} + ${num}]
    manipulation_sec_all+="manipulation_field_${num}"
    manipulation_field_all+="manipulation_field_${num} = ${account}::${account}::::::.::::"
    if [ ${num} -ne ${count} ]; then
        manipulation_sec_all+=";"
        manipulation_field_all+="\n"
    fi
done

echo "gw_type = dgw"
echo "gw_route = gw_route_1"
echo "gw_route_1 = test_1;${from};${to};;;manipulation_sec_1"
echo -e ${manipulation_sec_all}
echo -e ${manipulation_field_all}

