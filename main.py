import os
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import Image, ImageTk
import sys

# 检查资源路径（处理打包时的资源路径问题）
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def load_image(image_path):
    try:
        img = Image.open(image_path)
        img = img.resize((100, 100))  # 调整图片大小
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"加载图片失败: {image_path}, 错误: {e}")
        return None

def process_files():
    # 使用resource_path获取打包后的路径
    ball_replace_folder = resource_path('ball_replace')
    picture_folder = resource_path('picture')

    # 检查文件夹是否存在
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

    display_images(ball_images)

def display_images(ball_images):
    # 清除现有图片
    for widget in frame_images.winfo_children():
        widget.destroy()

    # 动态显示图片
    for idx, (ball_file, img) in enumerate(ball_images):
        frame = tk.Frame(frame_images, bd=1, relief="solid")
        frame.grid(row=idx // 5, column=idx % 5, padx=5, pady=5, sticky="nsew")

        if img:
            img_label = tk.Label(frame, image=img)
            img_label.image = img
            img_label.pack()
            img_label.bind("<Double-Button-1>", lambda event, ball_file=ball_file: replace_ball_file(ball_file))
        else:
            empty_img = ImageTk.PhotoImage(Image.new('RGB', (100, 100), (255, 255, 255)))
            img_label = tk.Label(frame, image=empty_img)
            img_label.image = empty_img
            img_label.pack()

        name_label = tk.Label(frame, text=ball_file)
        name_label.pack()

    frame_images.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))

def replace_ball_file(ball_file):
    ball_replace_folder = resource_path('ball_replace')
    
    # 获取用户选择的替换路径
    if not hasattr(root, "balls_folder") or not root.balls_folder:
        messagebox.showerror("错误", "请先选择一个替换路径")
        return
    
    balls_folder = root.balls_folder
    source_path = os.path.join(ball_replace_folder, ball_file)
    dest_path = os.path.join(balls_folder, "ball_gameplay_official_nba_official.iff")

    if not os.path.exists(source_path):
        messagebox.showerror("错误", f"{source_path} 不存在！")
        return

    try:
        shutil.copy(source_path, dest_path)
        messagebox.showinfo("成功", f"成功替换 {dest_path}")
    except Exception as e:
        messagebox.showerror("错误", f"复制文件失败: {e}")

# 选择替换路径
def select_balls_folder():
    selected_folder = filedialog.askdirectory(title="选择替换篮球文件的保存路径")
    if selected_folder:
        root.balls_folder = selected_folder
        # 成功选择路径后直接进入匹配界面
        process_files()

# 创建主窗口
root = tk.Tk()
root.title("篮球替换工具")

# 创建Canvas和Scrollbar
canvas = tk.Canvas(root)
canvas.pack(side="left", fill="both", expand=True)

scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")

canvas.configure(yscrollcommand=scrollbar.set)

frame_images = ttk.Frame(canvas)
canvas.create_window((0, 0), window=frame_images, anchor="nw")

def update_scroll_region(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

frame_images.bind("<Configure>", update_scroll_region)

# 配置每列的扩展性
for i in range(5):
    frame_images.grid_columnconfigure(i, weight=1)

# 添加“选择路径”按钮
select_button = tk.Button(root, text="选择篮球替换保存路径", command=select_balls_folder)
select_button.pack()

# 鼠标滚轮滚动
def on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

canvas.bind_all("<MouseWheel>", on_mousewheel)

root.mainloop()
