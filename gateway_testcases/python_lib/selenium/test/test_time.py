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

        self.count = 0

    def tearDown(self):
        u'''关闭文件，关闭浏览器'''
        self.driver.quit()

    def __scroll_down(self):
        js = 'var q=document.documentElement.scrollTop=10000'
        self.driver.execute_script(js)
        time.sleep(0.1)

    def __report(self):
        driver = self.driver
        self.__scroll_down()
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

    def test_client_time(self):
        self.driver.find_element_by_link_text("Time").click()
        self.count += 1
        driver = self.driver
        self.__scroll_down()
        driver.find_element_by_xpath("//input[@value='Sync from Client']").click()
        time.sleep(1)
        # 返回修改后的时间和报告
        return self.__report()

    def ntp_time_case(self, timezone, ntp_server1, ntp_server2, ntp_server3):
        self.driver.find_element_by_link_text("Time").click()
        self.count += 1
        driver = self.driver
        self.__scroll_down()
        Select(driver.find_element_by_id("system_timezone")).select_by_visible_text(timezone)
        driver.find_element_by_id('ntp_server1').clear()
        driver.find_element_by_id('ntp_server1').send_keys(ntp_server1)
        driver.find_element_by_id('ntp_server2').clear()
        driver.find_element_by_id('ntp_server2').send_keys(ntp_server2)
        driver.find_element_by_id('ntp_server3').clear()
        driver.find_element_by_id('ntp_server3').send_keys(ntp_server3)
        driver.find_element_by_xpath("//input[@value='Sync from NTP']").click()
        time.sleep(1)
        # 返回修改后的时间和报告
        return self.__report()

    @staticmethod
    def get_testcase(timezone, ntp_server1, ntp_server2, ntp_server3):
        def func(self):
            self.ntp_time_case(timezone, ntp_server1, ntp_server2, ntp_server3)
        return func

def __generate_testcases():
    config_file = 'config/web_cases.conf'
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    arglists = []
    count = 0
    testcases = config.get('test_time', 'testcases')
    testcases = testcases.split(';')
    for test in testcases:
        count += 1
        args = config.get('test_web_login', test)
        args = args.split(';')
        setattr(test_web_login, 'test_web_login_%d' % count, test_web_login.get_testcase(*args))

if __name__ == '__main__':
#	print 'This program is being run by itself'
#	
#	print '当前系统时间：%s' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#	case_time = gateway_time_settings('172.16.100.180')
#	timezone_list = ["Shanghai", "Chongqing", "Hong Kong"]
#	ntp_server1 = "time.asia.apple.com"
#	ntp_server2 = "time.windows.com"
#	ntp_server3 = "time.nist.gov"
#	for timezone in timezone_list:
#		#(gw_time, gw_report) = case_time.set_ntp_time(timezone, ntp_server1, ntp_server2, ntp_server3)
#		case_time.set_ntp_time(timezone, '', '', '')
#		time.sleep(1)
#		case_time.set_ntp_time(timezone, '', '', ntp_server3)
#		time.sleep(1)
#		case_time.set_ntp_time(timezone, '', ntp_server2, '')
#		time.sleep(1)
#		case_time.set_ntp_time(timezone, '', ntp_server2, ntp_server3)
#		time.sleep(1)
#		case_time.set_ntp_time(timezone, ntp_server1, '', '')
#		time.sleep(1)
#		case_time.set_ntp_time(timezone, ntp_server1, '', ntp_server3)
#		time.sleep(1)
#		case_time.set_ntp_time(timezone, ntp_server1, ntp_server2, '')
#		time.sleep(1)
#		case_time.set_ntp_time(timezone, ntp_server1, ntp_server2, ntp_server3)
#		time.sleep(1)
#	#(gw_time, gw_report) = case_time.set_client_time()
#	case_time.set_client_time()

    suite = unittest.TestSuite()
    suite.addTest(test_time('test_client_time'))

    #runner = unittest.TextTestRunner()
    #runner.run(suite)

    fp = file('report.html', 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title='Report_title', description='Report_description')
    runner.run(suite)
