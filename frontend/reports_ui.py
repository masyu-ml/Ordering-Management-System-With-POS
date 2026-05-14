import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class ReportsModule(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- HEADER ---
        header_layout = QHBoxLayout()
        title = QLabel("Sales & Reports")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #4b3621;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        export_btn = QPushButton("Export to CSV")
        export_btn.setStyleSheet(
            "background-color: #3498db; color: white; padding: 10px 20px; font-weight: bold; border-radius: 5px; font-size: 14px;")
        header_layout.addWidget(export_btn)
        layout.addLayout(header_layout)

        # --- DATE FILTERS ---
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("<b>Date From:</b>"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addDays(-7))
        self.date_from.setStyleSheet("padding: 5px; font-size: 14px; background: white;")
        filter_layout.addWidget(self.date_from)

        filter_layout.addWidget(QLabel("<b>Date To:</b>"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setStyleSheet("padding: 5px; font-size: 14px; background: white;")
        filter_layout.addWidget(self.date_to)

        gen_btn = QPushButton("Generate Report")
        gen_btn.setStyleSheet(
            "background-color: #2ecc71; color: white; padding: 8px 15px; font-weight: bold; border-radius: 3px;")
        filter_layout.addWidget(gen_btn)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # --- SUMMARY CARDS ---
        cards_layout = QHBoxLayout()
        cards = [("Gross Sales", "P 0.00"), ("Total VAT (12%)", "P 0.00"), ("Total Orders", "0")]

        for title_text, val_text in cards:
            card = QFrame()
            card.setStyleSheet("background-color: white; border-radius: 10px; border: 1px solid #ddd;")
            card_layout = QVBoxLayout(card)

            lbl1 = QLabel(title_text)
            lbl1.setStyleSheet("color: #7f8c8d; font-size: 14px; font-weight: bold;")
            lbl2 = QLabel(val_text)
            lbl2.setStyleSheet("color: #2c3e50; font-size: 28px; font-weight: bold;")

            card_layout.addWidget(lbl1)
            card_layout.addWidget(lbl2)
            cards_layout.addWidget(card)

        layout.addLayout(cards_layout)

        # --- TRANSACTION TABLE ---
        layout.addWidget(QLabel("<h3 style='margin-top: 15px;'>Recent Transactions</h3>"))
        self.table = QTableWidget(15, 4)
        self.table.setHorizontalHeaderLabels(["Date & Time", "Order ID", "Cashier Name", "Total Amount (P)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget { background-color: white; border: 1px solid #ddd; font-size: 14px; }
            QHeaderView::section { background-color: #f4eee8; padding: 8px; font-weight: bold; border: 1px solid #ddd; color: #333; }
        """)
        layout.addWidget(self.table)