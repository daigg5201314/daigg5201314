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

    display_images(ball_images)

def display_images(ball_images):
    for widget in frame_images.winfo_children():
        widget.destroy()

    for idx, (ball_file, img) in enumerate(ball_images):
        frame = ttk.Frame(frame_images, padding=5)
        frame.grid(row=idx // 5, column=idx % 5, padx=5, pady=5, sticky="nsew")

        if img:
            img_label = tk.Label(frame, image=img, bg="white", relief="solid", borderwidth=1)
            img_label.image = img
            img_label.pack()
            img_label.bind("<Double-Button-1>", lambda event, ball_file=ball_file: replace_ball_file(ball_file))
        else:
            empty_img = ImageTk.PhotoImage(Image.new('RGB', (100, 100), (255, 255, 255)))
            img_label = tk.Label(frame, image=empty_img, bg="white", relief="solid", borderwidth=1)
            img_label.image = empty_img
            img_label.pack()

        name_label = tk.Label(frame, text=ball_file, bg="white")
        name_label.pack()

    frame_images.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))

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

    try:
        shutil.copy(source_path, dest_path)
        messagebox.showinfo("成功", f"成功替换 {dest_path}")
    except Exception as e:
        messagebox.showerror("错误", f"复制文件失败: {e}")

def select_balls_folder():
    selected_folder = filedialog.askdirectory(title="选择替换篮球文件的保存路径")
    if selected_folder:
        root.balls_folder = selected_folder
        process_files()

# 创建主窗口
root = tk.Tk()
root.title("篮球替换工具 V0.1 Beta")
root.geometry("600x480")
root.configure(bg="#f0f0f0")  # 设置窗口背景色

canvas = tk.Canvas(root, bg="#f0f0f0")
canvas.pack(side="top", fill="both", expand=True)

scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")

canvas.configure(yscrollcommand=scrollbar.set)

frame_images = ttk.Frame(canvas, style="TFrame")
canvas.create_window((0, 0), window=frame_images, anchor="nw")

frame_images.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))

for i in range(5):
    frame_images.grid_columnconfigure(i, weight=1)

button_frame = tk.Frame(root, bg="#f0f0f0")
button_frame.pack(side="bottom", fill="x", pady=10)

select_button = ttk.Button(button_frame, text="选择篮球替换路径", command=select_balls_folder)
select_button.pack(side="bottom", anchor="center")

def on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

canvas.bind_all("<MouseWheel>", on_mousewheel)

# 程序启动后直接进入匹配页面
process_files()

root.mainloop()
