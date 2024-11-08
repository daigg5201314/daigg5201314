import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

def extract_values_from_scne(input_file_path, key):
    extracted_values = []
    with open(input_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if key in line:
                # 提取值，假设格式为 "key": "value"
                parts = line.split(':')
                if len(parts) > 1:
                    value = parts[1].strip().strip('",')
                    extracted_values.append(value)
                    # print(f"提取到: {key} -> {value}")  # 打印提取的值
    return extracted_values

def clean_extension(value):
    extensions = [".tld", ".bin", ".shader", ".gz", ".script"]
    for ext in extensions:
        if value.endswith(ext):
            return value[:-len(ext)]  # 去掉后缀
    return value

def copy_files_with_prefix(source_folder, destination_folder, prefixes):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    wait_copy_file = []
    for filename in os.listdir(source_folder):
        if any(prefix in filename for prefix in prefixes):
            wait_copy_file.append(filename)

    return wait_copy_file

def clear_destination_folder(destination_folder):
    if os.path.exists(destination_folder):  # 确保目标文件夹存在
        for filename in os.listdir(destination_folder):
            file_path = os.path.join(destination_folder, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"删除文件 {file_path} 时出错: {e}")
    else:
        print(f"目标文件夹不存在: {destination_folder}")


def process_file():
    input_file_path = entry.get()
    if not input_file_path.endswith('.SCNE'):
        messagebox.showerror("错误", "请选择一个 SCNE 文件")
        return

    source_folder_path = os.path.dirname(os.path.abspath(input_file_path))
    destination_folder_path = os.path.join(source_folder_path, 'scne_export')

    # print(f"源文件路径: {input_file_path}")
    # print(f"源文件夹路径: {source_folder_path}")

    # 确保目标文件夹路径有效
    if not os.path.isdir(source_folder_path):
        messagebox.showerror("错误", "源文件夹无效！")
        return

    # 清理目标文件夹
    clear_destination_folder(destination_folder_path)

    # 提取 "Binary" 和 "Script"
    all_keys_and_values = []
    binary_values = extract_values_from_scne(input_file_path, "Binary")
    script_values = extract_values_from_scne(input_file_path, "Script")

    if not binary_values and not script_values:
        messagebox.showwarning("警告", "在 SCNE 文件中未找到对应的关键字！")
        return

    all_keys_and_values.extend(binary_values)
    all_keys_and_values.extend(script_values)

    # 去掉后缀并生成新字符串列表
    stripped_strings = [clean_extension(value) for value in all_keys_and_values]

    wait_copy_files = copy_files_with_prefix(source_folder_path, destination_folder_path, stripped_strings)
    progress['maximum'] = len(wait_copy_files)

    for idx, wait_copyfile_name in enumerate(wait_copy_files):
        source_file = os.path.join(source_folder_path, wait_copyfile_name)
        destination_file = os.path.join(destination_folder_path, wait_copyfile_name)
        shutil.copy(source_file, destination_file)
        progress['value'] = idx + 1
        copied_count_label.config(text=f"已复制文件: {idx + 1}/{len(wait_copy_files)}")
        root.update_idletasks()

    messagebox.showinfo("完成", "处理完成！")

    # 清空输入框
    entry.delete(0, tk.END)

# 创建主窗口
root = tk.Tk()
root.title("SCNE文件处理器 V1.0")

# 创建输入框和按钮
label = tk.Label(root, text="选择 SCNE 文件:")
label.pack(pady=10)

entry = tk.Entry(root, width=50)
entry.pack(padx=10)

button_browse = tk.Button(root, text="浏览", command=lambda: entry.delete(0, tk.END) or entry.insert(0, filedialog.askopenfilename(filetypes=[("SCNE Files", "*.scne")])))
button_browse.pack(pady=5)

button_process = tk.Button(root, text="处理文件", command=process_file)
button_process.pack(pady=20)

# 添加进度条和文件数量标签
progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress.pack(pady=10)

copied_count_label = tk.Label(root, text="已复制文件: 0/0")
copied_count_label.pack(pady=5)

# 启动主循环
root.mainloop()