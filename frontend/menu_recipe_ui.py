import sys
import requests
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Pulls the backend URL from your config
from config import API_BASE_URL


class AddRecipeDialog(QDialog):
    """Integrated Dialog for adding ingredients to a Menu Item."""

    def __init__(self, parent=None, menu_item_id=None, item_name=""):
        super().__init__(parent)
        self.setWindowTitle(f"Add Ingredient to {item_name}")
        self.item_id = menu_item_id
        self.initUI()

    def initUI(self):
        layout = QFormLayout(self)

        # We use integer for inventory_id to match your Inventory item_id
        self.inv_id_input = QSpinBox()
        self.inv_id_input.setRange(1, 9999)

        self.qty_input = QDoubleSpinBox()
        self.qty_input.setRange(0.01, 1000.0)

        self.unit_input = QLineEdit()
        self.unit_input.setPlaceholderText("e.g., grams, pcs, kg")

        self.notes_input = QLineEdit()

        layout.addRow("Inventory ID:", self.inv_id_input)
        layout.addRow("Quantity Used:", self.qty_input)
        layout.addRow("Unit Measure:", self.unit_input)
        layout.addRow("Prep Notes:", self.notes_input)

        self.btn = QPushButton("Add to Recipe")
        self.btn.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; padding: 10px;")
        self.btn.clicked.connect(self.accept)
        layout.addRow(self.btn)

    def get_data(self):
        return {
            "item_id": self.item_id,
            "inventory_id": self.inv_id_input.value(),
            "quantity": self.qty_input.value(),
            "unit_measure": self.unit_input.text(),
            "prep_notes": self.notes_input.text()
        }


class AddMenuDialog(QDialog):
    """Integrated Dialog for declaring a new Menu Dish"""

    def __init__(self, parent=None, categories=[]):
        super().__init__(parent)
        self.setWindowTitle("Declare New Menu Item")
        self.categories = categories
        self.initUI()

    def initUI(self):
        layout = QFormLayout(self)
        self.name = QLineEdit()
        self.price = QDoubleSpinBox()
        self.price.setRange(0, 10000)

        self.cat_combo = QComboBox()
        for cat in self.categories:
            self.cat_combo.addItem(cat['category_name'], cat['category_id'])

        self.desc = QLineEdit()
        self.avail = QCheckBox("Available for Sale")
        self.avail.setChecked(True)

        layout.addRow("Dish Name:", self.name)
        layout.addRow("Category:", self.cat_combo)
        layout.addRow("Selling Price:", self.price)
        layout.addRow("Description:", self.desc)
        layout.addRow(self.avail)

        btn = QPushButton("Save to Database")
        btn.clicked.connect(self.accept)
        btn.setStyleSheet("background-color: #2ecc71; color: white; padding: 10px;")
        layout.addRow(btn)

    def get_data(self):
        return {
            "item_name": self.name.text(),
            "description": self.desc.text(),
            "price": self.price.value(),
            "category_id": self.cat_combo.currentData(),
            "available": self.avail.isChecked()
        }


class MenuRecipeModule(QWidget):
    def __init__(self):
        super().__init__()
        self.categories = []
        self.initUI()
        self.refresh_data()

    def initUI(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # --- HEADER ---
        header = QHBoxLayout()
        title = QLabel("Menu & Recipe Management")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #4b3621;")
        header.addWidget(title)
        header.addStretch()

        add_btn = QPushButton("+ New Menu Item")
        add_btn.setStyleSheet(
            "background-color: #2ecc71; color: white; padding: 12px 20px; font-weight: bold; border-radius: 5px;")
        add_btn.clicked.connect(self.add_menu_item)
        header.addWidget(add_btn)
        self.main_layout.addLayout(header)

        # --- SPLITTER FOR MENU AND RECIPE ---
        self.splitter = QSplitter(Qt.Vertical)

        # 1. Menu Table Section
        self.menu_container = QWidget()
        menu_vbox = QVBoxLayout(self.menu_container)
        menu_vbox.addWidget(QLabel("<b>Current Menu List</b>"))

        self.menu_table = QTableWidget(0, 5)
        self.menu_table.setHorizontalHeaderLabels(["ID", "Item Name", "Category", "Price", "Status"])
        self.menu_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.menu_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.menu_table.itemSelectionChanged.connect(self.load_selected_recipe)
        menu_vbox.addWidget(self.menu_table)

        self.splitter.addWidget(self.menu_container)

        # 2. Recipe Table Section
        self.recipe_container = QWidget()
        recipe_vbox = QVBoxLayout(self.recipe_container)

        rec_header = QHBoxLayout()
        self.recipe_label = QLabel("<b>Recipe Ingredients (Select an item above)</b>")
        rec_header.addWidget(self.recipe_label)
        rec_header.addStretch()

        self.add_ing_btn = QPushButton("+ Add Ingredient")
        self.add_ing_btn.setEnabled(False)
        self.add_ing_btn.clicked.connect(self.add_ingredient)
        rec_header.addWidget(self.add_ing_btn)
        recipe_vbox.addLayout(rec_header)

        self.recipe_table = QTableWidget(0, 3)
        self.recipe_table.setHorizontalHeaderLabels(["Inventory ID", "Quantity", "Unit"])
        self.recipe_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        recipe_vbox.addWidget(self.recipe_table)

        self.splitter.addWidget(self.recipe_container)
        self.main_layout.addWidget(self.splitter)

    def refresh_data(self):
        """Pulls categories and menu from backend"""
        try:
            # Load Categories
            cat_resp = requests.get(f"{API_BASE_URL}/menu/categories")
            if cat_resp.status_code == 200:
                self.categories = cat_resp.json()

            # Load Menu
            menu_resp = requests.get(f"{API_BASE_URL}/menu")
            if menu_resp.status_code == 200:
                items = menu_resp.json()
                self.menu_table.setRowCount(len(items))
                for row, item in enumerate(items):
                    self.menu_table.setItem(row, 0, QTableWidgetItem(str(item['item_id'])))
                    self.menu_table.setItem(row, 1, QTableWidgetItem(item['item_name']))

                    # Map Cat ID to Name
                    c_name = next(
                        (c['category_name'] for c in self.categories if c['category_id'] == item['category_id']),
                        "Unknown")
                    self.menu_table.setItem(row, 2, QTableWidgetItem(c_name))
                    self.menu_table.setItem(row, 3, QTableWidgetItem(f"P {item['price']:.2f}"))
                    self.menu_table.setItem(row, 4, QTableWidgetItem("Active" if item['available'] else "Disabled"))
        except Exception as e:
            print(f"Error refreshing menu: {e}")

    def add_menu_item(self):
        """Logic for POST /menu"""
        diag = AddMenuDialog(self, self.categories)
        if diag.exec_() == QDialog.Accepted:
            payload = diag.get_data()
            resp = requests.post(f"{API_BASE_URL}/menu", json=payload)
            if resp.status_code == 200:
                QMessageBox.information(self, "Success", "Dish declared successfully!")
                self.refresh_data()

    def load_selected_recipe(self):
        """Integrated logic: Fetching recipe based on Menu selection"""
        row = self.menu_table.currentRow()
        if row < 0: return

        item_id = self.menu_table.item(row, 0).text()
        item_name = self.menu_table.item(row, 1).text()
        self.recipe_label.setText(f"<b>Recipe for: {item_name}</b>")
        self.add_ing_btn.setEnabled(True)

        try:
            resp = requests.get(f"{API_BASE_URL}/recipe/{item_id}")
            if resp.status_code == 200:
                data = resp.json()
                self.recipe_table.setRowCount(len(data))
                for r, ing in enumerate(data):
                    self.recipe_table.setItem(r, 0, QTableWidgetItem(str(ing['inv_id'])))
                    self.recipe_table.setItem(r, 1, QTableWidgetItem(str(ing['quantity'])))
                    self.recipe_table.setItem(r, 2, QTableWidgetItem(ing['unit_measure']))
        except:
            self.recipe_table.setRowCount(0)

    def add_ingredient(self):
        """Logic for POST /recipe"""
        row = self.menu_table.currentRow()
        item_id = int(self.menu_table.item(row, 0).text())
        name = self.menu_table.item(row, 1).text()

        diag = AddRecipeDialog(self, item_id, name)
        if diag.exec_() == QDialog.Accepted:
            payload = diag.get_data()
            resp = requests.post(f"{API_BASE_URL}/recipe", json=payload)
            if resp.status_code == 200:
                self.load_selected_recipe()  # Refresh recipe table