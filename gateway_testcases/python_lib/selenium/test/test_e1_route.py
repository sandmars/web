#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from lib import gateway_func
import ConfigParser, unittest, sys, HTMLTestRunner

reload(sys)
sys.setdefaultencoding('utf-8')

class test_e1_route(unittest.TestCase):
    def setUp(self):
        '''初始化参数'''
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

    def tearDown(self):
        '''关闭文件，关闭浏览器'''
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

    def route_case(self, routing_name, from_channel, to_channel, forward_number, failover, manipulation_field):
        driver = self.driver
        route = gateway_func.route_func(driver, 'dgw')
        self.assertTrue(route.add_routing_rule(routing_name, from_channel, to_channel, forward_number, failover, manipulation_field), 'Can not find apply button to save route, ERROR!')

    @staticmethod
    def get_testcase(routing_name, from_channel, to_channel, forward_number, failover, manipulation_field):
        def func(self):
            self.route_case(routing_name, from_channel, to_channel, forward_number, failover, manipulation_field)
        return func

def __generate_testcases():
    config_file = 'config/web_cases.conf'
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    arglists = []
    for test in config.get('test_e1_route', 'testcases').split(';'):
        args = config.get('test_e1_route', test).split(';')
        manipulation = args.pop()
        if manipulation != '':
            manipulation_sec = config.get('test_e1_route', manipulation).split(';')
            count = 0
            manipulation_args = ''
            for sec in manipulation_sec:
                manipulation_args += config.get('test_e1_route', sec)
                if count != (len(manipulation_sec) - 1):
                    manipulation_args += ':'
                count += 1
            args.append(manipulation_args)
        else:
            args.append('')
        setattr(test_e1_route, 'test_e1_route_%s' % test, test_e1_route.get_testcase(*args))

if __name__ == '__main__':
    __generate_testcases()
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_e1_route))

    runner = unittest.TextTestRunner()
    runner.run(suite)

    #fp = file('report.html', 'wb')
    #runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title='Report_title', description='Report_description')
else:
    __generate_testcases()

