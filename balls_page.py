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
from debug_utils import debug_print

def display_balls_page(balls_page):
    debug_print("来到篮球界面")
    # 清空界面（防止重复加载时控件堆叠）
    for widget in balls_page.winfo_children():
        widget.destroy()

    # 创建一个居中提示的标签
    message_label = tk.Label(
        balls_page,
        text="暂未实装",
        font=("楷体", 28, "bold"),
        fg="#999999",
        bg="white"
    )
    message_label.place(relx=0.5, rely=0.5, anchor="center")

def switch_to_balls_page(balls_page):
    debug_print("切换到篮球界面")
    display_balls_page(balls_page)