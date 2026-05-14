import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class AnalyticsModule(QWidget):
    def __init__(self, token="", user_id="1"):
        super().__init__()
        self.token = token
        self.user_id = str(user_id)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Business Analytics & KPIs")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #4b3621;")
        layout.addWidget(title)

        kpi_layout = QHBoxLayout()
        metrics = [("Today's Revenue", "P 0.00", "#2ecc71"), ("Net Profit", "P 0.00", "#3498db"),
                   ("Growth %", "0.0%", "#9b59b6")]

        for name, val, color in metrics:
            card = QFrame()
            card.setStyleSheet(
                f"background-color: white; border-radius: 10px; border-top: 5px solid {color}; border-left: 1px solid #ddd; border-right: 1px solid #ddd; border-bottom: 1px solid #ddd;")
            card_layout = QVBoxLayout(card)
            lbl_title = QLabel(name)
            lbl_title.setStyleSheet("color: #7f8c8d; font-size: 16px; font-weight: bold;")
            lbl_val = QLabel(val)
            lbl_val.setStyleSheet("color: #2c3e50; font-size: 32px; font-weight: bold;")
            card_layout.addWidget(lbl_title)
            card_layout.addWidget(lbl_val)
            kpi_layout.addWidget(card)

        layout.addLayout(kpi_layout)

        layout.addWidget(QLabel("<h3 style='margin-top: 20px;'>Category Performance</h3>"))
        self.table = QTableWidget(10, 2)
        self.table.setHorizontalHeaderLabels(["Category", "Total Value (P)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet(
            "QTableWidget { background-color: white; border: 1px solid #ddd; } QHeaderView::section { background-color: #f4eee8; padding: 8px; font-weight: bold; }")
        layout.addWidget(self.table)

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "user-id": self.user_id
        }