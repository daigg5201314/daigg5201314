import os
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from functools import partial
import sys
import threading
import keyboard
from collections import OrderedDict
import balls_page
from courts_page import toggle_onoff,move_left,move_right,display_courts_page
import jersey_page
from config_floder import check_load_config,load_config,save_config
# Global variables
is_visible = True
listener = None
image_cache = OrderedDict()
visible_rows = set()

# 全局变量存储路径
paths = {
    "local_folder": None,
    "courts_folder": None
}

def switch_page(page_type):
    global balls_farme, courts_farme, jersey_farme
    # 先销毁当前显示的框架（如果框架已经初始化）
    if balls_farme is not None:
        balls_farme.destroy()
    if courts_farme is not None:
        courts_farme.destroy()
    if jersey_farme is not None:
        jersey_farme.destroy()

    # 根据选择显示相应的页面框架
    if page_type == "balls":
        balls_farme = tk.Frame(root, bg="white")
        balls_farme.pack(fill="both", expand=True)
        balls_page.display_balls_page(balls_farme)
    elif page_type == "courts":
        courts_farme = tk.Frame(root, bg="white")
        courts_farme.pack(fill="both", expand=True)
        display_courts_page(courts_farme)
    elif page_type == "jersey":
        jersey_farme = tk.Frame(root, bg="white")
        jersey_farme.pack(fill="both", expand=True)
        jersey_page.display_jersey_page(jersey_farme)

#显示前台
def bring_to_foreground():
    root.deiconify()  # 显示窗口
    # root.attributes('-topmost', True)  # 设置为置顶
    root.update()  # 更新窗口
    # ctypes.windll.user32.SetForegroundWindow(root.winfo_id())  # 强制切换到前台

#放置后台
def send_to_background():
    # root.attributes('-topmost', False)  # 取消置顶
    root.withdraw()  # 隐藏窗口，使其进入后台
    # ctypes.windll.user32.ShowWindow(root.winfo_id(), 2)  # 将窗口放到后台，ShowWindow(2)表示隐藏窗口

# 更新显示状态
def update_visibility():
    if is_visible:
        bring_to_foreground()  # 切换前台
    else:
        send_to_background() # 放置后台
    print(f"切换窗口 {'显示' if is_visible else '隐藏'}")

# 切换窗口显示
def toggle_visibility():
    global is_visible
    is_visible = not is_visible
    root.after(0, update_visibility)  # 在主线程中更新 UI

# 注册或更新快捷键
def update_hotkey(key_name, shortcut):
    global root,courts_farme
    print(f"调用update_hotkey,key_name={key_name},shortcur={shortcut}")
    if not shortcut.strip():  # 检查快捷键是否为空
        print(f"Error: Shortcut for '{key_name}' cannot be empty.")
        return

    config = load_config()  # 加载现有配置
    old_shortcut = config.get(key_name, '')  # 获取当前快捷键的旧值
    print(f"读取旧的快捷键 ({key_name}): {old_shortcut}")

    # 尝试移除旧快捷键
    if old_shortcut:
        if old_shortcut == shortcut:  # 如果新旧快捷键相同，直接返回
            print(f"新旧快捷键相同，跳过移除操作: {old_shortcut}")
            return  # 直接返回，不做任何操作

        try:
            keyboard.remove_hotkey(old_shortcut)  # 移除旧键以及对应的回调函数
            print(f"移除旧的快捷键 ({key_name}): {old_shortcut}")
        except KeyError:
            print(f"旧的快捷键未注册: {old_shortcut}")

    # 注册新的快捷键
    try:
        # 假设每个快捷键对应不同的功能，通过字典映射
        action_map = {
            "shortcut_windows": toggle_visibility,
            "shortcut_onoff": partial(toggle_onoff,root,courts_farme),
            "shortcut_left": partial(move_left,root,courts_farme),
            "shortcut_right": partial(move_right,root,courts_farme),
        }
        action = action_map.get(key_name)
        if action:
            keyboard.add_hotkey(shortcut, action)
            print(f"注册新的快捷键 ({key_name}): {shortcut}")
        else:
            print(f"未找到对应的动作处理函数: {key_name}")
    except ValueError as e:
        print(f"Error: 无法注册快捷键 '{shortcut}' ({key_name})，可能格式无效或被占用。详细错误: {e}")

    # 更新配置文件
    config[key_name] = shortcut  # 保存新的快捷键到指定键
    save_config(config)  # 保存更新后的配置到文件
    print(f"保存新的快捷键到配置文件 ({key_name}): {shortcut}")

# 启动快捷键监听线程
def start_listener():
    keyboard.wait()  # 等待用户按下快捷键

# 检查快捷键是否冲突
def check_shortcut_conflict(new_shortcuts, current_config, shortcuts_info):
    all_shortcuts = current_config.copy()
    conflicts = []
    
    # 合并当前配置和新配置
    all_shortcuts.update(new_shortcuts)
    
    # 逐一检查新快捷键是否与其他快捷键冲突
    for new_key, new_value in new_shortcuts.items():
        for existing_key, existing_value in all_shortcuts.items():
            if new_key != existing_key and new_value == existing_value:
                # 找到冲突项后，获取两项的描述
                conflicting_item = next((item[0] for item in shortcuts_info if item[1] == existing_key), existing_key)
                current_item = next((item[0] for item in shortcuts_info if item[1] == new_key), new_key)
                conflicts.append((current_item, conflicting_item))
    
    return conflicts

# 打开设置窗口
def open_settings():
    global courts_farme
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("300x300")
    settings_window.attributes('-topmost', True)
    print(f"调用open_settings")
    # 从配置文件加载当前快捷键
    config = load_config()
    print(f"从settings读取的快捷键: {config}")

    # 定义快捷键的标签和配置键
    shortcuts_info = [
        ("切换窗口:", "shortcut_windows"),
        ("开/关按钮:", "shortcut_onoff"),
        ("左移:", "shortcut_left"),
        ("右移:", "shortcut_right"),
    ]

    # 创建输入框与标签
    entries = {}
    for row, (label_text, config_key) in enumerate(shortcuts_info):
        label = tk.Label(settings_window, text=label_text)
        label.grid(row=row, column=0, padx=10, pady=5, sticky="w")

        entry = tk.Entry(settings_window)
        entry.insert(0, config.get(config_key, ''))  # 加载已保存的快捷键
        entry.grid(row=row, column=1, padx=10, pady=5, sticky="w")

        entries[config_key] = entry

    def save_shortcut():
        print("Save shortcut function called.")  # 调试信息
        # 禁用按钮以防止重复点击
        button_save.config(state=tk.DISABLED)

        # 获取用户输入的快捷键
        shortcuts = {key: entry.get() for key, entry in entries.items() if entry.get()}
        
        # 检查快捷键是否冲突
        conflicts = check_shortcut_conflict(shortcuts, config, shortcuts_info)

        if conflicts:
            # 如果有冲突，弹出提示框，显示简化的冲突信息
            conflict_messages = "\n".join(
                f"'{item1}' 与 '{item2}' 冲突，请修改 {item1}" for item1, item2 in conflicts
            )
            messagebox.showerror("快捷键冲突", conflict_messages)
        else:
            # 如果没有冲突，更新快捷键
            for key, value in shortcuts.items():
                update_hotkey(key, value)

        # 在销毁窗口之前恢复按钮状态
        button_save.config(state=tk.NORMAL)

        # 销毁设置窗口
        settings_window.destroy()

    # 保存按钮
    button_save = ttk.Button(settings_window, text="Save", command=save_shortcut)
    button_save.grid(row=len(shortcuts_info), column=0, columnspan=2, pady=20)

# 创建主窗口
def create_ui():
    global root,balls_farme, courts_farme, jersey_farme
    root = tk.Tk()
    root.title("切换页面示例")
    root.geometry("600x600")
    root.local_folder = None  # 本地球场路径
    root.courts_folder = None  # 替换球场路径

    # 添加菜单项
    menubar = tk.Menu(root)
    menubar.add_command(label="⚙️ 设置",command=open_settings)
    menubar.add_command(label="篮球", command=lambda: switch_page("balls"))
    menubar.add_command(label="球场", command=lambda: switch_page("courts"))
    menubar.add_command(label="球衣", command=lambda: switch_page("jersey"))
    root.config(menu=menubar)

    # 创建页面框架
    balls_farme = tk.Frame(root,bg="white")
    courts_farme = tk.Frame(root,bg="white")
    jersey_farme = tk.Frame(root,bg="white")

    check_load_config()
    config = load_config()
    # 初始化路径
    courts_farme.replace_folder = config.get("replace_folder", "")
    courts_farme.local_folder = config.get("local_folder", "")
    # 定义快捷键及其对应的功能
    hotkeys = {
        "shortcut_windows": toggle_visibility,
        "shortcut_onoff": partial(toggle_onoff,root,courts_farme),
        "shortcut_left": partial(move_left,root,courts_farme),
        "shortcut_right": partial(move_right,root,courts_farme),
    }

    # 注册快捷键
    for key, action in hotkeys.items():
        shortcut = config.get(key, '')
        if shortcut:  # 如果快捷键非空
            keyboard.add_hotkey(shortcut, action)

    # 启动监听器线程
    threading.Thread(target=start_listener, daemon=True).start()
    # # 启动后默认显示球场界面
    switch_page("courts")

if __name__ == "__main__":
    create_ui()
    root.mainloop()