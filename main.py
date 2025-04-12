import sys
import struct
import math
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem, 
                            QToolBar, QAction, QFileDialog, QHeaderView, QAbstractItemView)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, QObject, pyqtSlot

class HexEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FxTweakables Editor - Daigg")
        self.setGeometry(100, 100, 800, 600)
        self.table = QTableWidget()
        self.setup_ui()
        self.init_toolbar()
        self.data = bytearray()
        self.last_valid_value = {}  # 用于存储每行最后有效值

    def setup_ui(self):
        # 现代风格表格设置
        self.table.setStyleSheet("""
            QTableWidget {
                background: #F5F5F5;
                color: #333333;
                border: 1px solid #D3D3D3;
                font-family: 'Consolas';
                font-size: 13px;
            }
            QHeaderView::section {
                background: #607B8B;
                color: white;
                padding: 6px;
                border: none;
                font-weight: bold;
            }
            QToolBar {
                background: #607B8B;
                border: none;
                padding: 4px;
            }
            QTableWidget::item {
                border-bottom: 1px solid #E0E0E0;
                padding: 6px 8px;
            }
            QTableWidget::item:selected {
                background: #B0C4DE;
                color: black;
            }
            QTableWidget::item#column_1 {
                text-align: center;
                padding: 0 10px;
            }
        """)
        
        # 列宽设置
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Sequence", "Hex Data (4 Bytes)", "Float Value"])
        
        # 列宽比例（Hex列稍宽）
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 序列号列自适应
        header.setSectionResizeMode(1, QHeaderView.Stretch)          # HEX列拉伸
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents) # Float列固定宽度
        header.setStretchLastSection(False)
        
        # 行高设置
        self.table.verticalHeader().setDefaultSectionSize(28)
        self.table.verticalHeader().setVisible(False)
        
        # 表格行为设置
        self.table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.itemChanged.connect(self.on_cell_changed)
        
        self.setCentralWidget(self.table)

    def init_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        
        style = """
            QToolButton {
                background: #FFFFFF;
                color: white;
                border: none;
                padding: 5px;
                min-width: 80px;
            }
            QToolButton:hover { background: #FFFFFF; }
        """
        
        open_action = QAction("📁 Open", self)
        open_action.setToolTip("Open FxTweakables file")
        open_action.triggered.connect(self.open_file)
        
        save_action = QAction("💾 Save", self)
        save_action.setToolTip("Save modifications")
        save_action.triggered.connect(self.save_file)
        
        toolbar.addAction(open_action)
        toolbar.addAction(save_action)
        toolbar.setStyleSheet(style)
        self.addToolBar(toolbar)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "FxTweakables (*.FxTweakables)"
        )
        if path:
            with open(path, "rb") as f:
                self.data = bytearray(f.read())
                self.populate_table()

    def save_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save File", "", "FxTweakables (*.FxTweakables)"
        )
        if path:
            with open(path, "wb") as f:
                f.write(self.data)

    def populate_table(self):
        print(f"[Debug] 开始解析文件，总字节数: {len(self.data)}")
        self.table.setRowCount(0)
        
        # 修改为4字节基础校验
        if len(self.data) % 4 != 0:
            print(f"[Error] 文件长度异常, 不是4的倍数 (实际长度: {len(self.data)} bytes)")
            self.show_error_dialog("文件格式错误", "文件长度不是4的倍数")
            return

        total_rows = len(self.data) // 4  # 总4字节组数
        print(f"[Debug] 预计解析组数: {total_rows}")

        current_table_row = 0  # 表格行号计数器
        
        # 按16字节为一行处理
        for line_idx in range(0, len(self.data), 16):
            base_address = line_idx
            line_data = self.data[line_idx:line_idx + 16]
            
            # 计算当前行实际存在的4字节组数
            valid_groups = min(4, (len(line_data) + 3) // 4)
            
            for group_idx in range(valid_groups):
                chunk_start = group_idx * 4
                chunk_end = chunk_start + 4

                if chunk_end > len(line_data):
                    chunk = line_data[chunk_start:]
                else:
                    chunk = line_data[chunk_start:chunk_end]
                    
                # 生成序列号（基地址+组号）
                sequence = f"{base_address:08X}/{group_idx + 1}"
                
                # 插入表格行
                self.table.insertRow(current_table_row)
                
                # 设置序列号列
                seq_item = QTableWidgetItem(sequence)
                seq_item.setFlags(seq_item.flags() & ~Qt.ItemIsEditable)
                seq_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(current_table_row, 0, seq_item)
                
                # 设置HEX数据列
                hex_str = ' '.join(f"{b:02X}" for b in chunk[:4])  # 显式截取前4字节
                hex_item = QTableWidgetItem(hex_str)
                hex_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(current_table_row, 1, hex_item)
                
                # 解析浮点值
                try:
                    if len(chunk) < 4:
                        raise ValueError("数据不足4字节")
                        
                    float_value = struct.unpack('<f', chunk)[0]
                    if math.isnan(float_value):
                        float_str = "NaN"
                    elif math.isinf(float_value):
                        float_str = "Inf"
                    else:
                        float_str = f"{float_value:.4g}"  # 自动保留有效数字
                except Exception as e:
                    float_str = "解析错误"
                    print(f"[Error] {sequence} 解析失败: {str(e)}")
                
                # 设置浮点值列
                float_item = QTableWidgetItem(float_str)
                float_item.setFlags(float_item.flags() | Qt.ItemIsEditable)
                self.table.setItem(current_table_row, 2, float_item)
                
                current_table_row += 1

        print(f"[Debug] 文件解析完成，共处理{current_table_row}组数据")

    def format_hex_with_sequence(hex_data, start_address=0):
        lines = hex_data.strip().split('\n')
        result = []
        for line_idx, line in enumerate(lines):
            base_addr = start_address + line_idx * 16
            base_hex = f"{base_addr:08X}"
            
            # 动态计算有效组数
            valid_chunks = min(4, (len(line) + 7) // 8)
            
            for chunk_idx in range(1, valid_chunks+1):
                start_pos = (chunk_idx-1)*8
                chunk = line[start_pos:start_pos+8].ljust(8, '0')  # 不足部分补零
                seq = f"{base_hex}/{chunk_idx}"
                hex_value = f"0x{chunk.upper()}"
                result.append(f"{seq}: {hex_value}")
        
        return '\n'.join(result)

    @pyqtSlot(QTableWidgetItem)
    # 槽函数定义
    def on_cell_changed(self, item):
        row = item.row()
        column = item.column()
        
        if column != 2:  # 仅处理第三列（Float Value列）
            return

        try:
            new_value = item.text()
            float_val = float(new_value)
            packed_bytes = struct.pack('<f', float_val)
            start = row * 4
            
            # 更新数据存储
            self.data[start:start+4] = packed_bytes
            
            # 更新HEX列显示
            self.table.itemChanged.disconnect()  # 断开信号防止递归
            hex_str = ' '.join(f"{b:02X}" for b in packed_bytes)
            self.table.item(row, 1).setText(hex_str)
            self.table.itemChanged.connect(self.on_cell_changed)  # 重新连接
            
        except ValueError as e:
            # 恢复旧值
            item.setText(self.last_valid_value.get(row, "0.000000"))


    def show_error_dialog(self, title, message):
        error_box = QMessageBox(self)
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowTitle(title)
        error_box.setText(message)
        error_box.setStandardButtons(QMessageBox.Ok)
        error_box.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = HexEditor()
    window.show()
    sys.exit(app.exec_())
