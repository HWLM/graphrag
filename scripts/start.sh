#!/bin/bash

# 定义服务名称
SERVICE_NAME="service_start_search.py"

# 使用pgrep获取服务的PID
PID=$(pgrep -f $SERVICE_NAME)

# 检查是否找到了PID
if [ -z "$PID" ]; then
    echo "没有找到名为 $SERVICE_NAME 的进程。"
else
  # 打印找到的PID
  echo "找到名为 $SERVICE_NAME 的进程，PID为：$PID"
  # 使用kill命令尝试终止进程
  kill -9 $PID
  sleep 2
fi

# 运行服务脚本，并将输出重定向到日志文件
# 使用tee命令同时打印到控制台和日志文件
# 使用nohup命令让脚本在后台运行，即使终端关闭也不会影响服务
echo `pwd`
python3 ./graphrag/searchMethod/service_start_search.py