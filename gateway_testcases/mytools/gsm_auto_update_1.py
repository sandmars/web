#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: ZouHualong
# 配置网关自动升级

from fabric.api import run,env,roles,local

'''
env.roledefs = {
        'gsm': ['root@172.16.8.48:12345','root@192.168.250.2:12345','root@192.168.250.3:12345','root@192.168.250.4:12345','root@192.168.250.5:12345','root@192.168.250.6:12345','root@192.168.250.7:12345','root@192.168.250.8:12345','root@192.168.250.9:12345','root@192.168.250.10:12345',],
}
'''
env.roledefs = {
        'gsm': ['root@192.168.250.10:12345',],
}
env.password = 'pqfowpywpytubdl3124'
'''
env.passwords = {
    'root@172.16.8.48:12345': 'pqfowpywpytubdl3124',
    'root@192.168.250.2:12345': 'pqfowpywpytubdl3124',
    'root@192.168.250.3:12345': 'pqfowpywpytubdl3124',
    'root@192.168.250.4:12345': 'pqfowpywpytubdl3124',
    'root@192.168.250.5:12345': 'pqfowpywpytubdl3124',
    'root@192.168.250.6:12345': 'pqfowpywpytubdl3124',
    'root@192.168.250.7:12345': 'pqfowpywpytubdl3124',
    'root@192.168.250.8:12345': 'pqfowpywpytubdl3124',
    'root@192.168.250.9:12345': 'pqfowpywpytubdl3124',
    'root@192.168.250.10:12345': 'pqfowpywpytubdl3124',
}
'''
script_file = '/etc/asterisk/gw/custom.sh'

@roles('gsm')
def clean():
    env.shell = '/bin/ash -c'
    run('cat /dev/null > %s' % script_file)
    run('/my_tools/sync2flash')

@roles('gsm')
def config():
    env.shell = '/bin/ash -c'
    run('cat /dev/null > %s' % script_file)
    #run("echo '#!/bin/sh\nsleep 60\ncd /tmp\nfirmware=\"wg400.img\"\nversion=$(cat /version/version)\n[ \"${version}\" == \"2.2.0\" ] && wget -O ${firmware} http://172.16.0.96/firmware/wg400-2.2.2.img\n[ \"${version}\" == \"2.2.2\" ] && wget -O ${firmware} http://172.16.0.96/firmware/wg400-2.2.0.img\n/usr/bin/auto_update -f ${firmware} && reboot\n' > %s" % script_file)
    run("echo '#!/bin/sh\nversion=$(cat /version/version)\necho ${version} >> /etc/asterisk/gw/versions.txt\n/my_tools/sync2flash\nsleep 60\ncd /tmp\nrm -rf wg400*.img\n[ \"${version}\" == \"2.2.0\" ] && wget http://192.168.250.253/firmware/gsm/wg400-2.2.2.img && /usr/bin/auto_update -u -f wg400-2.2.2.img && reboot\n[ \"${version}\" == \"2.2.2\" ] && wget http://192.168.250.253/firmware/gsm/wg400-2.2.0.img && /my_tools/unpack.sh wg400-2.2.0.img && reboot\n' > %s" % script_file)
    run('/my_tools/sync2flash')
    #run('/bin/sh %s' % script_file)

