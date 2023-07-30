/*
 * Project: daigg5201314
 * Module: main
 * File: main.c
 * Created Date: 2023-07-30 16:41:18
 * Author: 堡烨
 * Description: 主函数
 * -----
 * todo: modified
 * -----
 * Copyright (c) 2023 - vDiscovery, Inc
 */

/* ======================================================================================
 * log(日志模块)
 */
#define LOG_ENABLE_DEBUG (1)

/* ======================================================================================
 * includes(头文件包含)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "atoi.h"
#include "itoa.h"

/* ======================================================================================
 * macros(宏指令)
 */

/* ======================================================================================
 * types(变量类型)
 */

/* ======================================================================================
 * declaration(函数声明)
 */

/* ======================================================================================
 * globals(全局函数/变量)
 */

/* ======================================================================================
 * helper(帮助函数)
 */

/* ======================================================================================
 * private implementation(内部使用函数)
 */

/* ======================================================================================
 * implementation(全局使用函数)
 */
int main(void *arg, void *argv[])
{
    int num;
    char *unit = "hertz"; // 单位赫兹
    char strbuf[10] = {0};
    char *numbuf = NULL;
    printf("请输入数字：");
    scanf("%d", &num);
    num_change_str(num, unit, strbuf); // 获取到strbuf
    numbuf = str_change_num(strbuf);   // 获取到numbuf
    if (numbuf != NULL)
    {
        free(numbuf);
    }
    else
    {
        printf("String is invalid.\n");
    }

    while (1)
        ;
    return 0;
}
