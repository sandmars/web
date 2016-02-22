#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: analysis_mos.py

'''
Usage: python analysis_mos.py hostname port username password remote_share_dir local_ip local_mount_dir
Example: python analysis_mos.py 172.16.8.26 22 root 111111 /var/log/asterisk 172.16.8.182 /nfs_share
    说明：
        hostname、port、username、password、remote_share_dir 均为远端信息
        local_ip、local_mount_dir 均为本地信息
    1. 配置远端NFS开启对本地的权限
    2. 挂载远端目录
    3. 分析挂载的目录中的WAV文件PESQ
    4. 卸载远端目录
'''

from fabric.api import local
from python_lib import pylab_pesq,shell_func
import sys,ConfigParser

def __nfs_command(hostname, share_dir):
    hosts_allow = 'sed -i "/^rpcbind/d" /etc/hosts.allow && echo "rpcbind:%s" >> /etc/hosts.allow' % hostname
    hosts_deny = 'sed -i "/^rpcbind/d" /etc/hosts.deny && echo "rpcbind:ALL" >> /etc/hosts.deny'
    exports = 'echo "%s %s(rw,sync,all_squash,anonuid=0,anongid=0)" > /etc/exports && exportfs -r' % (share_dir, hostname)
    restart_service = 'service rpcbind restart && service nfs restart'

    return [hosts_allow, hosts_deny, exports, restart_service]

def _local_nfs():
    command_list = __nfs_command(hostname, share_dir)
    for i in range(len(command_list)):
        local(command_list[i])

def _remote_nfs(remote_ip, remote_port, remote_username, remote_password, remote_share_dir, share_ip):
    command_list = __nfs_command(share_ip, remote_share_dir)
    for i in range(len(command_list)):
        remote_shell = shell_func.remote_func(remote_ip, remote_port, remote_username, remote_password)
        retval = remote_shell.remote_exec(command_list[i])
        if retval != '':
            print retval

def audio_quality(audio_dir, audio_prefix, pic_dir):
    pesq_results = pylab_pesq.pylab_pesq()
    pesq_results.run_pesq(audio_dir, audio_prefix)
    #pesq_results.result(500, '%s/mos-%s' % (pic_dir, audio_prefix))

if __name__ == '__main__':
    remote_ip = sys.argv[1]
    remote_port = int(sys.argv[2])
    remote_username = sys.argv[3]
    remote_password = sys.argv[4]
    remote_share_dir = sys.argv[5]
    share_ip = sys.argv[6]
    local_mount_dir = sys.argv[7]

    _remote_nfs(remote_ip, remote_port, remote_username, remote_password, remote_share_dir, share_ip)

    local('mount -o nolock -t nfs %s:%s %s' % (remote_ip, remote_share_dir, local_mount_dir))

    #pesq_results = pylab_pesq.pylab_pesq()
    #pesq_results.run_pesq('/nfs_share', '10000')
    #pesq_results.result(500, '/tmp/mos-10000')
    #audio_quality('/nfs_share', '10000', '/tmp')
    #audio_quality('/nfs_share', '10030', '/tmp')
    #audio_quality('/nfs_share', '10060', '/tmp')
    #audio_quality('/nfs_share', '10090', '/tmp')

    audio_quality('/nfs', '10000', '/tmp')
    local('umount %s' % local_mount_dir)

