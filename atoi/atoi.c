/*
 * Project: daigg5201314
 * Module: ATOI
 * File: atoi.c
 * Created Date: 2023-07-30 16:11:38
 * Author: 堡烨
 * Description: 字符串转换成数字
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
#include "atoi.h"

/* ======================================================================================
 * macros(宏指令)
 */
#define MAP_SIZE (sizeof(map) / sizeof(str_t))
/* ======================================================================================
 * types(变量类型)
 */
typedef struct
{
    const char *name;
    char data;
} str_t;

str_t map[] = {
    {"tile", 0x00},       // 瓦
    {"change", 0x01},     // 转
    {"hertz", 0x02},      // 赫兹
    {"firing", 0x03},     // 启动
    {"centigrade", 0x04}, // 摄氏度
    {"voltage", 0x05},    // 电压
    {"zero", 0x09},
    {"one", 0x0A},
    {"two", 0x0B},
    {"three", 0x0C},
    {"four", 0x0D},
    {"five", 0x0E},
    {"six", 0x0F},
    {"seven", 0x10},
    {"eight", 0x11},
    {"nine", 0x12},
    {"decade", 0x13},   // 十位
    {"hundred", 0x14},  // 百位
    {"thousand", 0x15}, // 千位
};
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

/**
 * @brief :根据字符串查表
 * @param name:输入字符串
 * @return :数据或者错误码
 */
static char name_find(const char *name)
{
    for (int i = 0; i < MAP_SIZE; i++)
    {
        if (strcmp(map[i].name, name) == 0)
        {
            return map[i].data;
        }
    }
    return -1;
}

/* ======================================================================================
 * implementation(全局使用函数)
 */

/**
 * @brief :输入字符串
 * @param str:输入的字符串
 * @return :NULL或者数组,需要手动释放数组
 */
char *str_change_num(char *str)
{
    char *token; // 获取单个字符串
    char data = 0;
    unsigned int length = 0;
    char *bytes = (char *)malloc(MAP_SIZE * sizeof(char));

    if (bytes == NULL)
    {
        printf("Memory allocation failed.\n");
        return NULL;
    }

    token = strtok(str, " ");
    while (token != NULL)
    {
        data = name_find(token);
        if (data != -1)
        {
            bytes[length++] = data;
        }
        else
        {
            printf("this data is no real!\n");
        }
        token = strtok(NULL, " ");
    }

    char *nums = (char *)malloc(length * sizeof(char));

    if (bytes == NULL)
    {
        printf("Memory allocation failed.\n");
        return NULL;
    }

    memcpy(nums, bytes, length * sizeof(char));

    for (int i = 0; i < length; i++)
    {
        printf(" 0x%02x", nums[i]); // 正确打印
    }

    // for (int i = 0; i < sizeof(nums)/sizeof(char); i++)
    // {
    //     printf(" 0x%02x", nums[i]); // 错误打印，打印的是指针大小 ,sizeof(nums)/sizeof(char)获取到的是编译器的指针大小
    // }
    printf("\n");
    return nums;
}