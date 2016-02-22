#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket, sys, unittest, HTMLTestRunner, ConfigParser, time
from selenium import webdriver

reload(sys)
sys.setdefaultencoding('utf-8')
 
class test_asterisk_cli(unittest.TestCase):
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
        self.driver.find_element_by_link_text('ADVANCED').click()
        self.driver.find_element_by_link_text('Asterisk CLI').click()

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

    def modify_asterisk_cli(self, command):
        '''执行Asterisk CLI，返回报告'''
        driver = self.driver
        driver.find_element_by_id('command').clear()
        driver.find_element_by_id('command').send_keys(command)
        driver.find_element_by_css_selector("input[type=\"submit\"]").click()
        result = driver.find_element_by_id('lps').text
        return(result)

    def test_asterisk_cli(self):
        '''测试Asterisk CLI功能'''
        driver = self.driver
        result = self.modify_asterisk_cli('core show version')
        self.assertTrue('Asterisk' in result and True or False, 'No Asterisk print!')
        time.sleep(1)
        result = self.modify_asterisk_cli('core show sysinfo')
        self.assertTrue('System Statistics' in result and True or False, 'No System Statistics print!')
        time.sleep(1)
        result = self.modify_asterisk_cli('core show uptime')
        self.assertTrue('Last reload' in result and True or False, 'No uptime print!')
        time.sleep(1)

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_asterisk_cli))

    runner = unittest.TextTestRunner()
    runner.run(suite)

    #fp = file('report.html', 'wb')
    #runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title='Report_title', description='Report_description')
    #runner.run(suite)

