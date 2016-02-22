#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.support.ui import Select
import unittest, time, ConfigParser, HTMLTestRunner, sys
from lib import gateway_func

reload(sys)
sys.setdefaultencoding('utf-8')

class test_sip_endpoint(unittest.TestCase):
    def setUp(self):
        u'''初始化参数'''
        config_file = 'config/web_cases.conf'
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_file)
        self.hostname = self.config.get('gateway', 'hostname')
        self.port = self.config.getint('gateway', 'web_port')
        self.username = self.config.get('gateway', 'web_username')
        self.password = self.config.get('gateway', 'web_password')
        self.baseurl = 'http://%s:%s@%s:%s' % (self.username, self.password, self.hostname, self.port)

        self.driver = webdriver.Firefox()
        #self.driver.maximize_window()
        self.driver.set_window_size(1024, 768)
        self.driver.implicitly_wait(5)
        self.verificationErrors = []
        self.driver.get(self.baseurl)
        self.count = 0

    def tearDown(self):
        u'''关闭文件，关闭浏览器'''
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)
    
    @staticmethod
    def get_testcase(gw_type, sip_type, endpoint_name, sip_username, sip_password, sip_ip, from_user):
        def func(self):
            u'''添加 SIP Endpoint 测试用例'''
            sip = gateway_func.endpoint_func(self.driver, gw_type)
            sip.delete_same_sip(endpoint_name)
            sip.add_sip_endpoint(sip_type, endpoint_name, sip_username, sip_password, sip_ip, from_user)
        return func

def __generate_testcases():
    config_file = 'config/web_cases.conf'
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    arglists = []
    testcases = config.get('test_sip_endpoint', 'testcases')
    testcases = testcases.split(';')
    # 增加gw_type，O口网关仅有SIP
    gw_type = config.get('test_sip_endpoint', 'gw_type')
    for test in testcases:
        args = config.get('test_sip_endpoint', test).split(';')
        setattr(test_sip_endpoint, 'test_sip_endpoint_%s' % test, test_sip_endpoint.get_testcase(gw_type,*args))

if __name__ == '__main__':
    __generate_testcases()
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_sip_endpoint))
    #suite.addTest(test_sip('test_sip'))

    #runner = unittest.TextTestRunner()
    #runner.run(suite)

    fp = file('report.html', 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title='Report_title', description='Report_description')
    runner.run(suite)
else:
    __generate_testcases()

