## Failover功能测试方案
### 测试目的
测试网关路由功能中的失效转换功能

功能说明：当目的通道不可用时，将呼叫转移到其他通道

### 测试工具
* python_sipp

### 测试设备
* 测试机1：SIPp
* 测试机2：Asterisk
* DGW网关

### 测试配置
#### openvox_testcases
配置文件：config/failover_test.conf
```
[gateway]：网关信息
[ippbx]：测试机信息
[sipp]：SIPp配置
[web_dgw]/[web_gsm]/[web_analog_o]：Selenium WEB配置
```

SIPp对应的SIP账号
```
[root@localhost openvox_testcases]# cat sipp_user/pri_failover_test.csv
SEQUENTIAL
9000;9000;[authentication username=9000 password=9000];1001
9000;9000;[authentication username=9000 password=9000];2001
9000;9000;[authentication username=9000 password=9000];3001
9000;9000;[authentication username=9000 password=9000];4001
```

#### DGW网关
DGW网关接受SIPp的呼叫，匹配被叫号码将呼叫转发至一个不可用通道，判断通道不可用后将呼叫转至其他通道
需分别测试：
* E1端口
* SIP Trunk
* IAX Trunk

信令协议配置
<table>
<tr><td>配置项</td><td>说明</td></tr>
<tr><td>SIP 9000</td><td>Dynamic模式</td></tr>
<tr><td>SIP 9001</td><td>对接测试机2</td></tr>
<tr><td>PRI Port 1</td><td>不接线，确保不可用</td></tr>
<tr><td>SIP 9002</td><td>Dynamic模式，确保不可用</td></tr>
<tr><td>IAX 8001</td><td>Dynamic模式，确保不可用</td></tr>
</table>

拨号规则配置
<table>
<tr><td>Route name</td><td>From</td><td>To</td><td>Match pattern</td><td>Failover</td></tr>
<tr><td>Failover_1</td><td>SIP 9000</td><td>Port 1</td><td>1.</td><td>SIP 9001</td></tr>
<tr><td>Failover_2</td><td>SIP 9000</td><td>SIP 9002</td><td>2.</td><td>SIP 9001</td></tr>
<tr><td>Failover_3</td><td>SIP 9000</td><td>IAX 8001</td><td>3.</td><td>SIP 9001</td></tr>
<tr><td>Failover_4</td><td>SIP 9000</td><td>Port 1</td><td>4.</td><td>SIP 9002, SIP 9001</td></tr>
</table>

**GSM网关配置为gsm-1.1不可用，其他同DGW网关**

#### 测试机
使用E1线、SIP Trunk、IAX Trunk等对接DGW网关，记录接受呼叫的通道，通过该记录判断呼叫是否正常转至Failover通道

信令配置：PRI Port 1对接DGW网关Port 1，context=from-pstn

SIP配置：对接DGW网关
```
[trunk_options](!)
type=friend
secret=123456
insecure=invite
canreinvite=yes
context=from-pstn

[9001](trunk_options)
host=DGW网关IP
fromuser=9001
```

拨号规则：记录来电使用的通道
```
[from-pstn]
exten => _X.,1,Answer()
exten => _X.,n,System(echo "${CALLERID(name)}:${CALLERID(num)}:${EXTEN}:${CHANNEL}" >> /var/log/asterisk/results.txt)
exten => _X.,n(playback),Playback(demo-instruct)
exten => _X.,n,Goto(playback)
```

### 测试流程
1. 清空IPPBX中记录的结果
2. 利用python脚本自动生成网关配置
3. 利用sipp自动测试
4. 获取IPPBX中记录的结果

DGW

```shell
python remote_result.py config/failover_test.conf clean
python init_gw.py config/failover_test.conf web_dgw
python test_sipp.py config/failover_test.conf sipp
python remote_result.py config/failover_test.conf get
```

GSM

```shell
python remote_result.py config/failover_test.conf clean
python init_gw.py config/failover_test.conf web_gsm
python test_sipp.py config/failover_test.conf sipp
python remote_result.py config/failover_test.conf get
```

Analog_o（暂不支持IAX）

```shell
python remote_result.py config/failover_test.conf clean
python init_gw.py config/failover_test.conf web_analog_o
python test_sipp.py config/failover_test.conf sipp
python remote_result.py config/failover_test.conf get
```

### 结果分析
DGW网关路由配置的To均为不可用通道，预期结果均使用Failover中的通道，与Asterisk中记录的通道进行对比，即可判断

分析结果：四行结果均为：SIP/9001
```shell
cat results.txt | awk -F ':' '{print $4}' | awk -F '-' '{print $1}'
```

