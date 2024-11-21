import os
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
import sys
import threading
import keyboard
from collections import OrderedDict
import re
import json

# Global variables
is_visible = True
listener = None
image_cache = OrderedDict()
visible_rows = set()
can_copy = True  # 默认允许点击
image_labels = {} # 全局字典用于存储图片标签
CONFIG_FILE = "config.json"
# 全局变量存储路径
paths = {
    "local_folder": None,
    "courts_folder": None
}

def load_config():
    """加载嵌入的配置文件"""
    config_path = resource_path("config.json")  # 获取配置文件路径
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}  # 如果配置文件不存在，返回空字典

def save_config(config):
    """保存配置到文件"""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        print("Configuration saved successfully.")
    except Exception as e:
        print(f"Error saving config: {e}")

def fade_out_label(window, alpha=3.0):
    """逐渐减少标签的透明度，直到完全消失"""
    if alpha > 0:
        alpha -= 0.1
        window.attributes("-alpha", alpha)  # 设置窗口透明度
        window.after(100, lambda: fade_out_label(window, alpha))  # 递归调用
    else:
        window.destroy()  # 完全消失后销毁窗口


# Check resource path
def resource_path(relative_path):
    """ 获取资源文件的正确路径，在开发和打包后都能正常访问 """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def switch_page(page_type):
    # 清除当前界面
    for widget in frame_main.winfo_children():
        widget.destroy()

    if page_type == "balls":
       print("don't basketball files...")
    elif page_type == "courts":
        display_courts_page()

from tkinter import filedialog

def select_folder(folder_type):
    """
    通用路径选择函数。
    根据类型选择路径，并调用对应的处理逻辑，同时保存路径到配置文件。
    """
    selected_folder = filedialog.askdirectory(title=f"Select replacement path for {folder_type} files")
    if selected_folder:
        config = load_config()  # 加载现有配置

        if folder_type == "balls":
            root.balls_folder = selected_folder
            config["balls_folder"] = selected_folder
            process_balls_files()  # 处理篮球文件的逻辑
            print(f"Balls folder selected: {selected_folder}")

        elif folder_type == "courts":
            root.courts_folder = selected_folder
            config["courts_folder"] = selected_folder
            process_courts_files()  # 处理球场文件的逻辑
            print(f"Courts folder selected: {selected_folder}")

        elif folder_type == "local":
            root.local_folder = selected_folder
            config["local_folder"] = selected_folder
            process_local_courts_files()  # 处理本地球场的逻辑
            print(f"Local folder selected: {selected_folder}")

        save_config(config)  # 保存更新的配置
    else:
        print(f"No folder selected for {folder_type} files.")


def process_balls_files():
    print("Processing basketball files...")

def process_courts_files():
    print("Processing courts files...")

def delete_existing_files(dest_folder):
    """删除目标文件夹中指定的文件"""
    # 定义需要检查并删除的文件名模式
    files_to_delete = [
        "arena_blacktop_ext.iff",
        "arena_blacktop_ext_floor.iff"
    ]
    # 定义需要删除的图片扩展名
    image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')

    # 遍历文件夹内容，删除匹配的文件
    try:
        for item in os.listdir(dest_folder):
            item_path = os.path.join(dest_folder, item)
            if os.path.isfile(item_path) and item in files_to_delete:
                os.remove(item_path)  # 删除文件
                print(f"Deleted {item} from {dest_folder}")
            elif item.lower().endswith(image_extensions):  # 删除图片文件
                os.remove(item_path)
                print(f"Deleted {item} from {dest_folder}")
    except Exception as e:
        print(f"Error deleting files: {e}")

def process_local_courts_files():
    """显示球场页面，并加载本地球场路径的图片"""
    global img_label, name_label

    # 图片显示框架
    image_display_frame = tk.Frame(frame_main, bg="white")
    image_display_frame.pack(fill="both", expand=True, pady=10, padx=10)

    # 如果 local_folder 属性存在且有效
    if hasattr(root, 'local_folder') and os.path.isdir(root.local_folder):
        court_images = []  # 用于存储球场图片和路径
        folder_paths = {}  # 保存文件夹路径用于复制操作
        image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')

        for folder_name in os.listdir(root.local_folder):
            folder_path = os.path.join(root.local_folder, folder_name)
            if os.path.isdir(folder_path):
                for file_name in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file_name)
                    if file_name.lower().endswith(image_extensions):
                        try:
                            image = Image.open(file_path)
                            image.thumbnail((180, 200))  # 缩略图大小
                            img = ImageTk.PhotoImage(image)
                            court_images.append((file_name, img, folder_path))
                            folder_paths[file_name] = folder_path
                        except Exception as e:
                            print(f"Failed to load image {file_path}: {e}")

        print(f"Loaded {len(court_images)} images for display.")  # 调试信息

        def handle_copy_event(src_folder):
            """处理图片点击事件并复制内容"""
            if not can_copy:
                print("图片点击行为已被禁用")
                return
            if hasattr(root, "courts_folder") and root.courts_folder:
                copy_folder_contents(src_folder, root.courts_folder)
                highlight_matching_images()

                # 创建顶级窗口，用于显示消息
                click_label_window = tk.Toplevel(root)
                click_label_window.overrideredirect(True)  # 去掉窗口边框
                click_label_window.attributes("-topmost", True)  # 窗口置顶
                click_label_window.geometry("+0+0")  # 设置位置为屏幕左上角

                # 在顶级窗口中添加标签
                click_label = tk.Label(
                    click_label_window,
                    text=f"已复制: {os.path.basename(src_folder)}",
                    bg="#4CAF50",
                    fg="white",
                    font=("Arial", 36, "bold"),
                    relief="solid",
                    padx=30,
                    pady=15
                )
                click_label.pack()

                # 调用淡出功能
                fade_out_label(click_label_window)
            else:
                print("目标路径未设置，请先选择球场替换路径！")
                messagebox.showwarning("路径错误", "请先选择球场替换路径！")

        def copy_folder_contents(src_folder, dest_folder):
            """将源文件夹中的内容复制到目标文件夹，不包括源文件夹本身"""
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)  # 如果目标路径不存在，创建它

            delete_existing_files(dest_folder)

            try:
                for item in os.listdir(src_folder):
                    src_path = os.path.join(src_folder, item)
                    dest_path = os.path.join(dest_folder, item)

                    if os.path.isdir(src_path):
                        shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src_path, dest_path)

                print(f"Copied contents from {src_folder} to {dest_folder}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy file: {e}")

        for idx, (court_file, img, folder_path) in enumerate(court_images):
            row_num = idx // 3
            col_num = idx % 3

            frame = tk.Frame(image_display_frame, bg="white", padx=5, pady=5)
            frame.grid(row=row_num, column=col_num, sticky="nsew")

            # 显示图片
            img_label = tk.Label(frame, image=img, bg="white", cursor="hand2")
            img_label.image = img  # 防止垃圾回收
            img_label.pack()
            img_label.bind(
                "<Button-1>",
                lambda event, src=folder_path: handle_copy_event(src)
            )

            # 显示名称（去掉后缀）
            file_name_without_ext = os.path.splitext(court_file)[0]  # 去掉文件后缀
            name_label = tk.Label(frame, text=file_name_without_ext, bg="white", font=("Arial", 10))
            name_label.pack()

            # 将标签存入全局字典
            image_labels[file_name_without_ext] = name_label

        # 加载完成后高亮匹配的标签
        highlight_matching_images()
    else:
        print("No valid folder selected or folder does not exist.")  # 调试信息
        tk.Label(
            image_display_frame,
            text="请先选择本地球场路径以加载图片。",
            bg="white",
            fg="red"
        ).pack(pady=20)

    image_display_frame.update_idletasks()
    print("Display courts page update completed.")  # 完成调试信息


def highlight_matching_images():
    """高亮显示与目标路径匹配的图片标签"""
    # 检查 courts_folder 属性是否存在且有效
    if not hasattr(root, "courts_folder") or not root.courts_folder or not os.path.isdir(root.courts_folder):
        print("目标路径未设置或无效，跳过高亮逻辑。")
        return

    # 获取目标文件夹中的所有图片名称（去掉扩展名）
    matching_names = {
        os.path.splitext(file_name)[0]
        for file_name in os.listdir(root.courts_folder)
        if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))
    }

    # 遍历标签字典，更新标签样式
    for name, label in image_labels.items():
        if name in matching_names:
            label.config(bg="yellow", font=("Arial", 12, "bold"))
        else:
            label.config(bg="white", font=("Arial", 10))


def disable_ui_elements():
    """禁用球场框架中除“开启/关闭”按钮外的其他按钮"""
    global can_copy
    can_copy = False  # 禁止点击图片
    print("球场框架已禁用，图片点击行为被禁止")
    if hasattr(root, "button_frame") and root.button_frame:  # 检查 button_frame 是否存在
        for child in root.button_frame.winfo_children():  # 遍历 button_frame 内的所有组件
            if isinstance(child, tk.Button) and child.cget("text") not in ["开启", "关闭"]:
                child.config(state="disabled")  # 禁用非“开启/关闭”按钮
        root.button_frame.config(bg="gray")  # 更改背景颜色以表示不可用状态
    print("球场框架已禁用（保留开启/关闭按钮）")


def enable_ui_elements():
    """启用按钮和界面"""
    global can_copy
    can_copy = True  # 恢复点击图片
    print("球场框架已启用，图片点击行为恢复")
    if hasattr(root, "button_frame") and root.button_frame:  # 检查 button_frame 是否存在
        for child in root.button_frame.winfo_children():  # 启用 button_frame 内的所有组件
            if isinstance(child, tk.Button):
                child.config(state="normal")
        root.button_frame.config(bg="white")  # 恢复背景颜色
    print("球场框架已启用")

def toggle_action(toggle_state):
    if hasattr(root, "courts_folder") and root.courts_folder:  # 确保路径存在
        original_path = root.courts_folder
        
        # 正则表达式匹配完整单词 'levels' 和 'levels_stop'
        pattern_levels = r'\blevels\b'
        pattern_levels_stop = r'\blevels_stop\b'

        if toggle_state.get():  # 开启状态，修改为 'levels'
            print("切换已开启")
            # 启用按钮和界面
            enable_ui_elements()

            # 如果路径中有 'levels_stop'，替换为 'levels'
            if re.search(pattern_levels_stop, original_path):  # 检查是否包含完整的 'levels_stop'
                updated_path = re.sub(pattern_levels_stop, 'levels', original_path, count=1)  # 只替换第一个 'levels_stop'
                try:
                    os.rename(original_path, updated_path)
                    root.courts_folder = updated_path
                    print(f"当前球场路径已修改为：{root.courts_folder}")
                except OSError as e:
                    print(f"重命名文件夹失败：{e}")
            else:
                print(f"路径已是 'levels'，无需修改：{original_path}")
                
        else:  # 关闭状态，修改为 'levels_stop'
            print("切换已关闭")
            # 禁用按钮和界面
            disable_ui_elements()

            # 如果路径中有 'levels'，替换为 'levels_stop'
            if re.search(pattern_levels, original_path):  # 检查是否包含完整的 'levels'
                updated_path = re.sub(pattern_levels, 'levels_stop', original_path, count=1)  # 只替换第一个 'levels'
                try:
                    os.rename(original_path, updated_path)
                    root.courts_folder = updated_path
                    print(f"当前球场路径已修改为：{root.courts_folder}")
                except OSError as e:
                    print(f"重命名文件夹失败：{e}")
            else:
                print(f"路径已是 'levels_stop'，无需修改：{original_path}")
    else:
        print("请先选择球场路径")


def display_courts_page():
    # 按钮布局框架
    root.button_frame = tk.Frame(frame_main, bg="white")
    root.button_frame.pack(fill="x", pady=10)
    root.buttons = []  # 全局按钮列表
    # 开关level按钮
    toggle_state = tk.BooleanVar(value=True)  # 初始状态为关闭
    toggle_action(toggle_state)
    toggle_button = tk.Button(
    root.button_frame,
    text="开启",
    command=lambda: [
        toggle_state.set(not toggle_state.get()),
        toggle_button.config(text="开启" if toggle_state.get() else "关闭"),
        toggle_action(toggle_state)
    ],
    bg="#4CAF50",
        fg="white",
        relief="flat",
        font=("Arial", 10, "bold"),
        activebackground="#45a049"
    )
    toggle_button.place(relx=0.0, rely=0.0, anchor="nw", x=10, y=10)

    # 选择替换路径按钮
    select_balls_button = tk.Button(
        root.button_frame,
        text="选择球场替换路径",
        command=lambda: select_folder("courts"),
        bg="#55A037",
        relief="ridge"
    )
    select_balls_button.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)
    root.buttons.append(select_balls_button)
    # 选择本地路径按钮
    local_courts_button = tk.Button(
        root.button_frame,
        text="选择本地球场路径",
        command=lambda: select_folder("local"),
        bg="#FF8017",
        relief="ridge"
    )
    local_courts_button.pack(side="top", pady=10)
    root.buttons.append(local_courts_button)

    # 加载配置文件
    config = load_config()
    print("Loaded configuration:", config)  # 调试信息，输出加载的配置

    # 初始化路径
    root.balls_folder = config.get("balls_folder", "")
    root.courts_folder = config.get("courts_folder", "")
    root.local_folder = config.get("local_folder", "")

    # 打印加载的路径并处理
    if root.balls_folder:
        print(f"Balls folder loaded from config: {root.balls_folder}")
        process_balls_files()  # 如果路径存在，直接处理篮球文件

    if root.courts_folder:
        print(f"Courts folder loaded from config: {root.courts_folder}")
        process_courts_files()  # 如果路径存在，直接处理球场文件

    if root.local_folder:
        print(f"Local folder loaded from config: {root.local_folder}")
        process_local_courts_files()  # 如果路径存在，直接处理本地球场文件

# 切换窗口显示
def toggle_visibility():
    global is_visible
    is_visible = not is_visible
    root.after(0, update_visibility)  # 在主线程中更新 UI

# 更新显示状态
def update_visibility():
    if is_visible:
        root.deiconify()  # 显示窗口
        root.attributes('-topmost', True)  # 置顶窗口
    else:
        root.withdraw()  # 隐藏窗口
    print(f"UI visibility is now {'visible' if is_visible else 'hidden'}")

# 注册或更新快捷键
def update_hotkey(shortcut):
    config = load_config()  # 加载现有配置
    old_shortcut = config.get('shortcut', '')  # 获取旧的快捷键
    print(f"读取旧的快捷键: {old_shortcut}")
    if old_shortcut and old_shortcut != shortcut:
        try:
            # 移除旧的快捷键，如果已经注册
            keyboard.remove_hotkey(old_shortcut)
        except KeyError:
            pass  # 如果快捷键未注册，则跳过，不抛出异常

    config['shortcut'] = shortcut  # 保存新的快捷键
    save_config(config)  # 保存更新后的配置到文件

    # 直接注册新的快捷键
    keyboard.add_hotkey(shortcut, toggle_visibility)
    print(f"保存新的快捷键: {shortcut}")

# 启动快捷键监听线程
def start_listener():
    keyboard.wait()  # 等待用户按下快捷键

# 打开设置窗口
def open_settings():
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("300x150")
    settings_window.attributes('-topmost', True)

    # 保存用户设置的快捷键
    def save_shortcut():
        shortcut = entry_shortcut.get()
        if shortcut:
            update_hotkey(shortcut)  # 更新快捷键
            settings_window.destroy()  # 关闭设置窗口

    label = tk.Label(settings_window, text="Custom shortcut (e.g <alt+r>):")
    label.pack(pady=10)

    entry_shortcut = tk.Entry(settings_window)
    # 默认加载已保存的快捷键，如果没有保存过，显示空白
    config = load_config()
    custom_shortcut = config.get('shortcut', '')  # 从配置文件加载快捷键
    print(f"从settings读取的快捷键: {custom_shortcut}")
    entry_shortcut.insert(0, custom_shortcut)
    entry_shortcut.pack(pady=5)

    button_save = ttk.Button(settings_window, text="Save", command=save_shortcut)
    button_save.pack(pady=10)

# 创建主窗口
def create_ui():
    global root,canvas,frame_main,progress_frame,progress_bar,progress_var
    root = tk.Tk()
    root.title("切换页面示例")
    root.geometry("600x600")
    root.local_folder = None  # 本地球场路径
    root.courts_folder = None  # 替换球场路径

    # 创建菜单栏
    menubar = tk.Menu(root)
    root.config(menu=menubar,bg="#ADD8E6")

    # 添加菜单项
    menubar = tk.Menu(root, bg="#66CDAA")
    menubar.add_command(label="⚙️ 设置",command=open_settings)
    menubar.add_command(label="球场", command=lambda: switch_page("courts"))
    root.config(menu=menubar)

    # 创建主框架
    frame_main = tk.Frame(root, bg="white")
    frame_main.pack(fill="both", expand=True)

    config = load_config()
    cur_short = config.get('shortcut', '')
    print(f"第一次启动读取: {cur_short}")
    # 注册快捷键
    keyboard.add_hotkey(cur_short, toggle_visibility)
    # 启动监听器线程
    threading.Thread(target=start_listener, daemon=True).start()

if __name__ == "__main__":
    create_ui()
    root.mainloop()