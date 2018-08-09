#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
参数: ip/hostname
输出: 扫描端口,输出该地址被占用的所有端口号
'''
# socket.connect_ex error code: https://gist.github.com/gabrielfalcao/4216897
from __future__ import unicode_literals
import sys
import time
import socket
from threading import Thread

socket.setdefaulttimeout(2)  # 设置默认超时时间
OK_PORTS = {}
ERROR_PORTS = {}
OTHER_PORTS = {}
R_OK = 1
R_ERROR = -1


def scan_port(ip, port):
    """ 输入IP和端口号，扫描判断端口是否占用 """
    assert port < 65535
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        result = s.connect_ex((ip, port))
        if result == 0:
            OK_PORTS[port] = R_OK
        else:
            OTHER_PORTS[result] = OTHER_PORTS.setdefault(result, 0) + 1
    except BaseException:
        ERROR_PORTS[port] = R_ERROR
    finally:
        s.close()


def scan_range_ports(ip, start, end):
    OK_PORTS.clear()
    t_list = []
    for port in range(start, end):
        t_list.append(Thread(target=scan_port, args=(ip, port), ))
    for t in t_list:
        t.start()
    for t in t_list:
        t.join()
    # output
    for port in sorted(OK_PORTS.keys()):
        print(port)


def ip_scan(ip):
    """ 输入IP，扫描IP端口情况 """
    print('begin scan...')
    start_time = int(time.time())
    # scan begin
    page = 1
    limit = 2000  # 假设的最大同时线程数
    while True:
        start = max(1, limit * (page-1))
        end = min(limit * page, 65535)
        scan_range_ports(ip, start, end)
        if end >= 65535:
            break
        else:
            page += 1
    print('end scan, used %.2f seconds' % (int(time.time()) - start_time))
    print('Error ports: %s' % ERROR_PORTS.keys())
    print('Other ports: %s' % OTHER_PORTS)


if __name__ == '__main__':
    _ip = sys.argv[1]
    _ip = socket.gethostbyname(_ip)  # change to ip
    ip_scan(_ip)
