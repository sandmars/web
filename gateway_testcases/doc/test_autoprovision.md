### 测试配置
#### 测试机
配置存放位置：/var/www/html

tftp: 
```shell
[root@localhost ~]# yum install tftp tftp-server

[root@localhost ~]# cat /etc/xinetd.d/tftp
service tftp
{
        socket_type     = dgram
        protocol        = udp
        wait            = yes
        user            = root
        server          = /usr/sbin/in.tftpd
        server_args     = -s /var/www/html -c
        disable         = no
        per_source      = 11
        cps             = 100 2
        flags           = IPv4
}

[root@localhost ~]# chmod -R 777 /var/lib/tftpboot
[root@localhost ~]# /etc/init.d/xinetd reload
[root@localhost ~]# /etc/init.d/xinetd restart
```

FTP:
```
[root@localhost ~]# yum install vsftpd

[root@localhost ~]# /etc/init.d/iptables stop
[root@localhost ~]# cat /etc/selinux/config | grep '^[^#]'
SELINUX=disabled
[root@localhost ~]# cat /etc/vsftpd/ftpusers 
#root
[root@localhost ~]# cat /etc/vsftpd/user_list 
#root
[root@localhost ~]# cat /etc/vsftpd/vsftpd.conf | grep '^[^#]'
anonymous_enable=YES
local_enable=YES
write_enable=YES
local_umask=022
dirmessage_enable=YES
xferlog_enable=YES
connect_from_port_20=YES
xferlog_std_format=YES
listen=YES
local_root=/var/www/html
pam_service_name=vsftpd
userlist_enable=YES
tcp_wrappers=YES

[root@localhost ~]# chmod -R 777 /var/lib/tftpboot
[root@localhost ~]# /etc/init.d/vsftpd restart
```

HTTP:
```shell
[root@localhost ~]# yum install httpd
[root@localhost ~]# /etc/init.d/httpd start
```

