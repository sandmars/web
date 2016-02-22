## Route测试方案
### 测试目的
测试网关最多支持创建几条路由规则

### 测试配置
#### Gateway_testcases
配置文件：config/multi_route_test.conf
```
[gateway]：网关信息
[ippbx]：测试机信息
[sipp]：SIPp配置
[web]：Selenium WEB配置
```

> 自动增加拨号规则域：mytools/multi_route.sh

SIPp对应的SIP账号
```
[root@localhost openvox_testcases]# cat sipp_user/multi_route_test.csv
SEQUENTIAL,PRINTF=200,PRINTFMULTIPLE=1,PRINTFOFFSET=1,
9000;9000;[authentication username=9000 password=123456];8%03d
```

#### 网关配置
SIP
```
9000, dynamic
9001, none, 对接测试机
```

路由

|Route Name|From|To|Prepend|Match Pattern|
|---|---|---|---|---|
|test_1|9000|9001|8001|8001|
|test_2|9000|9001|8002|8002|
|...|...|...|...|...|
|test_100|9000|9001|8200|8200|

#### 测试机
Asterisk配置对接网关的SIP Trunk 9001
拨号规则
```
exten => _X.,1,Answer()
exten => _X.,n,System(echo "${CALLERID(name)}:${CALLERID(num)}:${EXTEN}:${CHANNEL}" >> /var/log/asterisk/results.txt)
exten => _X.,n(playback),Playback(demo-moreinfo)
exten => _X.,n,Goto(playback)
```

## 测试流程
```
SIPp -> DGW -> 测试机
```

1. 清空IPPBX中记录的结果
2. 利用python脚本自动生成网关配置
3. 利用sipp自动测试
4. 获取IPPBX中记录的结果

DGW网关

```
python remote_result.py config/multi_route_test.conf clean
python init_gw.py config/multi_route_test.conf web_dgw
python test_sipp.py config/multi_route_test.conf sipp
python remote_result.py config/multi_route_test.conf get
```

GSM网关

```
python remote_result.py config/multi_route_test.conf clean
python init_gw.py config/multi_route_test.conf web_gsm
python test_sipp.py config/multi_route_test.conf sipp
python remote_result.py config/multi_route_test.conf get
```

Analog_o网关

```
python remote_result.py config/multi_route_test.conf clean
python init_gw.py config/multi_route_test.conf web_analog_o
python test_sipp.py config/multi_route_test.conf sipp
python remote_result.py config/multi_route_test.conf get
```

### 结果分析
```shell
cat results.txt | awk -F ':' '{print $3}'
```
每行前4个数字：
1. 8000
2. 8001
3. 8002
...

