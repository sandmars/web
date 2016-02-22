## 路由测试方案
### 测试目的
测试交换路由顺序功能

### 测试配置
#### Gateway_testcases
配置文件：config/route_order_test.conf
```
[gateway]：网关信息
[ippbx]：测试机信息
[sipp]：SIPp配置
[first]：Selenium WEB初始配置
[second]：交换路由顺序
```

SIPp对应的SIP账号
```
cat sipp_user/route_order_test.csv
SEQUENTIAL
9000;9000;[authentication username=9000 password=123456];8001
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
|test_1|9000|9001|0797|.|
|test_2|9000|9001|0755|.|

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
1. 清空IPPBX中记录的结果
2. 利用python脚本自动生成网关配置
3. 利用sipp自动测试
4. 利用python脚本自动交换路由顺序
5. 利用sipp自动测试
6. 获取IPPBX中记录的结果

DGW

```
python remote_result.py config/route_order_test.conf clean
python init_gw.py config/route_order_test.conf dgw_first
python test_sipp.py config/route_order_test.conf sipp
python init_gw.py config/route_order_test.conf dgw_second
python test_sipp.py config/route_order_test.conf sipp
python remote_result.py config/route_order_test.conf get
```

GSM

```
python remote_result.py config/route_order_test.conf clean
python init_gw.py config/route_order_test.conf gsm_first
python test_sipp.py config/route_order_test.conf sipp
python init_gw.py config/route_order_test.conf gsm_second
python test_sipp.py config/route_order_test.conf sipp
python remote_result.py config/route_order_test.conf get
```

Analog_o

```
python remote_result.py config/route_order_test.conf clean
python init_gw.py config/route_order_test.conf analog_o_first
python test_sipp.py config/route_order_test.conf sipp
python init_gw.py config/route_order_test.conf analog_o_second
python test_sipp.py config/route_order_test.conf sipp
python remote_result.py config/route_order_test.conf get
```

### 结果分析

```shell
cat results.txt | awk -F ':' '{print $3}'
```

每行前4个数字：
1. 0797
2. 0755

