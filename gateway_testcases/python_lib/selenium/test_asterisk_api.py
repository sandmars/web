#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket, sys, unittest, HTMLTestRunner, ConfigParser, time
from selenium import webdriver

reload(sys)
sys.setdefaultencoding('utf-8')
 
class asterisk_ami:
    def __init__(self, hostname, port):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            print('Failed to create socket!')
            sys.exit()
        self.sock.settimeout(10)
        try:
            self.sock.connect((hostname, port))
            self.connect_error = True
            time.sleep(3)
        except:
            self.connect_error = False

    def __del__(self):
        self.sock.close()

    def send_cmd(self, action, **args):
        cmd = 'Action: %s\r\n' % action
        for key, value in args.items():
            cmd += '%s: %s\r\n' % (key, value)
        cmd += "\r\n"
        self.sock.send(cmd)
        data = []
        while '\r\n\r\n' not in ''.join(data)[-4:]:
            buf = self.sock.recv(1)
            data.append(buf)
            ret_list = ''.join(data).split('\r\n')
        return ret_list

    def login(self, username, password):
        ret = self.send_cmd('Login', Username=username, Secret=password)
        if 'Success' in ret[1]:
            return True
        else:
            return False

    def logoff(self):
        ret = self.send_cmd('Logoff')
        if 'Goodbye' in ret[1]:
            return True
        else:
            return False

class test_asterisk_api(unittest.TestCase):
    def setUp(self):
        u'''初始化参数'''
        config_file = 'config/web_cases.conf'
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_file)
        self.hostname = self.config.get('gateway', 'hostname')
        self.port = self.config.getint('gateway', 'web_port')
        self.username = self.config.get('gateway', 'web_username')
        self.password = self.config.get('gateway', 'web_password')
        #self.gw_type = self.config.get('gateway', 'gw_type')
        self.baseurl = 'http://%s:%s@%s:%s' % (self.username, self.password, self.hostname, self.port)

        self.driver = webdriver.Firefox()
        #self.driver.maximize_window()
        self.driver.set_window_size(1024, 768)
        self.driver.implicitly_wait(5)
        self.verificationErrors = []
        #self.driver.get(self.baseurl)


    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

    def modify_asterisk_api(self, gw_type, is_enable, username, password, deny, permit):
        '''启用禁用 Asterisk AMI 测试'''
        port = self.config.getint('test_asterisk_api', 'port')
        driver = self.driver
        driver.get(self.baseurl)
        driver.find_element_by_link_text('ADVANCED').click()
        driver.find_element_by_link_text('Asterisk API').click()

        ami_sw = driver.find_element_by_id('enable_ami')
        if is_enable:
	        if ami_sw.get_attribute('checked') == None:
	            ami_sw.click()
	            time.sleep(1)
	        driver.find_element_by_id('name').clear()
	        driver.find_element_by_id('name').send_keys(username)
	        driver.find_element_by_id('secret').clear()
	        driver.find_element_by_id('secret').send_keys(password)
	        driver.find_element_by_id('deny').clear()
	        driver.find_element_by_id('deny').send_keys(deny)
	        driver.find_element_by_id('permit').clear()
	        driver.find_element_by_id('permit').send_keys(permit)
        else:
            if ami_sw.get_attribute('checked') != None:
                ami_sw.click()
                time.sleep(1)

        driver.execute_script('var q=document.documentElement.scrollTop=10000')
        driver.find_element_by_css_selector("input[type=\"submit\"]").click()
        time.sleep(1)
        try:
            driver.find_element_by_id('apply').click()
        except:
            self.assertTrue(False, 'can not find apply button!')
        time.sleep(1)
        ami = asterisk_ami(self.hostname, port)
        if is_enable:
            self.assertTrue(ami.connect_error, 'socket connect error!\n\thostname: %s\n\tport: %s' % (self.hostname, port))
            self.assertTrue(ami.login(username, password), 'Login failed!\n\tusername: %s\n\tpassword: %s\n\tdeny: %s\n\tpermit: %s' % (username, password, deny, permit))
            #self.assertTrue(ami.logoff(), 'Logoff failed')
        else:
            # E1/T1 Gateway 不能连接，GSM Gateway 可以连接不能登录
            time.sleep(1)
            if gw_type == 'dgw':
                self.assertTrue(ami.connect_error, 'socket connect error!')
            if gw_type == 'gsm':
                self.assertTrue(ami.connect_error, 'socket connect error!')
                #self.assertFalse(ami.login(username, password), 'After disable asterisk ami, login success, ERROR!')
                login_ret = ami.login(username, password)
                self.assertFalse(login_ret, 'After disable asterisk ami, login success, ERROR!')

    def asterisk_api_testcase(self, gw_type, username, password, deny, permit):
        '''Asterisk AMI 启用禁用测试用例集'''
        self.modify_asterisk_api(gw_type, True, username, password, deny, permit)
        self.modify_asterisk_api(gw_type, False, username, password, deny, permit)

    @staticmethod
    def get_testcase(gw_type, username, password, deny, permit):
        def func(self):
            '''Asterisk AMI 启用禁用测试用例'''
            self.asterisk_api_testcase(gw_type, username, password, deny, permit)
        return func

def __generate_testcases():
    config_file = 'config/web_cases.conf'
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    testcases = config.get('test_asterisk_api', 'testcases')
    testcases = testcases.split(';')
    gw_type = config.get('test_asterisk_api', 'gw_type')
    for test in testcases:
        args = config.get('test_asterisk_api', test).split(';')
        setattr(test_asterisk_api, 'test_asterisk_api_%s' % test, test_asterisk_api.get_testcase(gw_type,*args))

if __name__ == '__main__':
    __generate_testcases()
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_asterisk_api))

    #runner = unittest.TextTestRunner()
    #runner.run(suite)

    fp = file('report.html', 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title='Report_title', description='Report_description')
    runner.run(suite)
else:
    __generate_testcases()
