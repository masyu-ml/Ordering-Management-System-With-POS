import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class StaffModule(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        header_layout = QHBoxLayout()
        title = QLabel("Staff & Attendance Management")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #4b3621;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        shift_btn = QPushButton("Assign Shift")
        shift_btn.setStyleSheet("background-color: #f39c12; color: white; padding: 10px 20px; font-weight: bold; border-radius: 5px;")
        header_layout.addWidget(shift_btn)
        layout.addLayout(header_layout)

        self.table = QTableWidget(15, 5)
        self.table.setHorizontalHeaderLabels(["Employee ID", "Full Name", "Role", "Phone Number", "Current Shift"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("QTableWidget { background-color: white; border: 1px solid #ddd; } QHeaderView::section { background-color: #f4eee8; padding: 8px; font-weight: bold; }")
        layout.addWidget(self.table)