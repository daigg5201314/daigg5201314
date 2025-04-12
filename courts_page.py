import os
import stat
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
import ctypes
from config_floder import check_load_config,load_config,save_config
from debug_utils import debug_print

can_copy = True  # 默认允许点击
image_display_frame = None
image_labels = {} # 全局字典用于存储图片标签
current_index = -1 # 初始状态，没有图片被选中
feedback_window = None # 定义全局反馈窗口变量

# 如果全局未定义 image_cache，则初始化
try:
    image_cache
except NameError:
    image_cache = {}

def disable_ui_elements(courts_page):
    """禁用球场框架中除“开启/关闭”按钮外的其他按钮"""
    global can_copy
    can_copy = False  # 禁止点击图片
    debug_print("球场框架已禁用，图片点击行为被禁止")
    if hasattr(courts_page, "button_frame") and courts_page.button_frame:  # 检查 button_frame 是否存在
        for child in courts_page.button_frame.winfo_children():  # 遍历 button_frame 内的所有组件
            if isinstance(child, tk.Button) and child.cget("text") not in ["开启", "关闭"]:
                child.config(state="disabled")  # 禁用非“开启/关闭”按钮
        courts_page.button_frame.config(bg="gray")  # 更改背景颜色以表示不可用状态


def enable_ui_elements(courts_page):
    """启用按钮和界面"""
    global can_copy
    can_copy = True  # 恢复点击图片
    debug_print("球场框架已启用，图片点击行为恢复")
    if hasattr(courts_page, "button_frame") and courts_page.button_frame:  # 检查 button_frame 是否存在
        for child in courts_page.button_frame.winfo_children():  # 启用 button_frame 内的所有组件
            if isinstance(child, tk.Button):
                child.config(state="normal")
        courts_page.button_frame.config(bg="white")  # 恢复背景颜色

def rename_folder(courts_package,original_path, updated_path):
    """
    尝试重命名文件夹，并更新 local_folder 属性。
    """
    try:
        os.rename(original_path, updated_path)
        courts_package.local_folder = updated_path
        debug_print(f"路径成功修改为：{updated_path}")
    except OSError as e:
        # debug_print(f"重命名路径失败：{e}")
        messagebox.showwarning("重命名失败", f"重命名路径失败：{e}")

def toggle_action(toggle_state, courts_page):
    """
    根据开关状态切换路径并控制界面交互。
    """

    original_path = courts_page.local_folder
    debug_print(f"传入的路径: {original_path}")

    # 提取父目录和当前目录名
    parent_dir = os.path.dirname(original_path)
    current_dir = os.path.basename(original_path)

    try:
        # 根据开关状态生成目标目录名
        if toggle_state.get():  # 开启状态：目标目录名为 "levels"
            target_dir = "levels"
        else:  # 关闭状态：目标目录名为 "levels_stop"
            target_dir = "levels_stop"

        # 如果当前目录名与目标目录名不一致，则需要重命名
        if current_dir != target_dir:
            updated_path = os.path.join(parent_dir, target_dir)

            # 如果目标路径已存在，则更新 local_folder 指向目标路径并保存配置
            if os.path.exists(updated_path):
                courts_page.local_folder = updated_path
                config = load_config()
                config["local_folder"] = updated_path
                save_config(config)
                debug_print(f"目标路径已存在，直接使用现有路径: {updated_path}")
                return

            # 否则，进行重命名
            config = load_config()  # 加载现有配置
            os.rename(original_path, updated_path)
            courts_page.local_folder = updated_path  
            config["local_folder"] = updated_path  # 更新记录的路径
            save_config(config)
            debug_print(f"路径已更新: {original_path} -> {updated_path}")
        else:
            debug_print("路径无需更新，当前路径与目标路径一致")

    except Exception as e:
        messagebox.showerror("错误", f"操作失败: {str(e)}")

# 切换开关
def toggle_onoff(root, courts_page):
    """# 切换开关状态（这一步可以直接在当前线程更新变量）"""
    global toggle_state, toggle_button
    new_state = not toggle_state.get()
    toggle_state.set(new_state)
    debug_print(f"开关状态已切换为: {'开启' if toggle_state.get() else '关闭'}")
    
    # 将所有 tkinter 操作放入主线程调用
    root.after(0, lambda: (
        toggle_button.config(text="开启" if toggle_state.get() else "关闭"),
        toggle_action(toggle_state, courts_page),
        show_feedback(root, f"开关操作:{'开启' if toggle_state.get() else '关闭'}")
    ))

def show_feedback(root, message):
    """显示反馈信息，并执行淡出效果"""
    global feedback_window
    # 如果已有窗口，则先销毁
    if feedback_window is not None:
        feedback_window.destroy()
    feedback_window = tk.Toplevel(root)
    feedback_window.overrideredirect(True)      # 去掉窗口边框
    feedback_window.attributes("-topmost", True)  # 保持置顶
    feedback_window.geometry("+0+0")              # 固定在屏幕左上角

    label = tk.Label(
        feedback_window,
        text=message,
        bg="#E60000",
        fg="white",
        font=("楷体", 30, "bold"),
        relief="solid",
        padx=30,
        pady=15
    )
    label.pack()

    # 调用淡出效果，初始透明度为3.0
    fade_out_label(feedback_window)

def move_left(root,courts_page):
    switch_selection(root,courts_page,-1)
    debug_print("左移操作")

def move_right(root,courts_page):
    switch_selection(root,courts_page,1)
    debug_print("右移操作")

def select_folder(courts_page,folder_type):
    """
    通用路径选择函数。
    根据类型选择路径，并调用对应的处理逻辑，同时保存路径到配置文件。
    """
    selected_folder = filedialog.askdirectory(title=f"Select replacement path for {folder_type} files")
    if selected_folder:
        config = load_config()  # 加载现有配置

        if folder_type == "replace":
            courts_page.replace_folder = selected_folder
            config["replace_folder"] = selected_folder
            process_replace_courts_files(courts_page)  # 处理替换球场的逻辑
            debug_print(f"Courts folder selected: {selected_folder}")

        elif folder_type == "local":
            courts_page.local_folder = selected_folder
            config["local_folder"] = selected_folder
            process_local_courts_files(courts_page)  # 处理本地球场的逻辑
            debug_print(f"Local folder selected: {selected_folder}")

        save_config(config)  # 保存更新的配置
    else:
        debug_print(f"No folder selected for {folder_type} files.")

def process_replace_courts_files(courts_page):
    debug_print("Processing process_replace_court files...")

def process_local_courts_files(courts_page):
    """更新本地球场页面，并加载本地球场路径的图片，不重新创建显示页面"""
    global image_display_frame
    # 如果全局的 image_display_frame 已存在且有效，清空其子组件，否则创建新的 Frame
    if image_display_frame is None or not image_display_frame.winfo_exists():
        image_display_frame = tk.Frame(courts_page, bg="white")
        image_display_frame.pack(fill="both", expand=True, pady=10, padx=10)
    else:
        # 清空显示框中的所有组件，释放原有控件资源
        for widget in image_display_frame.winfo_children():
            widget.destroy()
    # 调用模块 1: 加载并显示图片
    display_court_images(courts_page, image_display_frame)
    # ✅ 新增：路径验证和同步 toggle 状态
    validate_local_folder(courts_page)
    # ✅ 同步更新按钮文本
    toggle_button.config(text="开启" if toggle_state.get() else "关闭")

def switch_selection(root,courts_page,direction):
    """切换选项"""
    global current_index, court_images

    if not court_images:  # 如果没有加载图片，直接返回====-
        return

    # 取消当前高亮
    if 0 <= current_index < len(court_images):
        deselect_current_option()

    # 更新索引
    current_index = (current_index + direction) % len(court_images)

    # 高亮新选项
    highlight_current_option(root,courts_page)

def deselect_current_option():
    """取消当前选项的高亮"""
    global current_index, court_images, image_labels

    if 0 <= current_index < len(court_images):
        court_file, _, _ = court_images[current_index]
        file_name_without_ext = os.path.splitext(court_file)[0]
        if file_name_without_ext in image_labels:
            image_labels[file_name_without_ext].config(bg="white")  # 恢复默认背景色

def highlight_current_option(root,courts_page):
    """高亮当前选中的选项"""
    global current_index, court_images, image_labels

    if 0 <= current_index < len(court_images):
        court_file, _, folder_path = court_images[current_index]
        file_name_without_ext = os.path.splitext(court_file)[0]

        if file_name_without_ext in image_labels:
            image_labels[file_name_without_ext].config(bg="#4CAF50")  # 设置高亮背景色

        # 自动模拟点击事件
        handle_image_click(root,courts_page,folder_path)

def load_image_cached(file_path):
    """
    尝试从缓存中读取图片，如果未加载则打开图片、生成缩略图、生成 PhotoImage 对象，
    并保存到缓存中。返回 PhotoImage 对象或 None。
    """
    global image_cache
    if file_path in image_cache:
        return image_cache[file_path]
    try:
        image = Image.open(file_path).convert("RGB")
        image.thumbnail((180, 200))  # 设定缩略图大小
        img = ImageTk.PhotoImage(image)
        image.close()  # 关闭打开的文件句柄
        image_cache[file_path] = img
        return img
    except Exception as e:
        debug_print(f"Failed to load image {file_path}: {e}")
        return None

def display_court_images(courts_page, image_display_frame):
    """显示球场页面并加载本地球场路径的图片，采用缓存策略优化加载速度和资源占用"""
    global court_images, image_labels, folder_paths, image_cache

    # 重置图片、标签和文件夹路径的数据结构
    court_images = []   # 存储 (文件名, PhotoImage 对象, 对应文件夹)
    image_labels = {}   # 按图片名称保存 Label 控件（用于后续高亮更新）
    folder_paths = {}   # 记录每个文件对应的文件夹路径
    image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')

    # 判断目标文件夹是否存在
    if hasattr(courts_page, 'replace_folder') and os.path.isdir(courts_page.replace_folder):
        # 遍历替换文件夹下的子文件夹中的图片文件
        for folder_name in os.listdir(courts_page.replace_folder):
            folder_path = os.path.join(courts_page.replace_folder, folder_name)
            if os.path.isdir(folder_path):
                for file_name in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file_name)
                    if file_name.lower().endswith(image_extensions):
                        img = load_image_cached(file_path)
                        if img is not None:
                            court_images.append((file_name, img, folder_path))
                            folder_paths[file_name] = folder_path

        debug_print(f"Total images in court_images: {len(court_images)}")
        for idx, (court_file, img, folder_path) in enumerate(court_images):
            debug_print(f"Image {idx + 1}: {court_file}, Folder: {folder_path}")

        # 清空显示区域中的所有旧控件
        for widget in image_display_frame.winfo_children():
            widget.destroy()

        # 创建一个容器 Frame，并设置布局自适应
        image_frame = tk.Frame(image_display_frame, bg="white")
        image_frame.grid(row=0, column=0, sticky="nsew")
        image_display_frame.grid_rowconfigure(0, weight=1)
        image_display_frame.grid_columnconfigure(0, weight=1)

        # 遍历 court_images 动态创建图片显示控件
        for idx, (court_file, img, folder_path) in enumerate(court_images):
            row_num = idx // 3
            col_num = idx % 3
            debug_print(f"row_num={row_num}, col_num={col_num}")
            frame = tk.Frame(image_frame, bg="white", padx=5, pady=5)
            frame.grid(row=row_num, column=col_num, sticky="nsew")

            # 图片控件
            img_label = tk.Label(frame, image=img, bg="white", cursor="hand2")
            img_label.image = img  # 防止图片被垃圾回收
            img_label.pack()
            # 注意：lambda 中的参数默认值会捕获当前 folder_path
            img_label.bind(
                "<Button-1>",
                lambda event, src=folder_path, rt=courts_page.master: handle_image_click(rt, courts_page, src)
            )

            # 文件名标签（去除扩展名）
            file_name_without_ext = os.path.splitext(court_file)[0]
            name_label = tk.Label(frame, text=file_name_without_ext, bg="white", font=("楷体", 10))
            name_label.pack()

            # 将标签存入全局字典（用于后续高亮匹配更新）
            image_labels[file_name_without_ext] = name_label

        # 调用高亮函数，更新匹配标签的样式
        highlight_matching_images(courts_page)
    else:
        debug_print("No valid folder selected or folder does not exist.")
        for widget in image_display_frame.winfo_children():
            widget.destroy()
        tk.Label(
            image_display_frame,
            text="请先选择本地球场路径以加载图片。",
            bg="white",
            fg="red"
        ).pack(pady=20)
    image_display_frame.update_idletasks()

def handle_image_click(root,courts_page,src_folder):
    """处理图片点击事件并复制内容"""
    if not can_copy:
        debug_print("图片点击行为已被禁用")
        return

    if hasattr(courts_page, "local_folder") and courts_page.local_folder:
        copy_folder_contents(src_folder, courts_page.local_folder)
        highlight_matching_images(courts_page)
        show_copy_feedback(root,src_folder)
    else:
        debug_print("目标路径未设置，请先选择球场替换路径！")
        messagebox.showwarning("路径错误", "请先选择球场替换路径！")

def show_copy_feedback(root,src_folder):
    """显示复制完成的反馈消息"""
    click_label_window = tk.Toplevel(root)
    click_label_window.overrideredirect(True)  # 去掉窗口边框
    click_label_window.attributes("-topmost", True)  # 窗口置顶
    click_label_window.geometry("+0+0")  # 设置位置为屏幕左上角

    click_label = tk.Label(
        click_label_window,
        text=f"已载入: {os.path.basename(src_folder)}",
        bg="#4CAF50",
        fg="white",
        font=("楷体", 30, "bold"),
        relief="solid",
        padx=30,
        pady=15
    )
    click_label.pack()

    fade_out_label(click_label_window)  # 调用淡出功能

def fade_out_label(window, alpha=3.0):
    """逐渐减少标签的透明度，直到完全消失"""
    if alpha > 0:
        alpha -= 0.1
        window.attributes("-alpha", alpha)  # 设置窗口透明度
        window.after(100, lambda: fade_out_label(window, alpha))  # 递归调用
    else:
        window.destroy()  # 完全消失后销毁窗口

def delete_existing_files(dest_folder):
    """删除目标文件夹中指定的文件"""
    files_to_delete = [
        "arena_blacktop_ext.iff",
        "arena_blacktop_ext_floor.iff"
    ]
    image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
    
    for item in os.listdir(dest_folder):
        item_path = os.path.join(dest_folder, item)
        try:
            # 如果是只读文件，先修改权限（例如777是完全权限）
            if os.path.isfile(item_path):
                os.chmod(item_path, stat.S_IWRITE)
            if os.path.isfile(item_path) and item in files_to_delete:
                os.remove(item_path)
                debug_print(f"Deleted {item} from {dest_folder}")
            elif item.lower().endswith(image_extensions):
                os.remove(item_path)
                debug_print(f"Deleted {item} from {dest_folder}")
        except Exception as e:
            debug_print(f"Error deleting file {item_path}: {e}")

def copy_folder_contents(src_folder, dest_folder):
    """将源文件夹中的内容复制到目标文件夹，不包括源文件夹本身"""
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)  # 如果目标路径不存在，创建它

    delete_existing_files(dest_folder)  # 删除目标路径中的现有文件

    try:
        for item in os.listdir(src_folder):
            src_path = os.path.join(src_folder, item)
            dest_path = os.path.join(dest_folder, item)

            if os.path.isdir(src_path):
                shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
            else:
                shutil.copy2(src_path, dest_path)

        debug_print(f"Copied contents from {src_folder} to {dest_folder}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to copy file: {e}")

def highlight_matching_images(courts_page):
    """高亮显示与目标路径匹配的图片标签"""
    global current_index
    # 检查 replace_folder 属性是否存在且有效
    if not hasattr(courts_page, "local_folder") or not courts_page.local_folder or not os.path.isdir(courts_page.local_folder):
        debug_print("目标路径未设置或无效，跳过高亮逻辑。")
        return

    # 获取目标文件夹中的所有图片名称（去掉扩展名）
    matching_names = {
        os.path.splitext(file_name)[0]
        for file_name in os.listdir(courts_page.local_folder)
        if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))
    }

    # 遍历标签字典，更新标签样式
    for idx, (name, label) in enumerate(image_labels.items()):
        if name in matching_names:
            label.config(bg="yellow", font=("楷体", 10, "bold"))
            current_index = idx
        else:
            label.config(bg="white", font=("楷体", 10))

def validate_local_folder(courts_page):
    """
    校验配置中读取的 local_folder 路径，并自动设置 toggle 状态
    """
    global toggle_state

    folder = courts_page.local_folder
    if not folder or not os.path.exists(folder):
        messagebox.showwarning("路径无效", "配置文件中的 mods 路径不存在，请重新选择！")
        return

    dir_name = os.path.basename(folder)
    if "levels" not in dir_name:
        messagebox.showwarning("路径错误", "路径名必须包含 'levels'，请重新选择正确路径！")
        return

    if dir_name == "levels":
        toggle_state.set(True)
    elif dir_name == "levels_stop":
        toggle_state.set(False)
    else:
        messagebox.showwarning("路径异常", f"路径名称应为 'levels' 或 'levels_stop'，当前为: {dir_name}")

def display_courts_page(courts_page):
    global toggle_state, toggle_button

    debug_print(f"来到球场界面")

    # 清空页面已有内容，防止重复加载
    for widget in courts_page.winfo_children():
        widget.destroy()

    # 按钮布局框架
    button_frame = tk.Frame(courts_page, bg="white")
    button_frame.pack(side='top', fill="x", padx=10, pady=10)

    # 读取配置并设置路径
    config = load_config()
    courts_page.replace_folder = config.get("replace_folder", "")
    courts_page.local_folder = config.get("local_folder", "")

    # 初始化开关
    toggle_state = tk.BooleanVar()
    validate_local_folder(courts_page)  # 根据路径设置 toggle 状态

    # ✅ 创建 toggle 按钮（状态已由上面更新）
    toggle_button = tk.Button(
        button_frame,
        text="开启" if toggle_state.get() else "关闭",
        command=lambda: [
            toggle_state.set(not toggle_state.get()),
            toggle_button.config(text="开启" if toggle_state.get() else "关闭"),
            toggle_action(toggle_state, courts_page)
        ],
        bg="#4CAF50",
        fg="white",
        relief="flat",
        font=("Arial", 10, "bold"),
        activebackground="#45a049"
    )
    toggle_button.pack(side='left', padx=10, pady=10)

    # 替换路径按钮
    select_balls_button = tk.Button(
        button_frame,
        text="选择街球场路径",
        command=lambda: select_folder(courts_page, "replace"),
        bg="#55A037",
        relief="ridge"
    )
    select_balls_button.pack(side='left', padx=10, pady=10, expand=True)

    # 本地 levels 路径按钮
    local_courts_button = tk.Button(
        button_frame,
        text="选择levels路径",
        command=lambda: select_folder(courts_page, "local"),
        bg="#FF8017",
        relief="ridge"
    )
    local_courts_button.pack(side='right', padx=10, pady=10)

    # ❗✅ 页面只加载控件，**不主动执行路径控制逻辑**
    # 不再执行 toggle_action / process_local_courts_files 自动逻辑
    # 保证页面切换时是纯展示，行为留给用户操作或 create_ui 控制