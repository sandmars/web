#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest, paramiko, socket, sys, time, HTMLTestRunner, ConfigParser
from selenium import webdriver

reload(sys)
sys.setdefaultencoding('utf-8')

#hostname1=''.join(config.get('IP','ipaddress'))    

class test_web_login(unittest.TestCase):
    def setUp(self):
        u'''初始化参数'''
        self.config_file = 'config/web_cases.conf'
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.config_file)
        self.hostname = self.config.get('gateway', 'hostname')
        cache = self.config.get('test_web_login', 'current')
        cache = cache.split(';')
        self.username = cache[0]
        self.password = cache[1]
        self.port = cache[3]
        self.login_mode = cache[4]
        if self.port == '':
            if self.login_mode == 'http and https':
                self.port = 80
            elif self.login_mode == 'only https':
                self.port = 443
            else:
                self.port = 80
        if self.login_mode == 'http and https':
            self.login_mode = 'http'
        elif self.login_mode == 'only https':
            self.login_mode = 'https'
        else:
                self.login_mode = 'http'
        self.baseurl = '%s://%s:%s@%s:%s' % (self.login_mode, self.username, self.password, self.hostname, int(self.port))

        self.verificationErrors = []
        self.driver = webdriver.Firefox()
        #self.driver.maximize_window()
        self.driver.set_window_size(1024, 768)
        self.driver.implicitly_wait(5)
        self.driver.get(self.baseurl)

    def tearDown(self):
        u'''关闭文件，关闭浏览器'''
        #self.driver.quit()
        self.assertEqual([], self.verificationErrors)

    def __modify_web_login(self, username, password1, password2, port, login_mode):
        '''在 WEB 界面上修改 WEB 设置
        参数：
            username：WEB用户名
            password1：WEB登陆密码
            password2：WEB确认密码
            port：WEB端口号，模拟网关不支持，设置为None
            login_mode：WEB登陆模式，仅E1网关支持http and https、only https，其他网关不支持，设置为None'''
        driver = self.driver
        driver.find_element_by_link_text('Login Settings').click()
        driver.find_element_by_id('user').clear()
        driver.find_element_by_id('user').send_keys(username)
        driver.find_element_by_id('pw1').clear()
        driver.find_element_by_id('pw1').send_keys(password1)
        driver.find_element_by_id('pw2').clear()
        driver.find_element_by_id('pw2').send_keys(password2)
        # 模拟网关无法修改WEB端口号
        if port != 'None':
            driver.find_element_by_id('web_server_port').clear()
            driver.find_element_by_id('web_server_port').send_keys(port)
        # E1网关增加此项功能
        if login_mode != '':
            from selenium.webdriver.support.ui import Select
            Select(driver.find_element_by_id('login_mode')).select_by_visible_text(login_mode)
        #driver.find_element_by_xpath("//*[@id='float_btn_tr']/input").click()
        js = 'var q=document.documentElement.scrollTop=10000'
        driver.execute_script(js)
        driver.find_element_by_xpath("//*[@id='float_btn_tr']/input").click()
            
        try:
            driver.find_element_by_id('apply').click()
            driver.quit()
            return True
        except:
            #print('用户名或密码或端口错误，无法找到 Apply 按钮！')
            #print('username: %s, password1: %s, password2: %s, port: %s' % (username, password1, password2, port))
            driver.save_screenshot('pictures/test_web_login-%s-%s-%s-%s.png' % (username, password1, password2, port))
            driver.quit()
            return False

    def __verify_web_setting(self, hostname, port, username, password, login_mode):
        '''验证 WEB 用户名、密码、端口号'''
        driver = webdriver.Firefox()
        #driver.maximize_window()
        driver.set_window_size(1024, 768)
        driver.implicitly_wait(5)
        if login_mode == 'http and https':
            mode = 'http'
        elif login_mode == 'only https':
            mode = 'https'
        else:
            mode = 'http'
        newurl = '%s://%s:%s@%s:%s' % (mode, username, password, hostname, port)
        driver.get(newurl)
        time.sleep(1)
        title = driver.title
        driver.quit()
        if title == 'System Status':
            return True
        else:
            return False

    def web_login_case(self, username, password1, password2, port, login_mode):
        '''WEB 登录测试用例集'''
        if self.__modify_web_login(username, password1, password2, port, login_mode) == True:
            if port == '':
                if login_mode == 'http and https':
                    port = 80
                elif login_mode == 'only https':
                    port = 443
                else:
                    port = 80
            self.config.set('test_web_login', 'current', '%s;%s;%s;%s;%s' % (username, password1, password2, port, login_mode))
            self.config.write(open(self.config_file, "w"))
            time.sleep(1)
            self.assertTrue(self.__verify_web_setting(self.hostname, port, username, password1, login_mode), 'Authentication error!')
        else:
            self.assertTrue(False, 'Input error, can not save!')

    @staticmethod
    def get_testcase(username, password1, password2, port, login_mode):
        def func(self):
            u'''WEB 登录测试用例'''
            self.web_login_case(username, password1, password2, port, login_mode)
        return func

def __generate_testcases():
    config_file = 'config/web_cases.conf'
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    arglists = []
    testcases = config.get('test_web_login', 'testcases')
    testcases = testcases.split(';')
    for test in testcases:
        args = config.get('test_web_login', test).split(';')
        setattr(test_web_login, 'test_web_login_%s' % test, test_web_login.get_testcase(*args))

if __name__ == '__main__':
    __generate_testcases()
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_web_login))

    #runner = unittest.TextTestRunner()
    #runner.run(suite)

    fp = file('report.html', 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title='Report_title', description='Report_description')
    runner.run(suite)
else:
    __generate_testcases()
