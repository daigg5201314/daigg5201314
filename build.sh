#!/bin/bash

echo -e "当前目录: $(pwd)"

echo -e "检查是否需要清理缓存。\r\n"

filename="./main.exe"  

if [ -f "$filename" ]; then  # 判断文件是否存在
    echo "文件存在"
    make clean  # 调用make clean命令进行清除
else
    echo "文件不存在"
fi


current_date=$(date +"%Y-%m-%d")
current_time=$(date +"%H:%M:%S")
echo -e "当前日期: $current_date"
echo -e "当前时间: $current_time"

echo -e "开始编译\r\n"
make all

echo -e "编译完成"
