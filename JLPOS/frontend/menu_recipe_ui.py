import sys
import requests
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from config import API_BASE_URL


# --- NEW: Dialog specifically for creating Categories ---
class AddCategoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Category")
        self.initUI()

    def initUI(self):
        layout = QFormLayout(self)
        self.name = QLineEdit()
        self.name.setPlaceholderText("e.g., Burgers, Drinks, Desserts")
        self.desc = QLineEdit()

        layout.addRow("Category Name:", self.name)
        layout.addRow("Description:", self.desc)

        btn = QPushButton("Save Category")
        btn.clicked.connect(self.accept)
        btn.setStyleSheet("background-color: #f39c12; color: white; padding: 10px; font-weight: bold;")
        layout.addRow(btn)

    def get_data(self):
        return {
            "category_name": self.name.text(),
            "description": self.desc.text()
        }


class AddRecipeDialog(QDialog):
    """Integrated Dialog for adding ingredients to a Menu Item."""

    def __init__(self, parent=None, menu_item_id=None, item_name="", inventory_items=[]):
        super().__init__(parent)
        self.setWindowTitle(f"Add Ingredient to {item_name}")
        self.item_id = menu_item_id
        self.inventory_items = inventory_items
        self.initUI()

    def initUI(self):
        layout = QFormLayout(self)

        self.inv_combo = QComboBox()
        for item in self.inventory_items:
            display_text = f"{item['item_name']} ({item['unit_measure']})"
            self.inv_combo.addItem(display_text, item['inventory_id'])

        self.qty_input = QDoubleSpinBox()
        self.qty_input.setRange(0.01, 9999.0)
        self.qty_input.setDecimals(2)

        self.unit_input = QLineEdit()
        self.unit_input.setPlaceholderText("Must match inventory unit (e.g., g, ml, pcs)")

        self.notes_input = QLineEdit()

        layout.addRow("Select Ingredient:", self.inv_combo)
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
            "inventory_id": self.inv_combo.currentData(),
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
        self.inventory_items = []
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

        # NEW: Button to Add Category
        add_cat_btn = QPushButton("+ New Category")
        add_cat_btn.setStyleSheet(
            "background-color: #f39c12; color: white; padding: 12px 20px; font-weight: bold; border-radius: 5px; margin-right: 10px;")
        add_cat_btn.clicked.connect(self.add_category)
        header.addWidget(add_cat_btn)

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

        self.recipe_table = QTableWidget(0, 4)
        self.recipe_table.setHorizontalHeaderLabels(["Inv ID", "Ingredient Name", "Quantity", "Unit"])
        self.recipe_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        recipe_vbox.addWidget(self.recipe_table)

        self.splitter.addWidget(self.recipe_container)
        self.main_layout.addWidget(self.splitter)

    def refresh_data(self):
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

                    c_name = next(
                        (c['category_name'] for c in self.categories if c['category_id'] == item['category_id']),
                        "Unknown")
                    self.menu_table.setItem(row, 2, QTableWidgetItem(c_name))
                    self.menu_table.setItem(row, 3, QTableWidgetItem(f"P {item['price']:.2f}"))
                    self.menu_table.setItem(row, 4, QTableWidgetItem("Active" if item['available'] else "Disabled"))

            # Load Inventory
            inv_resp = requests.get(f"{API_BASE_URL}/inventory")
            if inv_resp.status_code == 200:
                self.inventory_items = inv_resp.json()

        except Exception as e:
            print(f"Error refreshing data: {e}")

    # --- NEW: Function to handle the new category button ---
    def add_category(self):
        """Logic for POST /menu/categories"""
        diag = AddCategoryDialog(self)
        if diag.exec_() == QDialog.Accepted:
            payload = diag.get_data()
            try:
                resp = requests.post(f"{API_BASE_URL}/menu/categories", json=payload)
                if resp.status_code == 200:
                    QMessageBox.information(self, "Success", "Category created successfully!")
                    self.refresh_data()  # Refreshes the internal list so the Menu Dialog sees it!
                else:
                    QMessageBox.warning(self, "Error", resp.text)
            except Exception as e:
                QMessageBox.critical(self, "Network Error", str(e))

    def add_menu_item(self):
        if not self.categories:
            QMessageBox.warning(self, "Warning", "Please create a Category first before adding a Menu Item!")
            return

        diag = AddMenuDialog(self, self.categories)
        if diag.exec_() == QDialog.Accepted:
            payload = diag.get_data()
            resp = requests.post(f"{API_BASE_URL}/menu", json=payload)
            if resp.status_code == 200:
                QMessageBox.information(self, "Success", "Dish declared successfully!")
                self.refresh_data()

    def load_selected_recipe(self):
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
                    self.recipe_table.setItem(r, 0, QTableWidgetItem(str(ing['inventory_id'])))
                    self.recipe_table.setItem(r, 1, QTableWidgetItem(ing['item_name']))
                    self.recipe_table.setItem(r, 2, QTableWidgetItem(str(ing['quantity'])))
                    self.recipe_table.setItem(r, 3, QTableWidgetItem(ing['unit_measure']))
        except:
            self.recipe_table.setRowCount(0)

    def add_ingredient(self):
        row = self.menu_table.currentRow()
        item_id = int(self.menu_table.item(row, 0).text())
        name = self.menu_table.item(row, 1).text()

        diag = AddRecipeDialog(self, item_id, name, self.inventory_items)
        if diag.exec_() == QDialog.Accepted:
            payload = diag.get_data()
            resp = requests.post(f"{API_BASE_URL}/recipe", json=payload)
            if resp.status_code == 200:
                self.load_selected_recipe()