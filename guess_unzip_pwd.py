#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This will prompt for a password:
    zip --encrypt file.zip files
This is more insecure, as the password is entered/shown as plain text:
    zip --password (password) file.zip files
'''
from __future__ import unicode_literals
import sys
import time
import zipfile
import string
import itertools
from multiprocessing import Pool
from argparse import ArgumentParser

DESC = 'Guess the password of a zip file.'
PY3 = sys.version_info[0] == 3


def to_string(s):
    if PY3:
        return str(s)
    else:
        if isinstance(s, unicode):
            return s.encode('utf8')
        return str(s)


def calc_time(func):
    def _(*args, **kwargs):
        print('begin guess...')
        start_time = int(time.time())
        ret = func(*args, **kwargs)
        print('end guess, used %.2f seconds' % (int(time.time()) - start_time))
        return ret
    return _


def create_args():
    parser = ArgumentParser(description=DESC)
    parser.add_argument('filename', action='store', help='Zip file')
    parser.add_argument('-p', '--passwords', action='store', nargs='*', help='Passwords')
    parser.add_argument('-f', '--pwdfile', action='store', help='Passwords file')
    parser.add_argument('-s', '--string', action='store',
            help='Generate passwords from digits, lower, upper, punctuation. If char in digits, digits=True...')
    parser.add_argument('-c', '--custom', action='store', help='Generate passwords from custom-field')
    parser.add_argument('-l', '--length', action='store', help='Length of password: 4, or 4-6')
    args = parser.parse_args()
    data = {}
    data['filename'] = args.filename
    data['passwords'] = args.passwords
    data['pwdfile'] = args.pwdfile
    data['custom'] = args.custom
    if args.custom:
        data['custom'] = ''.join(list(set([c for c in args.custom])))  # delete repeated
    if args.custom or args.string:
        length = args.length
        if not length:
            print('-l is needed if -c or -g is enabled.')
            sys.exit(1)
        if '-' in length:
            min_l, max_l = length.split('-')
            data['min_l'], data['max_l'] = int(min_l), int(max_l)
        else:
            data['min_l'] = data['max_l'] = int(length)
    if args.string:
        data['digits'] = data['lower'] = data['upper'] = data['punctuation'] = False
        for char in args.string:
            if char in string.digits:
                data['digits'] = True
            elif char in string.ascii_lowercase:
                data['lower'] = True
            elif char in string.ascii_uppercase:
                data['upper'] = True
            elif char in string.punctuation:
                data['punctuation'] = True
    return type(to_string('Auto'), (object, ), data)


def iter_passwords(pwdfile):
    with open(pwdfile, 'r') as f_read:
        for line in f_read:
            line = line.strip()
            if line:
                yield line


def iter_generation(min_l, max_l, digits=True, lower=False, upper=False, punctuation=False, custom=None):
    ''' 根据条件产生密码
    :params min_l: 最短长度
    :params max_l: 最长长度
    :digits: 包含数字
    :lower: 包含小写字符
    :upper: 包含大写字符
    :punctuation: 包含标点符号
    :custom: 由自定义符号组成,忽略digits/lower/upper/punctuation
    '''
    assert min_l <= max_l
    if custom:
        possibles = custom
    else:
        possibles = ''
        if lower:
            possibles += string.ascii_lowercase
        if upper:
            possibles += string.ascii_uppercase
        if digits:
            possibles += string.digits
        if punctuation:
            possibles += string.punctuation
    for length in range(min_l, max_l + 1):
        for pwd in itertools.product(possibles, repeat=length):
            yield ''.join(pwd)


def extractFile(zobj, generator, cpucount):
    if not generator:
        return

    def _(password):
        try:
            zobj.extractall(pwd=password)
            print("Found Passwd: %s" % password)
            return True
        except BaseException:
            return False

    for password in generator:
        if _(password):
            return


@calc_time
def main():
    args = create_args()
    zobj = zipfile.ZipFile(args.filename)
    cpucount = 10

    # from commands
    passwords = args.passwords or []
    extractFile(zobj, passwords, cpucount)
    # from a file
    pwdfile = args.pwdfile
    if pwdfile:
        extractFile(zobj, iter_passwords(pwdfile), cpucount)
    # from custom or string, consider custom first.
    if hasattr(args, 'min_l'):
        min_l = args.min_l
        max_l = args.max_l
        if args.custom:
            generator = iter_generation(min_l=min_l, max_l=max_l, custom=args.custom)
        else:
            generator = iter_generation(min_l=min_l, max_l=max_l,
                digits=args.digits, lower=args.lower,
                upper=args.upper, punctuation=args.punctuation)
        # from generator(built by custom or string)
        extractFile(zobj, generator, cpucount)


if __name__ == '__main__':
    main()
