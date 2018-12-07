#!/bin/bash
# -*- coding: utf-8 -*-

# ------------------------------------------------
# 服务端A不可访问外网. 但是要使用yum安装依赖等访问网络的操作.
# 思路: 本地开启代理服务器,然后在本地启动远程转发,服务端设置http_proxy

# 本地: 使用翻墙软件/squid/squidman等(http://squidman.net/squidman/), 如41081
# 本地: ssh -N -R 9906:127.0.0.1:41081 rhlog@machineB
# 远程: export http_proxy=http://127.0.0.1:9906
# 远程: export https_proxy=http://127.0.0.1:9906
# ------------------------------------------------

local_port=41081   # 本地代理端口
remote_port=9906   # 远程http代理端口
login_cmd=""       # 登录命令,可以加上-p参数

function usage() {
    echo "usages: $0 [-l localPort] [-r remotePort] user@machineA"
}

if [ $# -lt 1 ]
then
    usage
    exit 1
fi

while [ "$1" != "" ]; do
    case $1 in
        -l | --local )          shift
                                local_port=$1
                                ;;
        -r | --remote )         shift
                                remote_port=$1
                                ;;
        -h | --help )           usage
                                exit
                                ;;
        * )                     login_cmd="${login_cmd} $1"
                                ;;
    esac
    shift
done

# 在远程机器初始执行脚本: 修改http_proxy
cat <<EOF | ssh ${login_cmd} "cat > ./tmp_open_proxy.sh"
export http_proxy=http://127.0.0.1:${remote_port}
export https_proxy=http://127.0.0.1:${remote_port}
export no_proxy="localhost,127.0.0.1,mirrors.cmrh.com"
EOF

# 提示
cmd="ssh -N -R ${remote_port}:127.0.0.1:${local_port} ${login_cmd}" 
echo "run: $cmd"
echo "在远程机器上执行: . tmp_open_proxy.sh"
echo "然后就可以在远程机器上, 经由本地的${local_port}端口访问网络"

# 执行远程代理
/bin/bash -c "$cmd"
