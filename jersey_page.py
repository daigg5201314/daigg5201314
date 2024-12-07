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

def display_jersey_page(jersey_page):
    # 按钮布局框架
    button_frame = tk.Frame(jersey_page, bg="white")
    button_frame.grid(row=1, column=0, sticky="w")  # 使用 grid 布局
    print(f"来到球衣界面")