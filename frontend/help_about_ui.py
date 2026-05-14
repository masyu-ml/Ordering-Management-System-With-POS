import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class HelpAboutModule(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setAlignment(Qt.AlignTop)

        title = QLabel("About JLPOS")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #4b3621;")
        layout.addWidget(title)

        info_box = QFrame()
        info_box.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 10px;")
        info_layout = QVBoxLayout(info_box)
        info_layout.setContentsMargins(20, 20, 20, 20)

        version = QLabel("<b>Version:</b> 1.0 (Production)")
        version.setStyleSheet("font-size: 16px; color: #333;")

        developer = QLabel("<b>Developed By:</b> JLPOS Team")
        developer.setStyleSheet("font-size: 16px; color: #333;")

        support = QLabel("<b>Technical Support:</b> support@jlpos.com")
        support.setStyleSheet("font-size: 16px; color: #333;")

        desc = QLabel(
            "<br>JLPOS is a comprehensive, modular Point of Sale and Restaurant Management system featuring real-time Kitchen Display routing, robust inventory tracking, and role-based access security.")
        desc.setStyleSheet("font-size: 14px; color: #555;")
        desc.setWordWrap(True)

        info_layout.addWidget(version)
        info_layout.addWidget(developer)
        info_layout.addWidget(support)
        info_layout.addWidget(desc)

        layout.addWidget(info_box)