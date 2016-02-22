#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest, paramiko, socket, sys, time, HTMLTestRunner, ConfigParser, logging
from selenium import webdriver

reload(sys)
sys.setdefaultencoding('utf-8')

class test_ssh_login(unittest.TestCase):
    def setUp(self):
        '''初始化参数'''
        logging.info('Testcase: test_ssh_login')
        logging.info('Testcase - test_ssh_login - setUp')

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
        logging.info('Testcase - test_ssh_login - tearDown')
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

    def __modify_ssh_setting(self, is_enable, username, password):
        '''在 WEB 界面上修改 SSH 设置'''
        driver = self.driver
        driver.find_element_by_link_text('Login Settings').click()
        time.sleep(1)
        js = 'var q=document.documentElement.scrollTop=10000'
        driver.execute_script(js)
        time.sleep(0.3)

        ssh_sw = driver.find_element_by_id('ssh_sw')
        if is_enable:
            if ssh_sw.get_attribute('checked') == None:
                ssh_sw.click()
                time.sleep(1)
            driver.find_element_by_id('ssh_user').clear()
            driver.find_element_by_id('ssh_user').send_keys(username)
            driver.find_element_by_id('ssh_password').clear()
            driver.find_element_by_id('ssh_password').send_keys(password)
        else:
            if ssh_sw.get_attribute('checked') != None:
                ssh_sw.click()
                time.sleep(0.3)

        driver.find_element_by_xpath("//*[@id='float_btn_tr']/input").click()
        time.sleep(0.1)
        try:
            driver.find_element_by_id('apply').click()
            return True
        except:
            #print('username: %s, password: %s' % (username, password))
            #logging.error('用户名或密码错误，无法找到 Apply 按钮！')x
            driver.save_screenshot('pictures/test_ssh_login_%s_%s.png' % (username, password))
            return False
        
    def __verify_ssh_setting(self, hostname, username, password, port):
        '''测试 SSH 设置是否可用'''
        logging.info('Testcase - test_ssh_login - __verify_ssh_setting')
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((hostname, port))
        except Exception, e:
            print('*** Connect failed: ' + str(e))
            sys.exit(1)
        
        t = paramiko.Transport(sock)
        try:
            t.start_client()
        except paramiko.SSHException:
            print('*** SSH negotiation failed.')
            sys.exit()
            
        try:
            t.auth_password(username, password)
            if t.is_authenticated():
                print('%s\t%s\t%s\tsuccess' % (hostname, username, password))
                logging.debug('%s\t%s\t%s\tsuccess' % (hostname, username, password))
                t.close()
                
                if username == 'super':
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(hostname, port, username, password)
                    stdin, stdout, stderr = ssh.exec_command('id -u')
                    uid = stdout.readline().strip('\n')
                    stdin, stdout, stderr = ssh.exec_command('id -g')
                    gid = stdout.readline().strip('\n')
                    stdin, stdout, stderr = ssh.exec_command('id -G')
                    group = stdout.readline().strip('\n')
                    ssh.close()

                    if uid == '0' and gid == '0' and group == '0':
                        return True
                    else:
                        return False
                else:
                    return True
            else:
                print('%s\t%s\t%s\tfailed' % (hostname, username, password))
                logging.debug('%s\t%s\t%s\tfailed' % (hostname, username, password))
                t.close()
                return False
        except:
            print('%s\t%s\t%s\tfailed' % (hostname, username, password))
            logging.debug('%s\t%s\t%s\tfailed' % (hostname, username, password))
            t.close()
            return False

    def ssh_login_case(self, username, password):
        '''SSH Login Settings 测试用例集'''
        if self.__modify_ssh_setting(True, username, password) == True:
            time.sleep(0.5)
            self.assertTrue(self.__verify_ssh_setting(self.hostname, username, password, port = 12345), 'Authentication error!, username/password: %s/%s' % (username, password))
            if self.__modify_ssh_setting(False, None, None) == True:
                time.sleep(0.5)
                self.assertFalse(self.__verify_ssh_setting(self.hostname, username, password, port = 12345), 'After disable ssh setting, authentication success, ERROR!')
            else:
                self.assertTrue(False, 'Disable ssh setting error!')
        else:
            self.assertTrue(False, 'Input error, can not save!, username/password: %s/%s' % (username, password))

    @staticmethod
    def get_testcase(username, password):
        def func(self):
            '''SSH 登录测试用例'''
            self.ssh_login_case(username, password)
        return func

def __generate_testcases():
    config_file = 'config/web_cases.conf'
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    arglists = []
    testcases = config.get('test_ssh_login', 'testcases')
    testcases = testcases.split(';')
    for test in testcases:
        args = config.get('test_ssh_login', test).split(';')
        setattr(test_ssh_login, 'test_ssh_login_%s' % test, test_ssh_login.get_testcase(*args))

if __name__ == '__main__':
    __generate_testcases()
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_ssh_login))

    #runner = unittest.TextTestRunner()
    #runner.run(suite)

    fp = file('report.html', 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title='Report_title', description='Report_description')
    runner.run(suite)
else:
    __generate_testcases()

