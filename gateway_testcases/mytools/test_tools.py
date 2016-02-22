#!/usr/bin/env python
# -*- coding: utf-8 -*-
# fab -f test_autoreboot.py test_dgw_autoreboot

from fabric.api import roles,local,cd,run,env,lcd
import time

env.roledefs = {
	'gsm_analog': ['root@172.16.99.1:12345',],
	'dgw': ['root@172.16.100.1:12345',]
}

env.passwords = {
	'root@172.16.99.1:12345': 'pqfowpywpytubdl3124',
	'root@172.16.100.1:12345': 'ixlteuc7Fa9NNqUc'
}

def __gsm_analog_factory():
    '''GSM/Analog网关自动恢复出厂设置'''
    env.shell = '/bin/ash -c'
    with cd('/my_tools'):
        run('./restore_cfg_file')

def __dgw_factory():
    '''E1网关恢复出厂设置'''
    env.shell = '/bin/bash -l -c'
    with cd('/bin'):
        run('./check_config.sh def_force')

@roles('gsm_analog')
def test_gsm_analog_factory():
    '''循环测试GSM/Analog网关恢复出厂设置，网关使用默认IP进行测试'''
    for i in range(100):
        __gsm_analog_factory()
        time.sleep(600)

@roles('dgw')
def test_dgw_factory():
    '''循环测试E1网关恢复出厂设置，网关使用默认IP进行测试'''
    for i in range(100):
        __dgw_factory()
        time.sleep(600)

@roles('dgw')
def enable_dgw_schedule_reboot():
    '''启用E1网关自动重启，每5分钟重启一次'''
    env.shell = '/bin/bash -l -c'
    crontab_cmd = '*/5 * * * * reboot'
    crontab_file = '/mnt/ext4/sda7/config/defconfig/sysconfig/cron/crontabs/root'
    run("sed -i '/reboot/d' %s" % crontab_file)
    run("echo '%s' >> %s" % (crontab_cmd, crontab_file))
    run("/etc/init.d/crond restart")
    disconnect_all()

@roles('dgw')
def disable_dgw_schedule_reboot():
    '''禁用E1网关自动重启'''
    crontab_file = '/mnt/ext4/sda7/config/defconfig/sysconfig/cron/crontabs/root'
    run("sed -i '/reboot/d' %s" % crontab_file)
    run("/etc/init.d/crond restart")
    disconnect_all()

