#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: 邹华龙

import datetime,ConfigParser,os
from fabric.api import local

class general_sipp_scenario:
    '''生成 SIPp 场景文件的类'''
    def __init__(self, caller_id_name='[field0]',caller_id_num='[field1]',
            auth_sec = '[field2]',callee_id_num='[field3]'):
        '''四个参数分别对应 SIPp 用户配置文件中的域
        field0;field1;field2;field3 -> caller_id_name;caller_id_num;auth_sec;callee_id_num'''
        self.caller_id_name = caller_id_name
        self.caller_id_num = caller_id_num
        self.auth_sec = auth_sec
        self.callee_id_num = callee_id_num

    def __make_uac_sdp_body(self, codec):
        '''生成 INVITE 的 SDP 部分
        参数：
            codec：支持 alaw/ulaw/g729/g723/g726
        返回值：返回包含 SDP 数据的字符串'''
        if codec == 'alaw':
            payload_type = 8
            encoding_name = 'PCMA'
        elif codec == 'ulaw':
            payload_type = 0
            encoding_name = 'PCMU'
        elif codec == 'g729':
            payload_type = 18
            encoding_name = 'G729'
        elif codec == 'g723':
            payload_type = 4
            encoding_name = 'G723'
        elif codec == 'g726':
            payload_type = 2
            encoding_name = 'G726'
        
        body = 'v=0\n'
        body += 'o=%s [pid][call_number] 8[pid][call_number]8 IN IP[local_ip_type] [local_ip]\n' % \
                self.caller_id_num
        body += 's=SIPp Media\n'
        body += 'i=Media Data\n'
        body += 'c=IN IP[media_ip_type] [media_ip]\n'
        body += 't=0 0\n'
        body += 'm=audio [media_port] RTP/AVP %s 101\n' % payload_type
        body += 'a=rtpmap:%s %s/8000\n' % (payload_type, encoding_name)
        body += 'a=rtpmap:101 telephone-event/8000\n'
        # fmtp: INVITE 0-15, 200OK 0-16
        body += 'a=fmtp:101 0-15,16\n'
        # ptime: ulaw/alaw/g729 20, g723 30
        #body += 'a=ptime:20\n'
        body += 'a=sendrecv\n'
        return body

    def __sipp_pause(self, audio_file):
        '''SIPp 的呼叫暂停部分：
            注册与注销的暂停部分（不带语音流）
            INVITE 建立通话后的语音传输部分
        参数：
            audio_file：携带的语音流文件名
        返回值：返回暂停部分的字符串'''
        if audio_file != '':
            action = '<nop><action><exec play_pcap_audio="%s"/></action></nop>\n' % audio_file
            action += '<pause/>\n'
        else:
            action = '<pause/>\n'
        return action
    
    def __uac_send_request(self, method, auth, **kwargs):
        '''UAC 发送的 SIP 请求部分
        参数：
            method：SIP 方法，UNREGISTER 表示注销
            auth：SIP 请求是否携带验证
            **kwargs：其他参数，支持 retrans、start_rtd、rtd、Expires、SDP
        返回值：返回 UAC SIP 请求字符串'''
        caller_id_name = self.caller_id_name
        caller_id_num = self.caller_id_num
        auth_sec = self.auth_sec
        callee_id_num = self.callee_id_num

        request = '<send'
        if 'retrans' in kwargs:
            request += ' retrans="%s"' % kwargs['retrans']
        if 'start_rtd' in kwargs:
            request += ' start_rtd="%s"' % kwargs['start_rtd']
        elif 'rtd' in kwargs:
            request += ' rtd="%s"' % kwargs['rtd']
        request += '>\n'
        request += '<![CDATA[\n'
        
        if method == 'REGISTER':
            request += '%s sip:[remote_ip]:[remote_port] SIP/2.0\n' % method
        else:
            request += '%s sip:%s@[remote_ip]:[remote_port] SIP/2.0\n' % \
                    (method, callee_id_num)
        
        request += 'Via: SIP/2.0/[transport] [local_ip]:[local_port];branch=[branch]\n'
        request += 'Max-Forwards: 70\n'
        request += 'Contact: <sip:%s@[local_ip]:[local_port];transport=[transport]>\n' % caller_id_num
        request += 'To: %s<sip:%s@[remote_ip]:[remote_port]>' % \
                ('REGISTER' in method and ('"'+caller_id_name+'"') or '', \
                caller_id_num)
        if method == 'ACK' or method == 'BYE':
            request += '[peer_tag_param]'
        request += '\n'
        
        request += 'From: "%s"<sip:%s@[remote_ip]:[remote_port]>;tag=[pid]SIPpTag%s[call_number]\n' % \
                (caller_id_name, caller_id_num, \
                ('REGISTER' in method and 'Register' or 'Invite'))
        request += 'Call-ID: [call_id]\n'
        request += 'CSeq: [cseq] %s\n' % ('REGISTER' in method and 'REGISTER' or method)
        
        if 'Expires' in kwargs:
            request += 'Expires: %s\n' % kwargs['Expires']
        
        if method == 'INVITE':
            request += 'Content-Type: application/sdp\n'
        request += 'User-Agent: SIPp\n'
        request += 'Subject: Call Performance Test made by ZouHualong\n'
        
        if auth:
            request += '%s\n' % auth_sec
        
        request += 'Content-Length: %s\n' % (method == 'INVITE' and '[len]' or '0')
        if 'SDP' in kwargs:
            request += kwargs['SDP']
        request += ']]>\n'
        request += '</send>\n'
        return request

    def __uac_recv_request(self, method):
        '''UAC 接收请求：尚未测试'''
        return '<recv request="%s"></recv>\n' % method

    def __uac_send_status(self, method, **kwargs):
        '''UAC 发送响应：尚未测试'''
        status_list = {
                '100': '100 Trying',
                '180': '180 Ringing',
                '183': '183 Session Progress',
                '200': '200 OK',
                }
        status = '<send>\n<![CDATA[\nSIP/2.0 %s\n' % status_list[method]
        status += '[last_Via:]\n[last_From:]\n[last_To:]\n[last_Call-ID:]\n[last_CSeq:]\n'
        status += 'Server: SIPp\n'
        status += 'Contact: <sip:[local_ip]:[local_port];transport=[transport]>\n'
        if 'SDP' in kwargs:
            status += 'Content-Length: [len]\n'
        else:
            status += 'Content-Length: 0\n'
        if 'SDP' in kwargs:
            status += kwargs['SDP']
        status += ']]>\n</send>\n'

        return status

    def __uac_recv_status(self, method, **kwargs):
        '''UAC 接收响应
        参数：
            method：SIP 方法，如 401/200
            auth：增加 auth="true"
            optional：是否可选
            crlf_sec：统计界面增加换行
        返回值：返回 UAC 接收响应的字符串'''
        status = '<recv response="%s"' % method
        if 'auth' in kwargs:
            if kwargs['auth']:
                status += ' auth="true"'
        if 'optional' in kwargs:
            if kwargs['optional']:
                status += ' optional="true"'
        if 'crlf' in kwargs:
            if kwargs['crlf']:
                status += ' crlf="true"'
        if 'start_rtd' in kwargs:
            status += ' start_rtd="%s"' % kwargs['start_rtd']
        elif 'rtd' in kwargs:
            status += ' rtd="%s"' % kwargs['rtd']
        status += '></recv>\n'
        return status

    def _make_scenario_start_end(self, inter_time):
        '''SIPp 场景起始、结束部分
        参数：
            inter_time：每轮呼叫的时间间隔
        返回值：返回元组(起始部分,结束部分)'''
        start = '<?xml version="1.0" encoding="ISO-8859-1" ?>\n'
        start += '<!DOCTYPE scenario SYSTEM "sipp.dtd">\n'
        start += '<scenario name="SIPp scenario">\n'

        end = '<timewait milliseconds="%s"/>\n' % inter_time
        end += '<ResponseTimeRepartition value="10, 20, 30, 40, 50, 100, 150, 200"/>\n'
        end += '<CallLengthRepartition value="10, 50, 100, 500, 1000, 5000, 10000"/>\n'
        end += '</scenario>\n'
        
        return(start, end)

    def _make_register_sec(self):
        '''SIPp 场景：注册、注销部分
        返回值：返回元组(注册部分,注销部分)'''
        register_sec = self.__uac_send_request('REGISTER', False, Expires=3600, retrans=500, start_rtd='register')
        register_sec += self.__uac_recv_status('401', auth=True, rtd='register')
        register_sec += self.__uac_send_request('REGISTER', True, Expires=3600, retrans=500)
        register_sec += self.__uac_recv_status('200', crlf=True)

        unregister_sec = self.__uac_send_request('REGISTER', True, Expires=0, retrans=500, start_rtd='unregister')
        unregister_sec += self.__uac_recv_status('401', auth=True, rtd='unregister')
        unregister_sec += self.__uac_send_request('REGISTER', True, Expires=0, retrans=500)
        unregister_sec += self.__uac_recv_status('200', crlf=True)

        return(register_sec, unregister_sec)

    def _make_call_sec(self, insecure_invite, codec, audio_file):
        '''SIPp 呼叫场景部分
        参数：
            insecure_invite：是否验证 INVITE 消息
            codec：INVITE 携带的语音编码信息
            audio_file：通话建立后使用的语音流
        返回值：呼叫场景字符串'''
        call_sec = self.__uac_send_request('INVITE', False, retrans=500, \
                start_rtd='invite', SDP=self.__make_uac_sdp_body(codec))
        if insecure_invite:
            call_sec += self.__uac_recv_status('100', optional=True, rtd='invite')
            call_sec += self.__uac_recv_status('180', optional=True, rtd='invite')
            call_sec += self.__uac_recv_status('183', optional=True, rtd='invite')
            call_sec += self.__uac_recv_status('200', rtd='invite')
            call_sec += self.__uac_send_request('ACK', False)
            call_sec += self.__sipp_pause(audio_file)
            call_sec += self.__uac_send_request('BYE', False, retrans=500, start_rtd='bye')
            call_sec += self.__uac_recv_status('200', crlf=True, rtd='bye')
        else:
            call_sec += self.__uac_recv_status('401', auth=True, rtd='invite')
            call_sec += self.__uac_send_request('ACK', False)
            call_sec += self.__uac_send_request('INVITE', True, retrans=500, \
                    start_rtd='reinvite', SDP=self.__make_uac_sdp_body(codec))
            call_sec += self.__uac_recv_status('100', optional=True, rtd='reinvite')
            call_sec += self.__uac_recv_status('180', optional=True, rtd='reinvite')
            call_sec += self.__uac_recv_status('183', optional=True, rtd='reinvite')
            call_sec += self.__uac_recv_status('200', rtd='reinvite')
            call_sec += self.__uac_send_request('ACK', True)
            call_sec += self.__sipp_pause(audio_file)
            call_sec += self.__uac_send_request('BYE', True, retrans=500, start_rtd='bye')
            call_sec += self.__uac_recv_status('200', crlf=True, rtd='bye')
        return call_sec

    def reg_unreg(self, inter_time):
        '''SIPp 注册注销场景
        参数：
            inter_time：每轮测试的时间间隔
        返回值：返回场景字符串'''
        scenario,end = self._make_scenario_start_end(inter_time)
        register_sec,unregister_sec = self._make_register_sec()
        scenario += register_sec
        scenario += self.__sipp_pause('')
        scenario += unregister_sec
        scenario += end
        return scenario

    def reg_call_unreg(self, inter_time, codec, audio_file, insecure_invite):
        '''SIPp 注册呼叫注销场景
        参数：
            inter_time：每轮测试的时间间隔
            codec：使用的语音编码
            audio_file：通话建立后使用的语音流
            insecure_invite：是否验证 INVITE 消息
        返回值：返回场景字符串'''
        scenario,end = self._make_scenario_start_end(inter_time)
        register_sec,unregister_sec = self._make_register_sec()
        scenario += register_sec
        scenario += self._make_call_sec(insecure_invite, codec, audio_file)
        scenario += unregister_sec
        scenario += end
        return scenario
    
    def call(self, inter_time, codec, audio_file, insecure_invite):
        '''SIPp 呼叫场景
        参数：
            inter_time：每轮测试的时间间隔
            codec：使用的语音编码
            audio_file：通话建立后使用的语音流
            insecure_invite：是否验证 INVITE 消息
            返回值：返回场景字符串'''
        scenario,end = self._make_scenario_start_end(inter_time)
        scenario += self._make_call_sec(insecure_invite, codec, audio_file)
        scenario += end
        return scenario

    def out_of_call(self, inter_time):
        '''其他消息的处理场景：Out-of-call UAS'''
        scenario,end = self._make_scenario_start_end(inter_time)
        scenario += '<recv request=".*" regexp_match="true"></recv>\n'
        scenario += self.__uac_send_status('200')
        scenario += end
        return scenario

    def scenario(self, filename, test_type, inter_time, **kwargs):
        fp = open(filename, 'wb')
        scenario_list = {
                'register': self.reg_unreg(inter_time),
                'out_of_call': self.out_of_call(inter_time),
                }
        if test_type == 'call' or test_type == 'register_call':
            if 'codec' not in kwargs or 'audio_file' not in kwargs or 'insecure_invite' not in kwargs:
                print('Use call or reg_call_unreg scenario, you must use codec&audio_file&insecure_invite parameters!')
                return False
            else:
                scenario_list['call'] = self.call(inter_time, kwargs['codec'], kwargs['audio_file'], kwargs['insecure_invite'])
                scenario_list['register_call'] = self.reg_call_unreg(inter_time, kwargs['codec'], kwargs['audio_file'], kwargs['insecure_invite'])
        fp.write(scenario_list[test_type])
        fp.close()

class sipp_func:
    def __init__(self, config_file, case_name):
        '''SIPp 测试类：生成测试场景，测试呼叫
            sipp = sipp_func('call_cases.conf', 'sipp')
            sipp.test()
        参数：
            config_file：配置文件，由多个 section 组成，一个 section 代表一个测试配置
                [section]
                parameter = value
            case_name：配置文件中的 section
                [case_name]
                local_ip = 本地地址
                remote_ip = 呼叫地址
                remote_port = 呼叫端口
                test_type = 测试类型
                insecure_invite = 是否验证 INVITE
                codec = 音频编码
                duration = 通话时长（ms）
                inter_time = 呼叫间隔时间（ms）
                max_call = 总呼叫数
                simultaneous = 并发呼叫数
                rate = 呼叫速率
                rate_period = 呼叫周期
                csv_file = 用户配置文件，参见 general_sipp_scenario 类说明'''
        '''初始化
        参数：
            config_file：配置文件
            case_name：配置文件中的 section'''
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_file)
        self.case_name = case_name
        self.pid = os.getpid()

    def __general_sipp_cmd(self, sip_xml_file, sip_csv_file, out_of_call_file):
        '''生成 SIPp 命令参数
        参数：
            sip_xml_file：SIPp 场景文件
            sip_csv_file：SIPp 用户配置文件
            out_of_call_file：out of call
        返回值：SIPp 参数字符串'''
        config = self.config
        case_name = self.case_name

        local_ip = config.get(case_name, 'local_ip')
        remote_ip = config.get(case_name, 'remote_ip')
        remote_port = config.get(case_name, 'remote_port')

        duration = config.get(case_name, 'duration')
        max_call = config.get(case_name, 'max_call')
        simultaneous = config.get(case_name, 'simultaneous')
        rate = config.get(case_name, 'rate')
        rate_period = config.get(case_name, 'rate_period')
        
        sipp_cmd = '/usr/local/bin/sipp -i %s %s:%s' % (local_ip, remote_ip, remote_port)
        sipp_cmd += ' -sf %s -inf %s' % (sip_xml_file, sip_csv_file)
        if duration != '':
            sipp_cmd += ' -d %s' % duration
        if max_call != '':
            sipp_cmd += ' -m %s' % max_call
        if simultaneous != '':
            sipp_cmd += ' -l %s' % simultaneous
        if rate != '' and rate_period != '':
            sipp_cmd += ' -r %s -rp %s' % (rate, rate_period)
        if out_of_call_file != '':
            sipp_cmd += ' -oocsf %s' % out_of_call_file

        pid = self.pid
        # SIPp 日志
        #sipp_cmd += ' -trace_stat -stf tmp/sipp-statistics-%s.csv -fd 30 -periodic_rtd' % pid
        sipp_cmd += ' -trace_stat -stf tmp/sipp-statistics-%s.csv' % pid
        sipp_cmd += ' -trace_rtt'# rtt_freq 3'
        sipp_cmd += ' -trace_screen'
        sipp_cmd += ' -trace_err -error_file tmp/sipp-error-%s.log' % pid
        sipp_cmd += ' -trace_error_codes'
        #sipp_cmd += ' -trace_msg -message_file tmp/sipp-message-%s.log -message_overwrite True' % pid
        #sipp_cmd += ' -trace_shortmsg -shortmessage_file tmp/sipp-shortmsg-%s.log -shortmessage_overwrite True' % pid
        #sipp_cmd += ' -trace_counts'
        #sipp_cmd += ' -trace_calldebug'
        #sipp_cmd += ' -trace_logs'
        
        return sipp_cmd

    def __run_sipp(self, sip_xml_file, sip_csv_file, out_of_call_file, **kwargs):
        '''执行 SIPp 测试
        参数：
            sip_xml_file：SIPp 场景文件
            sip_csv_file：SIPp 用户配置文件
            out_of_call_file：out of call
            kwargs：支持 codec'''
        sipp_cmd = self.__general_sipp_cmd(sip_xml_file, sip_csv_file, out_of_call_file)
        clean_cmd = 'rm -rf %s %s %s ' % (sip_xml_file, out_of_call_file, sip_csv_file)
        if 'codec' in kwargs:
            if kwargs['audio_file'] != '':
                src_audio = 'pcap/demo-instruct.%s.pcap' % kwargs['codec']
                audio_link = kwargs['audio_file'].split('/')[1]
                local('cd tmp && rm -rf %s && ln -s ../%s %s && cd ..' % (audio_link, src_audio, audio_link))
                clean_cmd += kwargs['audio_file']
        local('cp %s %s' % (self.config.get(self.case_name, 'csv_file'), sip_csv_file))
        local(sipp_cmd)
        local(clean_cmd)

    def test(self):
        '''测试：生成测试场景并执行测试
        参数：
            test_type：测试类型，有 register、register_call、call
            insecure_invite：取值分 True（不验证 INVITE）、False（验证 INVITE）
            codec：选用的编码信息
            inter_time：每轮测试之间的时间间隔
'''
        config = self.config
        case_name = self.case_name
        pid = self.pid

        test_type = config.get(case_name, 'test_type')
        inter_time = config.get(case_name, 'inter_time')

        sip_xml_file = 'tmp/sipp-%s.xml' % pid
        sip_csv_file = 'tmp/sipp-%s.csv' % pid
        out_of_call_file = 'tmp/ooc-%s.xml' % pid

        sipp = general_sipp_scenario()
        sipp.scenario(out_of_call_file, 'out_of_call', 400)
        if test_type == 'register':
            sipp.scenario(sip_xml_file, test_type, inter_time)
            self.__run_sipp(sip_xml_file, sip_csv_file, out_of_call_file)
        else:
            insecure_invite = config.get(case_name, 'insecure_invite')
            if insecure_invite == 'True' or insecure_invite == 'true':
                insecure_invite = True
            elif insecure_invite == 'False' or insecure_invite == 'false':
                insecure_invite = False
            else:
                print('insecure_invite: invalid value!')
                return False
            codec = config.get(case_name, 'codec')
            if config.has_option(case_name, 'audio'):
                audio = config.get(case_name, 'audio')
                if audio == 'True' or audio == 'true':
                    audio_file = 'tmp/sipp-%s-%s.pcap' % (codec, pid)
                else:
                    audio_file = ''
            else:
                audio_file = ''
            sipp.scenario(sip_xml_file, test_type, inter_time, codec=codec, audio_file=audio_file, insecure_invite=insecure_invite)
            self.__run_sipp(sip_xml_file, sip_csv_file, out_of_call_file, codec=codec, audio_file=audio_file)

if __name__ == '__main__':
    '''示例用法：
    1、使用 sipp_func 类
    2、执行类方法 test
'''
    sipp = sipp_func('config/call_cases.conf', 'test')
    sipp.test()

