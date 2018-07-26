echo 命令仅供参考
exit 1

# 添加公钥到服务器, 并使用对应私钥进行免密登录, -i参数省略时使用默认值
# 或者使用 ssh-add ~/.ssh/id_rsa 管理私钥
ssh-copy-id -i ~/.ssh/id_rsa.pub root@machineA
ssh -i ~/.ssh/id_rsa root@machineA


# 通过A作为跳板机登录到B机器, 认证基于A机器, 从B看也是A机器登录它
# 如果认证想要基于本地机器，可参考下面scp命令中设置的代理转发
ssh -t root@<A-ip> ssh root@<B-ip>


# 将A机器的文件直接从A机器上传到B机器，A到B必须已经添加known_hosts, 并支持免密登录
scp root@<A-ip>:./tmp root@<B-ip>:./
# 如果需要将上述命令修改为: 认证基于本地机器
# 需要符合条件:
# 1. A机器必须在/etc/ssh/sshd_config 中将AllowAgentForwarding设置为yes并重启
# 2. 本地机器的/etc/ssh/ssh_config中将ForwardAgent设置为yes
# 3. 本地机器上启动代理: ssh-agent bash && ssh-add ~/.ssh/id_rsa
# 4. 再次执行原命令 scp root@<A-ip>:./tmp root@<B-ip>:./ 即可,A到B必须添加known_hosts,此时认证都基于本地


# 默认配置AllowTcpForwarding yes,所以不需要设置
# 加上-f参数将在后台启动,-g会开启"网关功能"
# 比如: ssh -N -L 9906:10.0.0.1:3306 root@10.0.0.1
ssh -N -L 本地端口:远程IP:远程端口 root@远程IP
ssh -N -L 本地端口:服务B的IP:服务B的端口 root@服务C的IP  # 前提C可以访问B
ssh -N -R 远程端口:本地IP:本地端口 root@远程IP


# 下面例子演示如何进行连续的两次代理转发
# 假设A/B两个机器不互通，但是本地可以访问该两机器
# 现在B需要导出A上Mysql的数据
本地: ssh -N -L 9906:machineA:3306 root@machineA
本地: ssh -N -R 9906:127.0.0.1:9906 root@machineB
# 扩展: 如果将上述的3306端口改为 python -m http.server 8000 启动后的8000端口, 可以实现wget下载文件.
