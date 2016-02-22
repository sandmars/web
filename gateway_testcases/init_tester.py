#!/usr/bin/env python
# -*- coding: utf-8 -*-
# fab -f init_test.py config_remote

from fabric.api import run,env,cd,put
from fabric.network import disconnect_all
import time, ConfigParser

config_file = 'config/call_cases.conf'
config = ConfigParser.ConfigParser()
config.read(config_file)
host_ip = config.get('ippbx_host', 'hostname')
port = config.get('ippbx_host', 'ssh_port')
username = config.get('ippbx_host', 'username')

env.hosts.append('%s@%s:%s' % (username, host_ip, port))
env.password = config.get('ippbx_host', 'password')

def __restart_service():
    run('service asterisk stop && service dahdi restart && asterisk')
    #run('/etc/init.d/asterisk stop && /etc/init.d/dahdi restart && asterisk')

def __remote_e1(signalling):
    #signalling = config.get('ippbx_host', 'signalling')

    dahdi_system = {
            'pri_net': 'config_file/system.conf.4e1.pri',
            'pri_cpe': 'config_file/system.conf.4e1.pri',
            'mfcr2': 'config_file/system.conf.4e1.r2',
            'ss7': 'config_file/system.conf.4e1.ss7',
            }
    with cd('/etc/dahdi'):
        put(dahdi_system.get(signalling), 'system.conf')

    with cd('/etc/asterisk'):
        run('sed -i "/#include chan_dahdi_r2.conf/d" chan_dahdi.conf')
        run("sed -i '/#include \"dahdi-channels.conf\"/d' chan_dahdi.conf")
        run('sed -i "/#include dahdi-channels.conf/d" chan_dahdi.conf')
        run('sed -i "/chan_ss7.so/d" modules.conf')

        if signalling == 'mfcr2':
            run('echo "#include chan_dahdi_r2.conf" >> chan_dahdi.conf')
            put('config_file/chan_dahdi_r2.conf', 'chan_dahdi_r2.conf')
        if signalling != 'ss7':
            run('echo "noload => chan_ss7.so" >> modules.conf')
            run('echo "#include dahdi-channels.conf" >> chan_dahdi.conf')
            run('sed -i "/^signalling/csignalling = %s" dahdi-channels.conf' % signalling)
        else:
            run('echo "load => chan_ss7.so" >> modules.conf')
            put('config_file/ss7.conf.4e1', 'ss7.conf')
            hostname = run('hostname', quiet=True)
            run('sed -i "s/localhost.localdomain/%s/g" ss7.conf' % hostname)

    __restart_service()

def __remote_ext(sip_file, iax_file, ext_file):
    with cd('/etc/asterisk'):
        if sip_file != '':
            run('sed -i "/#include `basename %s`/d" sip.conf' % sip_file)
            run('echo "#include `basename %s`" >> sip.conf' % sip_file)
            put(sip_file, sip_file.split('/')[1])
            run('asterisk -rx "sip reload"')
        if iax_file != '':
            run('sed -i "/#include `basename %s`/d" iax.conf' % iax_file)
            run('echo "#include `basename %s`" >> iax.conf' % iax_file)
            put(iax_file, iax_file.split('/')[1])
            run('asterisk -rx "iax2 reload"')
        if ext_file != '':
            run('sed -i "/#include `basename %s`/d" extensions.conf' % ext_file)
            run('echo "#include `basename %s`" >> extensions.conf' % ext_file)
            put(ext_file, ext_file.split('/')[1])
            run('asterisk -rx "dialplan reload"')
        #disconnect_all()

def __remote_cdr():
    with cd('/etc/asterisk'):
        run("echo -e '[general]\nenable=yes\nunanswered=yes\n[csv]\nusegmtime=no\nloguniqueid=no\nloguserfield=yes' > cdr.conf")
        run('''echo -e '[mappings]\ncall_statistics.csv => "${CDR(accountcode)}","${CDR(clid)}","${CDR(dst)}","${CDR(channel)}","${CDR(dstchannel)}","${CDR(start)}","${CDR(answer)}","${CDR(end)}","${CDR(duration)}","${CDR(billsec)}","${CDR(disposition)}"' > cdr_custom.conf''')
        run('asterisk -rx "core reload"')

def test_pri_callid():
    '''号码变换测试：测试机配置'''
    __remote_e1('pri_net')
    time.sleep(5)
    __remote_ext('config_file/sip_callid.conf', '', 'config_file/extensions_testcases.conf')

def test_pri_forwardnumber():
    '''PRI Forwardnumber 测试：测试机配置'''
    test_pri_callid()

def test_pri_failover():
    '''Failover测试：测试机配置'''
    __remote_e1('pri_net')
    time.sleep(5)
    __remote_ext('config_file/sip_failover.conf', 'config_file/iax_failover.conf', 'config_file/extensions_testcases.conf')
    config_file = 'config/call_cases.conf'
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    hostname = config.get('gateway', 'hostname')
    run('sed -i "s/gw_ip_add/%s/g" /etc/asterisk/sip_failover.conf' % hostname)
    run('sed -i "s/gw_ip_add/%s/g" /etc/asterisk/iax_failover.conf' % hostname)
    run('asterisk -rx "sip reload"')
    run('asterisk -rx "iax2 reload"')

def test_echocancel():
    __remote_ext('config_file/sip_echocancel.conf', '', 'config_file/extensions_testcases.conf')
    config_file = 'config/call_cases.conf'
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    hostname = config.get('gateway', 'hostname')
    run('sed -i "s/gw_ip_add/%s/g" /etc/asterisk/sip_echocancel.conf' % hostname)
    run('asterisk -rx "sip reload"')

def test_simultaneous_pri():
    '''PRI群呼编码测试：测试机配置'''
    __remote_e1('pri_net')
    time.sleep(5)
    sip_file = 'config_file/sip_simultaneous.conf'
    __remote_ext(sip_file, '', 'config_file/extensions_testcases.conf')
    run('sed -i "s/gw_ip_addr/%s/g" /etc/asterisk/`basename %s`' % (config.get('gateway', 'hostname'), sip_file))
    run('sed -i "s/codec/%s/g" /etc/asterisk/`basename %s`' % (config.get('ippbx_host', 'codec'), sip_file))
    run('asterisk -rx "sip reload"')

def test_simultaneous_mfcr2():
    '''MFCR2群呼编码测试：测试机配置'''
    __remote_e1('mfcr2')
    time.sleep(5)
    sip_file = 'config_file/sip_simultaneous.conf'
    __remote_ext(sip_file, '', 'config_file/extensions_testcases.conf')
    run('sed -i "s/gw_ip_addr/%s/g" /etc/asterisk/`basename %s`' % (config.get('gateway', 'hostname'), sip_file))
    run('sed -i "s/codec/%s/g" /etc/asterisk/`basename %s`' % (config.get('ippbx_host', 'codec'), sip_file))
    run('asterisk -rx "sip reload"')

def test():
    __remote_cdr()

