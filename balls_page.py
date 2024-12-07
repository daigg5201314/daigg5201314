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

def display_balls_page(balls_page):
    # 按钮布局框架
    button_frame = tk.Frame(balls_page, bg="white")
    button_frame.grid(row=1, column=0, sticky="w")  # 使用 grid 布局
    print(f"来到篮球界面")