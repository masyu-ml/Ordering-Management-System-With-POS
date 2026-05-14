from PyQt5.QtWidgets import *

# --- IMPORT ALL 10 SEPARATE MODULE FILES ---
from pos_ui import POSModule
from kds_ui import KDSWindow
from inventory_ui import InventoryModule
from reports_ui import ReportsModule
from menu_recipe_ui import MenuRecipeModule
from expense_ui import ExpenseModule
from staff_ui import StaffModule
from analytics_ui import AnalyticsModule
from frontend.admin_ui import AdminModule
from help_about_ui import HelpAboutModule


# --- ADMIN PIN SECURITY GATE ---
class AdminPinDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Security Check")
        self.setFixedSize(300, 150)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Enter Admin PIN to access this module:"))
        self.pin = QLineEdit()
        self.pin.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pin)
        btn = QPushButton("Unlock")
        btn.clicked.connect(self.check_pin)
        layout.addWidget(btn)

    def check_pin(self):
        if self.pin.text() == "1234":
            self.accept()
        else:
            QMessageBox.warning(self, "Denied", "Incorrect PIN")


# --- MAIN DASHBOARD WINDOW ---
class JLPOSDashboard(QMainWindow):
    def __init__(self, user_role, user_name):
        super().__init__()
        self.role = user_role  # Fetched dynamically from FastAPI backend
        self.name = user_name
        self.kds_window_instance = None

        self.setWindowTitle(f"JLPOS Dashboard - {self.name}")
        self.resize(1280, 720)
        self.showMaximized()
        self.initUI()

    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. SIDEBAR
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(130)
        self.sidebar.setStyleSheet("background-color: #f4eee8; border-right: 1px solid #ddd;")
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(5, 20, 5, 20)
        self.build_sidebar()
        self.main_layout.addWidget(self.sidebar)

        # 2. WORKSPACE
        self.workspace = QVBoxLayout()
        self.build_header()

        # 3. THE MODULE STACK
        self.content_stack = QStackedWidget()
        self.load_modules()
        self.workspace.addWidget(self.content_stack)

        self.main_layout.addLayout(self.workspace)

    def build_header(self):
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("background-color: #f8f4ef; border-bottom: 1px solid #ddd;")
        h_layout = QHBoxLayout(header)

        logo = QLabel("JLPOS")
        logo.setStyleSheet("font-size: 30px; font-weight: bold; color: #4b3621;")

        search = QLineEdit()
        search.setPlaceholderText("Search...")
        search.setFixedWidth(400)
        search.setStyleSheet("padding: 10px; border-radius: 15px; background: #eee;")

        h_layout.addWidget(logo)
        h_layout.addSpacing(20)
        h_layout.addWidget(search)
        h_layout.addStretch()
        h_layout.addWidget(QLabel(f"<b>User:</b> {self.name} | <b>Role:</b> {self.role}"))
        self.workspace.addWidget(header)

    def build_sidebar(self):
        # MASTER ROUTING DICTIONARY (Backend RBAC Mapping)
        # Format: (Button Name, Allowed Roles, Stack Index)
        self.modules_config = [
            ("POS", ["Admin", "Cashier"], 0),
            ("Menu & Recipe", ["Admin"], 1),
            ("Inventory", ["Admin"], 2),
            ("Expenses", ["Admin"], 3),
            ("Staff", ["Admin"], 4),
            ("Analytics", ["Admin"], 5),
            ("Admin Panel", ["Admin"], 6),
            ("Reports", ["Admin", "Cashier"], 7),
            ("Help/About", ["Admin", "Cashier"], 8),
            ("KDS", ["Admin", "Cashier"], -1)  # -1 = Separate Window
        ]

        for name, roles, index in self.modules_config:
            if self.role in roles:
                btn = QPushButton(name)
                btn.setFixedSize(110, 70)
                btn.setStyleSheet("""
                    QPushButton { font-weight: bold; background: transparent; border: none; font-size: 13px; color: #333; }
                    QPushButton:hover { background: #e0d8d0; border-radius: 10px; }
                """)
                btn.clicked.connect(lambda checked, idx=index, n=name: self.switch_view(idx, n))
                self.sidebar_layout.addWidget(btn)

        self.sidebar_layout.addStretch()

        logout = QPushButton("Logout")
        logout.setFixedSize(110, 60)
        logout.setStyleSheet(
            "color: white; background: #c0392b; font-weight: bold; border-radius: 10px; font-size: 14px;")
        logout.clicked.connect(self.handle_logout)
        self.sidebar_layout.addWidget(logout)

    def load_modules(self):
        """Pre-loads all 9 stacked UI classes."""
        # 0: POS
        self.pos_view = POSModule()
        self.pos_view.order_sent.connect(self.route_to_kds)
        self.content_stack.addWidget(self.pos_view)

        # 1: Menu & Recipe
        self.menu_view = MenuRecipeModule()
        self.content_stack.addWidget(self.menu_view)

        # 2: Inventory
        self.inv_view = InventoryModule()
        self.content_stack.addWidget(self.inv_view)

        # 3: Expenses
        self.exp_view = ExpenseModule()
        self.content_stack.addWidget(self.exp_view)

        # 4: Staff
        self.staff_view = StaffModule()
        self.content_stack.addWidget(self.staff_view)

        # 5: Analytics
        self.analytics_view = AnalyticsModule()
        self.content_stack.addWidget(self.analytics_view)

        # 6: Administration
        self.admin_view = AdminModule()
        self.content_stack.addWidget(self.admin_view)

        # 7: Reports
        self.rep_view = ReportsModule()
        self.content_stack.addWidget(self.rep_view)

        # 8: Help & About
        self.help_view = HelpAboutModule()
        self.content_stack.addWidget(self.help_view)

    def route_to_kds(self, order_data):
        if self.kds_window_instance is not None and self.kds_window_instance.isVisible():
            self.kds_window_instance.add_new_order(order_data)
        else:
            QMessageBox.information(self, "KDS Offline", "Order recorded, but KDS window is closed!")

    def switch_view(self, index, module_name):
        # 1. Handle KDS Pop-out
        if index == -1:
            if self.kds_window_instance is None:
                self.kds_window_instance = KDSWindow()
            self.kds_window_instance.show()
            return

        # 2. Security Check for Sensitive Modules
        sensitive_modules = ["Inventory", "Expenses", "Staff", "Analytics", "Admin Panel"]
        if module_name in sensitive_modules:
            dialog = AdminPinDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                self.content_stack.setCurrentIndex(index)
        else:
            self.content_stack.setCurrentIndex(index)

    def handle_logout(self):
        try:
            if self.kds_window_instance is not None:
                self.kds_window_instance.close()

            from login_ui import JLPOSLogin
            self.login_window = JLPOSLogin()
            self.login_window.show()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Logout Error", str(e))