/*
 * Project: daigg5201314
 * Module: ATOI
 * File: atoi.h
 * Created Date: 2023-07-30 16:12:18
 * Author: 堡烨
 * Description: 字符串转换成数字
 * -----
 * todo: modified
 * -----
 * Copyright (c) 2023 - vDiscovery, Inc
 */
#ifndef ATOI_H
#define ATOI_H

/* ======================================================================================
 * includes(头文件包含)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ======================================================================================
 * macros(宏指令)
 */

/* ======================================================================================
 * types(变量类型)
 */

/* ======================================================================================
 * declaration(函数声明)
 */

/**
 * @brief :输入字符串
 * @param str:输入的字符串
 * @return :NULL或者数组,需要手动释放数组
 */
char *str_change_num(char *str);

#endif // ATOI_ATOI_H