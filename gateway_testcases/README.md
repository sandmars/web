## 使用说明
环境：
1. Linux 桌面环境

### 网关测试
|文件名|说明|
|---|---|
|prepare|本测试脚本所需的环境配置|
|python_lib|测试用例库|
|config|配置文件|
|clean.sh|清理工具|
|test_web.py|测试网关网页脚本，具体见：[WEB测试说明](doc/README_WEB.md)|
|init_tester|自动配置测试机环境|
|init_dgw.py|自动配置网关DAHDI、SIP、ROUTE|
|pcap|python SIPp 所用的语音流|
|sipp_user|python SIPp 所需用户配置|
|remote_result.py|获取远端结果文件/var/log/asterisk/results.txt到./results.txt、清空远端结果文件|
|result.temple|某些测试所要对比的预期结果，如 failover|

#### yum安装软件
```shell
yum install git
yum install gcc-c++ gcc automake autoconf libtool make ncurses ncurses-devel openssl openssl-devel libpcap libpcap-devel libnet lksctp-tools lksctp-tools-devel
yum install python-devel
yum install python-setuptools
yum install python-matplotlib
yum install apache2 php php-common php-devel
```

#### Python easy_install 安装
```shell
easy_install fabric
easy_install selenium
```

拷贝 prepare/HTMLTestRunner.py 到 /usr/lib/python2.7/HTMLTestRunner.py

#### 源码安装软件
安装SIPp
```
wget https://github.com/SIPp/sipp/archive/v3.4.1.tar.gz -O sipp-v3.4.1.tar.gz
tar -zxvf sipp-v3.4.1.tar.gz
cd sipp-3.4.1
./configure --with-sctp --with-pcap --with-openssl --libdir=/usr/lib64
make && make install
```

### 测试说明
#### WEB界面测试
1. WEB登陆测试
    * 使用脚本test_web.py，配置文件config/web_cases.conf的test_web_login部分
2. SSH登陆测试
    * 使用脚本test_web.py，配置文件config/web_cases.conf的test_ssh_login部分
3. Asterisk API测试
    * 使用脚本test_web.py，配置文件config/web_cases.conf的test_asterisk_api部分
4. 系统工具测试
    * 支持test_system_reboot、test_asterisk_reboot、test_update_sys
    * 使用脚本test_web.py，配置文件config/web_cases.conf的test_system_tools部分
5. 时间配置测试
    * 使用脚本test_web.py，配置文件config/web_cases.conf的test_time部分

详情请看：[doc/README_WEB.md](doc/README_WEB.md)

#### 功能测试
1. 多SIP测试，详情请看：[doc/multi_sip_test.md](doc/multi_sip_test.md)
2. Failover测试，详情请看：[doc/failover_test.md](doc/failover_test.md)
3. 号码变换测试，详情请看：[doc/manipulation_test.md](doc/manipulation_test.md)
4. 多号码变换测试，详情请看：[doc/multi_manipulation_test.md](doc/multi_manipulation_test.md)
5. 多路由测试，详情请看：[doc/multi_route_test.md](doc/multi_route_test.md)
6. 路由顺序测试，详情请看：[doc/route_order_test.md](doc/route_order_test.md)

