import sys
import requests
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Pulls the backend URL from your config
from config import API_BASE_URL


class AddInventoryDialog(QDialog):
    """Dialog for POST /inventory - Declaring new stock"""

    def __init__(self, parent=None, menu_items=[]):
        super().__init__(parent)
        self.setWindowTitle("Add New Inventory Item")
        self.menu_items = menu_items
        self.initUI()

    def initUI(self):
        layout = QFormLayout(self)

        # Dropdown to select an existing Menu Item ID to ensure the 1:1 link
        self.item_combo = QComboBox()
        for item in self.menu_items:
            # Display Name but store the ID
            self.item_combo.addItem(f"ID {item['item_id']}: {item['item_name']}", item['item_id'])

        self.qty_input = QDoubleSpinBox()
        self.qty_input.setRange(0, 10000)

        self.thresh_input = QDoubleSpinBox()
        self.thresh_input.setRange(0, 5000)

        self.cost_input = QDoubleSpinBox()
        self.cost_input.setRange(0, 10000)
        self.cost_input.setPrefix("P ")

        self.status_check = QCheckBox("Active")
        self.status_check.setChecked(True)

        layout.addRow("Link to Menu Item:", self.item_combo)
        layout.addRow("Initial Quantity:", self.qty_input)
        layout.addRow("Low Stock Threshold:", self.thresh_input)
        layout.addRow("Unit Cost (What you pay):", self.cost_input)
        layout.addRow("Status:", self.status_check)

        btn = QPushButton("Save to Inventory")
        btn.setStyleSheet("background-color: #2ecc71; color: white; padding: 10px; font-weight: bold;")
        btn.clicked.connect(self.accept)
        layout.addRow(btn)

    def get_data(self):
        return {
            "item_id": self.item_combo.currentData(),
            "quantity": self.qty_input.value(),
            "threshold": self.thresh_input.value(),
            "unit_cost": self.cost_input.value(),
            "status": self.status_check.isChecked()
        }


class ReceiveStockDialog(QDialog):
    """Dialog for PUT /inventory/receive/{item_id}"""

    def __init__(self, parent=None, item_id=None, item_name=""):
        super().__init__(parent)
        self.setWindowTitle(f"Receive Stock for {item_name}")
        self.item_id = item_id
        self.initUI()

    def initUI(self):
        layout = QFormLayout(self)

        self.qty_input = QDoubleSpinBox()
        self.qty_input.setRange(0, 10000)
        self.qty_input.setToolTip("Amount of NEW stock arriving")

        self.cost_input = QDoubleSpinBox()
        self.cost_input.setRange(0, 10000)
        self.cost_input.setPrefix("P ")
        self.cost_input.setToolTip("Update unit cost if supplier prices changed")

        layout.addRow("Amount Received:", self.qty_input)
        layout.addRow("New Unit Cost:", self.cost_input)

        btn = QPushButton("Update Stock")
        btn.setStyleSheet("background-color: #f39c12; color: white; padding: 10px; font-weight: bold;")
        btn.clicked.connect(self.accept)
        layout.addRow(btn)

    def get_data(self):
        return {
            "quantity": self.qty_input.value(),
            "unit_cost": self.cost_input.value()
        }


class InventoryModule(QWidget):
    def __init__(self, token=""):
        super().__init__()
        self.token = token  # Assuming you pass the auth token for the Admin routes
        self.menu_items = []
        self.initUI()
        self.refresh_table()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- HEADER ---
        header_layout = QHBoxLayout()
        title = QLabel("Inventory Management")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #4b3621;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        add_btn = QPushButton("+ Add New Item")
        add_btn.setStyleSheet(
            "background-color: #2ecc71; color: white; padding: 12px 20px; font-weight: bold; border-radius: 5px;")
        add_btn.clicked.connect(self.handle_add_item)
        header_layout.addWidget(add_btn)
        layout.addLayout(header_layout)

        # --- MAIN DATA TABLE ---
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Item ID", "Product Name", "Stock Level", "Threshold", "Unit Cost (P)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setStyleSheet("""
            QTableWidget { background-color: white; border: 1px solid #ddd; font-size: 14px; }
            QHeaderView::section { background-color: #f4eee8; padding: 8px; font-weight: bold; color: #333; }
        """)
        layout.addWidget(self.table)

        # --- ACTION BUTTONS ---
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        receive_btn = QPushButton("Receive Stock (Edit)")
        receive_btn.setStyleSheet(
            "background-color: #f39c12; color: white; padding: 10px 25px; font-weight: bold; border-radius: 5px;")
        receive_btn.clicked.connect(self.handle_receive_stock)

        btn_layout.addWidget(receive_btn)
        layout.addLayout(btn_layout)

    def get_headers(self):
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def refresh_table(self):
        """Fetches data and populates the table."""
        try:
            # 1. Fetch Menu Items to get names
            menu_res = requests.get(f"{API_BASE_URL}/menu")
            if menu_res.status_code == 200:
                self.menu_items = menu_res.json()

            # 2. Fetch Inventory details
            # (Assuming you have a GET /inventory route. If not, see the note below!)
            inv_res = requests.get(f"{API_BASE_URL}/inventory", headers=self.get_headers())

            if inv_res.status_code == 200:
                data = inv_res.json()
                self.table.setRowCount(len(data))
                for row, item in enumerate(data):
                    self.table.setItem(row, 0, QTableWidgetItem(str(item['item_id'])))

                    # Match name from menu
                    name = next((m['item_name'] for m in self.menu_items if m['item_id'] == item['item_id']),
                                "Unknown Ingredient")
                    self.table.setItem(row, 1, QTableWidgetItem(name))

                    # Highlight low stock
                    qty_item = QTableWidgetItem(str(item['quantity']))
                    if item['quantity'] <= item['threshold']:
                        qty_item.setBackground(QColor("#ffcccc"))  # Light red warning

                    self.table.setItem(row, 2, qty_item)
                    self.table.setItem(row, 3, QTableWidgetItem(str(item['threshold'])))
                    self.table.setItem(row, 4, QTableWidgetItem(f"P {item['unit_cost']:.2f}"))
        except Exception as e:
            print(f"Error loading inventory: {e}")

    def handle_add_item(self):
        """Logic for POST /inventory"""
        dialog = AddInventoryDialog(self, self.menu_items)
        if dialog.exec_() == QDialog.Accepted:
            payload = dialog.get_data()
            try:
                resp = requests.post(f"{API_BASE_URL}/inventory", json=payload, headers=self.get_headers())
                if resp.status_code == 200:
                    QMessageBox.information(self, "Success", "Inventory record created!")
                    self.refresh_table()
                else:
                    QMessageBox.warning(self, "Error", resp.text)
            except Exception as e:
                QMessageBox.critical(self, "Network Error", str(e))

    def handle_receive_stock(self):
        """Logic for PUT /inventory/receive/{item_id}"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection", "Select an item to receive stock for.")
            return

        item_id = int(self.table.item(row, 0).text())
        item_name = self.table.item(row, 1).text()

        dialog = ReceiveStockDialog(self, item_id, item_name)
        if dialog.exec_() == QDialog.Accepted:
            payload = dialog.get_data()
            try:
                resp = requests.put(f"{API_BASE_URL}/inventory/receive/{item_id}", json=payload,
                                    headers=self.get_headers())
                if resp.status_code == 200:
                    result = resp.json()
                    msg = f"Stock updated! New Total: {result.get('new_total', 'N/A')}"
                    if result.get('low_stock_alert'):
                        msg += "\n\nWARNING: Item is still below threshold."
                    QMessageBox.information(self, "Success", msg)
                    self.refresh_table()
                else:
                    QMessageBox.warning(self, "Error", resp.text)
            except Exception as e:
                QMessageBox.critical(self, "Network Error", str(e))