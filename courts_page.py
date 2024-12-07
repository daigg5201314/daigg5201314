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
import ctypes
from config_floder import check_load_config,load_config,save_config
can_copy = True  # 默认允许点击
image_display_frame = None
image_labels = {} # 全局字典用于存储图片标签
current_index = -1 # 初始状态，没有图片被选中

def disable_ui_elements(courts_page):
    """禁用球场框架中除“开启/关闭”按钮外的其他按钮"""
    global can_copy
    can_copy = False  # 禁止点击图片
    print("球场框架已禁用，图片点击行为被禁止")
    if hasattr(courts_page, "button_frame") and courts_page.button_frame:  # 检查 button_frame 是否存在
        for child in courts_page.button_frame.winfo_children():  # 遍历 button_frame 内的所有组件
            if isinstance(child, tk.Button) and child.cget("text") not in ["开启", "关闭"]:
                child.config(state="disabled")  # 禁用非“开启/关闭”按钮
        courts_page.button_frame.config(bg="gray")  # 更改背景颜色以表示不可用状态


def enable_ui_elements(courts_page):
    """启用按钮和界面"""
    global can_copy
    can_copy = True  # 恢复点击图片
    print("球场框架已启用，图片点击行为恢复")
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
        if os.path.isdir(updated_path):
            print(f"目标路径已存在：{updated_path}，无需重命名")
            # messagebox.showwarning("路径冲突", f"目标路径已存在：{updated_path}")
        else:
            os.rename(original_path, updated_path)
            courts_package.local_folder = updated_path
            # print(f"路径成功修改为：{updated_path}")
    except OSError as e:
        # print(f"重命名路径失败：{e}")
        messagebox.showwarning("重命名失败", f"重命名路径失败：{e}")

def toggle_action(toggle_state,courts_page):
    """
    根据开关状态切换路径并控制界面交互。
    """
    if not hasattr(courts_page, "local_folder") or not courts_page.local_folder:
        print("当前未选择球场路径，无法切换状态")
        messagebox.showwarning("路径错误", "请先选择球场路径！")
        return

    original_path = courts_page.local_folder
    pattern_levels = r'\blevels\b'
    pattern_levels_stop = r'\blevels_stop\b'

    if toggle_state.get():  # 开启状态
        enable_ui_elements(courts_page)
        updated_path = re.sub(pattern_levels_stop, 'levels', original_path, count=1)
        rename_folder(courts_page, original_path, updated_path)
    else:  # 关闭状态
        disable_ui_elements(courts_page)
        updated_path = re.sub(pattern_levels, 'levels_stop', original_path, count=1)
        rename_folder(courts_page, original_path, updated_path)

# 切换开关
def toggle_onoff(root,courts_page):
    global toggle_state,toggle_button
    toggle_state.set(not toggle_state.get()),
    toggle_button.config(text="开启" if toggle_state.get() else "关闭"),
    toggle_action(toggle_state,courts_page)

    # 创建顶级窗口，用于显示消息
    click_label_window = tk.Toplevel(root)
    click_label_window.overrideredirect(True)  # 去掉窗口边框
    click_label_window.attributes("-topmost", True)  # 窗口置顶
    click_label_window.geometry("+0+0")  # 设置位置为屏幕左上角

    # 在顶级窗口中添加标签
    click_label = tk.Label(
        click_label_window,
        text=f"开关操作:{'开启' if toggle_state.get() else '关闭'}",
        bg="#4CAF50",
        fg="white",
        font=("楷体", 30, "bold"),
        relief="solid",
        padx=30,
        pady=15
    )
    click_label.pack()

    # 调用淡出功能
    fade_out_label(click_label_window)
    # print(f"开关操作 {'开启' if toggle_state.get() else '关闭'}")

def move_left(root,courts_page):
    switch_selection(root,courts_page,-1)
    print("左移操作")

def move_right(root,courts_page):
    switch_selection(root,courts_page,1)
    print("右移操作")

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
            print(f"Courts folder selected: {selected_folder}")

        elif folder_type == "local":
            courts_page.local_folder = selected_folder
            config["local_folder"] = selected_folder
            process_local_courts_files(courts_page)  # 处理本地球场的逻辑
            print(f"Local folder selected: {selected_folder}")

        save_config(config)  # 保存更新的配置
    else:
        print(f"No folder selected for {folder_type} files.")

def process_replace_courts_files(courts_page):
    print("Processing process_replace_court files...")

def process_local_courts_files(courts_page):
    """显示球场页面，并加载本地球场路径的图片"""
    global image_display_frame

    # 图片显示框架
    image_display_frame = tk.Frame(courts_page, bg="white")
    image_display_frame.pack(fill="both", expand=True, pady=10, padx=10)

    # 调用模块 1: 加载并显示图片
    display_court_images(courts_page,image_display_frame)

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

def display_court_images(courts_page,image_display_frame):
    """显示球场页面并加载本地球场路径的图片"""
    global court_images, image_labels, folder_paths

    # 清空旧的图像资源
    for label in image_labels.values():
        label.image = None  # 释放图片资源

    # 清空旧内容和全局变量
    court_images = []  # 用于存储球场图片和路径
    image_labels = {}  # 清空标签字典
    folder_paths = {}  # 保存文件夹路径用于复制操作
    image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')

    if hasattr(courts_page, 'replace_folder') and os.path.isdir(courts_page.replace_folder):
        for folder_name in os.listdir(courts_page.replace_folder):
            folder_path = os.path.join(courts_page.replace_folder, folder_name)
            if os.path.isdir(folder_path):
                for file_name in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file_name)
                    if file_name.lower().endswith(image_extensions):
                        try:
                            image = Image.open(file_path).convert("RGB")
                            image.thumbnail((180, 200))  # 缩略图大小
                            img = ImageTk.PhotoImage(image)
                            court_images.append((file_name, img, folder_path))
                            folder_paths[file_name] = folder_path
                        except Exception as e:
                            print(f"Failed to load image {file_path}: {e}")

        # 打印 court_images 的内容和个数
        print(f"Total images in court_images: {len(court_images)}")
        for idx, (court_file, img, folder_path) in enumerate(court_images):
            print(f"Image {idx + 1}: {court_file}, Folder: {folder_path}")
        
        # 清空显示框中的所有组件
        for widget in image_display_frame.winfo_children():
            widget.destroy()

        # 创建图片和标签的显示
        image_frame = tk.Frame(image_display_frame, bg="white")
        image_frame.grid(row=0, column=0, sticky="nsew")  # 使用 grid 布局

        # 为 grid 布局设置列和行的权重，确保显示区域自适应
        image_display_frame.grid_rowconfigure(0, weight=1)
        image_display_frame.grid_columnconfigure(0, weight=1)

        for idx, (court_file, img, folder_path) in enumerate(court_images):
            row_num = idx // 3
            col_num = idx % 3
            print(f"row_num={row_num},col_num={col_num}")
            frame = tk.Frame(image_frame, bg="white", padx=5, pady=5)
            frame.grid(row=row_num, column=col_num, sticky="nsew")  # 使用 grid 布局

            # 显示图片
            img_label = tk.Label(frame, image=img, bg="white", cursor="hand2")
            img_label.image = img  # 防止垃圾回收
            img_label.pack()
            img_label.bind(
                "<Button-1>",
                lambda event, src=folder_path: handle_image_click(courts_page,src)
            )

            # 显示名称（去掉后缀）
            file_name_without_ext = os.path.splitext(court_file)[0]
            name_label = tk.Label(frame, text=file_name_without_ext, bg="white", font=("楷体", 10))
            name_label.pack()

            # 将标签存入全局字典
            image_labels[file_name_without_ext] = name_label

        # 加载完成后高亮匹配的标签
        highlight_matching_images(courts_page)

    else:
        print("No valid folder selected or folder does not exist.")
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
        print("图片点击行为已被禁用")
        return

    if hasattr(courts_page, "local_folder") and courts_page.local_folder:
        copy_folder_contents(src_folder, courts_page.local_folder)
        highlight_matching_images(courts_page)
        show_copy_feedback(root,src_folder)
    else:
        print("目标路径未设置，请先选择球场替换路径！")
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

        print(f"Copied contents from {src_folder} to {dest_folder}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to copy file: {e}")

def highlight_matching_images(courts_page):
    """高亮显示与目标路径匹配的图片标签"""
    global current_index
    # 检查 replace_folder 属性是否存在且有效
    if not hasattr(courts_page, "local_folder") or not courts_page.local_folder or not os.path.isdir(courts_page.local_folder):
        print("目标路径未设置或无效，跳过高亮逻辑。")
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

def display_courts_page(courts_page):
    global toggle_state,toggle_button
    # 按钮布局框架
    button_frame = tk.Frame(courts_page, bg="white")
    button_frame.pack(side='top',fill="x",padx=10,pady=10)  # 使用 grid 布局
    print(f"来到球场界面")
    # # 加载配置文件
    config = load_config()

    # 初始化路径
    courts_page.replace_folder = config.get("replace_folder", "")
    courts_page.local_folder = config.get("local_folder", "")

    # 开关level按钮
    toggle_state = tk.BooleanVar(value=True)  # 初始状态为打开
    toggle_action(toggle_state,courts_page)
    toggle_button = tk.Button(
    button_frame,
    text="开启",
    command=lambda: [
        toggle_state.set(not toggle_state.get()),
        toggle_button.config(text="开启" if toggle_state.get() else "关闭"),
        toggle_action(toggle_state,courts_page)
    ],
    bg="#4CAF50",
        fg="white",
        relief="flat",
        font=("Arial", 10, "bold"),
        activebackground="#45a049"
    )
    toggle_button.pack(side='left', padx=10, pady=10)  # 使用 pack 布局放置第一个按钮（左对齐）
    # 选择替换路径按钮
    select_balls_button = tk.Button(
        button_frame,
        text="选择球场替换路径",
        command=lambda: select_folder(courts_page,"replace"),
        bg="#55A037",
        relief="ridge"
    )
    select_balls_button.pack(side='left', padx=10, pady=10, expand=True)  # 第二个按钮占据剩余空间，并居中
    # 选择本地路径按钮
    local_courts_button = tk.Button(
        button_frame,
        text="选择本地球场路径",
        command=lambda: select_folder(courts_page,"local"),
        bg="#FF8017",
        relief="ridge"
    )
    local_courts_button.pack(side='right', padx=10, pady=10)  # 使用 pack 布局放置第三个按钮（右对齐）

    #打印加载的路径并处理
    if courts_page.replace_folder:
        print(f"从配置加载的替换文件夹: {courts_page.replace_folder}")
        process_replace_courts_files(courts_page)  # 如果路径存在，直接处理球场文件

    if courts_page.local_folder:
        print(f"从配置加载的本地文件夹: {courts_page.local_folder}")
        process_local_courts_files(courts_page)  # 如果路径存在，直接处理本地球场文件