#!/bin/bash

echo -e "Windows中文显示异常解决"
CHCP 65001

echo -e "当前目录: $(pwd)"

echo -e "清理编译缓存"
make clean

current_date=$(date +"%Y-%m-%d")
current_time=$(date +"%H:%M:%S")
echo -e "当前日期: $current_date"
echo -e "当前时间: $current_time"

echo -e "开始编译"
make all

echo -e "编译完成"
