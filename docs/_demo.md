### git下载时减少代码量

    git clone --recursive --depth 1 -b develop $GIT_FFMPEG


### 获取CPU核数

    make -j`cat /proc/cpuinfo| grep "processor"| wc -l`


### 自动输入Git账号密码 params: username, password

    function cmd_using_auth(){
    expect -c "spawn git clone https://xxxx.xx/xxx/xx.git;
    set timeout 20;
    expect \"Username for\"; send \"$1\n\"
    expect \"Password for\"; send \"$2\n\"
    interact"
    }


### 跨域请求

    var request = new XMLHttpRequest();
    request.open("GET","http://extremevision-hz-forever.oss-cn-hangzhou.aliyuncs.com/IPC-100430/2017_01_02_14h.m3u8");
    result = request.send();


### 测试socket的网页端代码

    var wsl= 'ws://socket.extremevision.com.cn:9603';
    ws = new WebSocket(wsl);
    ws.onopen = function(){
        ws.send('{"cids":"11,12","appid":"sUser130"}');
    };
    ws.onmessage = function(evt){console.log(evt.data);
    ws.onclose = function(evt){console.log('WebSocketClosed!');};
    ws.onerror = function(evt){console.log('WebSocketError!');};
