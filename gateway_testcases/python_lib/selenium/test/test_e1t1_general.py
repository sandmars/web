#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest, sys, time, HTMLTestRunner, ConfigParser
from selenium import webdriver
#import selenium
from selenium.webdriver.support.ui import Select

reload(sys)
sys.setdefaultencoding('utf-8')

class test_e1t1_general(unittest.TestCase):
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
        #self.driver.find_element_by_link_text('Tools').click()
        self.driver.find_element_by_link_text('T1/E1').click()
        time.sleep(1)

    def tearDown(self):
        u'''关闭文件，关闭浏览器'''
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

    def general_e1t1(self, locale, interface_type, timing_source, framing, coding, lbo, cb_crc, signalling, switchtype, description):
        driver = self.driver

        Select(driver.find_element_by_name("zonecode_list")).select_by_visible_text(locale)

        if interface_type == 'T1':
            driver.find_element_by_id("interface_t1").click()
        else:
            driver.find_element_by_id("interface_e1").click()

        timing_source = timing_source.split(':')
        framing = framing.split(':')
        coding = coding.split(':')
        lbo = lbo.split(':')
        cb_crc = cb_crc.split(':')
        signalling = signalling.split(':')
        switchtype = switchtype.split(':')
        description = description.split(':')

        for num in range(4):
            Select(driver.find_element_by_id("timingsource%d" % (num+1))).select_by_visible_text(timing_source[num])
            Select(driver.find_element_by_id("framing%d" % (num+1))).select_by_visible_text(framing[num])
            Select(driver.find_element_by_id("coding%d" % (num+1))).select_by_visible_text(coding[num])
            if lbo[num] != '':
                Select(driver.find_element_by_id("lbo%d" % (num+1))).select_by_visible_text(lbo[num])
            if cb_crc[num] != '':
                Select(driver.find_element_by_id("cb_crc%d" % (num+1))).select_by_visible_text(cb_crc[num])
            Select(driver.find_element_by_id("signalling%d" % (num+1))).select_by_visible_text(signalling[num])
            if switchtype[num] != '':
                Select(driver.find_element_by_id("switchtype%d" % (num+1))).select_by_visible_text(switchtype[num])
            if description[num] != '':
                driver.find_element_by_id('description%d' % (num+1)).clear()
                driver.find_element_by_id('description%d' % (num+1)).send_keys(description[num])

        driver.find_element_by_css_selector("input[type=\"submit\"]").click()
        try:
            driver.find_element_by_id("apply").click()
        except:
            self.assertTrue(False, 'Input error, can not save!')

    @staticmethod
    def get_testcase(locale, interface_type, timing_source, framing, coding, lbo, cb_crc, signalling, switchtype, description):
        def func(self):
            self.general_e1t1(locale, interface_type, timing_source, framing, coding, lbo, cb_crc, signalling, switchtype, description)
        return func

def __generate_testcases():
    config_file = 'config/web_cases.conf'
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    arglists = []
    testcases = config.get('test_e1t1_general', 'testcases')
    testcases = testcases.split(';')
    for test in testcases:
        args = config.get('test_e1t1_general', test).split(';')
        setattr(test_e1t1_general, 'test_e1t1_general_%s' % test, test_e1t1_general.get_testcase(*args))

if __name__ == '__main__':
    __generate_testcases()
    suite = unittest.TestSuite()
    #suite.addTest(test_e1t1_general('test_exchange_e1t1'))
    #suite.addTest(test_e1t1_general('test_general'))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_e1t1_general))
    runner = unittest.TextTestRunner()
    runner.run(suite)

    #fp = file('report.html', 'wb')
    #runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title='Report_title', description='Report_description')
    #runner.run(suite)
else:
    __generate_testcases()

