#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, ConfigParser, logging, logging.config
#sys.path.append('python_lib')

import unittest,doctest
import HTMLTestRunner
from python_lib import *

#logging.basicConfig(level=logging.DEBUG,
        #format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        #datefmt='%Y-%b-%d-%a %H:%M:%S',
        #filename='test_ssh_login.log',
        #filemode='w')
#logging.config.fileConfig("logger.conf")
#logger = logging.getLogger("test_all")

suite = unittest.TestSuite()

config_file = 'config/web_cases.conf'
config = ConfigParser.ConfigParser()
config.read(config_file)

testcase_set = config.get('work', 'load_from_name').split(';')
testcase_list = []
for testcase in testcase_set:
        testcase_list.append('python_lib.%s' % testcase)
for test in testcase_list:
    try:
        suite.addTest(unittest.defaultTestLoader.loadTestsFromName(test))
    except Exception:
        print('ERROR: Skipping tests from "%s".' % test)
        try:
            __import__(test)
        except ImportError:
            print('Could not import the test module.')
        else:
            print('Cound not load the test suite.')
        from traceback import print_exc
        print_exc()

#runner = unittest.TextTestRunner()
#runner.run(suite)

fp = file('report.html', 'wb')
runner = HTMLTestRunner.HTMLTestRunner(stream=fp,title=u'测试报告',description=u'详细报告')
runner.run(suite)

