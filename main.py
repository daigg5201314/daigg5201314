import tkinter as tk
from tkinter import ttk, filedialog
import re
import os

# =========================
# 全局状态（回撤 & 高亮）
# =========================

last_added_paths = []
undo_stack = []
full_tree_data = None   # 保存完整 SCNE 结构
# =========================
# SCNE 结构解析（仅结构）
# =========================

def parse_scne_structure(scne_path):
    root = {}
    stack = [root]
    pattern = re.compile(r'"([^"]+)"\s*:\s*\{')

    with open(scne_path, "r", encoding="utf-8") as f:
        for line in f:
            match = pattern.search(line)
            if match:
                key = match.group(1)
                node = {}
                stack[-1][key] = node
                stack.append(node)
            elif "}" in line and len(stack) > 1:
                stack.pop()
    return root


def build_tree(parent, data):
    for key, value in data.items():
        full = get_tree_path(parent) + "/" + key
        tag = "new" if full in last_added_paths else ""
        node = tree.insert(parent, "end", text=key, tags=(tag,))
        build_tree(node, value)


def get_tree_path(item):
    parts = []
    while item:
        parts.insert(0, tree.item(item, "text"))
        item = tree.parent(item)
    return "/".join(parts)

def reload_tree():
    global full_tree_data

    tree.delete(*tree.get_children())
    data = parse_scne_structure(entry.get())
    full_tree_data = data   # ⭐ 缓存完整结构

    root_node = tree.insert("", "end", text=os.path.basename(entry.get()), open=True)
    build_tree(root_node, data)

def collect_matches(data, keyword, path=()):
    """
    返回所有匹配节点的完整路径
    e.g. ('arena', 'Object', 'homeShape9')
    """
    results = []
    for k, v in data.items():
        new_path = path + (k,)
        if keyword in k.lower():
            results.append(new_path)
        results.extend(collect_matches(v, keyword, new_path))
    return results

def build_tree_from_paths(paths):
    tree.delete(*tree.get_children())

    root_name = os.path.basename(entry.get())
    root = tree.insert("", "end", text=root_name, open=True)

    node_map = {(): root}

    for path in paths:
        cur = ()
        parent = root
        for p in path:
            cur = cur + (p,)
            if cur not in node_map:
                node_map[cur] = tree.insert(
                    parent,
                    "end",
                    text=p,
                    open=True   # ⭐ 强制展开
                )
            parent = node_map[cur]

# =========================
# 枚举识别
# =========================

enum_re = re.compile(r'^(.*?)(\d+)$')


def analyze_enum(item):
    name = tree.item(item, "text")
    parent = tree.parent(item)

    m = enum_re.match(name)
    if m:
        prefix = m.group(1)
    else:
        prefix = name

    # ⭐ 父路径（去掉 level.SCNE 根）
    parent_path = get_tree_path(parent).split("/")[1:]

    siblings = tree.get_children(parent)

    enums = []
    for s in siblings:
        n = tree.item(s, "text")
        m2 = enum_re.match(n)
        if m2 and m2.group(1) == prefix:
            enums.append((int(m2.group(2)), n))
        elif n == prefix:
            enums.append((0, n))

    if not enums:
        return None, "未找到同级枚举"

    enums.sort(key=lambda x: x[0])

    return {
        "prefix": prefix,
        "parent_path": parent_path,   # ⭐ 关键
        "max_index": enums[-1][0],
        "template": enums[-1][1],
    }, None



def undo():
    global undo_stack, last_added_paths

    if not undo_stack:
        status.set("无可撤回操作")
        detail.insert(tk.END, "❌ 无可撤回操作\n")
        return

    last = undo_stack.pop()

    with open(entry.get(), "w", encoding="utf-8") as f:
        f.write(last["snapshot"])

    last_added_paths = []
    reload_tree()

    # ⭐ 统一写入操作详情
    detail.insert(tk.END, f"↩ 已撤回操作：{last['desc']}\n")
    detail.see(tk.END)

    status.set(f"已撤回：{last['desc']}")


# =========================
# SCNE 文本操作（核心）
# =========================

def find_block(lines, key):
    start = None
    depth = 0

    for i, line in enumerate(lines):
        if start is None and f'"{key}"' in line and "{" in line:
            start = i
            depth = 1
            continue

        if start is not None:
            depth += line.count("{")
            depth -= line.count("}")
            if depth == 0:
                return start, i

    return None, None

def find_block_in_parent(lines, parent_path, key):
    """
    只在指定 parent_path 内查找 key 对应的块
    parent_path: ['Object', 'xxx', ...]
    """
    stack = []
    start = None
    depth = 0
    path_idx = 0

    for i, line in enumerate(lines):
        # 进入父路径
        if path_idx < len(parent_path):
            if f'"{parent_path[path_idx]}"' in line and "{" in line:
                path_idx += 1
            continue

        # 已在目标父块内，查模板
        if start is None and f'"{key}"' in line and "{" in line:
            start = i
            depth = 1
            continue

        if start is not None:
            depth += line.count("{")
            depth -= line.count("}")
            if depth == 0:
                return start, i

        # 离开父块
        if path_idx == len(parent_path) and "}" in line:
            break

    return None, None

def find_block_with_parent_path(lines, template_key, parent_path):
    """
    在整个文件中找 template_key，
    并确认它属于指定 parent_path（向上回溯）
    """
    stack = []
    stack_keys = []

    for i, line in enumerate(lines):
        # 进入新块
        m = re.search(r'"([^"]+)"\s*:\s*\{', line)
        if m:
            stack.append(i)
            stack_keys.append(m.group(1))

            # ⭐ 命中模板
            if m.group(1) == template_key:
                # 判断父路径是否匹配
                if stack_keys[-len(parent_path)-1:-1] == parent_path:
                    # 找结束行
                    depth = 1
                    for j in range(i + 1, len(lines)):
                        depth += lines[j].count("{")
                        depth -= lines[j].count("}")
                        if depth == 0:
                            return i, j
                # 否则继续找下一个
        # 离开块
        if "}" in line and stack:
            stack.pop()
            stack_keys.pop()

    return None, None

def search_tree_realtime(keyword):
    global full_tree_data

    if not full_tree_data:
        return

    keyword = keyword.strip().lower()

    # 清空 Tree
    tree.delete(*tree.get_children())

    if not keyword:
        # 恢复完整结构
        root_node = tree.insert(
            "", "end",
            text=os.path.basename(entry.get()),
            open=True
        )
        build_tree(root_node, full_tree_data)
        status.set("搜索清空，已恢复全部结构")
        return

    # ⭐ 核心变化：直接收集命中路径
    matches = collect_matches(full_tree_data, keyword)

    if not matches:
        status.set(f"未找到：{keyword}")
        return

    build_tree_from_paths(matches)

    status.set(f"搜索命中 {len(matches)} 项：{keyword}")




def add_enum_to_scne(scne_path, parent_path, template_key, new_keys):
    global last_added_paths

    with open(scne_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    last_added_paths = []

    # 1. 找模板块范围
    t_start, t_end = find_block_with_parent_path(lines, template_key, parent_path)
    if t_start is None:
        raise RuntimeError("未在指定父路径中找到模板枚举块")

    template_lines = lines[t_start:t_end + 1]
    template_text = "".join(template_lines)

    # 获取缩进
    indent = re.match(r'(\s*)"', template_lines[0]).group(1)

    # 2. 找插入点（模板块结束后）
    insert_pos = t_end + 1

    new_blocks = []

    for new_key in new_keys:
        block_text = template_text

        # ✅ 只做“精确安全替换”
        # 1) 外层 key
        block_text = re.sub(
            rf'"{re.escape(template_key)}"\s*:',
            f'"{new_key}":',
            block_text,
            count=1
        )


        # 2) value 中引用的枚举名（如 Target / 引用字段）
        block_text = re.sub(
            rf'(:\s*")({re.escape(template_key)})(")',
            lambda m: m.group(1) + new_key + m.group(3),
            block_text
        )


        new_blocks.append(block_text)

        last_added_paths.append(f"{parent_path}/{new_key}")

    # 插入
    lines[insert_pos:insert_pos] = new_blocks

    with open(scne_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

# =========================
# 操作入口
# =========================

def generate_and_add():
    sel = tree.selection()
    if not sel:
        return

    info, err = analyze_enum(sel[0])
    detail.delete("1.0", tk.END)

    if err:
        detail.insert(tk.END, f"❌ {err}")
        return

    try:
        count = int(enum_count.get())
        if count <= 0:
            raise ValueError
    except ValueError:
        detail.insert(tk.END, "❌ 枚举数量必须为正整数")
        return

    new_keys = [
        f"{info['prefix']}{info['max_index'] + i + 1}"
        for i in range(count)
    ]

    # ===== 记录撤回快照 =====
    with open(entry.get(), "r", encoding="utf-8") as f:
        before_text = f.read()

    undo_stack.append({
        "snapshot": before_text,
        "desc": f"{info['template']} → 新增 {len(new_keys)} 项"
    })

    add_enum_to_scne(
        entry.get(),
        info["parent_path"],
        info["template"],
        new_keys
    )

    reload_tree()

    detail.insert(tk.END, "✅ 枚举已生成并写入\n\n")
    detail.insert(tk.END, f"模板: {info['template']}\n")
    detail.insert(tk.END, f"新增枚举:\n")
    for k in new_keys:
        detail.insert(tk.END, f"  - {k}\n")

    status.set(f"已新增 {len(new_keys)} 个枚举（可回撤）")

# =========================
# SCNE 加载
# =========================

def reload_tree():
    global full_tree_data

    tree.delete(*tree.get_children())
    full_tree_data = parse_scne_structure(entry.get())

    root_node = tree.insert(
        "", "end",
        text=os.path.basename(entry.get()),
        open=True
    )
    build_tree(root_node, full_tree_data)

    status.set("SCNE 已加载，可搜索")


def browse():
    p = filedialog.askopenfilename(filetypes=[("SCNE Files", "*.scne")])
    if p:
        entry.delete(0, tk.END)
        entry.insert(0, p)
        reload_tree()


# =========================
# UI
# =========================

root = tk.Tk()
root.title("SCNE 枚举工具 V7.0（顺序 + 克隆 + 批量）")
root.geometry("1150x680")

top = tk.Frame(root)
top.pack(fill=tk.X, padx=10, pady=6)

tk.Label(top, text="SCNE 文件：").pack(side=tk.LEFT)
entry = tk.Entry(top, width=60)
entry.pack(side=tk.LEFT, padx=5)

tk.Button(top, text="浏览", command=browse).pack(side=tk.LEFT)

tk.Label(top, text="枚举数量：").pack(side=tk.LEFT, padx=10)
enum_count = tk.Entry(top, width=5)
enum_count.insert(0, "1")
enum_count.pack(side=tk.LEFT)

tk.Button(top, text="生成并写入", command=generate_and_add).pack(side=tk.LEFT, padx=10)
tk.Button(top, text="回撤", command=undo).pack(side=tk.LEFT)

main = tk.PanedWindow(root, orient=tk.HORIZONTAL)
main.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

tree_frame = tk.Frame(main)

# ===== 搜索栏 =====
search_bar = tk.Frame(tree_frame)
search_bar.pack(fill=tk.X, pady=(0, 4))

search_entry = tk.Entry(search_bar)
search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
search_entry.bind(
    "<KeyRelease>",
    lambda e: search_tree_realtime(search_entry.get())
)

search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

tk.Button(search_bar, text="搜索", command=lambda: search_tree_realtime(search_entry.get()))\
    .pack(side=tk.LEFT)

# ===== Tree =====
tree = ttk.Treeview(tree_frame)
tree.tag_configure("new", foreground="green")
tree.pack(fill=tk.BOTH, expand=True)

main.add(tree_frame)

# ===== Tooltip（必须在 tree 创建之后）=====
tooltip = tk.Label(
    root,
    text="",
    bg="#ffffe0",
    relief=tk.SOLID,
    borderwidth=1,
    font=("Arial", 9)
)
tooltip.place_forget()

def on_tree_motion(event):
    item = tree.identify_row(event.y)
    if not item:
        tooltip.place_forget()
        return

    path = get_tree_path(item)
    tooltip.config(text=path)
    tooltip.place(x=event.x_root + 10, y=event.y_root + 10)

tree.bind("<Motion>", on_tree_motion)
tree.bind("<Leave>", lambda e: tooltip.place_forget())

detail_frame = tk.Frame(main)
tk.Label(detail_frame, text="操作详情", font=("Arial", 10, "bold")).pack(anchor="w")
detail = tk.Text(detail_frame, width=42)
detail.pack(fill=tk.BOTH, expand=True)
main.add(detail_frame)

status = tk.StringVar(value="就绪")
tk.Label(root, textvariable=status, relief=tk.SUNKEN, anchor="w").pack(fill=tk.X, side=tk.BOTTOM)

root.mainloop()
