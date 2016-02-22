## 呼叫测试
配置网关、测试机

* init_gw.py：自动生成网关测试配置
    - python init_gw.py section_of_config_file
    - section_of_config_file 对应配置文件中 [] 中的名字
* init_gw_ssh.py：自动生成网关测试配置
* init_tester.py：自动生成测试机配置
    - fab -f init_tester.py section_name
    - section_name 可通过 fab -f init_tester.py -l 查看
* test_call.py：SIPp自动测试
    - 配置文件：config/call_cases.conf

### PRI 号码变换测试
测试号码变换：
    1、2口对接测试机
    Port-1 接收呼叫，转到 Port-2，回送至测试机 Playback

自动生成网关测试配置：python init_gw.py test_pri_callid
自动生成测试机配置：fab -f init_tester.py test_pri_callid
SIPp自动测试：fab -f test_call.py test_pri_callid

### PRI Forwardnumber 测试
1、2口对接测试机
Port-1 接收呼叫，转到 Port-2，回送至测试机 Playback

自动生成网关测试配置：python init_gw.py test_pri_forwardnumber
自动生成测试机配置：fab -f init_tester.py test_pri_forwardnumber
SIPp自动测试：fab -f test_call.py test_pri_forwardnumber

