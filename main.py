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
import json
from collections import OrderedDict
import courts_page
import balls_page
import jersey_page
from courts_page import toggle_onoff,move_left,move_right,display_courts_page,validate_local_folder,toggle_action,process_local_courts_files
from balls_page import display_balls_page,switch_to_balls_page  
from jersey_page import display_jersey_page,switch_to_jersey_page
from config_floder import check_load_config,load_config,save_config
from debug_utils import debug_print,set_debug

# Global variables
is_visible = True
listener = None
image_cache = OrderedDict()
visible_rows = set()
# 全局字典用于存储已注册的热键句柄
hotkey_handles = {}
# 全局字典用于存储页面信息
pages = {}
# 全局变量存储路径
paths = {
    "local_folder": None,
    "courts_folder": None
}
# 默认快捷键设置（请根据实际需要修改）
default_hotkeys = {
    "shortcut_windows": "alt+w",
    "shortcut_onoff": "alt+r",
    "shortcut_left": "-",
    "shortcut_right": "="
}

def switch_page(page_type):
    """统一的页面切换函数，根据页面类型切换到相应页面"""
    page_info = pages.get(page_type)
    if page_info:
        # 可选：如果需要每次切换时刷新内容，可以调用其 display 方法
        page_info["display"](page_info["frame"])
        page_info["frame"].tkraise()
    else:
        debug_print(f"未知页面类型: {page_type}")

def bring_to_foreground():
    """放置前台"""
    root.deiconify()  # 显示窗口
    root.update()     # 更新窗口

def send_to_background():
    """放置后台"""
    root.withdraw()   # 隐藏窗口

def update_visibility():
    """更新显示状态"""
    if is_visible:
        bring_to_foreground()
    else:
        send_to_background()
    debug_print(f"切换窗口 {'显示' if is_visible else '隐藏'}")

# 切换窗口显示
def toggle_visibility():
    """切换窗口显示状态"""
    global is_visible
    is_visible = not is_visible
    root.after(0, update_visibility)  

def start_listener():
    """启动全局热键监听线程"""
    keyboard.wait()  # 阻塞等待快捷键触发


def update_and_register_hotkey(key_name, new_shortcut):
    """
    更新和注册指定的快捷键。
    无论新旧是否相同，都先移除原注册的热键，然后注册新快捷键并更新配置。
    """
    global root, courts_farme, hotkey_handles

    new_shortcut = new_shortcut.strip()
    if not new_shortcut:
        debug_print(f"[ERROR] {key_name} 的快捷键不能为空")
        return

    config = load_config()
    old_shortcut = config.get(key_name, '').strip()

    # ① 如果之前已注册，则无条件先移除旧的快捷键注册
    if key_name in hotkey_handles:
        try:
            keyboard.remove_hotkey(hotkey_handles[key_name])
            debug_print(f"[移除] 成功移除 {key_name} 的旧快捷键: {old_shortcut}")
        except Exception as e:
            debug_print(f"[WARN] 移除 {key_name} 的旧快捷键失败：{e}")
        finally:
            hotkey_handles.pop(key_name, None)
    else:
        # 如果没有记录在 hotkey_handles 中，但配置有旧值，也打印日志
        if old_shortcut:
            debug_print(f"[提示] 未在 hotkey_handles 中找到 {key_name} 对应的注册项，旧快捷键：{old_shortcut}")

    # ② 注册新的快捷键
    # 定义快捷键对应的回调函数映射，确保它能正确调用你的业务函数
    action_map = {
        "shortcut_windows": toggle_visibility,
        "shortcut_onoff": partial(toggle_onoff, root, courts_farme),
        "shortcut_left": partial(move_left, root, courts_farme),
        "shortcut_right": partial(move_right, root, courts_farme),
    }
    action = action_map.get(key_name)
    if not action:
        debug_print(f"[跳过] 未找到 {key_name} 对应的操作函数")
        return

    try:
        # 注册新热键
        handle = keyboard.add_hotkey(new_shortcut, action)
        hotkey_handles[key_name] = handle
        debug_print(f"[注册] {key_name} 注册为：{new_shortcut}")
    except Exception as e:
        debug_print(f"[错误] 注册 {key_name} 快捷键失败：{new_shortcut}，错误：{e}")
        return

    # ③ 更新配置（无论新旧是否相同，都更新配置记录）
    config[key_name] = new_shortcut
    save_config(config)
    debug_print(f"[保存] {key_name} 快捷键更新完毕：{new_shortcut}")

def check_and_update_hotkeys(new_shortcut_dict, shortcuts_info):
    """
    检查新设置的快捷键是否存在冲突；若无冲突则逐一调用 update_and_register_hotkey 完成更新。
    new_shortcut_dict: dict, 如 { "shortcut_windows": "ctrl+alt+w", ... }
    shortcuts_info: list of (显示名称, 配置键) 用于提示冲突信息。
    """
    config = load_config()
    conflicts = []
    for key1, val1 in new_shortcut_dict.items():
        for key2, val2 in new_shortcut_dict.items():
            if key1 != key2 and val1.strip() == val2.strip() and val1.strip():
                desc1 = next((name for name, k in shortcuts_info if k == key1), key1)
                desc2 = next((name for name, k in shortcuts_info if k == key2), key2)
                conflicts.append((desc1, desc2))
    if conflicts:
        msg = "\n".join(f"'{a}' 与 '{b}' 冲突" for a, b in conflicts)
        messagebox.showerror("快捷键冲突", f"存在以下冲突，请修改：\n{msg}")
        return

    for key, shortcut in new_shortcut_dict.items():
        update_and_register_hotkey(key, shortcut)

# 注册或更新快捷键
def restore_default_hotkeys():
    """
    恢复所有默认快捷键：
      - 移除当前注册的热键
      - 更新配置文件为默认值
      - 重新注册默认热键
    """
    global hotkey_handles
    config = load_config()
    for key, default_shortcut in default_hotkeys.items():
        if key in hotkey_handles:
            try:
                keyboard.remove_hotkey(hotkey_handles[key])
                debug_print(f"[恢复] 移除 {key} 的旧快捷键")
            except Exception as e:
                debug_print(f"[恢复] 移除 {key} 快捷键失败：{e}")
            hotkey_handles.pop(key, None)
        # 重新注册默认快捷键
        update_and_register_hotkey(key, default_shortcut)
    config.update(default_hotkeys)
    save_config(config)
    messagebox.showinfo("恢复默认", "快捷键已恢复为默认设置！")
    debug_print("[恢复默认] 快捷键恢复完成")

# 打开设置窗口
def open_settings():
    global courts_farme
    settings_window = tk.Toplevel(root)
    settings_window.title("设置")
    settings_window.geometry("300x400")
    settings_window.attributes("-topmost", True)

    config = load_config()
    # 快捷键信息：显示名称和配置键
    shortcuts_info = [
        ("切换窗口", "shortcut_windows"),
        ("开/关按钮", "shortcut_onoff"),
        ("左移", "shortcut_left"),
        ("右移", "shortcut_right"),
    ]

    entries = {}
    # 创建快捷键输入框
    for i, (label_text, config_key) in enumerate(shortcuts_info):
        tk.Label(settings_window, text=label_text).grid(row=i, column=0, padx=10, pady=5, sticky="w")
        entry = tk.Entry(settings_window)
        entry.insert(0, config.get(config_key, ""))
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries[config_key] = entry

    # 新增 Debug 模式选项
    # 从配置中读取 debug_mode 状态（若不存在则默认为 False）
    debug_mode = config.get("debug_mode", False)
    debug_var = tk.BooleanVar(value=debug_mode)
    tk.Label(settings_window, text="开启 Debug").grid(row=len(shortcuts_info), column=0, padx=10, pady=5, sticky="w")
    debug_checkbox = tk.Checkbutton(settings_window, variable=debug_var, bg="white")
    debug_checkbox.grid(row=len(shortcuts_info), column=1, padx=10, pady=5, sticky="w")

    def save_shortcut():
        button_save.config(state="disabled")
        # 更新快捷键设置
        new_shortcuts = { key: entry.get().strip() for key, entry in entries.items() if entry.get().strip() }
        check_and_update_hotkeys(new_shortcuts, shortcuts_info)
        # 保存 debug 模式设置到配置，并调用 set_debug 切换调试输出
        config["debug_mode"] = debug_var.get()
        save_config(config)
        # 此处调用 debug_utils.set_debug(debug_var.get()) 进行实际切换
        try:
            from debug_utils import set_debug  # 假设 debug_utils.py 已在项目中
            set_debug(debug_var.get())
        except Exception as e:
            print(f"[WARN] 设置 debug 模式失败: {e}")
        settings_window.destroy()

    def restore_defaults():
        restore_default_hotkeys()
        # 同步更新输入框显示默认快捷键
        for label_text, config_key in shortcuts_info:
            entries[config_key].delete(0, "end")
            entries[config_key].insert(0, default_hotkeys.get(config_key, ""))
        # 恢复默认 debug 模式（假设默认为 False，可根据需要修改）
        debug_var.set(False)
        config["debug_mode"] = False
        save_config(config)
        try:
            from debug_utils import set_debug
            set_debug(False)
        except Exception as e:
            print(f"[WARN] 恢复默认 debug 模式失败: {e}")

    button_save = tk.Button(
        settings_window,
        text="保存",
        command=save_shortcut,
        bg="#4CAF50",
        fg="white",
        font=("Arial", 10, "bold")
    )
    button_save.grid(row=len(shortcuts_info)+1, column=0, columnspan=2, pady=10)

    button_restore = tk.Button(
        settings_window,
        text="恢复默认快捷键",
        command=restore_defaults,
        bg="#FF3333",
        fg="white",
        font=("Arial", 10, "bold")
    )
    button_restore.grid(row=len(shortcuts_info)+2, column=0, columnspan=2, pady=10)

# 创建主窗口
def create_ui():
    global root, balls_farme, courts_farme, jersey_farme, pages

    root = tk.Tk()
    root.title("篮球资源管理器")
    root.geometry("1000x700")
    root.configure(bg="white")

    # 设置 root 的 grid 权重，确保界面自适应
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # 设置菜单栏
    menubar = tk.Menu(root)
    menubar.add_command(label="⚙️ 设置", command=open_settings)
    menubar.add_command(label="篮球", command=lambda: switch_page("balls"))
    menubar.add_command(label="球场", command=lambda: switch_page("courts"))
    menubar.add_command(label="球衣", command=lambda: switch_page("jersey"))
    root.config(menu=menubar)

    # 创建各页面 Frame
    balls_farme = tk.Frame(root, bg="white")
    courts_farme = tk.Frame(root, bg="white")
    jersey_farme = tk.Frame(root, bg="white")

    # 放入 grid 中，并设置每个 Frame 拉伸填满
    for frame in (balls_farme, courts_farme, jersey_farme):
        frame.grid(row=0, column=0, sticky="nsew")

    # 加载配置，并初始化各页面的本地路径（这里仅做路径设置）
    check_load_config()
    config = load_config()
    courts_farme.replace_folder = config.get("replace_folder", "")
    courts_farme.local_folder = config.get("local_folder", "")
    balls_farme.local_folder = config.get("balls_folder", "")
    jersey_farme.local_folder = config.get("jersey_folder", "")

    # 初始化页面 UI（各 display 函数只负责填充内容，不做 tkraise 操作）
    balls_page.display_balls_page(balls_farme)
    jersey_page.display_jersey_page(jersey_farme)
    courts_page.display_courts_page(courts_farme)

    # 构建统一页面管理字典
    pages = {
        "balls": {"frame": balls_farme, "display": balls_page.switch_to_balls_page},
        "courts": {"frame": courts_farme, "display": courts_page.switch_to_courts_page},
        "jersey": {"frame": jersey_farme, "display": jersey_page.switch_to_jersey_page},
    }

    # 默认显示球场页面
    switch_page("courts")

    # 注册快捷键
    hotkeys = {
        "shortcut_windows": toggle_visibility,
        "shortcut_onoff": partial(toggle_onoff, root, courts_farme),
        "shortcut_left": partial(move_left, root, courts_farme),
        "shortcut_right": partial(move_right, root, courts_farme),
    }
    for key, action in hotkeys.items():
        shortcut = config.get(key, '')
        if shortcut:
            keyboard.add_hotkey(shortcut, action)

    # 启动全局快捷键监听线程
    threading.Thread(target=start_listener, daemon=True).start()

    # 启动主循环
    root.mainloop()


if __name__ == "__main__":
    create_ui()
    root.mainloop()