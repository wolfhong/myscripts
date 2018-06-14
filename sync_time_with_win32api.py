# -*- coding: utf-8 -*-
'''
修改win电脑的系统时间

requirements:
    pip install pypiwin32
'''

import sys
import socket
import struct
import time
import win32api

PY3 = sys.version_info[0] == 3

TimeServer = 'cn.pool.ntp.org'
Port = 123

def getTime():
    TIME_1970 = 2208988800
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if PY3:
        data = b'\x1b' + 47 * b'\0'
    else:
        data = '\x1b' + 47 * '\0'
    client.sendto(data, (TimeServer, Port))
    data, address = client.recvfrom(1024)
    data_result = struct.unpack('!12I', data)[10]
    data_result -= TIME_1970
    return data_result

def setSystemTime():
    tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec, tm_wday, tm_yday, tm_isdst = time.gmtime(getTime())
    win32api.SetSystemTime(tm_year, tm_mon, tm_wday, tm_mday, tm_hour, tm_min, tm_sec, 0)
    print("Set System OK!")
  
if __name__ == '__main__':
    setSystemTime()
    print("%d-%d-%d %d:%d:%d" % time.localtime(getTime())[:6])
