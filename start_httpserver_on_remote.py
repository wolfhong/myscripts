# -*- coding: utf-8 -*-
'''
应用场景: 与ssh_with_proxy.sh 中描述的一致, 假设A/B两个机器不互通，但是本地可以访问该两机器.
现在B需要下载A机器上的资源.

原理: 基于如下三条命令
1. 本地: ssh -t -t root@machineA 'python -m http.server 8998'
2. 本地: ssh -N -L 9906:machineA:8998 root@machineA
3. 本地: ssh -N -R 9906:127.0.0.1:9906 root@machineB
在A机器上开启http.server后启用8998端口,然后在本地进行一次本地转发和远程转发.

第1条中, ssh -t -t 的原因参考: https://unix.stackexchange.com/questions/103699/kill-process-spawned-by-ssh-when-ssh-dies
'''

import sys
import os
import time
from multiprocessing import Process

# 本地转发和远程转发使用的临时端口,只要不被使用即可
TMP_PORT = 9906


def open_http_server(user, host, port, path, servport):
    cmd = "ssh -t -t -p{port} {user}@{host} 'cd {path} && python -m http.server {servport} || python -m SimpleHTTPServer {servport} '".format(user=user, host=host, port=port, path=path, servport=servport)
    print(cmd)
    os.system(cmd)


def local_proxy(user, host, port, servport):
    cmd = "ssh -N -L {tmpport}:{host}:{servport} {user}@{host} -p{port}".format(user=user, host=host, port=port, servport=servport, tmpport=TMP_PORT)
    print(cmd)
    os.system(cmd)


def remote_proxy(userB, hostB, portB):
    cmd = "ssh -N -R {tmpport}:127.0.0.1:{tmpport} {user}@{host} -p{port}".format(user=userB, host=hostB, port=portB, tmpport=TMP_PORT)
    print(cmd)
    os.system(cmd)


def main():
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("usage: ./main.py hostA hostB [path-in-hostA]")
        sys.exit(1)
    hostA, hostB = sys.argv[1], sys.argv[2]
    userA, userB = 'root', 'root'
    portA, portB = 22, 22
    path = sys.argv[3] if len(sys.argv) == 4 else './'
    servport = 8998

    t1 = Process(target=open_http_server, args=(userA, hostA, portA, path, servport), )
    t2 = Process(target=local_proxy, args=(userA, hostA, portA, servport), )
    t3 = Process(target=remote_proxy, args=(userB, hostB, portB), )
    t_list = [t1, t2, t3]

    for t in t_list:
        t.start()

    print("On hostB(%s), visit http://127.0.0.1:%s/" % (hostB, TMP_PORT))

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
