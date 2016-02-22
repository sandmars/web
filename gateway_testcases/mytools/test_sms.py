#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from python_lib import gateway_func
import time,ConfigParser,sys

def enable_sms2http():
    '''使能网关 SMS2HTTP 功能，配置本机接收 SMS 环境'''
    config_file = 'config/sms_cases.conf'
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    gateway_ip = config.get('gateway', 'hostname')
    port = config.getint('gateway', 'web_port')
    username = config.get('gateway', 'web_username')
    password = config.get('gateway', 'web_password')
    baseurl = 'http://%s:%s@%s:%s' % (username, password, gateway_ip, port)
    local_ip = config.get('localhost', 'hostname')
    local_web_port = config.get('localhost', 'web_port')

    driver = webdriver.Firefox()
    driver.set_window_size(1024, 768)
    driver.implicitly_wait(5)
    driver.get(baseurl)
    sms2http = gateway_func.sms_func(driver)

    if config.has_section('sms2http'):
        php_file = config.get('sms2http', 'php_file')
        sms_file = config.get('sms2http', 'sms_file')
        php_file_basename = config.get('sms2http', 'php_file_basename')
        phone_num = config.get('sms2http', 'phone_num')
        from_port = config.get('sms2http', 'from_port')
        message = config.get('sms2http', 'message')
        receive_time = config.get('sms2http', 'receive_time')
        user_fefined = config.get('sms2http', 'user_fefined')
        separator = config.get('sms2http', 'separator')
        sms2http.sms2http_gw_config(local_ip, local_web_port, php_file_basename, phone_num, from_port, message, receive_time, user_fefined)
        sms2http.sms2http_recv_config(php_file, sms_file, phone_num, from_port, message, receive_time, separator)
    else:
        sms2http.sms2http_gw_config(local_ip)
        sms2http.sms2http_recv_config()
    driver.quit()

if __name__ == '__main__':
    if sys.argv[1] == 'sms2http':
        enable_sms2http()
    else:
        pass

