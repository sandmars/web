## 路由测试方案
### 测试目的
测试网关1条路由规则号码变换功能

### 测试配置
#### Gateway_testcases
配置文件：config/manipulation_test.conf
```
[gateway]：网关信息
[ippbx]：测试机信息
[sipp]：SIPp配置
[web]：Selenium WEB配置
```

SIPp对应的SIP账号：sipp_user/manipulation_test.csv

#### 网关配置
SIP
```
9000, dynamic
9001, none, 对接测试机
```

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

Analog_o

```shell
python remote_result.py config/manipulation_test.conf clean
python init_gw.py config/manipulation_test.conf web_analog_o
python test_sipp.py config/manipulation_test.conf sipp
python remote_result.py config/manipulation_test.conf get
```

### 结果分析
```shell
cat results.txt | awk -F ':' '{print $3}'
```

