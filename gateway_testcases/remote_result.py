#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: remote_result.py
#   Usage: python remote_result.py get|clean
#       get: Get remote file (/var/log/asterisk/results.txt) to ./results.txt
#       clean: clean up remote file (/var/log/asterisk/results.txt)

from python_lib import shell_func
import ConfigParser,sys

if __name__ == '__main__':
    config = ConfigParser.ConfigParser()
    config.read(sys.argv[1])
    remote_ip = config.get('ippbx', 'hostname')
    remote_port = int(config.get('ippbx', 'port'))
    remote_username = config.get('ippbx', 'username')
    remote_password = config.get('ippbx', 'password')
    remote_file = config.get('ippbx', 'result_file')

    remote_shell = shell_func.remote_func(remote_ip, remote_port, remote_username, remote_password)
    if sys.argv[2] == 'get':
        retval = remote_shell.download_file(remote_file, remote_file.split('/').pop())
    elif sys.argv[2] == 'clean':
        remote_shell.remote_exec('cat /dev/null > %s' % remote_file)
    else:
        pass

