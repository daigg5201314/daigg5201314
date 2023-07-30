#!/bin/bash

echo -e "Windows中文显示异常解决"
export LANG=zh_CN.UTF-8
CHCP 65001

echo -e "当前目录: $(pwd)"

echo -e "检查是否需要清理缓存。\r\n"
make check_clean
if [ $? -eq 0 ]; then
    echo -e "编译缓存已清理。\r\n"
else
    echo -e "编译缓存未清理。\r\n"
    echo -e "清理编译缓存。\r\n"
make clean
fi



current_date=$(date +"%Y-%m-%d")
current_time=$(date +"%H:%M:%S")
echo -e "当前日期: $current_date"
echo -e "当前时间: $current_time"

echo -e "开始编译。\r\n"
make all

echo -e "编译完成"
