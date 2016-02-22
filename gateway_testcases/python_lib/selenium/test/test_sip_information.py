#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
import ConfigParser, unittest, HTMLTestRunner, sys, os
from lib import gateway_func

reload(sys)
sys.setdefaultencoding('utf-8')

class test_sip_information(unittest.TestCase):
    def setUp(self):
        u'''初始化参数'''
        config_file = 'config/web_cases.conf'
        config = ConfigParser.ConfigParser()
        config.read(config_file)
        hostname = config.get('gateway', 'hostname')
        port = config.getint('gateway', 'web_port')
        username = config.get('gateway', 'web_username')
        password = config.get('gateway', 'web_password')
        self.localhost = config.get('localhost', 'hostname')
        self.baseurl = 'http://%s:%s@%s:%s' % (username, password, hostname, port)

        self.driver = webdriver.Firefox()
        #self.driver.maximize_window()
        self.driver.set_window_size(1024, 768)
        self.driver.implicitly_wait(5)
        self.verificationErrors = []
        self.driver.get(self.baseurl)

    def tearDown(self):
        u'''关闭文件，关闭浏览器'''
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

    def check_sip(self, sip_type, sip_status, endpoint_name, sip_username, sip_ip):
        driver = self.driver
        driver.get(self.baseurl)
        sip_info = driver.find_element_by_class_name('tshow').text
        sip_info = ';'.join(sip_info.split('\n')).split(';')
        for i in range(len(sip_info)):
            if endpoint_name in sip_info[i]:
                self.assertEqual(sip_info[i].split(' ')[0], endpoint_name, 'Endpoint name is different!')
                if sip_type == 'anonymous':
                    self.assertEqual(sip_info[i].split(' ')[1], 'anonymous', 'User name is different!')
                    self.assertEqual(sip_info[i].split(' ')[3], 'none', 'Type error! T:none, F:%s' % sip_info[i].split(' ')[3])
                else:
                    self.assertEqual(sip_info[i].split(' ')[1], sip_username, 'User name is different!')
                    self.assertEqual(sip_info[i].split(' ')[3], sip_type, 'Type error! T:%s, F:%s' % (sip_type, sip_info[i].split(' ')[3]))
                if sip_type == 'server':
                    if sip_status == 'noregister':
                        self.assertEqual(sip_info[i].split(' ')[2], '(Unspecified)', 'Read IP error!')
                        self.assertEqual(sip_info[i].split(' ')[4], 'UNKNOWN', 'Status error!')
                    if sip_status == 'register':
                        self.assertEqual(sip_info[i].split(' ')[2], sip_ip, 'Read IP error!')
                        if 'OK' not in sip_info[i].split(' ')[4]:
                            self.assertFalse(True, 'Register Error!')
                    if sip_status == 'unregister':
                        self.assertEqual(sip_info[i].split(' ')[2], '(Unspecified)', 'Read IP error!')
                        if 'OK' not in sip_info[i].split(' ')[4]:
                            self.assertFalse(True, 'Register Error!')
                elif sip_type == 'client':
                    self.assertEqual(sip_info[i].split(' ')[2], sip_ip, 'Read IP error!')
                    if sip_status == 'noregister':
                        self.assertEqual(sip_info[i].split(' ')[4], 'UNKNOWN', 'Status error!')
                    if sip_status == 'register':
                        if 'OK' not in sip_info[i].split(' ')[4]:
                            self.assertFalse(True, 'Register Error!')
                else:
                    self.assertEqual(sip_info[i].split(' ')[2], sip_ip, 'Read IP error!')
                    self.assertEqual(sip_info[i].split(' ')[4], 'UNKNOWN', 'Status error!')

    def test_sip_server(self):
        driver = self.driver
        sip_type = 'server'
        endpoint_name = '10001'
        sip_username = '10001'
        sip_password = '10001'
        sip_ip = ''
        from_user = ''
        sip = gateway_func.endpoint_func(driver)
        sip.delete_same_sip(endpoint_name)
        sip.add_sip_endpoint(sip_type, endpoint_name, sip_username, sip_password, sip_ip, from_user)
        self.check_sip(sip_type, 'noregister', endpoint_name, sip_username, '')
        os.system('cd sipp && ./run_sipp.sh sipp_conf/case_sip_info_reg.conf')
        self.check_sip(sip_type, 'register', endpoint_name, sip_username, self.localhost)
        os.system('cd sipp && ./run_sipp.sh sipp_conf/case_sip_info_unreg.conf')
        self.check_sip(sip_type, 'unregister', endpoint_name, sip_username, '')

    def test_sip_client(self):
        driver = self.driver
        sip_type = 'client'
        endpoint_name = '10002'
        sip_username = '10002'
        sip_password = '10002'
        sip_ip = '172.16.8.183'
        from_user = '10002'
        sip = gateway_func.endpoint_func(driver)
        sip.delete_same_sip(endpoint_name)
        sip.add_sip_endpoint(sip_type, endpoint_name, sip_username, sip_password, sip_ip, from_user)
        self.check_sip(sip_type, 'register', endpoint_name, sip_username, sip_ip)

    def test_sip_none(self):
        driver = self.driver
        sip_type = 'none'
        endpoint_name = '10003'
        sip_username = '10003'
        sip_password = '10003'
        sip_ip = '172.16.8.180'
        from_user = '10003'
        sip = gateway_func.endpoint_func(driver)
        sip.delete_same_sip(endpoint_name)
        sip.add_sip_endpoint(sip_type, endpoint_name, sip_username, sip_password, sip_ip, from_user)
        self.check_sip(sip_type, 'none', endpoint_name, sip_username, sip_ip)

    def test_sip_anonymous(self):
        driver = self.driver
        sip_type = 'anonymous'
        endpoint_name = '10004'
        sip_username = ''
        sip_password = ''
        sip_ip = '172.16.8.181'
        from_user = '10004'
        sip = gateway_func.endpoint_func(driver)
        sip.delete_same_sip(endpoint_name)
        sip.add_sip_endpoint(sip_type, endpoint_name, sip_username, sip_password, sip_ip, from_user)
        self.check_sip(sip_type, '', endpoint_name, sip_username, sip_ip)

if __name__ == '__main__':
    #__generate_testcases()
    suite = unittest.TestSuite()
    #suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_sip_information))
    suite.addTest(test_sip_information('test_sip_server'))
    suite.addTest(test_sip_information('test_sip_client'))
    suite.addTest(test_sip_information('test_sip_none'))
    suite.addTest(test_sip_information('test_sip_anonymous'))

    runner = unittest.TextTestRunner()
    runner.run(suite)

    #fp = file('report.html', 'wb')
    #runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title='Report_title', description='Report_description')
    #runner.run(suite)
else:
    #__generate_testcases()
    pass

