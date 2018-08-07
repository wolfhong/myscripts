#!/usr/bin/env python
# -*- coding: utf-8 -*-
# you can also replace prettytable with https://github.com/wolfhong/PTable
from prettytable import PrettyTable
import re
import os

# State       Recv-Q Send-Q  Local Address:Port       Peer Address:Port     Commands
# LISTEN      0      50      *:2181                   *:*                   users:(("java",pid=5772,fd=121))


def short_cmd(cmd):
    cmd = cmd.strip()
    length = 50
    if len(cmd) <= length:
        return cmd
    return cmd[:length] + '...'


class ShowData(object):
    def __init__(self, **kwargs):
        self.State = kwargs.get('State', None)
        self.LocalPort = kwargs.get('LocalPort', None)
        self.Port = kwargs.get('Port', None)
        self.PeerPort = kwargs.get('PeerPort', None)
        self.Pid = kwargs.get('Pid', None)
        self.Command = kwargs.get('Command', None)


def main():
    table = PrettyTable()
    table.field_names = ['State', 'LocalPort', 'PeerPort', 'Pid', 'Command']
    pid_list = []  # use `ps -q pid -o comm=` to show all pids
    data_list = []

    result = os.popen('sudo ss -nltp').read()
    lines = result.split('\n')
    regular = re.compile(r'\bpid=(\d+)\b')
    for i, line in enumerate(lines):
        if i == 0:
            continue
        fields = [k.strip() for k in line.split() if k.strip()]
        if len(fields) < 6:
            continue
        match_list = regular.findall(fields[5])  # analysis Commands
        if match_list:
            pid_list.append(match_list[-1])  # get command's pid
            data_list.append(ShowData(State=fields[0], LocalPort=fields[3], PeerPort=fields[4]))

    # print(','.join(pid_list))
    result = os.popen('ps -q %s -o cmd=' % ','.join(pid_list)).read()
    command_list = [short_cmd(k) for k in result.split('\n') if k.strip()]
    for d, pid, cmd in zip(data_list, pid_list, command_list):
        d.Pid = pid
        d.Command = cmd
        d.Port = int(d.LocalPort.split(':')[-1])

    # sort by Port
    data_list.sort(key=lambda d: d.Port)
    for data in data_list:
        table.add_row([data.State, data.LocalPort, data.PeerPort, data.Pid, data.Command])

    print(table.get_string())

if __name__ == '__main__':
    main()
