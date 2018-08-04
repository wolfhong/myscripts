#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
应用场景: 与ssh_with_proxy.sh 中描述的一致, 假设A/B两个机器不互通，但是本地可以访问该两机器.
现在B需要下载A机器上的资源.

原理: 基于如下三条命令
1. 本地: ssh -t -t root@machineA 'python -m http.server 8998'
2. 本地: ssh -N -L 9906:machineA:8998 root@machineA
3. 本地: ssh -N -R 9906:127.0.0.1:9906 root@machineB
在A机器上开启http.server后启用8998端口,然后在本地进行一次本地转发和远程转发.
如果不启动1命令，可以使用其他端口，代理转发其他服务(Mysql, ssh, MangoDB, etc)

第1条中, ssh -t -t 的原因参考: https://unix.stackexchange.com/questions/103699/kill-process-spawned-by-ssh-when-ssh-dies
'''

# import sys
import os
import time
from multiprocessing import Process
from argparse import ArgumentParser, RawDescriptionHelpFormatter


def open_http_server(user, host, port, path, servport):
    cmd = "ssh -t -t -p{port} {user}@{host} 'cd {path} && python -m http.server {servport} || python -m SimpleHTTPServer {servport} '".format(user=user, host=host, port=port, path=path, servport=servport)
    print(cmd)
    os.system(cmd)


def local_proxy(user, host, port, servport, tmpport):
    cmd = "ssh -N -L {tmpport}:{host}:{servport} {user}@{host} -p{port}".format(user=user, host=host, port=port, servport=servport, tmpport=tmpport)
    print(cmd)
    os.system(cmd)


def remote_proxy(userB, hostB, portB, tmpport):
    cmd = "ssh -N -R {tmpport}:127.0.0.1:{tmpport} {user}@{host} -p{port}".format(user=userB, host=hostB, port=portB, tmpport=tmpport)
    print(cmd)
    os.system(cmd)


EPILOG = '''examples:
./start_httpserver_on_remote.py --path=./ zhdev02 zhdev03
Or:
./start_httpserver_on_remote.py --ua=centos --ub=centos --path=./ zhdev28 zhdev30
Or:
./start_httpserver_on_remote.py --from=3306 zhdev28 zhdev30
'''
DESC = "Connecting A and B machines using C, A/B can only be connected from C. C can be localhost."


def create_parser():
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter, description=DESC, epilog=EPILOG)
    parser.add_argument('hostA', action='store')
    parser.add_argument('hostB', action='store')
    parser.add_argument('--ua', dest='userA', action='store', default='root', help='userA')
    parser.add_argument('--ub', dest='userB', action='store', default='root', help='userB')
    parser.add_argument('--pa', dest='portA', action='store', default=22, type=int, help='portA')
    parser.add_argument('--pb', dest='portB', action='store', default=22, type=int, help='portB')
    parser.add_argument('--path', action='store', default=None, help='You need path if you use server.http')
    parser.add_argument('--from', dest='servport', action='store', default=8998, type=int, help='The service port on hostA')
    parser.add_argument('--to', dest='tmpport', action='store', default=9906, type=int, help='The proxy port on hostB and C')
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    hostA, hostB = args.hostA, args.hostB
    userA, userB = args.userA, args.userB
    portA, portB = args.portA, args.portB
    path = args.path
    servport = args.servport  # 8998
    tmpport = args.tmpport  # 9906

    t1 = Process(target=open_http_server, args=(userA, hostA, portA, path, servport), )
    t2 = Process(target=local_proxy, args=(userA, hostA, portA, servport, tmpport), )
    t3 = Process(target=remote_proxy, args=(userB, hostB, portB, tmpport), )

    if path:  # http service
        t_list = [t1, t2, t3, ]
        print("On hostB(%s), visit http://127.0.0.1:%s/" % (hostB, tmpport))
    else:
        t_list = [t2, t3, ]
        print("On hostB, mapping %s to hostA(%s:%s)" % (tmpport, hostA, servport))

    for t in t_list:
        t.start()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            for t in t_list:
                if t.is_alive:
                    t.terminate()
            return


if __name__ == '__main__':
    main()
