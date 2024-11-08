import os
import shutil
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk

def load_image(image_path):
    try:
        img = Image.open(image_path)
        img = img.resize((100, 100))  # 调整图片大小
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"加载图片失败: {image_path}, 错误: {e}")
        return None

def process_files():
    ball_replace_folder = 'ball_replace'
    picture_folder = 'picture'
    balls_folder = 'balls'

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
    ball_replace_folder = 'ball_replace'
    balls_folder = 'balls'

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

# 在应用启动时自动加载图片
process_files()

# 鼠标滚轮滚动
def on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

canvas.bind_all("<MouseWheel>", on_mousewheel)

root.mainloop()
