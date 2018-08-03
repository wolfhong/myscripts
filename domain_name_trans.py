#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
将unicode域名转为punycode域名,
或者将punycode域名转为unicode域名.
'''
import sys

PY3 = sys.version_info[0] == 3
unicode_type = str if PY3 else unicode


def main(name):
    if not isinstance(name, unicode_type):
        name = name.decode(sys.stdin.encoding)
    byte_name = name.encode('utf8')
    # if filter(lambda x: ord(x) > 127, byte_name):
    if not all(ord(c) < 128 for c in byte_name):
        print(name.encode('idna'))
    else:
        print(byte_name.decode('idna'))


# 恋爱记.我爱你 -> xn--x9t711bqts.xn--6qq986b3xl
# xn--x9t711bqts.xn--6qq986b3xl -> 恋爱记.我爱你

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print("usage: domain_name_trans.py [DomainName]")
        sys.exit(1)
    main(sys.argv[1])
