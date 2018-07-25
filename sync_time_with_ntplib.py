# -*- coding: utf-8 -*-
'''
通过 ntplib 修改系统时间
1. 如果不带上参数, 进行ntpdate时间同步
2. 如果参数格式为 "年-月-日 时:分:秒", 设置为对应时间
3. 如果参数格式为时间戳, 设置为对应时间
本脚本需要管理员权限或者sudo权限才可执行
本脚本适用于各种操作系统

requirements:
    pip install ntplib

NTP服务器在中国推荐如下:
3.cn.pool.ntp.org
2.cn.pool.ntp.org
1.cn.pool.ntp.org
cn.pool.ntp.org

'''

import sys
import os
import time
from datetime import datetime

NTP_SERVER = 'cn.pool.ntp.org'

def get_local_dt_from_ntp():
    import ntplib
    c = ntplib.NTPClient()
    response = c.request(NTP_SERVER)
    ts = response.tx_time
    dt_obj = time.localtime(ts)
    return dt_obj


def set_local_dt(dt_obj, use_ntp=False):
    date_str = time.strftime('%Y-%m-%d', dt_obj)
    time_str = time.strftime('%X', dt_obj)
    # time_str = time.strftime('%H:%M:%S', dt_obj)  # the same as above

    print('date {} and time {}'.format(date_str, time_str))

    if sys.platform in ['win32', 'cygwin']:
        os.system('date {} && time {}'.format(date_str, time_str))
    else:  # linux/linux2/darwin
        '''
        参考 http://osxdaily.com/2012/07/04/set-system-time-mac-os-x-command-line/
        以下命令只能同步到分钟，秒会被重置为0
        如果要同步到秒，请执行 sudo ntpdate -u cn.pool.ntp.org
        '''
        if use_ntp:
            os.system('sudo ntpdate -u %s' % NTP_SERVER)
        else:
            os.system('sudo date %s' % time.strftime('%m%d%H%M%y', dt_obj))


if __name__ == '__main__':
    if len(sys.argv) <= 1:  # 没参数
        set_local_dt(get_local_dt_from_ntp(), use_ntp=True)
        sys.exit(0)
    _arg1 = sys.argv[1]
    try:
        # 时分秒格式
        _dt = datetime.strptime(_arg1, '%Y-%m-%d %H:%M:%S')
        set_local_dt(_dt.timetuple())
    except ValueError:
        # 时间戳格式
        _dt_obj = time.localtime(float(_arg1))
        set_local_dt(_dt_obj)
