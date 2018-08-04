#! /bin/bash
# -*- coding: utf-8 -*-
# 查找IP地址信息: http://ip.chinaz.com/
# 提供IP解析的API: http://www.boip.net/

function show_usage() {
    echo "查找自己的IP地址: ./findip.sh"
    echo "查找对方的IP地址: ./findip.sh [ip [ip]]"
}

export iplist=""

if [ $# -lt 1 ]; then
    curl http://ip.chinaz.com/getip.aspx
    echo
    exit
fi

while [ "$1" != "" ]; do
    case $1 in
        -h | --help )           show_usage
                                exit
                                ;;
        * )                     iplist="$iplist $1"
                                ;;
    esac
    shift
done

for ip in $iplist
do
    curl -F ip=$ip 'http://ip.chinaz.com/ajaxsync.aspx?at=ipbatch&callback=jq&jdfwkey=oymcy2'
    echo
done
