#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct
{
    const char *name;
    char data;
} str_t;

static str_t map[] = {
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

#define MAP_SIZE (sizeof(map) / sizeof(str_t))

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

/**
 * @brief :数字转成字符串
 * @param num:输入的数字
 * @param unit:输入的单位
 * @param result_str:获取的字符串结果
 * @return :void
 */
void num_change_str(int num, const char *unit, char *result_str)
{
    const char *digits[] = {
        "zero", "one", "two", "three", "four", "five",
        "six", "seven", "eight", "nine"}; // 存放数字

    const char *units[] = {
        "decade", "hundred", "thousand", "million", "billion"}; // 存放单位

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

int main(void *arg)
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