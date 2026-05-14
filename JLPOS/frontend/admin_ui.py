import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class AdminModule(QWidget):
    def __init__(self, token="", user_id="1"):
        super().__init__()
        self.token = token
        self.user_id = str(user_id)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        header_layout = QHBoxLayout()
        title = QLabel("System Administration")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #4b3621;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        add_user_btn = QPushButton("+ Register System User")
        add_user_btn.setStyleSheet("background-color: #2c3e50; color: white; padding: 10px 20px; font-weight: bold; border-radius: 5px;")
        header_layout.addWidget(add_user_btn)
        layout.addLayout(header_layout)

        self.table = QTableWidget(15, 4)
        self.table.setHorizontalHeaderLabels(["User ID", "Username", "Linked Employee", "System Role"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("QTableWidget { background-color: white; border: 1px solid #ddd; } QHeaderView::section { background-color: #f4eee8; padding: 8px; font-weight: bold; }")
        layout.addWidget(self.table)

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "user-id": self.user_id
        }