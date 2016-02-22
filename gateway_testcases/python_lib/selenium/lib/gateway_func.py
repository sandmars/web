#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from fabric.api import local
from selenium.webdriver.support.ui import Select
import time,sys

class dahdi:
    def __init__(self, driver):
        self.driver = driver
        self.driver.find_element_by_link_text('T1/E1').click()
        time.sleep(1)

    def general(self, spans, locale, interface_type, timing_source, framing, coding, lbo, cb_crc, signalling, switchtype, description):
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

        driver.execute_script('var q=document.documentElement.scrollTop=1000')
        for num in range(int(spans)):
            Select(driver.find_element_by_id("timingsource%d" % (num+1))).select_by_visible_text(timing_source[num])
            #Select(driver.find_element_by_id("framing%d" % (num+1))).select_by_visible_text(framing[num])
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

class endpoint_func:
    def __init__(self, driver, gw_type):
        self.driver = driver
        if gw_type == 'analog_o':
            # O口网关仅有SIP
            driver.find_element_by_link_text("SIP").click()
            #driver.find_element_by_link_text("SIP Endpoints").click()
        else:
            driver.find_element_by_link_text("VOIP").click()
            #driver.find_element_by_link_text("VOIP Endpoints").click()

    def delete_all_endpoints(self):
        '''删除所有的SIP/IAX Endpoints'''
        driver = self.driver
        while True:
            try:
                #driver.find_element_by_css_selector("button[type=\"submit\"]").click()
                driver.find_element_by_xpath("//button[@value='Delete']").click()
                driver.switch_to.alert.accept()
                time.sleep(1)
                try:
                    driver.find_element_by_id("apply").click()
                except:
                    self.assertTrue(False, 'When delete all sip endpoint, can not find apply button, ERROR!')
            except:
                break

    def delete_same_sip(self, endpoint_name):
        '''检查是否有同名的 sip endpoint，有则删除
        参数：
            endpoint_name：SIP账号的名称'''
        driver = self.driver
        try:
            #driver.find_elements_by_class_name('tshow')[0].text.index(endpoint_name)
            driver.find_element_by_xpath("//form[1]/table/tbody/tr/td[text()[contains(.,'%s')]]/parent::tr//button[@value='Delete']" % endpoint_name).click()
            driver.switch_to.alert.accept()
            time.sleep(1)
            try:
                driver.find_element_by_id("apply").click()
            except:
                driver.save_screenshot('pictures/%s_%s.png' % (sys._getframe().f_code.co_name, endpoint_name))
                self.assertTrue(False, 'When delete a sip endpoint, can not find apply button, ERROR!\n\tendpoint_name: %s' % endpoint_name)
        except:
            pass
        finally:
            pass

    def add_sip_endpoint(self, sip_type, endpoint_name, sip_username, sip_password, sip_ip, from_user):
        '''添加 SIP Endpoint
        参数：
            sip_type：类型，支持server、client、anonymous、none
            endpoint_name：SIP账号名称
            sip_username：SIP用户名
            sip_password：SIP密码
            sip_ip：对接IP，无则为空
            from_user：from_user域，无则为空'''
        driver = self.driver
        driver.execute_script('var q=document.documentElement.scrollTop=999999')
        driver.find_element_by_css_selector("input[type=\"submit\"]").click()

        driver.find_element_by_id("endpoint_name").clear()
        driver.find_element_by_id("endpoint_name").send_keys(endpoint_name)
        if sip_type == 'anonymous':
            driver.find_element_by_id("anonymous").click()
        else:
            driver.find_element_by_id("sip_username").clear()
            driver.find_element_by_id("sip_username").send_keys(sip_username)
            driver.find_element_by_id("sip_password").clear()
            driver.find_element_by_id("sip_password").send_keys(sip_password)
        if sip_type == 'server':
            Select(driver.find_element_by_id("registration")).select_by_visible_text("Endpoint registers with this gateway")
        elif sip_type == 'client':
            Select(driver.find_element_by_id("registration")).select_by_visible_text("This gateway registers with the endpoint")
        else:
            Select(driver.find_element_by_id("registration")).select_by_visible_text("None")
        if sip_type != 'server':
            driver.find_element_by_id("sip_ip").clear()
            driver.find_element_by_id("sip_ip").send_keys(sip_ip)
            driver.execute_script('var q=document.documentElement.scrollTop=1000')
            driver.find_element_by_css_selector("#tab_main > #tab > li.tbg_fold").click()
            driver.find_element_by_id("from_user_readonly").click()
            driver.find_element_by_id("from_user").clear()
            driver.find_element_by_id("from_user").send_keys(from_user)

        driver.find_element_by_id("float_button_1").click()
        #driver.execute_script('var q=document.documentElement.scrollTop=10000')
        #driver.find_element_by_xpath("//input[@value='Save']").click()
        time.sleep(1)
        try:
            driver.find_element_by_id("apply").click()
        except:
            #self.__class__.__name__
            driver.save_screenshot('pictures/%s_%s_%s_%s_%s_%s_%s.png' % (sys._getframe().f_code.co_name, sip_type, endpoint_name, sip_username, sip_password, sip_ip, from_user))
            self.assertTrue(False, 'When save a sip endpoint, can not find apply button, ERROR!\n\tsip_type: %s\n\tendpoint_name: %s\n\tsip_username: %s\n\tsip_password: %s\n\tsip_ip: %s\n\tfrom_user: %s' % (sip_type, endpoint_name, sip_username, sip_password, sip_ip, from_user))

    def delete_same_iax(self, endpoint_name):
        '''检查是否有同名的 IAX endpoint，有则删除
        参数：
            endpoint_name：IAX名称'''
        driver = self.driver
        try:
            #driver.find_elements_by_class_name('tshow')[1].text.index(endpoint_name)
            #test = driver.find_elements_by_class_name('tshow')[1]
            driver.find_element_by_xpath("//form[2]/table/tbody/tr/td[text()[contains(.,'%s')]]/parent::tr//button[@value='Delete']" % endpoint_name).click()
            driver.switch_to.alert.accept()
            time.sleep(1)
            try:
                driver.find_element_by_id("apply").click()
            except:
                driver.save_screenshot('pictures/%s_%s.png' % (sys._getframe().f_code.co_name, endpoint_name))
                self.assertTrue(False, 'When delete a sip endpoint, can not find apply button, ERROR!\n\tendpoint_name: %s' % endpoint_name)
        except:
            pass
        finally:
            pass

    def add_iax_endpoint(self, iax_type, endpoint_name, iax_username, iax_password, iax_ip, auth):
        '''添加 IAX Endpoint
        参数：
            iax_type：IAX类型，支持server、client、none
            endpoint_name：IAX名称
            iax_username：IAX用户名
            iax_password：IAX密码
            iax_ip：对接IP，无则为空
            auth：验证类型，支持md5、plaintext、rsa'''
        driver = self.driver
        driver.execute_script('var q=document.documentElement.scrollTop=999999')
        add_button = driver.find_elements_by_css_selector("input[type=\"submit\"]")
        for button in add_button:
            if button.get_attribute('value') == 'Add New IAX2 Endpoint':
                button.click()

        driver.find_element_by_id("endpoint_name").clear()
        driver.find_element_by_id("endpoint_name").send_keys(endpoint_name)
        driver.find_element_by_id("iax_username").clear()
        driver.find_element_by_id("iax_username").send_keys(iax_username)
        driver.find_element_by_id("iax_password").clear()
        driver.find_element_by_id("iax_password").send_keys(iax_password)

        if iax_type == 'server':
            Select(driver.find_element_by_id("registration")).select_by_visible_text("Endpoint registers with this gateway")
        else:
            if iax_type == 'client':
                Select(driver.find_element_by_id("registration")).select_by_visible_text("This gateway registers with the endpoint")
            else:
                Select(driver.find_element_by_id("registration")).select_by_visible_text("None")

            driver.find_element_by_id("iax_ip").clear()
            driver.find_element_by_id("iax_ip").send_keys(iax_ip)

        #auth: md5, plaintext, rsa
        Select(driver.find_element_by_id("auth")).select_by_visible_text(auth)

        driver.find_element_by_id("float_button_1").click()
        try:
            driver.find_element_by_id("apply").click()
        except:
            driver.save_screenshot('pictures/%s_%s_%s_%s_%s_%s.png' % (sys._getframe().f_code.co_name, iax_type, endpoint_name, iax_username, iax_password, iax_ip))
            self.assertTrue(False, 'When save a iax endpoint, can not find apply button, ERROR!\n\tiax_type: %s\n\tendpoint_name: %s\n\tiax_username: %s\n\tiax_password: %s\n\tiax_ip: %s' % (iax_type, endpoint_name, iax_username, iax_password, iax_ip))

class route_func:
    def __init__(self, driver, gw_type):
        '''
        参数：
            driver：webdriver
            gw_type：网关类型，支持dgw、gsm'''
        self.driver = driver
        driver.find_element_by_link_text('ROUTING').click()
        #driver.find_element_by_link_text("Call Routing Rules").click()
        self.gw_type = gw_type

    def delete_same_group(self, group_name):
        '''检查是否有同名的group，有则删除
        参数：
            group_name：组名'''
        driver = self.driver
        driver.find_element_by_link_text("Groups").click()
        try:
            driver.find_element_by_xpath("//table/tbody/tr/td[text()[contains(.,'%s')]]/parent::tr//button[@value='Delete']" % group_name).click()
            driver.switch_to.alert.accept()
            time.sleep(1)
            try:
                driver.find_element_by_id("apply").click()
            except:
                driver.save_screenshot('pictures/%s_%s.png' % (sys._getframe().f_code.co_name, group_name))
                self.assertTrue(False, 'When delete a group, can not find apply button, ERROR!\n\tgroup_name: %s' % group_name)
        except:
            pass
        finally:
            pass

    def delete_all_groups(self):
        '''删除所有组'''
        driver = self.driver
        driver.find_element_by_link_text("Groups").click()
        while True:
            try:
                #driver.find_element_by_css_selector("button[type=\"submit\"]").click()
                driver.find_element_by_xpath("//button[@value='Delete']").click()
                driver.switch_to.alert.accept()
                time.sleep(1)
                try:
                    driver.find_element_by_id("apply").click()
                except:
                    self.assertTrue(False, 'When delete all groups, can not find apply button, ERROR!')
            except:
                break

    def add_group(self, grp_name, member_type, policy, all_member, members):
        '''添加端口、SIP组
        参数：
            grp_name：组名
            member_type: 成员类型，T1/E1, SIP, GSM
            policy：策略，Ascending/Descending/Roundrobin/Reverse Roundrobin
            all_member：是否选择所有成员，True/true、False/false
            members：格式为start:end:step，第start个开始，第end-1个结束，步进值step
                all_member=False, members=1:200:1：选中1-199
                all_member=True, members=200:201:1：选中所有，取消选择第200个'''
        driver = self.driver
        driver.find_element_by_link_text("Groups").click()
        driver.find_element_by_css_selector("input[type=\"submit\"]").click()
        driver.find_element_by_id("group_name").clear()
        driver.find_element_by_id("group_name").send_keys(grp_name)
        Select(driver.find_element_by_id("type")).select_by_visible_text(member_type)
        Select(driver.find_element_by_id("policy")).select_by_visible_text(policy)
        if all_member == 'True' or all_member == 'true':
            if member_type == 'SIP':
                driver.find_element_by_name('selsipall').click()
            elif member_type == 'T1/E1' or member_type == 'GSM':
                driver.find_element_by_name('selgsmall').click()
        members_list = members.split(':')
        for i in range(int(members_list[0]), int(members_list[1]), int(members_list[2])):
            if member_type == 'SIP':
                driver.find_element_by_xpath("(//input[@name='sip_members[]'])[%s]" % int(i)).click()
            elif member_type == 'T1/E1' or member_type == 'GSM':
                driver.find_element_by_xpath("(//input[@name='gsm_members[]'])[%s]" % int(i)).click()
        #for i in members_list:
            #if member_type == 'SIP':
                #driver.find_element_by_xpath("(//input[@name='sip_members[]'])[%s]" % int(i)).click()
            #elif member_type == 'T1/E1' or member_type == 'GSM':
                #driver.find_element_by_xpath("(//input[@name='gsm_members[]'])[%s]" % int(i)).click()
        time.sleep(0.5)
        driver.execute_script('var q=document.documentElement.scrollTop=999999')
        driver.find_element_by_css_selector("input.float_btn.gen_short_btn").click()
        driver.find_element_by_id("apply").click()

    def delete_all_routes(self):
        '''删除所有路由'''
        driver = self.driver
        while True:
            try:
                #driver.find_element_by_css_selector("button[type=\"submit\"]").click()
                driver.find_element_by_xpath("//button[@value='Delete']").click()
                driver.switch_to.alert.accept()
                time.sleep(1.5)
                try:
                    driver.find_element_by_id("apply").click()
                except:
                    self.assertTrue(False, 'When delete all sip endpoint, can not find apply button, ERROR!')
            except:
                break

    def delete_same_route(self, routing_name):
        driver = self.driver
        try:
            #driver.find_element_by_class_name('tdrag').text.index(routing_name)
            driver.find_element_by_xpath("//table/tbody/tr/td[text()[contains(.,'%s')]]/parent::tr//button[@value='Delete']" % routing_name).click()
            driver.switch_to.alert.accept()
            time.sleep(1)
            try:
                driver.find_element_by_id("apply").click()
            except:
                driver.save_screenshot('pictures/%s_%s.png' % (sys._getframe().f_code.co_name, routing_name))
                self.assertTrue(False, 'When delete a routing rule, can not find apply button, ERROR!\n\trouting_name: %s' % routing_name)
        except:
            #print('There is no endpoint named %s' % routing_name)
            pass
        finally:
            pass

    def advanced_route(self, prepend, prefix, pattern, cid):
        '''填充号码变换域，用于GSM、Analog_o产品
        参数：
            prepend：prepend域
            prefix：prefix域
            pattern：match pattern域
            cid：caller id域'''
        driver = self.driver

        name_dict = {}
        name_dict['prepend'] = prepend
        name_dict['prefix'] = prefix
        name_dict['pattern'] = pattern
        name_dict['cid'] = cid

        #driver.find_element_by_xpath("(//input[@name='prepend[]'])[2]").clear()
        new_advanced_route = lambda driver, element_name: driver.find_elements_by_name('%s[]' % element_name).pop()
        for key, value in name_dict.items():
            if value != '':
                input_box = new_advanced_route(driver, key)
                input_box.clear()
                input_box.send_keys(value)

    def manipulation_filed(self, prepend_e, prefix_e, match_e, sdfr_e, sta_e, rdfr_e, prepend_r, prefix_r, match_r, sdfr_r, sta_r, rdfr_r, callername):
        '''填充号码变换域，用于DGW产品
        参数：
            依次对应每个号码变换域的13个值'''
        driver = self.driver

        name_dict = {}
        name_dict['prepend_e'] = prepend_e
        name_dict['prefix_e'] = prefix_e
        name_dict['match_pattern_e'] = match_e
        name_dict['sdfr_e'] = sdfr_e
        name_dict['sta_e'] = sta_e
        name_dict['rdfr_e'] = rdfr_e
        name_dict['prepend_r'] = prepend_r
        name_dict['prefix_r'] = prefix_r
        name_dict['match_pattern_r'] = match_r
        name_dict['sdfr_r'] = sdfr_r
        name_dict['sta_r'] = sta_r
        name_dict['rdfr_r'] = rdfr_r
        name_dict['callername_r'] = callername

        #new_manipulation = lambda driver, element_name: driver.find_elements_by_xpath("(//input[@name='%s[]'])" % element_name).pop()
        new_manipulation = lambda driver, element_name: driver.find_elements_by_name('%s[]' % element_name).pop()
        for key, value in name_dict.items():
            if value != '':
                input_box = new_manipulation(driver, key)
                input_box.clear()
                input_box.send_keys(value)

    def add_routing_rule(self, routing_name, from_channel, to_channel, forward_number, failover, manipulation_field):
        '''添加高级路由：routing_name, from_channel, to_channel, forward_number, failover, manipulation_field
        manipulation_field: 
            DGW: prepend_e:prefix_e:match_e:sdfr_e:sta_e:rdfr_e:prepend_r:prefix_r:match_r:sdfr_r:sta_r:rdfr_r:callername:prepend_e:prefix_e:match_e:sdfr_e:sta_e:rdfr_e:prepend_r:prefix_r:match_r:sdfr_r:sta_r:rdfr_r:callername
            GSM/Analog_o: prepend:prefix:pattern:cid'''
        driver = self.driver
        driver.find_element_by_css_selector("input[type=\"submit\"]").click()
        gw_type = self.gw_type

        # Basic call routing rule
        driver.find_element_by_id("routing_name").clear()
        driver.find_element_by_id("routing_name").send_keys(routing_name)
        Select(driver.find_element_by_id("from_channel")).select_by_visible_text(from_channel)
        Select(driver.find_element_by_id("to_channel")).select_by_visible_text(to_channel)

        # CalleeID/CallerID manipulation
        if manipulation_field != '':
            arg_list = manipulation_field.split(':')
            if gw_type == 'gsm' or gw_type == 'analog_o':
                driver.find_element_by_xpath("(//li[@onclick=\"lud(this,'tab_advance')\"])[2]").click()
                base_count = 4
            elif gw_type == 'dgw':
                base_count = 13
            count = len(arg_list) / base_count
            for i in range(count):
                args = []
                if i > 0:
                    # Add More Manipulation Fields Button
                    driver.execute_script('var q=document.documentElement.scrollTop=999999')
                    driver.find_element_by_css_selector("input[type=\"button\"]").click()
                for j in range(base_count):
                    args.append(arg_list.pop(0))
                if gw_type == 'gsm' or gw_type == 'analog_o':
                    self.advanced_route(*args)
                elif gw_type == 'dgw':
                    self.manipulation_filed(*args)

        # Forward number
        if forward_number != '':
            driver.find_element_by_name("forward_number").clear()
            driver.find_element_by_name("forward_number").send_keys(forward_number)

        # Failover section
        if failover != '':
            count = 1
            for i in failover.split(':'):
                driver.find_element_by_name("add_failover_call").click()
                Select(driver.find_element_by_id("fctn_channel%d" % count)).select_by_visible_text(i)
                count += 1

        # 针对目前的模拟网关，Save按钮在上方，且没有浮动的Save按钮
        driver.execute_script('var q=document.documentElement.scrollTop=0')
        time.sleep(1)
        driver.find_element_by_xpath("//input[@value='Save']").click()
        # 浮动的Save按钮
        #driver.find_element_by_id("float_button_1").click()
        time.sleep(1)
        try:
            driver.find_element_by_id("apply").click()
            time.sleep(1)
            return True
        except:
            return False

    def exchange_routes(self, src_route, dst_route):
        '''交换两条路由
        参数：
            src_route：起始路由
            dst_route：目的路由
            将src_route移动到dst_route的位置上
            经测试，目前只能把下方的路由拖到上方的位置'''
        from selenium.webdriver.common.action_chains import ActionChains
        driver = self.driver
        src = driver.find_element_by_xpath("//table/tbody/tr/td[text()[contains(.,'%s')]]" % src_route)
        dst = driver.find_element_by_xpath("//table/tbody/tr/td[text()[contains(.,'%s')]]" % dst_route)
        ActionChains(driver).drag_and_drop(src, dst).perform()

        driver.execute_script('var q=document.documentElement.scrollTop=0')
        time.sleep(1)
        driver.find_element_by_xpath("//input[@value='Save Orders']").click()
        try:
            time.sleep(1)
            driver.find_element_by_id("apply").click()
            time.sleep(1)
            return True
        except:
            return False

class ss7_func:
    def __init__(self, driver):
        self.driver = driver
        driver.find_element_by_link_text('T1/E1').click()
        driver.find_element_by_link_text('SS7').click()

    def del_all_linkset(self):
        driver = self.driver
        driver.find_element_by_link_text('SS7').click()

        # 若添加一个链路集，则会添加一个删除按钮，即一个类型为 submit 的 button
        del_btn_list = driver.find_elements_by_css_selector("button[type=\"submit\"]")
        # 删除所有可删除的链路集
        if len(del_btn_list) > 0:
            del_btn_list[0].click()
            driver.switch_to.alert.accept()
            try:
                driver.find_element_by_id("apply").click()
                return True
            except:
                return False

    def __edit_link_set(self, linkset_name, linkset_enable, linkset_enable_st, linkset_use_connect, policy, subservice, t35, variant, opc, dpc, linkset_default):
        driver = self.driver
        driver.find_element_by_id('linkset_name').clear()
        driver.find_element_by_id('linkset_name').send_keys(linkset_name)

        enable_btn = driver.find_element_by_id('linkset_enabled')
        if linkset_enable:
            if not enable_btn.is_selected():
                enable_btn.click()
        else:
            if enable_btn.is_selected():
                enable_btn.click()

        enable_st_btn = driver.find_element_by_id('linkset_enable_st')
        if linkset_enable_st:
            if not enable_st_btn.is_selected():
                enable_st_btn.click()
        else:
            if enable_st_btn.is_selected():
                enable_st_btn.click()

        use_connect_btn = driver.find_element_by_id('linkset_use_connect')
        if linkset_use_connect:
            if not use_connect_btn.is_selected():
                use_connect_btn.click()
        else:
            if use_connect_btn.is_selected():
                use_connect_btn.click()

        Select(driver.find_element_by_id('linkset_hunting_policy')).select_by_visible_text(policy)
        Select(driver.find_element_by_name('linkset_subservice')).select_by_visible_text(subservice)
        driver.find_element_by_id('linkset_t35').clear()
        driver.find_element_by_id('linkset_t35').send_keys(t35)
        Select(driver.find_element_by_name('linkset_variant')).select_by_visible_text(variant)
        driver.find_element_by_id('linkset_opc').clear()
        driver.find_element_by_id('linkset_opc').send_keys(opc)
        driver.find_element_by_id('linkset_dpc').clear()
        driver.find_element_by_id('linkset_dpc').send_keys(dpc)

        default_btn = driver.find_element_by_id('linkset_default')
        if linkset_default:
            if not default_btn.is_selected():
                default_btn.click()
        else:
            if default_btn.is_selected():
                default_btn.click()

        driver.find_element_by_css_selector("input[type=\"submit\"]").click()
        try:
            driver.find_element_by_id("apply").click()
            return True
        except:
            return False

    def __edit_link(self, link_enable, linkset_name, channels, schannel, firstcic, echocancel, echocan_train, echocan_taps, link_sls, enable_sltm, port):
        driver = self.driver
        enable_btn = driver.find_element_by_id('link_enabled')
        if link_enable:
            if not enable_btn.is_selected():
                enable_btn.click()
        else:
            if enable_btn.is_selected():
                enable_btn.click()

        Select(driver.find_element_by_id('link_linkset')).select_by_visible_text(linkset_name)
        driver.find_element_by_id('link_channels').clear()
        driver.find_element_by_id('link_channels').send_keys(channels)
        driver.find_element_by_id('link_schannel').clear()
        driver.find_element_by_id('link_schannel').send_keys(schannel)
        driver.find_element_by_id('link_firstcic').clear()
        driver.find_element_by_id('link_firstcic').send_keys(firstcic)
        Select(driver.find_element_by_id('link_echocancel')).select_by_visible_text(echocancel)
        driver.find_element_by_id('link_echocan_train').clear()
        driver.find_element_by_id('link_echocan_train').send_keys(echocan_train)
        Select(driver.find_element_by_id('link_echocan_taps')).select_by_visible_text(echocan_taps)
        driver.find_element_by_id('link_sls').clear()
        driver.find_element_by_id('link_sls').send_keys(link_sls)

        sltm_btn = driver.find_element_by_id('link_sltm')
        if enable_sltm:
            if not sltm_btn.is_selected():
                sltm_btn.click()
        else:
            if sltm_btn.is_selected():
                sltm_btn.click()

        Select(driver.find_element_by_id('link_port')).select_by_visible_text(port)

        driver.find_element_by_css_selector("input[type=\"submit\"]").click()
        try:
            driver.find_element_by_id("apply").click()
            return True
        except:
            return False

    def modify_link(self, link_num, link_enable, linkset_name, channels, schannel, firstcic, echocancel, echocan_train, echocan_taps, link_sls, enable_sltm, port):
        driver = self.driver
        port_list = [-4, -3, -2, -1]
        driver.find_elements_by_css_selector("button[type=\"button\"]")[port_list[link_num]]
        self.__edit_link(link_enable, linkset_name, channels, schannel, firstcic, echocancel, echocan_train, echocan_taps, link_sls, enable_sltm, port)

    def add_new_link_set(self, linkset_name, linkset_enable, linkset_enable_st, linkset_use_connect, policy, subservice, t35, variant, opc, dpc, linkset_default):
        driver = self.driver
        driver.find_element_by_link_text('SS7').click()

        # 共 3 个类型为 submit 的 input，添加链路集、Backup、Restore
        driver.find_elements_by_css_selector("input[type=\"submit\"]")[0].click()
        return self.__edit_link_set(linkset_name, linkset_enable, linkset_enable_st, linkset_use_connect, policy, subservice, t35, variant, opc, dpc, linkset_default)

class sms_func:
    def __init__(self, driver):
        self.driver = driver
        driver.find_element_by_link_text('SMS').click()

    def sms2http_gw_config(self,
            hostname, port='80',
            php_file='receive_sms.php',
            phone_num='phone_num', from_port='port', message='message', receive_time='time', user_fefined=''):
        '''设置网关开启SMS2HTTP功能'''
        driver = self.driver
        driver.find_element_by_link_text('SMS Settings').click()
        sms_recv_enable = driver.find_element_by_id('smsprocess')
        if not sms_recv_enable.is_selected():
            sms_recv_enable.click()
        sms2http_enable = driver.find_element_by_id('sms_sw')
        if not sms2http_enable.is_selected():
            sms2http_enable.click()
        name_dict = {}
        name_dict['sms_url_host'] = hostname
        name_dict['sms_url_port'] = port
        name_dict['sms_url_path'] = php_file
        name_dict['sms_url_from_num'] = phone_num
        name_dict['sms_url_to_num'] = from_port
        name_dict['sms_url_message'] = message
        name_dict['sms_url_time'] = receive_time
        name_dict['sms_url_user_defined'] = user_fefined
        for key, value in name_dict.items():
            if value != '':
                driver.find_element_by_id(key).clear()
                driver.find_element_by_id(key).send_keys(value)
        driver.find_element_by_css_selector("input[type=\"submit\"]").click()
        try:
            driver.find_element_by_id('apply').click()
            return True
        except:
            return False

    def sms2http_recv_config(self, php_file='/var/www/html/receive_sms.php',
            sms_file='/var/www/html/message.txt',
            phone_num='phone_num',port='port',message='message',time='time',separator=';'):
        '''设置本机接收网关SMS2HTTP短信的PHP脚本
测试：http://HTTP服务器IP:80/receive_sms.php?phone_num=phonenumber&port=port&message=message&time=time'''
        php_context = '''<?php
@$phone_num = $_GET['%(phone_num)s'];
@$port = $_GET['%(port)s'];
@$message = $_GET['%(message)s'];
@$time = $_GET['%(time)s'];
$store_sms = $time."%(separator)s".$phone_num."%(separator)s".$port."%(separator)s".$message."\\n";
if(!empty($phone_num))
{
	$file_pointer = fopen("%(sms_file)s","a+");
	fwrite($file_pointer,$store_sms);
	fclose($file_pointer);
} 
?>
'''
        fp = file(php_file, 'wb')
        fp.write(php_context % dict(phone_num=phone_num,port=port,message=message,time=time,sms_file=sms_file,separator=separator))
        fp.close()
        local("chmod 777 %s" % php_file)
        local("rm -rf %s && touch %s && chmod 666 %s" % (sms_file, sms_file, sms_file))
        local("service httpd restart")

    def sms2http_read_sms(self, sms_file='/var/www/html/message.txt', separator=';'):
        '''读取SMS2HTTP功能存储在本地的短信'''
        pass

