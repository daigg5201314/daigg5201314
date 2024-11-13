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

# Global variables
is_visible = True
listener = None
image_cache = OrderedDict()
visible_rows = set()
custom_shortcut = 'alt+h'

# Check resource path
def resource_path(relative_path):
    """ 获取资源文件的正确路径，在开发和打包后都能正常访问 """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

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

# Toggle window visibility
def toggle_visibility():
    """切换主窗口的可见性"""
    global is_visible
    is_visible = not is_visible
    if is_visible:
        root.deiconify()  # 显示窗口
        root.attributes('-topmost', True)
        print("窗口已显示并置顶。")
    else:
        root.withdraw()  # 隐藏窗口
        print("窗口已隐藏。")

# Register global hotkey
def register_hotkey():
    try:
        keyboard.add_hotkey(custom_shortcut, toggle_visibility)
        print(f"全局快捷键监听已启动。按 {custom_shortcut} 切换窗口显示状态。")
    except Exception as e:
        print(f"启动全局快捷键监听失败: {e}")

# Start hotkey listener
def start_listener():
    """使用 keyboard 模块设置全局快捷键监听"""
    global listener
    if listener:
        listener.stop()  # 先停止已有的监听器

    # 注册全局快捷键 - 例如使用 Ctrl+Alt+H
    register_hotkey()
    # 启动新的监听器线程
    listener = keyboard.GlobalHotKeys({custom_shortcut: toggle_visibility})
    listener.start()


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
    picture_files = sorted([f for f in os.listdir(picture_folder) if f.endswith('.jpg')])

    ball_images = []
    for ball_file in ball_files:
        index = ball_file.split('.')[0]
        matching_picture = f"{index}.jpg"

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
            # 使用线程启动监听器，避免阻塞主线程
            threading.Thread(target=start_listener, daemon=True).start()
            settings_window.destroy()  # 关闭设置窗口

    label = tk.Label(settings_window, text="Custom shortcut (e.g <alt+r>):")
    label.pack(pady=10)

    entry_shortcut = tk.Entry(settings_window)
    entry_shortcut.insert(0, custom_shortcut)
    entry_shortcut.pack(pady=5)

    button_save = ttk.Button(settings_window, text="Save", command=save_shortcut)
    button_save.pack(pady=10)

def toggle_button(button):
    if button == "hide":
        select_button.pack_forget()  # 隐藏按钮
    elif button == "show":
        button_frame.pack(side='bottom')
        select_button.pack(pady=10) #显示按钮

# UI creation
def create_ui():
    global root, canvas, frame_images, button_frame, progress_bar, select_button, basketball_frame, court_frame
    root = tk.Tk()
    root.title("篮球替换工具 V1.1")
    root.geometry("600x600")
    
    # 使用浅蓝色的背景色
    root.configure(bg="#ADD8E6")  # 浅蓝色背景

    # 创建菜单栏
    menubar = tk.Menu(root, bg="#66CDAA")
    menubar.add_command(label="⚙️ 设置", command=open_settings)
    root.config(menu=menubar)

    # 创建画布和滚动条框架
    main_frame = tk.Frame(root, bg="#66CDAA")
    main_frame.pack(fill="both", expand=True)

    # 创建画布
    canvas = tk.Canvas(main_frame, bg="#66CDAA", highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)

    # 获取 picture 文件夹路径
    picture_folder = resource_path('picture')
    if not os.path.exists(picture_folder):
        messagebox.showerror("Error", f"{picture_folder} folder does not exist!")
    else:
        daigg_image_path = os.path.join(picture_folder, 'daigg.jpg')
    
    if not os.path.exists(daigg_image_path):
        messagebox.showerror("Error", f"daigg.jpg does not exist in {picture_folder}!")

    # 加载并固定背景图片在画布左上角
    image_path = daigg_image_path  # 替换为图片的实际路径
    original_image = Image.open(image_path)
    resized_image = original_image.resize((600, 520), Image.LANCZOS)  # 根据实际画布大小设定
    background_image = ImageTk.PhotoImage(resized_image)
    canvas.create_image(0, 0, anchor="nw", image=background_image)
    canvas.image = background_image

    # 禁用滚动条功能（在加载期间）
    canvas.config(scrollregion=(0, 0, 600, 480))

    # 创建进度条和提示文本框架
    progress_frame = tk.Frame(root, bg="#ADD8E6")
    progress_frame.pack(fill="x", pady=5)

    progress_label = tk.Label(progress_frame, text="篮球资源正在加载中，请稍等...", font=("Arial", 10), fg="#000080", bg="#ADD8E6")
    progress_label.pack()

    style = ttk.Style()
    style.configure("Custom.Horizontal.TProgressbar", thickness=20, troughcolor="#f0f0f0", background="#66CDAA")
    
    progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=580, mode="determinate", style="Custom.Horizontal.TProgressbar")
    progress_bar.pack(fill="x", pady=10, padx=10)
    progress_bar["maximum"] = 100

    # 创建框架用于不同页面
    court_frame = tk.Frame(root, bg="#66CDAA")
    basketball_frame = main_frame

    # 加载图像并显示
    def load_images_with_progress():
    # 定义文件夹路径
        ball_replace_folder = './ball_replace'
        picture_folder = './picture'

        # 如果程序是打包后的可执行文件
        if getattr(sys, 'frozen', False):  # 判断是否是通过 PyInstaller 打包后的 exe 文件
            # 获取打包后的临时目录路径
            ball_replace_folder = os.path.join(sys._MEIPASS, 'ball_replace')
            picture_folder = os.path.join(sys._MEIPASS, 'picture')
    
        if not os.path.exists(ball_replace_folder) or not os.path.exists(picture_folder):
            messagebox.showerror("Error", "需要的文件夹不存在！")
            return

        ball_files = sorted([f for f in os.listdir(ball_replace_folder) if f.endswith('.iff')])
        picture_files = sorted([f for f in os.listdir(picture_folder) if f.endswith('.jpg')])

        ball_images = []
        total_files = len(ball_files)

        def load_next_image(index):
            if index < total_files:
                ball_file = ball_files[index]
                index_str = ball_file.split('.')[0]
                matching_picture = f"{index_str}.jpg"

                img = None
                if matching_picture in picture_files:
                    picture_path = os.path.join(picture_folder, matching_picture)
                    img = load_image(picture_path)  # 假设 load_image 函数存在并加载图片

                ball_images.append((ball_file, img))

                # 更新进度条
                progress = (index + 1) / total_files * 100
                progress_bar["value"] = progress
                progress_bar.update_idletasks()

                # 延迟加载下一张图像
                root.after(50, load_next_image, index + 1)
            else:
                # 所有图像加载完后显示图像并切换界面
                display_images(ball_images)
                show_images()

        # 开始加载图像
        load_next_image(0)

    # 显示图像界面
    def show_images():
        # 更新滚动区域
        canvas.configure(scrollregion=canvas.bbox("all"))
        frame_images.tkraise()  # 显示包含图片的 frame
        progress_frame.pack_forget()  # 隐藏进度条框架
        select_button.pack(pady=10)  # 显示“选择篮球替换路径”按钮
        menubar.add_command(label="篮球", command=lambda: switch_page("basketball"))
        menubar.add_command(label="球场", command=lambda: switch_page("court"))
        switch_page("basketball") #选择篮球为主标签
        # 启用滚轮滚动功能
        canvas.bind("<MouseWheel>", fast_scroll)  # 绑定滚轮事件以启用滚动功能
        root.bind_all("<MouseWheel>", fast_scroll)  # 在 root 中绑定以确保滚动捕获

    # 创建显示图像的框架
    frame_images = tk.Frame(canvas, bg="#66CDAA")
    canvas.create_window((0, 0), window=frame_images, anchor="nw")

    # 切换页面函数
    def switch_page(page):
        if page == "basketball":
            basketball_frame.pack(fill="both", expand=True)
            court_frame.pack_forget()
            toggle_button("show")
        elif page == "court":
            court_frame.pack(fill="both", expand=True)
            basketball_frame.pack_forget()
            toggle_button("hide")

    # 快速滚动功能
    def fast_scroll(event):
        # 使用滚轮控制画布上下滚动
        if event.delta > 0:
            canvas.yview_scroll(-3, "units")
        else:
            canvas.yview_scroll(3, "units")

    # 创建“选择篮球替换路径”按钮框架，并默认隐藏按钮
    button_frame = tk.Frame(root, bg="#ADD8E6")
    button_frame.pack(fill="x")
    select_button = tk.Button(button_frame, text="选择篮球替换路径", command=select_balls_folder)
    select_button.pack(pady=10)
    select_button.pack_forget()  # 默认隐藏按钮

    # 启动监听器线程
    threading.Thread(target=start_listener, daemon=True).start()

    # 启动加载图像和更新进度条的过程
    load_images_with_progress()


# 主函数入口
if __name__ == "__main__":
    create_ui()
    # start_listener()
    root.mainloop()