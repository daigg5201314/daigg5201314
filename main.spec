# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=['.'],  # 可以指定当前目录，如：pathex=['.']
    binaries=[],
    # 打包 ball_replace, picture 文件夹，以及 daigg.jpg 图片文件
    datas=[
        ('picture/daigg.jpg', 'daigg.jpg'), # 使用相对路径引用 daigg.jpg 文件
        ('ball_replace', 'ball_replace'),  # 打包 'ball_replace' 文件夹
        ('picture', 'picture')  # 打包 'picture' 文件夹
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='篮球替换工具',  # 程序名称
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 设置为 False 以去除控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='daigg.ico',  # 程序图标
)
