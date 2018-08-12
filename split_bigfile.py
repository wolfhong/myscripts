#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import re
from argparse import ArgumentParser, RawDescriptionHelpFormatter


DESC = "将一个大文件分割成多个小文件"
EPILOG = '''在Linux系统中, 可以使用split和cat命令来完成大文件的拆分和拼接.
examples:
    split -b 20m --numeric-suffixes input_filename output_prefix
Or:
    cat bigfile.00 bigfile.01 bigfile.02 > bigfile

在Win系统中, 才需要使用代码来完成这部分工作.

examples:
    ./split_bigfile.py -b 20m input_filename [output_prefix]
'''


def create_parser():
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter, description=DESC, epilog=EPILOG)
    parser.add_argument('input_filename', action='store')
    parser.add_argument('output_prefix', action='store', default=None, nargs="?")
    parser.add_argument('-b', dest='bytecount', action='store', help='小文件的大小')
    return parser


def bytes2human(n):
    # http://code.activestate.com/recipes/578019
    '''
    >>> bytes2human(10000)
    '9.8K'
    >>> bytes2human(100001221)
    '95.4M'
    '''

    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n


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
    count = sumsize // onesize + 1
    length = (count-1) // 10 + 1
    with open(input_filename, 'rb') as f_read:
        for i in range(0, count):
            with open(output_prefix + str(i).zfill(length), 'wb') as f_write:
                _write(f_write, f_read, onesize)


def main():
    parser = create_parser()
    args = parser.parse_args()
    onesize = human2bytes(args.bytecount)
    input_filename = args.input_filename
    output_prefix = args.output_prefix or input_filename
    if not os.path.isfile(input_filename):
        raise ValueError('file {} not exists'.format(input_filename))
    sumsize = os.path.getsize(input_filename)
    if not output_prefix.endswith('.'):
        output_prefix = output_prefix + '.'
    # get split count
    _split(input_filename, output_prefix, sumsize, onesize)


if __name__ == '__main__':
    # import doctest
    # doctest.testmod()
    main()
