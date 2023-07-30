/*
 * Project: daigg5201314
 * Module: ITOA
 * File: itoa.h
 * Created Date: 2023-07-30 16:19:54
 * Author: 堡烨
 * Description: description
 * -----
 * todo: modified
 * -----
 * Copyright (c) 2023 - vDiscovery, Inc
 */
#ifndef ITOA_H
#define ITOA_H

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
 * @brief :数字转成字符串
 * @param num:输入的数字
 * @param unit:输入的单位
 * @param result_str:获取的字符串结果
 * @return :void
 */
void num_change_str(int num, const char *unit, char *result_str);

#endif // ITOA_ITOA_H