## 短信测试
    配置文件：config/sms_cases.conf
    脚本文件：test_sms.py

### 配置文件说明
#### [localhost] 部分
    本机配置
    hostname：本机 IP
    web_port：本机 WEB 端口

#### [gateway] 部分
    网关配置
    hostname：网关 IP
    web_username：WEB 用户名
    web_password：WEB 密码
    web_port：WEB 端口号

#### SMS2HTTP 部分
    读取 [sms2http]，如果没有该 section，则使用默认配置

    php_file：生成的接收SMS的PHP脚本存放位置，默认/var/www/html/receive_sms.php
    sms_file：存储SMS的文件位置，默认/var/www/html/message.txt
    php_file_basename：在网关中填写的PHP脚本名，默认receive_sms.php
    phone_num：SMS2HTTP功能中的主叫号码变量名，默认phone_num
    from_port：SMS2HTTP功能中的接收端口变量名，默认port
    message：SMS2HTTP功能中的短信内容变量名，默认message
    receive_time：SMS2HTTP功能中的时间变量名，默认time
    user_fefined：SMS2HTTP功能中的自定义变量名，默认为空
    separator：短信存储时，各个变量之间的分隔符，默认;

### 脚本文件说明
#### enable_sms2http
    配置网关使能SMS2HTTP功能
    配置本机可接收SMS
    执行方式：python test_sms.py sms2http
