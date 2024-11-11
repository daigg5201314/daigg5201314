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
    global root, canvas, frame_images, button_frame
    root = ttk.Window(themename="cosmo")  # Set a theme from ttkbootstrap
    root.title("篮球替换工具 V0.6 Beta")
    root.geometry("600x480")
    
    # Use calming shades of blue and green
    root.configure(bg="#ADD8E6")  # Light Blue for background

    # 创建菜单栏
    menubar = tk.Menu(root, bg="#66CDAA")  # Medium Aquamarine for the menu bar
    menubar.add_command(label="⚙️ 设置", command=open_settings)  # 将齿轮图标作为菜单项
    root.config(menu=menubar)

    # 菜单风格
    menubar.configure(bg="#66CDAA", fg="white")  # Menu bar background color

    # 创建画布和滚动条框架
    main_frame = tk.Frame(root, bg="#66CDAA")  # Medium Aquamarine for the frame
    main_frame.pack(fill="both", expand=True)

    # 创建 canvas 和滚动条
    canvas = ttk.Canvas(main_frame, bg="#f0f0f0")
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)

    # 快速滚动功能，通过滚轮事件来实现
    def fast_scroll(event):
        if event.delta > 0:
            canvas.yview_scroll(-3, "units")  # 每次向上滚动多个单位
        else:
            canvas.yview_scroll(3, "units")   # 每次向下滚动多个单位

    # 绑定滚轮滚动事件
    canvas.bind_all("<MouseWheel>", fast_scroll)

    # 创建用于显示图像的 frame (No bg here, using style)
    frame_images = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=frame_images, anchor="nw")

    # Use style to set the background color for ttk.Frame
    style = ttk.Style()
    style.configure("Custom.TFrame", background="#AFEEEE")  # Pale Turquoise for image frame
    frame_images.configure(style="Custom.TFrame")

    # 在 frame_images 配置事件中更新 scrollregion
    def update_scrollregion(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    frame_images.bind("<Configure>", update_scrollregion)

    # 创建底部的按钮
    button_frame = ttk.Frame(root)  # Light Blue for the button area
    button_frame.pack(side="bottom", fill="x", pady=10)
    select_button = ttk.Button(button_frame, text="选择篮球替换路径", command=select_balls_folder, style="TButton")
    select_button.pack(side="bottom", anchor="center")

    # 底部按钮风格
    style.configure("TButton", padding=6, relief="flat", background="#40E0D0")  # Turquoise for button background

    # 调整列权重，以便图像可以自适应布局
    for i in range(5):
        frame_images.grid_columnconfigure(i, weight=1)

    # 处理文件并显示图像
    process_files()


# Program entry point
def main():
    create_ui()
    root.after(0, start_listener)
    root.mainloop()

if __name__ == "__main__":
    main()
