import os
from ttkbootstrap.constants import *
import sys
import json


CONFIG_FILE = "config.json"
def save_default_config(config_path):
    """保存默认配置到指定路径"""
    default_config = {
        "shortcut_windows": "alt+h",
        "shortcut_onoff": "alt+r",
        "shortcut_left": "-",
        "shortcut_right": "=",
        "local_folder": "",
        "balls_folder": "",
        "courts_folder": "",
    }
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(default_config, f, indent=4)
    print(f"默认配置保存在 {config_path}.")

# Check resource path
def resource_path(relative_path):
    """
    获取资源文件的正确路径，始终指向当前可执行文件所在目录
    """
    # 获取当前可执行文件的路径（即 .exe 所在目录）
    base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(base_path, relative_path)

def check_load_config():
 """检查文件是否存在"""
 config_path = resource_path(CONFIG_FILE)  # 获取配置文件路径
#  print(f"Config file path: {config_path}")
 if not os.path.exists(config_path):
    try:
        # 检查文件是否为空
        if os.path.getsize(config_path) == 0:
            save_default_config(config_path)
    except Exception as e:
        save_default_config(config_path)

def load_config():
    """加载嵌入的配置文件"""
    config_path = resource_path(CONFIG_FILE)  # 获取配置文件路径
    # print(f"文件加载路径：{config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config):
    """保存配置到文件"""
    config_path = resource_path(CONFIG_FILE)  # 获取配置文件路径
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        print("配置已经保存.")
    except Exception as e:
        print(f"Error saving config: {e}")

