# 使用ssh从A机器下载文件的同时，也使用ssh上传该文件到B机器
# 适用范围: 本地可以访问A机器和B机器，但A和B之间不互通
# 缺点: 不能显示进度条, 文件的wrx属性会丢失

echo 命令仅供参考
exit 1

# 针对文件,最后比对文件的md5sum
ssh -p31109 root@hong01 'cat source.png' | ssh -p31109 root@hong02 'cat > destination.png'
ssh -p31109 root@hong01 'md5sum source.png'
ssh -p31109 root@hong02 'md5sum destination.png'

# 针对目录,传输流的同时进行压缩
# -表示stdout或者stdin, 结果在hong02机器上出现形式如 destination/source 的目录
# 同机器上比对目录差异: diff -r <dir1> <dir2>
# 如果非同一机器上，需要另寻方法
ssh -p31109 root@hong02 'mkdir -p destination'  # 确保destination目录在hong02机器上存在
ssh -p31109 root@hong01 'tar -czf - source/' | ssh -p31109 root@hong02 'tar -xzf - -C destination/'

# 从网络下载文件并上传B服务器,B服务器不能联网
curl -Ss https://www.python.org/ftp/python/3.7.0/python-3.7.0-macosx10.9.pkg | ssh -p31109 root@hong02 'cat > py37.pkg'
