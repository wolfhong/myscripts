#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
使用:
    ./scan_ip_ports.py all
    ./scan_ip_ports.py 22,33,44 80 9090
    ./scan_ip_ports.py 22-100
输出: 扫描端口,输出该地址被占用的所有端口号
'''
# socket.connect_ex error code: https://gist.github.com/gabrielfalcao/4216897
from __future__ import unicode_literals
import re
import sys
import time
import socket
import traceback
from threading import Thread, Semaphore

socket.setdefaulttimeout(2)  # 设置默认超时时间
printLock = Semaphore(value=1)
OTHER_PORTS = {}
PY3 = sys.version_info[0] == 3


def _scan_one_port(ip, port):
    """ 输入IP和端口号，扫描判断端口是否占用 """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        result = s.connect_ex((ip, port))
        if result == 0:
            if PY3:
                s.send(b"helloworld\n")
            else:
                s.send("helloworld\n")
            r = repr(s.recv(100))
            printLock.acquire()
            print("%s: %s" % (str(port).ljust(5), r))
        else:
            printLock.acquire()  # 否则累计会出错
            OTHER_PORTS[result] = OTHER_PORTS.setdefault(result, 0) + 1
    except BaseException:
        e_text = 'Error: %s' % traceback.format_exc().splitlines()[-1]
        printLock.acquire()
        print("%s: %s" % (str(port).ljust(5), e_text))
    finally:
        printLock.release()
        s.close()


def _scan_range_ports(ip, port_list):
    t_list = []
    for port in port_list:
        t_list.append(Thread(target=_scan_one_port, args=(ip, port), ))
    for t in t_list:
        t.start()
    for t in t_list:
        t.join()


def calc_time(func):
    def _(*args, **kwargs):
        print('begin scan...')
        start_time = int(time.time())
        ret = func(*args, **kwargs)
        print('end scan, used %.2f seconds' % (int(time.time()) - start_time))
        return ret
    return _


@calc_time
def scan_selected_ports(ip, port_list):
    limit = 2000  # 假设的最大同时线程数
    page = 1
    page_ports = port_list[(page-1)*limit: page*limit]
    while page_ports:
        _scan_range_ports(ip, page_ports)
        page += 1
        page_ports = port_list[(page-1)*limit: page*limit]
    print('Other ports: %s' % OTHER_PORTS)


def main():
    ip = sys.argv[1]
    port_str = sys.argv[2]
    ip = socket.gethostbyname(ip)  # change to ip
    port_list = []
    if port_str == 'all':
        port_list = range(1, 65535 + 1)
    else:
        regular = re.compile(r'\d+(-\d+)?')
        for p in ','.join(sys.argv[2:]).split(','):
            match = regular.match(p)
            if not match:
                continue
            port_str = match.group()
            if port_str.find('-') > 0:
                start, end = port_str.split('-')
                start, end = int(start), int(end)
                port_list.extend(range(start, end + 1))
            else:
                port_list.append(int(port_str))
    if port_list:
        scan_selected_ports(ip, port_list)


if __name__ == '__main__':
    main()
