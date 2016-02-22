#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''配置网关环境：DAHDI、SIP/IAX2、ROUTE'''

from selenium import webdriver
from python_lib import gateway_func
import ConfigParser,sys,time,codecs

def __config_dgw_endpoint_route(config_file, section):
    config = ConfigParser.ConfigParser()
    # 读取中文参数
    with codecs.open(config_file, encoding='utf-8-sig') as f:
        config.readfp(f)
    #python3: config.read(config_file, encoding='utf-8-sig')
    
    hostname = config.get('gateway', 'hostname')
    port = config.getint('gateway', 'web_port')
    username = config.get('gateway', 'web_username')
    password = config.get('gateway', 'web_password')
    baseurl = 'http://%s:%s@%s:%s' % (username, password, hostname, port)
    #baseurl = 'http://admin:admin@demo.openvox.cn:65325'
    
    driver = webdriver.Firefox()
    driver.set_window_size(1024, 768)
    driver.implicitly_wait(5)
    driver.get(baseurl)

    # 读取配置文件中的dahdi，针对E1网关配置
    if config.has_option(section, 'dahdi'):
        dahdi = gateway_func.dahdi(driver)
        args = config.get(section, 'dahdi').split(';')
        dahdi.general(*args)
        time.sleep(10)

    #if config.has_option(section, 'groups') or config.has_option(section, 'gw_route') or config.has_option(section, 'gw_route_exchange' or ):
        #gw_type = config.get(section, 'gw_type')
    gw_type = config.get(section, 'gw_type')

    # 删除所有的SIP、IAX
    if config.has_option(section, 'gw_sip') or config.has_option(section, 'gw_iax'):
        endpoint = gateway_func.endpoint_func(driver, gw_type)
        endpoint.delete_all_endpoints()

    # 读取配置文件中的gw_sip，配置网关SIP
    if config.has_option(section, 'gw_sip'):
        sip = gateway_func.endpoint_func(driver, gw_type)
        for gw_sip in config.get(section, 'gw_sip').split(';'):
            args = config.get(section, gw_sip).split(';')
            # 删除同名的endpoint
            #sip.delete_same_sip(args[1])
            sip.add_sip_endpoint(*args)

    if config.has_option(section, 'gw_iax'):
        iax = gateway_func.endpoint_func(driver, gw_type)
        for gw_iax in config.get(section, 'gw_iax').split(';'):
            args = config.get(section, gw_iax).split(';')
            # 删除同名的endpoint
            #iax.delete_same_iax(args[1])
            iax.add_iax_endpoint(*args)

    if config.has_option(section, 'groups'):
        group = gateway_func.route_func(driver, gw_type)
        #删除所有的group
        #group.delete_all_groups()
        for groups in config.get(section, 'groups').split(';'):
            args = config.get(section, groups).split(';')
            # 删除同名的group
            #group.delete_same_group(args[0])
            group.add_group(*args)

    if config.has_option(section, 'gw_route'):
        route = gateway_func.route_func(driver, gw_type)
        # 删除所有的路由
        route.delete_all_routes()
        for gw_route in config.get(section, 'gw_route').split(';'):
            args = config.get(section, gw_route).split(';')
            manipulation = args.pop()
            if manipulation != '':
                manipulation_sec = config.get(section, manipulation).split(';')
                count = 0
                manipulation_args = ''
                for sec in manipulation_sec:
                    manipulation_args += config.get(section, sec)
                    if count != (len(manipulation_sec) - 1):
                        manipulation_args += ':'
                    count += 1
                args.append(manipulation_args)
            else:
                args.append('')
            # 删除同名的route
            #route.delete_same_route(args[0])
            route.add_routing_rule(*args)

    if config.has_option(section, 'gw_route_exchange'):
        route = gateway_func.route_func(driver, gw_type)
        for route_pair in config.get(section, 'gw_route_exchange').split(';'):
            pair = config.get(section, route_pair).split(';')
            route.exchange_routes(*pair)
    
    driver.quit()

__config_dgw_endpoint_route(sys.argv[1], sys.argv[2])

