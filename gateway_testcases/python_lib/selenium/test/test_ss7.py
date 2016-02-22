#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest, sys, time, HTMLTestRunner, ConfigParser
from lib import shell_func,gateway_func
from selenium import webdriver
from selenium.webdriver.support.ui import Select

reload(sys)
sys.setdefaultencoding('utf-8')

if __name__ == '__main__':
    hostname = '172.16.100.180'
    port = 80
    username = 'admin'
    password = 'admin'
    baseurl = 'http://%s:%s@%s:%s' % (username, password, hostname, port)
    
    driver = webdriver.Firefox()
    driver.set_window_size(1024, 768)
    driver.implicitly_wait(5)
    driver.get(baseurl)

    linkset_name = 'siuc2'
    linkset_enable = True
    linkset_enable_st = False
    linkset_use_connect = True
    policy = 'even_mru'
    subservice = 'auto'
    t35 = '15000,timeout'
    variant = 'ITU'
    opc = '0x32'
    dpc = '0x1'
    linkset_default = False
    ss7_func = gateway_func.ss7_func(driver)
    ss7_func.del_all_linkset()
    ss7_func.add_new_link_set(linkset_name, linkset_enable, linkset_enable_st, linkset_use_connect, policy, subservice, t35, variant, opc, dpc, linkset_default)

    link_num = 1
    link_enable = False
    linkset_name = 'siuc2'
    channels = '1-31'
    schannel = ''
    firstcic = 33
    echocancel = 'no (default)'
    echocan_train = '350'
    echocan_taps = '128 (default)'
    link_sls = 1
    enable_sltm = False
    port = 2
    ss7_func.modify_link(link_num, link_enable, linkset_name, channels, schannel, firstcic, echocancel, echocan_train, echocan_taps, link_sls, enable_sltm, port)
    
    driver.quit()

