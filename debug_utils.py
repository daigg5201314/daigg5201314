import logging
DEBUG_MODE = False  # ✅ 设置为 False 可关闭所有日志打印（适用于正式固件）

# 创建全局 logger
logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG if DEBUG_MODE else logging.WARNING)

# 定义控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG if DEBUG_MODE else logging.WARNING)
console_formatter = logging.Formatter("[%(levelname)s] %(message)s")
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# 创建文件处理器（初始不添加，待 debug 开启时添加）
file_handler = logging.FileHandler("debug.log", mode='w', encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(file_formatter)

def set_debug(enabled: bool):
    """
    动态切换 Debug 模式：
    - 如果 enabled 为 True，则将 logger 级别设为 DEBUG 并添加文件处理器；
    - 如果 False，则设为 WARNING 并移除文件处理器。
    """
    global DEBUG_MODE
    DEBUG_MODE = enabled
    if DEBUG_MODE:
        logger.setLevel(logging.DEBUG)
        console_handler.setLevel(logging.DEBUG)
        if file_handler not in logger.handlers:
            logger.addHandler(file_handler)
        logger.debug("Debug 模式已开启，日志将写入 debug.log")
    else:
        logger.setLevel(logging.WARNING)
        console_handler.setLevel(logging.WARNING)
        if file_handler in logger.handlers:
            logger.removeHandler(file_handler)
        logger.debug("Debug 模式已关闭")  # 这条在关闭后可能不会输出
    print(f"[debug_utils] 调试日志 {'开启' if DEBUG_MODE else '关闭'}")

def debug_print(*args, **kwargs):
    """
    替代内置 print，用于输出调试信息。
    当 DEBUG_MODE 为 True 时，输出 DEBUG 日志，否则只输出 WARNING 级别及以上的日志。
    """
    logger.debug(" ".join(str(arg) for arg in args), **kwargs)
