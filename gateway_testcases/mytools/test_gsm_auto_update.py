#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: ZouHualong
# 配置网关自动升级

from fabric.api import run,env,roles,local

env.hosts = ['root@192.168.250.10:12345',]
env.password = 'pqfowpywpytubdl3124'
env.shell = '/bin/ash -c'

script_file = '/etc/asterisk/gw/custom.sh'

def clean():
    run('cat /dev/null > %s' % script_file)
    run('/my_tools/sync2flash')

def config():
    run('cat /dev/null > %s' % script_file)
    run("echo '#!/bin/sh\nversion=$(cat /version/version)\necho ${version} >> /etc/asterisk/gw/versions.txt\n/my_tools/sync2flash\nsleep 60\ncd /tmp\nrm -rf wg400*.img\n[ \"${version}\" == \"2.2.0\" ] && wget http://192.168.250.253/firmware/gsm/wg400-2.2.2.img && /usr/bin/auto_update -u -f wg400-2.2.2.img && reboot\n[ \"${version}\" == \"2.2.2\" ] && wget http://192.168.250.253/firmware/gsm/wg400-2.2.0.img && /my_tools/unpack.sh wg400-2.2.0.img && reboot\n' > %s" % script_file)
    run('/my_tools/sync2flash')

def test():
    run('cat /version/version')
