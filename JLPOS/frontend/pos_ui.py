import sys
import requests
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Pulls the backend URL dynamically from your config.py
from config import API_BASE_URL


class POSModule(QWidget):
    # Broadcasts the completed order to the KDS Window
    order_sent = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.cart = {}  # Format: {item_id: {'name': str, 'price': float, 'quantity': int}}
        self.menu_data = []
        self.category_data = []
        self.active_category_id = None  # None means "All Items"
        self.current_grand_total = 0.0

        self.initUI()
        self.load_database_content()  # Fetches DB info as soon as POS opens

    def initUI(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # --- LEFT SIDE: MENU & CATEGORIES ---
        self.menu_area = QWidget()
        self.menu_layout = QVBoxLayout(self.menu_area)

        # Category Bar (Scrollable horizontally)
        self.cat_scroll = QScrollArea()
        self.cat_scroll.setFixedHeight(80)
        self.cat_scroll.setWidgetResizable(True)
        self.cat_scroll.setStyleSheet("border: none; background: transparent;")

        self.cat_container = QWidget()
        self.cat_layout = QHBoxLayout(self.cat_container)
        self.cat_layout.setAlignment(Qt.AlignLeft)
        self.cat_scroll.setWidget(self.cat_container)

        self.menu_layout.addWidget(self.cat_scroll)

        # Item Grid (Scrollable vertically)
        self.item_scroll = QScrollArea()
        self.item_scroll.setWidgetResizable(True)
        self.item_scroll.setStyleSheet("border: none;")
        self.grid_widget = QWidget()
        self.grid = QGridLayout(self.grid_widget)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.item_scroll.setWidget(self.grid_widget)
        self.menu_layout.addWidget(self.item_scroll)

        self.main_layout.addWidget(self.menu_area, 3)

        # --- RIGHT SIDE: ORDER PANEL (RECEIPT) ---
        self.order_panel = QFrame()
        self.order_panel.setFixedWidth(380)
        self.order_panel.setStyleSheet("background-color: #f8f4ef; border-left: 2px dashed #ccc;")
        self.order_layout = QVBoxLayout(self.order_panel)

        self.order_number_label = QLabel("<h2 style='color: #333;'>Current Order</h2>")
        self.order_layout.addWidget(self.order_number_label)

        # Dine In / Take Out Toggles
        self.type_layout = QHBoxLayout()
        self.dine_in = QPushButton("Dine in")
        self.dine_in.setStyleSheet("background-color: #ccc; padding: 8px; font-weight: bold; border-radius: 5px;")
        self.take_out = QPushButton("Take out")
        self.take_out.setStyleSheet("background-color: transparent; padding: 8px;")
        self.type_layout.addWidget(self.dine_in)
        self.type_layout.addWidget(self.take_out)
        self.order_layout.addLayout(self.type_layout)

        # Interactive Receipt List (Double click to remove)
        self.order_list = QListWidget()
        self.order_list.setStyleSheet("background: white; border: 1px solid #ddd; font-size: 15px; padding: 5px;")
        self.order_list.itemDoubleClicked.connect(self.remove_from_cart)
        self.order_layout.addWidget(self.order_list)

        # Totals Display
        self.lbl_subtotal = QLabel("<span style='font-size: 15px; color: #555;'>Subtotal : P0.00</span>")
        self.lbl_vat = QLabel("<span style='font-size: 15px; color: #555;'>VAT 12% : P0.00</span>")
        self.lbl_total = QLabel("<h1 style='color: #222; margin-top: 10px;'>TOTAL: P0.00</h1>")

        self.order_layout.addWidget(self.lbl_subtotal)
        self.order_layout.addWidget(self.lbl_vat)
        self.order_layout.addWidget(self.lbl_total)

        # Action Buttons
        self.btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel Order")
        cancel_btn.setStyleSheet(
            "background: #c0392b; color: white; padding: 15px; border-radius: 5px; font-weight: bold; font-size: 14px;")
        cancel_btn.clicked.connect(self.clear_cart)

        send_btn = QPushButton("Checkout")
        send_btn.setStyleSheet(
            "background: #2ecc71; color: white; padding: 15px; border-radius: 5px; font-weight: bold; font-size: 14px;")
        send_btn.clicked.connect(self.process_checkout)

        self.btn_layout.addWidget(cancel_btn)
        self.btn_layout.addWidget(send_btn)
        self.order_layout.addLayout(self.btn_layout)

        self.main_layout.addWidget(self.order_panel, 1)

    def load_database_content(self):
        """Fetches REAL Categories and Menu Items from MySQL via FastAPI."""
        try:
            # 1. Fetch Categories [Mapped to your GET /menu/categories in menu.py]
            cat_resp = requests.get(f"{API_BASE_URL}/menu/categories")
            if cat_resp.status_code == 200:
                self.category_data = cat_resp.json()
                self.populate_category_bar()
            else:
                print("Error: Could not load categories from backend.")

            # 2. Fetch Menu Items [Mapped to your GET /menu in menu.py]
            menu_resp = requests.get(f"{API_BASE_URL}/menu")
            if menu_resp.status_code == 200:
                self.menu_data = menu_resp.json()
                self.populate_menu_grid()
            else:
                print("Error: Could not load menu items from backend.")

        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, "Server Offline", f"Cannot connect to FastAPI at {API_BASE_URL}")

    def populate_category_bar(self):
        """Builds the category buttons using DB records."""
        # Clear existing buttons
        for i in reversed(range(self.cat_layout.count())):
            self.cat_layout.itemAt(i).widget().setParent(None)

        # "All Items" Button
        all_btn = QPushButton("All Items")
        all_btn.setFixedSize(130, 55)
        self.apply_category_style(all_btn, is_active=(self.active_category_id is None))
        all_btn.clicked.connect(lambda checked: self.filter_by_category(None))
        self.cat_layout.addWidget(all_btn)

        # Dynamic Database Categories
        for cat in self.category_data:
            cat_id = cat.get('category_id')
            cat_name = cat.get('category_name', 'Unknown')

            btn = QPushButton(cat_name)
            btn.setFixedSize(130, 55)
            self.apply_category_style(btn, is_active=(self.active_category_id == cat_id))
            btn.clicked.connect(lambda checked, c_id=cat_id: self.filter_by_category(c_id))
            self.cat_layout.addWidget(btn)

    def apply_category_style(self, button, is_active):
        """Changes color depending on active filter (Matches Figma Design)"""
        if is_active:
            button.setStyleSheet(
                "background-color: #c0392b; color: white; font-weight: bold; border-radius: 10px; font-size: 16px;")
        else:
            button.setStyleSheet(
                "background-color: #bfa58a; color: white; font-weight: bold; border-radius: 10px; font-size: 16px;")

    def filter_by_category(self, category_id):
        """Sets the active category and refreshes UI."""
        self.active_category_id = category_id
        self.populate_category_bar()
        self.populate_menu_grid()

    def populate_menu_grid(self):
        """Builds item buttons filtered by category."""
        # Clear existing grid
        for i in reversed(range(self.grid.count())):
            self.grid.itemAt(i).widget().setParent(None)

        if not self.menu_data:
            self.grid.addWidget(QLabel("Menu is empty. Add items via the Menu & Recipe module."))
            return

        visible_index = 0
        for item in self.menu_data:
            # Check 'available' flag from MenuSchema
            if not item.get('available', True):
                continue

            # Filter logic
            item_cat_id = item.get('category_id')
            if self.active_category_id is not None and item_cat_id != self.active_category_id:
                continue

            item_id = item.get('item_id')
            name = item.get('item_name', 'Unknown')
            price = float(item.get('price', 0.0))

            btn = QPushButton(f"{name}\nP {price:.2f}")
            btn.setFixedSize(200, 140)
            btn.setStyleSheet("""
                QPushButton { background-color: #e74c3c; color: white; font-weight: bold; border-radius: 10px; font-size: 15px; }
                QPushButton:hover { background-color: #c0392b; }
            """)
            btn.clicked.connect(lambda checked, i_id=item_id, n=name, p=price: self.add_to_cart(i_id, n, p))

            row, col = divmod(visible_index, 4)  # 4 items per row
            self.grid.addWidget(btn, row, col)
            visible_index += 1

    def add_to_cart(self, item_id, name, price):
        """Adds DB item to cart dictionary."""
        if item_id in self.cart:
            self.cart[item_id]['quantity'] += 1
        else:
            self.cart[item_id] = {'name': name, 'price': price, 'quantity': 1}
        self.update_receipt_ui()

    def remove_from_cart(self, list_item):
        """Removes item on double-click."""
        item_id = list_item.data(Qt.UserRole)
        if item_id in self.cart:
            self.cart[item_id]['quantity'] -= 1
            if self.cart[item_id]['quantity'] <= 0:
                del self.cart[item_id]
        self.update_receipt_ui()

    def update_receipt_ui(self):
        """Calculates real totals based on cart contents."""
        self.order_list.clear()
        subtotal = 0.0

        for item_id, data in self.cart.items():
            qty = data['quantity']
            price = data['price']
            total_price = qty * price
            subtotal += total_price

            display_text = f"{qty}x  {data['name']}  -  P{total_price:.2f}"
            list_item = QListWidgetItem(display_text)
            list_item.setData(Qt.UserRole, item_id)
            self.order_list.addItem(list_item)

        # Exact VAT match to your backend order.py
        vat = subtotal * 0.12
        grand_total = subtotal + vat

        self.lbl_subtotal.setText(f"<span style='font-size: 15px; color: #555;'>Subtotal : P{subtotal:.2f}</span>")
        self.lbl_vat.setText(f"<span style='font-size: 15px; color: #555;'>VAT 12% : P{vat:.2f}</span>")
        self.lbl_total.setText(f"<h1 style='color: #222; margin-top: 10px;'>TOTAL: P{grand_total:.2f}</h1>")
        self.current_grand_total = grand_total

    def clear_cart(self):
        self.cart.clear()
        self.update_receipt_ui()

    def process_checkout(self):
        """Constructs models.py payload and fires it to order.py backend."""
        if not self.cart:
            QMessageBox.warning(self, "Empty Cart", "Please add items to the order first.")
            return

        # 1. Payment Prompt (Must be >= Grand Total)
        amount_paid, ok = QInputDialog.getDouble(
            self, "Payment Collection",
            f"Grand Total: P{self.current_grand_total:.2f}\n\nEnter Cash Amount:",
            decimals=2, min=self.current_grand_total, max=999999.0
        )
        if not ok:
            return

            # 2. Build items array matching OrderDetailSchema
        order_items = []
        for item_id, data in self.cart.items():
            order_items.append({
                "item_id": item_id,
                "quantity": data['quantity'],
                "unit_price": data['price'],
                "notes": ""
            })

        # 3. Build payload matching OrderSchema
        payload = {
            "status": "1",  # 1 = Active/Kitchen Pending
            "items": order_items,
            "payment_method": "Cash",
            "amount_paid": amount_paid,
            "discount_amount": 0.0
        }

        # 4. Mandatory Security Header (Required by verify_role in auth.py)
        # Assuming User 1 is logged in. In a fully connected app, pass `self.current_user_id` from the Login.
        headers = {
            "user-id": "1",
            "Content-Type": "application/json"
        }

        try:
            # Hit your POST /checkout route
            resp = requests.post(f"{API_BASE_URL}/checkout", json=payload, headers=headers)

            if resp.status_code == 200:
                result = resp.json()

                # Emit KDS Signal for Kitchen Screen
                kds_data = {
                    "order_number": result['order_id'],
                    "type": "Dine In",
                    "items": [f"{v['quantity']}x {v['name']}" for v in self.cart.values()]
                }
                self.order_sent.emit(kds_data)

                # Success Pop-up with backend-calculated change
                change = result['receipt']['change_due']
                QMessageBox.information(self, "Transaction Successful",
                                        f"Order #{result['order_id']} saved to database.\n\nChange Due: P{change:.2f}")
                self.clear_cart()
            else:
                # Extracts backend error (e.g., "Insufficient stock for item ID X")
                QMessageBox.critical(self, "Checkout Failed",
                                     f"Database Error:\n{resp.json().get('detail', resp.text)}")

        except Exception as e:
            QMessageBox.critical(self, "Server Error", f"Could not reach FastAPI backend:\n{e}")