from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QHeaderView, QCheckBox, QLabel, QAbstractItemView
)
from PyQt5.QtCore import Qt
import chrome_manager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chrome 多用户批量管理")
        self.resize(700, 500)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # 用户表格
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["选择", "用户名", "状态", "目录名", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked)
        self.layout.addWidget(self.table)
        self.table.setColumnWidth(0, 40)  # 缩小选择列宽度
        self.table.setSortingEnabled(True)  # 启用所有列排序

        # 按钮区
        self.button_layout = QHBoxLayout()
        self.btn_select_all = QPushButton("全选")
        self.btn_unselect_all = QPushButton("反选")
        self.btn_refresh = QPushButton("刷新")
        self.btn_open = QPushButton("一键批量打开")
        self.btn_arrange = QPushButton("自动排列窗口")
        self.btn_sync = QPushButton("同步操作")
        self.btn_set_main = QPushButton("主窗口选择")
        for btn in [self.btn_select_all, self.btn_unselect_all, self.btn_refresh, self.btn_open, self.btn_arrange, self.btn_sync, self.btn_set_main]:
            self.button_layout.addWidget(btn)
        self.layout.addLayout(self.button_layout)

        # 日志提示区
        self.log_label = QLabel("操作日志/提示区域")
        self.layout.addWidget(self.log_label)

        # 事件绑定
        self.btn_select_all.clicked.connect(self.select_all)
        self.btn_unselect_all.clicked.connect(self.unselect_all)
        self.btn_refresh.clicked.connect(self.load_profiles)
        self.btn_open.clicked.connect(self.batch_open_selected)
        self.btn_arrange.clicked.connect(self.arrange_windows)

        self.load_profiles()

    def load_profiles(self):
        # 1. 记录排序状态
        header = self.table.horizontalHeader()
        sort_col = header.sortIndicatorSection()
        sort_order = header.sortIndicatorOrder()

        # 2. 记录勾选的 profile_dir
        checked_dirs = set()
        for row in range(self.table.rowCount()):
            chk = self.table.cellWidget(row, 0)
            if chk and chk.isChecked():
                dir_val = self.table.item(row, 3).text().strip()
                checked_dirs.add(dir_val)

        # 3. 禁用排序，刷新数据
        self.table.setSortingEnabled(False)  # 禁止用户手工排序
        self.table.setRowCount(0)
        profiles = chrome_manager.list_profiles()
        profiles = sorted(profiles, key=lambda p: p.name)  # 始终用户名正序
        for row, profile in enumerate(profiles):
            # 检查是否已打开
            status = "已打开" if chrome_manager.is_profile_running(profile.profile_dir) else "未打开"
            profile.status = status
            self.table.insertRow(row)
            chk = QCheckBox()
            if profile.profile_dir in checked_dirs:
                chk.setChecked(True)
            self.table.setCellWidget(row, 0, chk)
            # 用户名列可编辑
            item_name = QTableWidgetItem(profile.name)
            item_name.setFlags(item_name.flags() | Qt.ItemIsEditable)
            self.table.setItem(row, 1, item_name)
            item_status = QTableWidgetItem(status)
            self.table.setItem(row, 2, item_status)
            item_dir = QTableWidgetItem(profile.profile_dir)
            self.table.setItem(row, 3, item_dir)
            # 操作列加保存、打开按钮
            op_widget = QWidget()
            op_layout = QHBoxLayout()
            op_layout.setContentsMargins(0,0,0,0)
            btn_save = QPushButton("保存")
            btn_open = QPushButton("打开")
            btn_save.clicked.connect(lambda _, r=row: self.save_row_name(r))
            btn_open.clicked.connect(lambda _, r=row: self.open_row_profile(r))
            op_layout.addWidget(btn_save)
            op_layout.addWidget(btn_open)
            op_widget.setLayout(op_layout)
            self.table.setCellWidget(row, 4, op_widget)

        # 4. 恢复排序
        self.table.setSortingEnabled(True)
        if sort_col >= 0:
            self.table.sortItems(sort_col, sort_order)

    def save_row_name(self, row):
        new_name = self.table.item(row, 1).text().strip()
        profile_dir = self.table.item(row, 3).text().strip()
        if new_name:
            ok = chrome_manager.save_profile_name(profile_dir, new_name)
            if ok:
                self.log_label.setText(f"{profile_dir} 用户名保存成功！")
            else:
                self.log_label.setText(f"{profile_dir} 用户名保存失败！")
            self.load_profiles()
        else:
            self.log_label.setText("用户名不能为空！")

    def open_row_profile(self, row):
        profile_dir = self.table.item(row, 3).text().strip()
        chrome_manager.open_profile(profile_dir)
        self.log_label.setText(f"已打开 {profile_dir} 浏览器窗口")

    def arrange_windows(self):
        import window_arranger
        # 收集所有勾选且已打开的 profile_dir
        selected_dirs = []
        for row in range(self.table.rowCount()):
            chk = self.table.cellWidget(row, 0)
            status = self.table.item(row, 2).text().strip()
            if chk.isChecked() and status == "已打开":
                profile_dir = self.table.item(row, 3).text().strip()
                selected_dirs.append(profile_dir)
        if not selected_dirs:
            self.log_label.setText("请先勾选已打开的用户窗口！")
            return
        result = window_arranger.arrange_windows_grid(selected_dirs)
        self.log_label.setText(result)


    def select_all(self):
        for row in range(self.table.rowCount()):
            chk = self.table.cellWidget(row, 0)
            if chk:
                chk.setChecked(True)

    def unselect_all(self):
        for row in range(self.table.rowCount()):
            chk = self.table.cellWidget(row, 0)
            if chk:
                chk.setChecked(False)

    def batch_open_selected(self):
        selected_profiles = []
        for row in range(self.table.rowCount()):
            chk = self.table.cellWidget(row, 0)
            if chk and chk.isChecked():
                # 直接从表格获取目录名，确保和界面一致
                profile_dir = self.table.item(row, 3).text().strip()
                if not chrome_manager.is_profile_running(profile_dir):
                    selected_profiles.append(profile_dir)
        if selected_profiles:
            chrome_manager.batch_open_profiles(selected_profiles)
            self.log_label.setText(f"已批量打开 {len(selected_profiles)} 个用户窗口")
        else:
            self.log_label.setText("没有需要打开的用户窗口")
        self.load_profiles()
