## SIP测试方案
### 测试目的
测试网关最多支持创建几个SIP

### 测试配置
#### openvox_testcases
配置文件：config/multi_sip_test.conf
```
[gateway]：网关信息
[ippbx]：测试机信息
[sipp]：SIPp配置
[web]：Selenium WEB配置
```

> 批量创建SIP域的脚本：mytools/multi_gw_sip.sh


SIPp对应的SIP账号
```
cat sipp_user/multi_sip_test.csv
SEQUENTIAL,PRINTF=200,PRINTFMULTIPLE=1,PRINTFOFFSET=1,
8%03d;1%03d;[authentication username=1%03d password=123456];1%03d
```

SIPp执行文件test_sipp.py
```shell
python test_sipp.py config/multi_sip_test.conf multi_sip_test
```

#### 网关配置
通过openvox_testcases自动创建200个SIP账号
```
8001, dynamic
8002, dynamic
...
8200, dynamic
```

## 测试流程
```
SIPp -> DGW -> 测试机
```

1. 利用python脚本自动生成网关配置
2. 利用sipp自动测试

```
python init_gw.py config/multi_sip_test.conf web
python test_sipp.py config/multi_sip_test.conf sipp
```

### 结果分析
SIPp全部注册成功
