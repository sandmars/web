#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#http://www.bianceng.cn/Programming/extra/201307/36944.htm

import paramiko,subprocess

class remote_func:
    def __init__(self, hostname, port, username, password):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        # SSH log
        #paramiko.util.log_to_file('paramiko.log')

    def __del__(self):
        pass

    def remote_exec(self, command):
        ssh = paramiko.SSHClient()
        #ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 使用E1网关时报错
        ssh.connect(hostname=self.hostname, port=self.port, username=self.username, password=self.password)
        stdin, stdout, stderr = ssh.exec_command(command)
#        print stdout.readlines()
#        while True:
#            line = stdout.readline()
#            if len(line) == 0:
#                break
#            line = line.strip('\n')
#            print(line)
        output = stdout.read()
        ssh.close()
        print('[%s@%s:%s] run: %s' % (self.username, self.hostname, self.port, command))
        return output

    def download_file(self, remote_path, local_path):
        try:
            t = paramiko.Transport((self.hostname, self.port))
            t.connect(username = self.username, password = self.password)
            sftp = paramiko.SFTPClient.from_transport(t)
            sftp.get(remote_path, local_path)
            t.close()
        except Exception:
            print("Download file error!")
            #t.close()

    def upload_file(self, local_path, remote_path):
        try:
            t = paramiko.Transport((self.hostname, self.port))
            t.connect(username = self.username, password = self.password)
            sftp = paramiko.SFTPClient.from_transport(t)
            #sftp.put(os.path.join(local_dir, filename), os.path.join(remote_dir, filename))
            sftp.put(local_path, remote_path)
            t.close()
        except Exception:
            print("Upload file error!")
            t.close()

class local_func:
    def local_exec(self, command):
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        for line in p.stdout.readlines():
            print line,
        retval = p.wait()

if __name__ == '__main__':
    test = remote_func('172.16.8.24', 22, 'root', '111111')
    test.remote_exec('uname')
    test.remote_exec('ifconfig')
    #test.download_file('/etc/sysconfig/network-scripts/ifcfg-eth0', '/tmp/test1.txt')
    #test.upload_file('/etc/redhat-release', '/tmp/test2.txt')

