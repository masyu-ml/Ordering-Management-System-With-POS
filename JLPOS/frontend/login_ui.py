# login_ui.py
import sys
import requests
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Import the global config and the dashboard file
from config import API_BASE_URL
from dashboard_ui import JLPOSDashboard


class JLPOSLogin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JLPOS - Login")
        self.setFixedSize(1000, 600)
        self.initUI()

    def initUI(self):
        self.bg = QLabel(self)
        self.bg.setPixmap(QPixmap("login.png"))
        self.bg.setScaledContents(True)
        self.bg.resize(1000, 600)

        self.box = QFrame(self)
        self.box.setGeometry(300, 150, 400, 320)
        self.box.setStyleSheet("background-color: rgba(139, 106, 80, 210); border-radius: 20px;")

        layout = QVBoxLayout(self.box)
        layout.setContentsMargins(40, 20, 40, 30)

        self.u_input = QLineEdit()
        self.u_input.setPlaceholderText("Username")
        self.u_input.setStyleSheet("padding: 12px; background: white; border-radius: 5px;")

        self.p_input = QLineEdit()
        self.p_input.setPlaceholderText("Password")
        self.p_input.setEchoMode(QLineEdit.Password)
        self.p_input.setStyleSheet("padding: 12px; background: white; border-radius: 5px;")

        btn = QPushButton("Login")
        btn.setStyleSheet("background: #2ecc71; color: white; padding: 12px; font-weight: bold;")
        btn.clicked.connect(self.run_login)

        layout.addWidget(QLabel("<h1 style='color: white; text-align: center;'>JLPOS</h1>"))
        layout.addWidget(self.u_input)
        layout.addWidget(self.p_input)
        layout.addWidget(btn)

    def run_login(self):
        username = self.u_input.text()
        password = self.p_input.text()
        payload = {"username": username, "password": password}

        try:
            resp = requests.post(f"{API_BASE_URL}/login", json=payload)

            if resp.status_code == 200:
                result = resp.json()
                user_data = result.get('data', {})

                # 1. Grab the user_id from the backend response
                u_id = user_data.get('user_id', "1")
                role = user_data.get('role', 'Staff')
                display_name = user_data.get('first_name', username)

                # 2. UPDATED: Pass the u_id to the Dashboard!
                self.main_window = JLPOSDashboard(role, display_name, u_id)
                self.main_window.show()
                self.close()
            else:
                QMessageBox.warning(self, "Denied", "Invalid Credentials")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Backend Connection Failed: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JLPOSLogin()
    window.show()
    sys.exit(app.exec_())