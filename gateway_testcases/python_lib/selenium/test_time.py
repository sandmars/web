#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.support.ui import Select
import sys, unittest, time, datetime, HTMLTestRunner, ConfigParser

reload(sys)
sys.setdefaultencoding('utf-8')

class test_time(unittest.TestCase):
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
        self.driver.set_window_size(1024, 768)
        self.driver.implicitly_wait(5)
        self.driver.get(self.baseurl)
        self.driver.find_element_by_link_text("Time").click()

    def tearDown(self):
        u'''关闭文件，关闭浏览器'''
        self.driver.quit()

    def __report(self):
        driver = self.driver
        driver.execute_script('var q=document.documentElement.scrollTop=10000')
        gw_time = driver.find_element_by_id('currenttime').text
        try:
            gw_report = driver.find_element_by_xpath("/html/body/div[1]/div[3]/table/tbody/tr[2]/td").text
        except:
            gw_report = 'No report!'
        print("当前个数: %d" % self.count)
        report_file = open('time_report.txt', 'a')
        report_file.write("count:   %d\ngw_time: %s\nreport:  %s\n\n" % (self.count, gw_time, gw_report))
        report_file.close()
        driver.save_screenshot('%d.png' % (self.count))
        return (gw_time, gw_report)

    def sync_from_client(self):
        '''从客户端同步时间'''
        driver = self.driver
        driver.execute_script('var q=document.documentElement.scrollTop=10000')
        driver.find_element_by_xpath("//input[@value='Sync from Client']").click()
        time.sleep(1)
        result = driver.find_element_by_xpath("/html/body/div[1]/div[3]/table/tbody/tr[2]/td").text
        self.assertTrue('Succeeded' in result and True or False, 'Syn from client ERROR')

    def sync_from_ntp(self, timezone, ntp_server1, ntp_server2, ntp_server3):
        '''从NTP服务器同步时间'''
        driver = self.driver
        driver.execute_script('var q=document.documentElement.scrollTop=0')
        Select(driver.find_element_by_id("system_timezone")).select_by_visible_text(timezone)
        driver.find_element_by_id('ntp_server1').clear()
        driver.find_element_by_id('ntp_server1').send_keys(ntp_server1)
        driver.find_element_by_id('ntp_server2').clear()
        driver.find_element_by_id('ntp_server2').send_keys(ntp_server2)
        driver.find_element_by_id('ntp_server3').clear()
        driver.find_element_by_id('ntp_server3').send_keys(ntp_server3)
        driver.execute_script('var q=document.documentElement.scrollTop=10000')
        driver.find_element_by_xpath("//input[@value='Sync from NTP']").click()
        driver.execute_script('var q=document.documentElement.scrollTop=10000')
        result = driver.find_element_by_xpath("/html/body/div[1]/div[3]/table/tbody/tr[2]/td").text
        time.sleep(1)
        self.assertTrue('Succeeded' in result and True or False, 'Syn from NTP server ERROR')

    @staticmethod
    def get_testcase(test_type, timezone, ntp_server1, ntp_server2, ntp_server3):
        '''
        参数：
            test_type：测试类型，client、ntp
                设置为client时，其他参数为空'''
        def func(self):
            '''测试时间同步功能'''
            if test_type == 'ntp':
                self.sync_from_ntp(timezone, ntp_server1, ntp_server2, ntp_server3)
            elif test_type == 'client':
                self.sync_from_client()
        return func

def __generate_testcases():
    config_file = 'config/web_cases.conf'
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    arglists = []
    testcases = config.get('test_time', 'testcases')
    testcases = testcases.split(';')
    for test in testcases:
        args = config.get('test_time', test)
        args = args.split(';')
        setattr(test_time, 'test_time_%s' % test, test_time.get_testcase(*args))

if __name__ != '__main__':
    __generate_testcases()

