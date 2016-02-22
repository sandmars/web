#!/usr/bin/env bash

# 使用方式：本脚本（测试机） -> 测试机 SIP Trunk -> 网关 -> E1线 -> 测试机

# 测试机 SIP Trunk 如下：
# [fax_options](!)
# type=friend
# secret=123456
# insecure=invite
# canreinvite=yes
# setvar=FAXOPT(gateway)=yes,10
# t38pt_udptl=yes,redundancy,maxdatagram=400
# t38pt_rtp=no
# t38pt_tcp=no
# context=from-internal-fax
# 
# [9002](fax_options)
# host=172.16.100.181
# fromuser=9002
#
# [from-internal-fax]
# exten => _X.,1,Answer()
# exten => _X.,n,Set(FAXOPT(gateway)=no)
# exten => _X.,n,Set(FAXOPT(ecm)=no)
# exten => _X.,n,SendFax(${TIFF},dF)
# exten => _X.,n,Hangup()

# 网关 SIP Trunk 如下：
# Protocol: T.38
# Enabled Yes
# Error Correction: Redundancy
# Max Datagram: 400
# Fax Detect: Yes
# Fax Activity: Yes
# Fax Timeout: 10

# 测试机接收传真
# [from-pstn-fax]
# exten => _X.,1,Answer()
# exten => _X.,n,Set(FAXOPT(gateway)=no)
# exten => _X.,n,Set(NOW=${STRFTIME(${EPOCH},,%Y%m%d%H%M%S)})
# exten => _X.,n,Set(tif_file=/var/log/asterisk/FaxIn-${CALLERID(num)}-${NOW}.tif)
# exten => _X.,n,ReceiveFax(${tif_file},f)
# exten => _X.,n,Hangup()

# 生成 CallFile 文件内容
# Usage: general_call_file exten channel fax_file
#   first：第一个分机号
#   count：分机数量
#   channel：使用的通道，如 SIP/9002
#   fax_file：携带的传真文件
#   eg. general_call_file 8000 SIP/9002 10.tif
general_call_file()
{
    exten=$1
    channel=$2
    fax_file=$3
    echo "Channel: ${channel}/${exten}"
    echo "CallerID: T38 ${exten}"
    echo "WaitTime: 300"
    echo "MaxRetries: 0"
    echo "RetryTime: 300"
    echo "Archive: false"
    echo "Context: from-internal-fax"
    echo "Extension: ${exten}"
    echo "Priority: 1"
    echo "SetVar: T38CALL=1"
    echo "SetVar: LOCALSTATIONID=T38-SendFax"
    echo "SetVar: TIFF=${fax_file}"
    echo "SetVar: ACCOUNT=3987"
    echo "SetVar: REMOTESTATIONID=${exten}"
    #echo "SetVar: SENDER=from-${exten}"
}

# 生成多个 CallFile 文件，存放为 /tmp/test_${exten}.call
# Usage: multi_call_file first count channel fax_file
#   first：第一个分机号
#   count：分机数量
#   channel：使用的通道，如 SIP/9002
#   fax_file：携带的传真文件
#   eg. multi_call_file 8000 120 SIP/9002 10.tif
multi_call_file()
{
    first=$1
    count=$2
    channel=$3
    fax_file=$4
    for exten in `seq ${first} $[${first} + ${count} - 1]`; do
        general_call_file ${exten} ${channel} ${fax_file} > /tmp/test_${exten}.call
    done
}

# 清除 CallFile
clean_callfile()
{
    rm -rf /tmp/test_*.call
    rm -rf /tmp/10.tif
}

# 测试传真
# Usage: test_fax first count channel fax_file cycle
#   first：第一个分机号
#   count：分机数量
#   channel：使用的通道，如 SIP/9002
#   fax_file：携带的传真文件
#   cycle：循环周期
#   eg. test_fax 8000 120 SIP/9002 config_file/10.tif 2
test_fax()
{
    first=$1
    count=$2
    channel=$3
    fax_file=$4
    cycle=$5

    clean_callfile
    multi_call_file ${first} ${count} ${channel} ${fax_file}
    cp ${fax_file} /tmp/
    sleep 1

    for cyc in `seq 1 ${cycle}`; do
        for exten in `seq ${first} $[${first} + ${count} - 1]`; do
            echo "Cycle: ${cyc} - Caller: ${exten}"
            cp /tmp/test_${exten}.call /var/spool/asterisk/outgoing/
            sleep 0.5
        done
        [ "${cyc}" -lt "${cycle}" ] && sleep 300
    done
}

test_fax 8000 120 SIP/9002 config_file/10.tif 2

