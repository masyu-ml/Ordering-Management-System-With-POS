import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class ExpenseModule(QWidget):
    def __init__(self, token="", user_id="1"):
        super().__init__()
        self.token = token
        self.user_id = str(user_id)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Expense Tracking")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #4b3621;")
        layout.addWidget(title)

        form_layout = QHBoxLayout()
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Description (e.g., Electric Bill)")
        self.desc_input.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 5px;")

        self.amt_input = QLineEdit()
        self.amt_input.setPlaceholderText("Amount (P)")
        self.amt_input.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 5px;")

        log_btn = QPushButton("Log Expense")
        log_btn.setStyleSheet(
            "background-color: #e74c3c; color: white; padding: 10px 20px; font-weight: bold; border-radius: 5px;")

        form_layout.addWidget(self.desc_input, 2)
        form_layout.addWidget(self.amt_input, 1)
        form_layout.addWidget(log_btn)
        layout.addLayout(form_layout)

        self.table = QTableWidget(15, 4)
        self.table.setHorizontalHeaderLabels(["Expense ID", "Date Logged", "Description", "Amount (P)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet(
            "QTableWidget { background-color: white; border: 1px solid #ddd; } QHeaderView::section { background-color: #f4eee8; padding: 8px; font-weight: bold; }")
        layout.addWidget(self.table)

        def get_headers(self):
            return {
                "Authorization": f"Bearer {self.token}",
                "user-id": self.user_id
            }