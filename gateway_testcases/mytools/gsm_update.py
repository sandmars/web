#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, time
from selenium import webdriver

reload(sys)
sys.setdefaultencoding('utf-8')

def update_system(baseurl):
    driver = webdriver.Firefox()
    driver.set_window_size(1024, 768)
    driver.get(baseurl)
    driver.find_element_by_link_text('Information').click()
    current_version = driver.find_element_by_xpath("//table/tbody/tr[3]/td").text
    if current_version == '2.2.0':
        firmware = '/root/gsm/wg400-2.2.2.img'
        #firmware = '/root/gsm/wg400-2.1.3.img'
    elif current_version == '2.2.2':
        firmware = '/root/gsm/wg400-2.2.0.img'
        #firmware = '/root/gsm/wg400-2.1.3.img'
    else:
        firmware = '/root/gsm/wg400-2.2.0.img'
    print('%s - %s' % (current_version, firmware.split('/').pop()))
    driver.find_element_by_link_text('Tools').click()
    driver.find_element_by_id('update_sys_file').send_keys(firmware)
    time.sleep(1)
    driver.find_element_by_xpath("//input[@value='System Update']").click()
    time.sleep(1)
    driver.switch_to.alert.accept()
    driver.execute_script('var q=document.documentElement.scrollTop=10000')
    report = driver.find_element_by_class_name('output_tab').text
    if 'reboot system' in report:
        driver.quit()
        return(True)
    else:
        driver.quit()
        return(False)

def reboot_system(baseurl):
    driver = webdriver.Firefox()
    driver.set_window_size(1024, 768)
    driver.get(baseurl)
    driver.find_element_by_link_text('Tools').click()
    driver.find_element_by_xpath("//input[@value='System Reboot']").click()
    driver.switch_to.alert.accept()
    time.sleep(80)
    driver.refresh()
    if driver.title == 'System Status':
        driver.quit()
        return True
    else:
        driver.quit()
        return(False)

if __name__ == '__main__':
    #hostname = '172.16.1.150'
    hostname = '172.16.8.48'
    port = 80
    username = 'admin'
    password = 'admin'
    baseurl = 'http://%s:%s@%s:%s' % (username, password, hostname, port)
    suc = 0
    fail = 0
    while True:
        if update_system(baseurl):
            if reboot_system(baseurl):
                suc += 1
                print('Success: %d' % suc)
            else:
                fail += 1
                print('Failed: %d, Reboot system failed' % fail)
                break
        else:
            fail += 1
            print('Failed: %d, Update system failed!' % fail)
            break

