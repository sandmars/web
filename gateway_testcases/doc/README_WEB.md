## 使用说明
环境：需要使用桌面环境
配置：默认配置config/web_cases.conf
执行：python test_web.py

## 配置说明
配置文件：config/web_cases.conf，包含所需测试用例、测试数据
格式：
```
[section]
key = value
```

### [work] 部分
load_from_name：所要测试的测试用例集，以";"分隔，为本文件其他section的名字
如需要测试SSH登录、AsteriskAPI两部分，本配置文件需有test_ssh_login、test_asterisk_api部分

支持的测试有：
* test_time
* test_ssh_login
* test_web_login
* test_system_tools
    - 暂时仅支持System Reboot、Asterisk Reboot、System Update
* test_sip_endpoint
* test_iax_endpoint
* test_asterisk_api
    - API不稳定，测试前可能需要重启Asterisk
* test_asterisk_cli

例如：测试SSH登陆模块、AsteriskAPI模块

```
[work]
load_from_name = test_ssh_login;test_asterisk_api
```

### [localhost] 部分
本测试脚本所在的本机信息
hostname：本机 IP

```
[localhost]
hostname = 172.16.8.182
```

### [gateway] 部分
待测网关信息
hostname：网关 IP
default_hostname：网关初始 IP
web_username：WEB 用户名
web_password：WEB 密码
web_port：WEB 端口
ssh_username：SSH 用户名
ssh_password：SSH 密码
ssh_port：SSH 端口

```
[gateway]
hostname = 172.16.8.213
default_hostname = 172.16.100.1
web_username = admin
web_password = admin
web_port = 80
ssh_username = root
ssh_password = ixlteuc7Fa9NNqUc
ssh_port = 12345
```

### 其他部分
测试用例详细信息，如测试数据，[work]部分从这些部分读取测试数据

均包含：
testcases：测试数据集合，包含所需要测试的所有数据集合，以';'分隔

#### [test_web_login] 部分
测试 SYSTEM - Login Settings - WEB Login Settings 部分

**BUG: 由于使用 http://username:password@hostname:port 方式登录验证，无法验证 password 为特殊字符**

* current：当前的WEB用户名、密码及端口号信息
    - 格式：**username;password;confirm_passwork;port;login_mode**
* testcases：测试数据集合，包含所需要测试的所有数据集合，以';'分隔
    - **测试数据格式：username;password;confirm_passwork;port;login_mode**
* login_mode：登陆模式，仅E1网关支持，不支持则不填
    - 支持：http and https、only https

例如：测试三组数据

```
[test_web_login]
current = admin;admin;admin;80;
testcases = tc_username_001;tc_password_001;tc_port_001
tc_username_001 = a;admin;admin;80;
tc_password_001 = admin;adm;adm;80;
tc_port_001 = admin;admin;admin;65321;
```

#### [test_ssh_login] 部分
测试 SYSTEM - Login Settings - SSH Login Settings 部分

* testcases：测试数据集合，包含所需要测试的所有数据集合，以';'分隔
    - 测试数据格式：**ssh_username;ssh_password**

例如：测试三组数据

```
[test_ssh_login]
testcases = tc_username_001;tc_username_002;tc_password_001
tc_username_001 = root;admin
tc_username_002 = super;admin
tc_password_001 = admin;adm
```

#### [test_asterisk_api] 部分
测试 ADVANCED - Asterisk API 部分

* testcases：测试数据集合，包含所需要测试的所有数据集合，以';'分隔
* gw_type：网关类型，支持dgw、gsm
* port：Asterisk API 端口号
    - 测试数据格式：**username;password;deny;permit**

例如：测试三组数据

```
[test_asterisk_api]
gw_type = dgw
port = 5038
testcases = test1;test2;test3
test1 = admin;admin;0.0.0.0/0.0.0.0;172.16.8.182/24
test2 = hello;world;0.0.0.0/0.0.0.0;192.168.1.126/255.255.255.0
test3 = nihao;zhongguo;0.0.0.0/0.0.0.0;192.168.1.126/255.255.255.0
```

#### [test_sip_endpoint] 部分
测试 VOIP - VoIP Endpoints - SIP Endpoint 部分

添加SIP账号，仅填写了Name，User Name，Password，Registration，Hostname or IP Address，From User部分

* testcases：测试数据集合，包含所需要测试的所有数据集合，以';'分隔
    - 测试数据格式：**sip_type;endpoint_name;sip_username;sip_password;sip_ip;from_user**
* gw_type：dgw、gsm、analog_o
* sip_type：server、client、anonymous、none

例如：添加4个SIP账号

```
[test_sip_endpoint]
gw_type = dgw
testcases = test1;test2;test3;test4
test1 = server;1001;1001;1001;;
test2 = anonymous;1002;;;172.16.8.180;1002
test3 = client;1003;1003;1003;172.16.8.181;
test4 = none;1004;1004;1004;172.16.8.182;1004
```

#### [test_iax_endpoint] 部分
测试 VOIP - VoIP Endpoints - IAX2 Endpoint 部分

添加IAX账号，仅填写了Name，User Name，Password，Registration，Hostname or IP Address部分

* testcases：测试数据集合，包含所需要测试的所有数据集合，以';'分隔
    - 测试数据格式：**iax_type;endpoint_name;iax_name;iax_password;iax_ip**
* gw_type：dgw、gsm、analog_o
* iax_type：server、client、none

例如：添加3个IAX账号

```
[test_iax_endpoint]
gw_type = dgw
testcases = test1;test2;test3;test4
test1 = server;1001;1001;1001;
test2 = client;1003;1003;1003;172.16.8.184
test3 = none;1004;1004;1004;172.16.8.185
```

#### [test_system_tools] 部分
测试 SYSTEM - Tools 部分

**仍需修改**
**暂时仅支持test_asterisk_reboot**

* testcases：测试数据集合，包含所需要测试的所有数据集合，以';'分隔

支持如下测试数据：
* test_asterisk_reboot：测试AsteriskReboot，如要测试多次，可填写多个test_asterisk_reboot
* test_system_reboot：测试SystemReboot，如要测试多次，可填写多个test_system_reboot
* test_update_sys：包含test_update_sys的字符串，需有相应的选项，如：
    - testcases = test_update_sys_1
    - test_update_sys_1 = /opt/wg400-2.1.3.img
    - 测试升级固件/opt/wg400-2.1.3.img，需用全路径

例如：

```
[test_system_tools]
testcases = test_asterisk_reboot;test_system_reboot;test_update_sys_1
test_update_sys_1 = /opt/firmware/DGW100x-1.1.0-1157-release.bin
```

#### [test_time] 部分
测试 SYSTEM - Time 部分

* testcases：测试数据集合，包含所需要测试的所有数据集合，以';'分隔
    - 测试数据格式：**test_type;timezone;ntp1;ntp2;ntp3**
* test_type：可取ntp、client
    - 取client时，其他参数为空，即client;;;;

```
[test_time]
testcases = test_1;test_2;test_3;test_4
test_1 = client;;;;
test_2 = ntp;Shanghai;;;cn.pool.ntp.org
test_3 = ntp;Chongqing;;tw.pool.ntp.org;
test_4 = ntp;Hong Kong;cn.pool.ntp.org;;
```

