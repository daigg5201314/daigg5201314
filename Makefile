# 定义编译器和编译器标志
CC = gcc
CFLAGS = -Wall -g

# 定义目标文件
TARGET = main.exe

# 头文件路径
INCLUDE = -I . -I ./atoi -I ./itoa

# 定义源文件和对象文件
SRCS := $(wildcard *.c) $(wildcard */*.c)
OBJS := $(patsubst %.c, %.o, $(SRCS))

# 默认目标
all: $(TARGET)

# 打印变量信息
printf:
	@echo $(OBJS) 
	@echo $(SRCS)
	@echo $(TARGET)

# 编译中间文件
%.o: %.c
	$(CC) $(INCLUDE) $(CFLAGS) -c $< -o $@

# 生成可执行文件
$(TARGET): $(OBJS)
	$(CC) $(INCLUDE) $(CFLAGS) -o $@ $^

#伪目标
.PHONY: check_clean clean make printf

# 检查是否需要运行 "make clean"
check_clean:
ifeq ($(wildcard ./main.exe),)
	@echo main.exe does not exist
	@exit 1
else
	@echo main.exe exists
	@exit 0
endif

# 清理生成的文件
clean:
	rm -f $(TARGET) $(OBJS)
