/*
 * Project: daigg5201314
 * Module: itoa
 * File: itoa.c
 * Created Date: 2023-07-30 16:19:22
 * Author: 堡烨
 * Description: 数字转换成字符串
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
#include "itoa.h"

/* ======================================================================================
 * macros(宏指令)
 */

/* ======================================================================================
 * types(变量类型)
 */
// 存放数字
const char *digits[] = {
    "zero", "one", "two", "three", "four", "five",
    "six", "seven", "eight", "nine"};

// 存放单位
const char *units[] = {
    "decade", "hundred", "thousand", "million", "billion"};
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

/**
 * @brief :数字转成字符串
 * @param num:输入的数字
 * @param unit:输入的单位
 * @param result_str:获取的字符串结果
 * @return :void
 */
void num_change_str(int num, const char *unit, char *result_str)
{

    int thousands = num / 1000;
    int hundreds = num / 100 % 10;
    int decades = num / 10 % 10;
    int ones = num % 10;

    if (num == 0)
    {

        strcat(result_str, digits[0]);
        if (unit != NULL)
        {
            strcat(result_str, " ");
            strcat(result_str, unit); // 拼接单位
        }
        printf(" %s", result_str);
        printf("\n");
        return;
    }

    if (thousands > 0)
    {
        strcat(result_str, digits[thousands]);
        strcat(result_str, " ");
        strcat(result_str, units[2]);
        strcat(result_str, " ");
    }

    if (hundreds > 0)
    {
        strcat(result_str, digits[hundreds]);
        strcat(result_str, " ");
        strcat(result_str, units[1]);
        strcat(result_str, " ");
    }
    else if (thousands > 0 && decades > 0)
    {
        strcat(result_str, digits[0]);
        strcat(result_str, " ");
    }

    if (decades > 0)
    {
        strcat(result_str, digits[decades]);
        strcat(result_str, " ");
        strcat(result_str, units[0]);
        strcat(result_str, " ");
    }
    else if (hundreds > 0 && ones > 0)
    {
        strcat(result_str, digits[0]);
        strcat(result_str, " ");
    }
    else if (hundreds == 0 && ones > 0)
    {
        strcat(result_str, digits[0]);
        strcat(result_str, " ");
    }

    if (ones > 0)
    {
        strcat(result_str, digits[ones]);
        if (unit != NULL)
        {
            strcat(result_str, " ");
            strcat(result_str, unit); // 拼接单位
        }
    }
    else
    {
        if (unit != NULL)
        {
            strcat(result_str, " ");
            strcat(result_str, unit); // 拼接单位
        }
    }

    printf("%s", result_str);
    printf("\n");
    return;
}