import sys
import requests
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Pulls the backend URL from your config
from config import API_BASE_URL


class AddInventoryDialog(QDialog):
    """Dialog for POST /inventory - Declaring new raw ingredients"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Raw Ingredient")
        self.initUI()

    def initUI(self):
        layout = QFormLayout(self)

        # CHANGED: Replaced Menu Link dropdown with a simple text input for the Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Salt, Beef Patty, Mayonnaise")

        # CHANGED: Added QDoubleSpinBox and increased range to handle large decimal weights
        self.qty_input = QDoubleSpinBox()
        self.qty_input.setRange(0, 99999)
        self.qty_input.setDecimals(2)

        # NEW: Dropdown for Unit of Measure
        self.unit_input = QComboBox()
        self.unit_input.addItems(["g", "kg", "ml", "L", "pcs", "packs"])

        self.thresh_input = QDoubleSpinBox()
        self.thresh_input.setRange(0, 99999)
        self.thresh_input.setDecimals(2)

        self.cost_input = QDoubleSpinBox()
        self.cost_input.setRange(0, 99999)
        self.cost_input.setPrefix("P ")
        self.cost_input.setDecimals(2)

        self.status_check = QCheckBox("Active")
        self.status_check.setChecked(True)

        layout.addRow("Ingredient Name:", self.name_input)
        layout.addRow("Initial Quantity:", self.qty_input)
        layout.addRow("Unit of Measure:", self.unit_input)
        layout.addRow("Low Stock Threshold:", self.thresh_input)
        layout.addRow("Unit Cost (P):", self.cost_input)
        layout.addRow("Status:", self.status_check)

        btn = QPushButton("Save to Inventory")
        btn.setStyleSheet("background-color: #2ecc71; color: white; padding: 10px; font-weight: bold;")
        btn.clicked.connect(self.accept)
        layout.addRow(btn)

    def get_data(self):
        return {
            "item_name": self.name_input.text(),  # Sends item_name directly
            "quantity": self.qty_input.value(),
            "unit_measure": self.unit_input.currentText(),  # Sends the selected unit
            "threshold": self.thresh_input.value(),
            "unit_cost": self.cost_input.value(),
            "status": self.status_check.isChecked()
        }


class ReceiveStockDialog(QDialog):
    """Dialog for PUT /inventory/receive/{inventory_id}"""

    def __init__(self, parent=None, inventory_id=None, item_name=""):
        super().__init__(parent)
        self.setWindowTitle(f"Receive Stock for {item_name}")
        self.inventory_id = inventory_id
        self.initUI()

    def initUI(self):
        layout = QFormLayout(self)

        self.qty_input = QDoubleSpinBox()
        self.qty_input.setRange(0, 99999)
        self.qty_input.setDecimals(2)
        self.qty_input.setToolTip("Amount of NEW stock arriving")

        self.cost_input = QDoubleSpinBox()
        self.cost_input.setRange(0, 99999)
        self.cost_input.setPrefix("P ")
        self.cost_input.setDecimals(2)
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
    def __init__(self, token="", user_id="1"):
        super().__init__()
        self.token = token
        self.user_id = str(user_id) # Store the dynamic user ID
        self.initUI()
        self.refresh_table()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- HEADER ---
        header_layout = QHBoxLayout()
        title = QLabel("Inventory & Pantry Management")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #4b3621;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        add_btn = QPushButton("+ Add Raw Ingredient")
        add_btn.setStyleSheet(
            "background-color: #2ecc71; color: white; padding: 12px 20px; font-weight: bold; border-radius: 5px;")
        add_btn.clicked.connect(self.handle_add_item)
        header_layout.addWidget(add_btn)
        layout.addLayout(header_layout)

        # --- MAIN DATA TABLE ---
        # CHANGED: Added "Unit" column and updated labels
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Ingredient Name", "Stock Level", "Unit", "Threshold", "Unit Cost (P)"])
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

        return {
            "Authorization": f"Bearer {self.token}",
            "user-id": self.user_id
        }

    def refresh_table(self):
        """Fetches data and populates the table."""
        try:
            # CHANGED: Completely removed the secondary fetch to the Menu API
            # It now strictly pulls from the Inventory table only
            inv_res = requests.get(f"{API_BASE_URL}/inventory", headers=self.get_headers())

            if inv_res.status_code == 200:
                data = inv_res.json()
                self.table.setRowCount(len(data))

                for row, item in enumerate(data):
                    # Uses inventory_id and item_name directly from the database response
                    self.table.setItem(row, 0, QTableWidgetItem(str(item['inventory_id'])))
                    self.table.setItem(row, 1, QTableWidgetItem(item['item_name']))

                    # Format quantities to 2 decimal places for weight/volume tracking
                    qty_item = QTableWidgetItem(f"{item['quantity']:.2f}")

                    if float(item['quantity']) <= float(item['threshold']):
                        qty_item.setBackground(QColor("#ffcccc"))  # Light red warning

                    self.table.setItem(row, 2, qty_item)
                    self.table.setItem(row, 3, QTableWidgetItem(item['unit_measure']))
                    self.table.setItem(row, 4, QTableWidgetItem(f"{item['threshold']:.2f}"))
                    self.table.setItem(row, 5, QTableWidgetItem(f"P {item['unit_cost']:.2f}"))
        except Exception as e:
            print(f"Error loading inventory: {e}")

    def handle_add_item(self):
        """Logic for POST /inventory"""
        # CHANGED: No longer passing self.menu_items
        dialog = AddInventoryDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            payload = dialog.get_data()
            try:
                resp = requests.post(f"{API_BASE_URL}/inventory", json=payload, headers=self.get_headers())
                if resp.status_code == 200:
                    QMessageBox.information(self, "Success", "Ingredient added to inventory!")
                    self.refresh_table()
                else:
                    QMessageBox.warning(self, "Error", resp.text)
            except Exception as e:
                QMessageBox.critical(self, "Network Error", str(e))

    def handle_receive_stock(self):
        """Logic for PUT /inventory/receive/{inventory_id}"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection", "Select an item to receive stock for.")
            return

        inventory_id = int(self.table.item(row, 0).text())
        item_name = self.table.item(row, 1).text()

        dialog = ReceiveStockDialog(self, inventory_id, item_name)
        if dialog.exec_() == QDialog.Accepted:
            payload = dialog.get_data()
            try:
                # CHANGED: Route now points to inventory_id instead of item_id
                resp = requests.put(f"{API_BASE_URL}/inventory/receive/{inventory_id}", json=payload,
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