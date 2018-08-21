#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import re
# from threading import Thread
from multiprocessing import Process
from argparse import ArgumentParser, RawDescriptionHelpFormatter


DESC = "将一个大文件分割成多个小文件, 然后scp到远程服务器, 最终在远程服务器合并为原文件"
EPILOG = '''适合糟糕网络下scp上传大文件到目标机器. 可以保证不断重试直到上传成功.
由于上传文件使用了scp命令, 因此需要系统支持.
请使用sshkey认证登录, 避免重复输入密码.

examples:
    ./scp_bigfile.py -b 20m -P31109 tar_filename root@hong01:./
'''


def create_parser():
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter, description=DESC, epilog=EPILOG)
    parser.add_argument('input_filename', action='store')
    parser.add_argument('remote_info', action='store', help='root@machineA:./')
    parser.add_argument('-b', dest='bytecount', action='store', help='小文件的大小')
    parser.add_argument('-P', dest='port', action='store', default=22, help='scp的端口')
    return parser


def human2bytes(string):
    '''
    >>> human2bytes('20G')
    21474836480
    >>> human2bytes('1.5gb')
    1610612736
    >>> human2bytes('20.0KB')
    20480
    >>> human2bytes('20B')
    20
    '''

    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    regular = re.compile(r'([0-9.]+)([a-zA-Z]?)[Bb]?')
    match = regular.match(string)
    if not match:
        raise ValueError('Not match')
    size = match.groups()[0]
    unit = match.groups()[1].upper()
    if not unit or unit == 'B':
        return int(size)
    if unit not in symbols:
        raise ValueError('Symbols not match')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    return int(float(size) * prefix[unit])


def _write(f_write, f_read, onesize):
    index = 0
    while index < onesize:
        diff = min(1024 * 1024, onesize - index)
        f_write.write(f_read.read(diff))
        index += diff


def _split(input_filename, output_prefix, sumsize, onesize):
    assert sumsize > onesize
    filename_list = []
    count = sumsize // onesize + 1
    length = (count-1) // 10 + 1
    with open(input_filename, 'rb') as f_read:
        for i in range(0, count):
            write_target = output_prefix + str(i).zfill(length)
            with open(write_target, 'wb') as f_write:
                _write(f_write, f_read, onesize)
                filename_list.append(write_target)
    return filename_list


def call_scp(port, filename, remote_info):
    result = 1
    while result != 0:
        result = os.system("scp -P{} {} {}".format(port, filename, remote_info))
    os.system("rm {}".format(filename))


def main():
    parser = create_parser()
    args = parser.parse_args()

    onesize = human2bytes(args.bytecount)
    port = args.port
    input_filename = os.path.abspath(args.input_filename)
    remote_info = args.remote_info
    if not re.compile(r'\S*@\S*:\S*').match(remote_info):
        raise ValueError('remote_info error')

    if not os.path.isfile(input_filename):
        raise ValueError('file {} not exists'.format(input_filename))

    sumsize = os.path.getsize(input_filename)
    output_prefix = input_filename
    if not output_prefix.endswith('.'):
        output_prefix = output_prefix + '.'
    # get split count
    scp_filename_list = _split(input_filename, output_prefix, sumsize, onesize)
    cmd_list = ['scp -P{} {} {}'.format(port, f, remote_info) for f in scp_filename_list]
    for cmd in cmd_list:
        print(cmd)
    # start scp threads
    t_list = [Process(target=call_scp, args=(port, f, remote_info)) for f in scp_filename_list]
    [t.start() for t in t_list]
    [t.join() for t in t_list]
    # join splited files on remote machine
    remote_account, remote_path = remote_info.split(':')
    final_name = os.path.basename(input_filename)
    part_names = ' '.join([os.path.basename(f) for f in scp_filename_list])
    merge_cmd = "ssh -p{port} {remote_account} 'cd {remote_path} && cat {part_names} > {final_name} && rm {part_names}' ".format(
        port=port, remote_account=remote_account, remote_path=remote_path,
        part_names=part_names, final_name=final_name,
    )
    print(merge_cmd)
    os.system(merge_cmd)
    # md5sum check files
    os.system("md5sum %s" % input_filename)
    os.system("ssh -p{port} {remote_account} 'cd {remote_path} && md5sum {final_name}' ".format(
        port=port, remote_account=remote_account, remote_path=remote_path,
        final_name=final_name,
    ))

if __name__ == '__main__':
    # import doctest
    # doctest.testmod()
    main()
