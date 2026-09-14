#!/bin/bash
# 一键启动本地服务器试玩「无人机足球」原型
cd "$(dirname "$0")"
echo "启动中... 电脑访问 http://localhost:8746/　手机访问 http://<你的电脑局域网IP>:8746/"
python3 -m http.server 8746
