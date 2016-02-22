#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest, sys, time, HTMLTestRunner, ConfigParser
from lib import shell_func
from selenium import webdriver

reload(sys)
sys.setdefaultencoding('utf-8')

class test_system_tools(unittest.TestCase):
    def setUp(self):
        u'''初始化参数'''
        config_file = 'config/web_cases.conf'
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_file)
        self.hostname = self.config.get('gateway', 'hostname')
        port = self.config.getint('gateway', 'web_port')
        username = self.config.get('gateway', 'web_username')
        password = self.config.get('gateway', 'web_password')
        baseurl = 'http://%s:%s@%s:%s' % (username, password, self.hostname, port)

        self.driver = webdriver.Firefox()
        #self.driver.maximize_window()
        self.driver.set_window_size(1024, 768)
        self.driver.implicitly_wait(5)
        self.verificationErrors = []
        self.driver.get(baseurl)
        self.driver.find_element_by_link_text('Tools').click()

    def tearDown(self):
        u'''关闭文件，关闭浏览器'''
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

    def __system_reboot(self):
        u'''重启系统'''
        driver = self.driver
        time.sleep(1)
        driver.find_element_by_xpath("//input[@value='System Reboot']").click()
        driver.switch_to.alert.accept()
        time.sleep(60)
        driver.refresh()
        if driver.title == 'System Status':
            return True
        else:
            return False

    def __asterisk_reboot(self):
        u'''重启 Asterisk
        
        仅适用于E1网关，GSM网关获取asterisk PID命令不同'''
        driver = self.driver
        driver.find_element_by_xpath("//input[@value='Asterisk Reboot']").click()
        time.sleep(1)
        driver.switch_to.alert.accept()
        time.sleep(3)
        driver.execute_script('var q=document.documentElement.scrollTop=10000')
        result = driver.find_element_by_xpath('//table/tbody/tr[4]/td').text
        if 'Succeeded' in result:
            return True
        else:
            return False

    def __update_sys(self, firmware):
        '''本地升级系统测试'''
        driver = self.driver
        driver.find_element_by_id('update_sys_file').send_keys(firmware)
        time.sleep(1)
        driver.find_element_by_xpath("//input[@value='System Update']").click()
        time.sleep(1)
        driver.switch_to.alert.accept()
        time.sleep(1)
        driver.execute_script('var q=document.documentElement.scrollTop=10000')
        #report = driver.find_element_by_class_name('output_tab').text
        if 'reboot system' in driver.page_source:
            return(True)
        else:
            return(False)

    def __factory_reset(self):
        '''恢复出厂设置'''
        driver = self.driver
        driver.find_element_by_link_text('Tools').click()
        time.sleep(1)
        for element in driver.find_elements_by_css_selector("input[type=\"submit\"]"):
            if element.get_attribute('value') == 'Factory Reset':
                element.click()
                break
        time.sleep(1)
        driver.switch_to.alert.accept()
        time.sleep(60)
        driver.get('http://admin:admin@172.16.100.1:80')
        assertEqual(driver.title, 'System Status', 'After reset, can not access to System Status page!')
        # 对比MAC
        eth_info = driver.find_elements_by_class_name('tshow')[2].text
        eth_info = ';'.join(eth_info.split('\n')).split(';')
        eth0_mac = eth_info[1].split(' ')[1]
        self.assertEqual(eth0_mac, self.config.get('localhost', 'eth1_mac'), "ETH1 MAC ERROR, maybe this isn't your gateway!")

    @staticmethod
    def get_testcase(test_type):
        if test_type == 'test_system_reboot':
            def func(self):
                '''System Reboot测试用例'''
                self.assertTrue(self.__system_reboot(), 'Reboot system error!')
        elif test_type == 'test_asterisk_reboot':
            def func(self):
                '''Asterisk Reboot测试用例'''
                self.assertTrue(self.__asterisk_reboot(), 'Reboot Asterisk error!')
        elif 'test_update_sys' in test_type:
            def func(self):
                '''系统升级测试用例'''
                firmware = self.config.get('test_system_tools', test_type)
                self.assertTrue(self.__update_sys(firmware), 'Update system error!')
                self.assertTrue(self.__system_reboot(), 'Reboot system error!')
        return func

def __generate_testcases():
    config_file = 'config/web_cases.conf'
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    testcases = config.get('test_system_tools', 'testcases').split(';')
    for test in testcases:
        setattr(test_system_tools, 'test_system_tools_%s' % test, test_system_tools.get_testcase(test))

if __name__ == '__main__':
    suite = unittest.TestSuite()
    #suite.addTest(test_system_tools('test_system_reboot'))
    #suite.addTest(test_system_tools('test_asterisk_reboot'))
    ##suite.addTest(test_system_tools('test_update_sys'))
    ##suite.addTest(test_system_tools('test_upload_file'))
    ##suite.addTest(test_system_tools('test_online_update'))
    #suite.addTest(test_system_tools('test_factory_reset'))
    runner = unittest.TextTestRunner()
    runner.run(suite)

    #fp = file('report.html', 'wb')
    #runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title='Report_title', description='Report_description')
    #runner.run(suite)
else:
    __generate_testcases()
