import os
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import Image, ImageTk
import sys
import threading
from pynput import keyboard
from collections import OrderedDict  # 使用 OrderedDict 替代普通字典

# 检查资源路径
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# 全局变量
is_visible = True
listener = None
image_cache = OrderedDict()  # 使用 OrderedDict 作为图片缓存
visible_rows = set()  # 可视行集合
custom_shortcut = '<F8>'  # 默认快捷键

# 加载图片并进行缓存
def load_image(image_path):
    try:
        if image_path in image_cache:
            image_cache.move_to_end(image_path)  # 移动到最前面
            return image_cache[image_path]
        
        img = Image.open(image_path)
        img = img.resize((100, 100))  # 这里可以根据需要调整尺寸
        img_tk = ImageTk.PhotoImage(img)
        
        # 限制缓存大小为10
        if len(image_cache) >= 10:
            image_cache.popitem(last=False)  # 移除最旧的缓存
        
        image_cache[image_path] = img_tk
        return img_tk
    except Exception as e:
        print(f"加载图片失败: {image_path}, 错误: {e}")
        return None

# 鼠标滚轮事件处理
def on_scroll(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    update_visible_rows()

# 切换窗口显示状态
def toggle_visibility():
    global is_visible
    is_visible = not is_visible
    try:
        if is_visible:
            root.after(100, lambda: root.deiconify())  # 延时100ms显示窗口
            root.attributes('-topmost', True)
            print("窗口已显示并置顶")
        else:
            root.after(100, lambda: root.withdraw())  # 延时100ms隐藏窗口
            print("窗口已隐藏")
    except RuntimeError as e:
        print(f"切换窗口显示状态时出错: {e}")

# 快捷键激活函数
def on_activate():
    root.after(0, toggle_visibility)

# 启动快捷键监听
def start_listener():
    global listener
    try:
        listener = keyboard.GlobalHotKeys({
            custom_shortcut: on_activate,  # 使用自定义的快捷键
        })
        listener.start()
        print(f"快捷键监听器已启动，按 {custom_shortcut} 切换窗口显示状态")
    except Exception as e:
        print(f"启动快捷键监听器失败: {e}")

# 处理文件逻辑
def process_files():
    ball_replace_folder = resource_path('ball_replace')
    picture_folder = resource_path('picture')

    if not os.path.exists(ball_replace_folder):
        messagebox.showerror("错误", f"{ball_replace_folder} 文件夹不存在！")
        return

    if not os.path.exists(picture_folder):
        messagebox.showerror("错误", f"{picture_folder} 文件夹不存在！")
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

    # 不删除原有的行，直接添加/更新图片
    display_images(ball_images)

# 显示图片
def display_images(ball_images):
    # 清理当前显示的内容
    for widget in frame_images.winfo_children():
        widget.destroy()

    # 遍历所有图片并更新显示
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

   # 更新canvas的滚动区域
    frame_images.update_idletasks()  # 强制更新布局
    canvas.configure(scrollregion=canvas.bbox("all"))  # 更新滚动区域

# 创建图片行
def create_image_row(frame, ball_file, img):
    img_label = tk.Label(frame, image=img, bg="white", relief="solid", borderwidth=1)
    img_label.image = img
    img_label.pack()
    img_label.bind("<Double-Button-1>", lambda event, ball_file=ball_file: replace_ball_file(ball_file))

    name_label = tk.Label(frame, text=ball_file, bg="white")
    name_label.pack()

# 替换篮球文件
def replace_ball_file(ball_file):
    ball_replace_folder = resource_path('ball_replace')
    
    if not hasattr(root, "balls_folder") or not root.balls_folder:
        messagebox.showerror("错误", "请先选择一个替换路径")
        return
    
    balls_folder = root.balls_folder
    source_path = os.path.join(ball_replace_folder, ball_file)
    dest_path = os.path.join(balls_folder, "ball_gameplay_official_nba_official.iff")

    if not os.path.exists(source_path):
        messagebox.showerror("错误", f"{source_path} 不存在！")
        return

    # 使用后台线程进行文件复制
    def copy_file():
        try:
            shutil.copy(source_path, dest_path)
            messagebox.showinfo("成功", f"成功替换 {dest_path}")
        except Exception as e:
            messagebox.showerror("错误", f"复制文件失败: {e}")
    
    # 启动线程
    threading.Thread(target=copy_file, daemon=True).start()

# 选择篮球替换路径
def select_balls_folder():
    selected_folder = filedialog.askdirectory(title="选择替换篮球文件的保存路径")
    if selected_folder:
        root.balls_folder = selected_folder
        process_files()

# 打开设置窗口
def open_settings():
    settings_window = tk.Toplevel(root)
    settings_window.title("设置")
    settings_window.geometry("300x150")
    settings_window.attributes('-topmost', True)  # 设置为置顶窗口，防止被主窗口遮挡

    def save_shortcut():
        global custom_shortcut
        shortcut = entry_shortcut.get()
        if shortcut:
            custom_shortcut = shortcut
            listener.stop()  # 停止旧的监听器
            start_listener()  # 启动新的监听器
            settings_window.destroy()  # 关闭设置窗口

    label = tk.Label(settings_window, text="自定义快捷键（例如：<F9>）：")
    label.pack(pady=10)

    entry_shortcut = tk.Entry(settings_window)
    entry_shortcut.insert(0, custom_shortcut)  # 显示当前的快捷键
    entry_shortcut.pack(pady=5)

    button_save = ttk.Button(settings_window, text="保存", command=save_shortcut)
    button_save.pack(pady=10)

# UI 界面创建
def create_ui():
    global root, canvas, frame_images, button_frame
    root = tk.Tk()
    root.title("篮球替换工具 V0.5 Beta")
    root.geometry("600x480")
    root.configure(bg="#f0f0f0")
    root.attributes('-topmost', is_visible)  # 设置窗口置顶

    # 创建顶栏的齿轮按钮
    menu_button = ttk.Button(root, text="⚙️", command=open_settings)
    menu_button.pack(side="top", anchor="e", padx=10, pady=10)
    
    canvas = tk.Canvas(root, bg="#f0f0f0")
    canvas.pack(side="top", fill="both", expand=True)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)

    # 绑定滚轮滚动事件
    canvas.bind_all("<MouseWheel>", on_scroll)

    frame_images = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=frame_images, anchor="nw")
    button_frame = tk.Frame(root, bg="#f0f0f0")
    button_frame.pack(side="bottom", fill="x", pady=10)

    select_button = ttk.Button(button_frame, text="选择篮球替换路径", command=select_balls_folder)
    select_button.pack(side="bottom", anchor="center")

    frame_images.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))

    for i in range(5):
        frame_images.grid_columnconfigure(i, weight=1)

    process_files()

# 程序入口
def main():
    create_ui()
    root.after(0, start_listener)
    root.mainloop()

if __name__ == "__main__":
    main()
