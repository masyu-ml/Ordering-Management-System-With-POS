# kds_ui.py
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class KDSWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kitchen Display System (KDS)")
        # Usually KDS is full screen on a separate kitchen monitor
        self.resize(1000, 700)
        self.setStyleSheet("background-color: #2c3e50;")  # Dark theme for kitchen visibility
        self.initUI()

    def initUI(self):
        self.main_layout = QVBoxLayout(self)

        # Header
        header = QLabel("Active Kitchen Orders")
        header.setStyleSheet("color: white; font-size: 24px; font-weight: bold; padding: 10px;")
        header.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(header)

        # Scrollable area for tickets
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none; background: transparent;")

        # Ticket Container
        self.ticket_container = QWidget()
        # We use a Flow-like layout using a Grid for now, but a horizontal layout works for a ticket line
        self.ticket_layout = QHBoxLayout(self.ticket_container)
        self.ticket_layout.setAlignment(Qt.AlignLeft)

        self.scroll.setWidget(self.ticket_container)
        self.main_layout.addWidget(self.scroll)

    @pyqtSlot(dict)
    def add_new_order(self, order_data):
        """This function is triggered automatically when the POS sends an order."""
        ticket = QFrame()
        ticket.setFixedSize(250, 350)
        ticket.setStyleSheet("background-color: #ecf0f1; border-radius: 10px; border-top: 10px solid #e74c3c;")

        layout = QVBoxLayout(ticket)

        # Ticket Header
        order_num = QLabel(f"Order #{order_data['order_number']}")
        order_num.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        type_lbl = QLabel(order_data['type'])
        type_lbl.setStyleSheet("color: #e74c3c; font-weight: bold;")

        layout.addWidget(order_num)
        layout.addWidget(type_lbl)
        layout.addWidget(QLabel("-----------------"))

        # Ticket Items
        items_list = QListWidget()
        items_list.setStyleSheet("background: transparent; border: none; font-size: 14px;")
        for item in order_data['items']:
            items_list.addItem(item)
        layout.addWidget(items_list)

        # Complete Button
        done_btn = QPushButton("Mark Done")
        done_btn.setStyleSheet(
            "background-color: #27ae60; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        # Clicking done removes the ticket from the screen
        done_btn.clicked.connect(lambda: ticket.deleteLater())
        layout.addWidget(done_btn)

        self.ticket_layout.addWidget(ticket)