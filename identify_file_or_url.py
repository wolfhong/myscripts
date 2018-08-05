#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import os
import sys
from argparse import ArgumentParser

missing_pkg = False

try:
    import magic
except ImportError:
    print('Missing some python libraries, please run commands below:')
    if sys.platform in ['win32', 'cgywin']:
        print('    pip install python-magic-bin 0.4.14')
    elif sys.platform.startswith('linux'):
        print('    pip install python-magic')
    elif sys.platform in ['darwin']:
        print('    brew install libmagic')
        print('    pip install python-magic')
    missing_pkg = True
try:
    import requests
except ImportError:
    if not missing_pkg:
        print('Missing some python libraries, please run commands below:')
    print('    pip install requests')
    missing_pkg = True

if missing_pkg:
    sys.exit(1)


def create_parser():
    parser = ArgumentParser(description='Identify a file or url')
    parser.add_argument('files', action='store', nargs='*')
    parser.add_argument('-b', '--brief', action='store_true')
    parser.add_argument('-I', '--mime', action='store_true')
    return parser


def identify(file_or_url, mime=False):
    if file_or_url.startswith('http://') or \
            file_or_url.startswith('https://') or \
            file_or_url.startswith('ftp://') or \
            file_or_url.startswith('ftps://') or \
            file_or_url.startswith('file://'):
        return magic.from_buffer(requests.get(file_or_url, stream=True, timeout=5).raw.read(1024), mime=mime)
    elif os.path.isfile(file_or_url):
        return magic.from_buffer(open(file_or_url, "rb").read(1024), mime=mime)


def main():
    parser = create_parser()
    args = parser.parse_args()
    files = args.files
    for fou in files:
        if not args.brief:
            sys.stdout.write(fou + ': ')
        print(identify(fou, mime=args.mime))


if __name__ == '__main__':
    main()
