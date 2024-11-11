import os
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
import sys
import threading
from pynput import keyboard
from collections import OrderedDict

# Check resource path
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Global variables
is_visible = True
listener = None
image_cache = OrderedDict()
visible_rows = set()
custom_shortcut = '<F8>'

# Load image and cache it
def load_image(image_path):
    try:
        if image_path in image_cache:
            image_cache.move_to_end(image_path)
            return image_cache[image_path]
        
        img = Image.open(image_path)
        img = img.resize((100, 100))
        img_tk = ImageTk.PhotoImage(img)
        
        # Limit the cache size to 10
        if len(image_cache) >= 10:
            image_cache.popitem(last=False)
        
        image_cache[image_path] = img_tk
        return img_tk
    except Exception as e:
        print(f"Failed to load image: {image_path}, Error: {e}")
        return None

# Handle mouse scroll
def on_scroll(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    update_visible_rows()

# Toggle window visibility
def toggle_visibility():
    global is_visible
    is_visible = not is_visible
    try:
        if is_visible:
            root.after(100, lambda: root.deiconify())
            root.attributes('-topmost', True)
            print("Window visible and on top")
        else:
            root.after(100, lambda: root.withdraw())
            print("Window hidden")
    except RuntimeError as e:
        print(f"Error toggling visibility: {e}")

# Activate hotkey
def on_activate():
    root.after(0, toggle_visibility)

# Start hotkey listener
def start_listener():
    global listener
    try:
        listener = keyboard.GlobalHotKeys({
            custom_shortcut: on_activate,
        })
        listener.start()
        print(f"Hotkey listener started, press {custom_shortcut} to toggle window")
    except Exception as e:
        print(f"Error starting hotkey listener: {e}")


# Process files
def process_files():
    ball_replace_folder = resource_path('ball_replace')
    picture_folder = resource_path('picture')

    if not os.path.exists(ball_replace_folder):
        messagebox.showerror("Error", f"{ball_replace_folder} folder does not exist!")
        return

    if not os.path.exists(picture_folder):
        messagebox.showerror("Error", f"{picture_folder} folder does not exist!")
        return

    ball_files = sorted([f for f in os.listdir(ball_replace_folder) if f.endswith('.iff')])
    picture_files = sorted([f for f in os.listdir(picture_folder) if f.endswith('.png')])

    ball_images = []
    for ball_file in ball_files:
        index = ball_file.split('.')[0]
        matching_picture = f"{index}.png"

        if matching_picture in picture_files:
            picture_path = os.path.join(picture_folder, matching_picture)
            img = load_image(picture_path)
            if img:
                ball_images.append((ball_file, img))
        else:
            ball_images.append((ball_file, None))

    display_images(ball_images)

# Display images
def display_images(ball_images):
    for widget in frame_images.winfo_children():
        widget.destroy()

    for idx, (ball_file, img) in enumerate(ball_images):
        row_num = idx // 5
        col_num = idx % 5

        frame = ttk.Frame(frame_images, padding=5)
        frame.grid(row=row_num, column=col_num, padx=5, pady=5, sticky="nsew")

        if img:
            create_image_row(frame, ball_file, img)
        else:
            empty_img = ImageTk.PhotoImage(Image.new('RGB', (100, 100), (255, 255, 255)))
            create_image_row(frame, ball_file, empty_img)

    frame_images.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))

# Create image row
def create_image_row(frame, ball_file, img):
    img_label = tk.Label(frame, image=img, bg="white", relief="solid", borderwidth=1)
    img_label.image = img
    img_label.pack()
    img_label.bind("<Double-Button-1>", lambda event, ball_file=ball_file: replace_ball_file(ball_file))

    name_label = tk.Label(frame, text=ball_file, bg="white")
    name_label.pack()

# Replace basketball file
def replace_ball_file(ball_file):
    ball_replace_folder = resource_path('ball_replace')
    
    if not hasattr(root, "balls_folder") or not root.balls_folder:
        messagebox.showerror("Error", "Please select a replacement path first")
        return
    
    balls_folder = root.balls_folder
    source_path = os.path.join(ball_replace_folder, ball_file)
    dest_path = os.path.join(balls_folder, "ball_gameplay_official_nba_official.iff")

    if not os.path.exists(source_path):
        messagebox.showerror("Error", f"{source_path} does not exist!")
        return

    def copy_file():
        try:
            shutil.copy(source_path, dest_path)
            messagebox.showinfo("Success", f"Successfully replaced {dest_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy file: {e}")
    
    threading.Thread(target=copy_file, daemon=True).start()

# Select basketball folder
def select_balls_folder():
    selected_folder = filedialog.askdirectory(title="Select replacement path for basketball files")
    if selected_folder:
        root.balls_folder = selected_folder
        process_files()

# Open settings window
def open_settings():
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("300x150")
    settings_window.attributes('-topmost', True)

    def save_shortcut():
        global custom_shortcut
        shortcut = entry_shortcut.get()
        if shortcut:
            custom_shortcut = shortcut
            listener.stop()
            start_listener()
            settings_window.destroy()

    label = tk.Label(settings_window, text="Custom shortcut (e.g., <F9>):")
    label.pack(pady=10)

    entry_shortcut = tk.Entry(settings_window)
    entry_shortcut.insert(0, custom_shortcut)
    entry_shortcut.pack(pady=5)

    button_save = ttk.Button(settings_window, text="Save", command=save_shortcut)
    button_save.pack(pady=10)

# UI creation
def create_ui():
    global root, canvas, frame_images, button_frame, progress_bar, select_button
    root = ttk.Window(themename="cosmo")  # 设置主题
    root.title("篮球替换工具 V0.7 Beta")
    root.geometry("600x600")
    
    # 使用蓝绿色调的背景色
    root.configure(bg="#ADD8E6")  # 浅蓝色背景

    # 创建菜单栏
    menubar = tk.Menu(root, bg="#66CDAA")  # 中等绿松石色
    menubar.add_command(label="⚙️ 设置", command=open_settings)  # 设置菜单项
    root.config(menu=menubar)

    # 设置菜单风格
    menubar.configure(bg="#66CDAA", fg="white")  # 菜单背景色

    # 创建画布和滚动条框架
    main_frame = tk.Frame(root, bg="#66CDAA")  # 中等绿松石色
    main_frame.pack(fill="both", expand=True)

    # 创建画布和滚动条
    canvas = ttk.Canvas(main_frame, bg="#66CDAA")
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)

    # 加载图片
    image_path = "./daigg.jpg"  # 请替换为你图片的实际路径
    original_image = Image.open(image_path)
    # 调整图片大小以填满画布区域，假设画布的宽度和高度
    canvas_width = 600  # 根据实际画布大小设定宽度
    canvas_height = 480  # 根据实际画布大小设定高度
    resized_image = original_image.resize((canvas_width, canvas_height), Image.LANCZOS)
    progress_image = ImageTk.PhotoImage(resized_image)
    # 将图片添加到画布的左上角，填充画布
    canvas.create_image(0, 0, anchor="nw", image=progress_image)  # 左上角对齐
    canvas.image = progress_image  # 保存引用避免垃圾回收

    # 快速滚动功能
    def fast_scroll(event):
        if event.delta > 0:
            canvas.yview_scroll(-3, "units")
        else:
            canvas.yview_scroll(3, "units")

    # 绑定鼠标滚轮事件
    canvas.bind_all("<MouseWheel>", fast_scroll)

    # 创建显示图像的框架
    frame_images = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=frame_images, anchor="nw")

    progress_frame = ttk.Frame(root, style="Primary.TFrame", padding=10)
    progress_frame.pack(fill="x")

    # 添加提示文本
    progress_label = ttk.Label(progress_frame, text="篮球资源正在加载中，请稍等...", font=("Arial", 10), foreground="#000080")
    progress_label.pack(pady=(0, 5))  # 放置在进度条上方，并设置间距

    # 设置进度条样式
    style = ttk.Style()
    style.configure("Custom.Horizontal.TProgressbar", thickness=20, troughcolor="#f0f0f0", background="#66CDAA")  # 设置背景颜色和前景颜色
    
    progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=580, mode="determinate", style="Custom.Horizontal.TProgressbar")
    progress_bar.pack(fill="x", pady=20, padx=10)
    
    # 初始化进度条
    progress_bar["value"] = 0
    progress_bar["maximum"] = 100

    # 更新进度条的函数
    def update_progress(value=0):
        progress_bar["value"] = value
        progress_bar.update_idletasks()  # 刷新进度条
        root.after(500, load_images_with_progress)  # 延迟500ms加载图像

    # 加载图像并显示
    def load_images_with_progress():
        ball_replace_folder = resource_path('ball_replace')
        picture_folder = resource_path('picture')

        if not os.path.exists(ball_replace_folder):
            messagebox.showerror("Error", f"{ball_replace_folder} folder does not exist!")
            return

        if not os.path.exists(picture_folder):
            messagebox.showerror("Error", f"{picture_folder} folder does not exist!")
            return

        ball_files = sorted([f for f in os.listdir(ball_replace_folder) if f.endswith('.iff')])
        picture_files = sorted([f for f in os.listdir(picture_folder) if f.endswith('.png')])

        ball_images = []
        total_files = len(ball_files)

        def load_next_image(index):
            if index < total_files:
                ball_file = ball_files[index]
                index_str = ball_file.split('.')[0]
                matching_picture = f"{index_str}.png"

                img = None
                if matching_picture in picture_files:
                    picture_path = os.path.join(picture_folder, matching_picture)
                    img = load_image(picture_path)

                ball_images.append((ball_file, img))

                # 更新进度条
                progress = (index + 1) / total_files * 100
                progress_bar["value"] = progress
                progress_bar.update_idletasks()  # 刷新进度条

                # 延迟加载下一张图像
                root.after(50, load_next_image, index + 1)
            else:
                # 所有图像加载完后显示图像并切换界面
                display_images(ball_images)
                show_images()
                show_balls_folder_button()  # 显示“选择篮球替换路径”按钮

        # 开始加载图像
        load_next_image(0)

    # 显示图像界面
    def show_images():
        # 确保滚动区域更新
        canvas.configure(scrollregion=canvas.bbox("all"))
        frame_images.tkraise()  # 提升包含图像的 frame 到最前面
        
        # 隐藏或销毁蓝色背景框架
        progress_frame.destroy()  # 或 progress_frame.destroy()

    # 显示“选择篮球替换路径”按钮，并隐藏进度条
    def show_balls_folder_button():
        # 隐藏进度条
        progress_bar.pack_forget()

        # 显示选择篮球替换路径按钮
        select_button.pack(pady=10)

    # 隐藏“选择篮球替换路径”按钮
    button_frame = ttk.Frame(root, padding=10)
    button_frame.pack()
    select_button = ttk.Button(button_frame, text="选择篮球替换路径", command=select_balls_folder)
    select_button.pack(pady=10)
    select_button.pack_forget()  # 默认隐藏按钮

    # 启动进度条更新
    update_progress()  # 开始更新进度条


# 主函数入口
if __name__ == "__main__":
    create_ui()
    start_listener()
    root.mainloop()