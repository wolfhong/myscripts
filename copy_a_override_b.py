#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
将目标目录拷贝到备份目录, 仅拷贝有差异的部分. 但不覆盖backupDir中才有的目录和文件.
Usage: ./xxxx.py dataDir backupDir
'''

import os
import sys
import filecmp
import re
import shutil

holderlist = []


def compareme(dir1, dir2):
    dircomp = filecmp.dircmp(dir1, dir2)
    only_in_one = dircomp.left_only
    diff_in_one = dircomp.diff_files
    [holderlist.append(os.path.abspath(os.path.join(dir1, x))) for x in only_in_one]
    [holderlist.append(os.path.abspath(os.path.join(dir1, x))) for x in diff_in_one]
    if len(dircomp.common_dirs) > 0:
        for item in dircomp.common_dirs:
            compareme(os.path.abspath(os.path.join(dir1, item)), os.path.abspath(os.path.join(dir2, item)))
    return holderlist


def main():
    if len(sys.argv) > 2:
        dir1 = sys.argv[1]
        dir2 = sys.argv[2]
    else:
        print("Usage: %s %s" % (sys.argv[0], "dataDir backupDir"))
        sys.exit()

    source_all = compareme(dir1, dir2)
    source_files = []
    source_dirs = []
    destination_files = []
    destination_dirs = []
    dir1 = os.path.abspath(dir1)

    if not dir2.endswith('/'):
        dir2 = dir2 + '/'
    dir2 = os.path.abspath(dir2)

    for item in source_all:
        destination = re.sub(dir1, dir2, item)
        if os.path.isdir(item):
            source_dirs.append(item)
            destination_dirs.append(destination)
        elif os.path.isfile(item):
            source_files.append(item)
            destination_files.append(destination)

    print("update items: %s" % source_all)

    for item in zip(source_dirs, destination_dirs):
        shutil.copytree(item[0], item[1])
    for item in zip(source_files, destination_files):
        shutil.copy(item[0], item[1])

if __name__ == '__main__':
    main()
