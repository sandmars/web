## 路由测试方案
### 测试目的
测试网关1条路由规则最多支持几条号码变换

### 测试配置
#### Gateway_testcases
配置文件：config/multi_manipulation_test.conf
```
[gateway]：网关信息
[ippbx]：测试机信息
[sipp]：SIPp配置
[web]：Selenium WEB配置
```

> 批量创建号码变换域的脚本：mytools/multi_manipulation.sh
>
> 在config/multi_manipulation_test.conf的值manipulation_sec_1尾部添加：";manipulation_field_0"
>
> 在config/multi_manipulation_test.conf文件尾添加："manipulation_field_0 = 0000::.::::::.::::"
>

SIPp对应的SIP账号
```
cat sipp_user/multi_manipulation_test.csv
SEQUENTIAL,PRINTF=201,PRINTFMULTIPLE=1,PRINTFOFFSET=0,
9000;9000;[authentication username=9000 password=123456];8%03d
```

#### 网关配置
SIP
```
9000, dynamic
9001, none, 对接测试机
```

通过openvox_testcases自动创建1条路由，200个号码变换
From: 9000
To: 9001

|Prepend|Match Pattern|
|---|---|
|8001|8001|
|8002|8002|
|...|...|
|8200|8200|
|0000|.|

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

```shell
python remote_result.py config/multi_manipulation_test.conf clean
python init_gw.py config/multi_manipulation_test.conf web_dgw
python test_sipp.py config/multi_manipulation_test.conf sipp
python remote_result.py config/multi_manipulation_test.conf get
```

GSM网关

```shell
python remote_result.py config/multi_manipulation_test.conf clean
python init_gw.py config/multi_manipulation_test.conf web_gsm
python test_sipp.py config/multi_manipulation_test.conf sipp
python remote_result.py config/multi_manipulation_test.conf get
```

Analog_O网关

```shell
python remote_result.py config/multi_manipulation_test.conf clean
python init_gw.py config/multi_manipulation_test.conf web_analog_o
python test_sipp.py config/multi_manipulation_test.conf sipp
python remote_result.py config/multi_manipulation_test.conf get
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

```shell
cat results.txt | awk -F ':' '{print $3}' | wc -l
```

