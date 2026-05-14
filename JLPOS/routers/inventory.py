from fastapi import APIRouter, HTTPException, Depends
from database import pull_db
from schemas.models import InventorySchema, InventoryUpdate
from routers.auth import verify_role

router = APIRouter()

# --- 1. ADMIN ONLY: ENCODE NEW ITEM ---
@router.post("/inventory", tags=["inventory"], dependencies=[Depends(verify_role(["Admin"]))])
def create_inventory(stock: InventorySchema):
    db = pull_db()
    cursor = db.cursor()
    try:
        # Changed to insert item_name and unit_measure; inventory_id auto-generates
        sql = """INSERT INTO inventory(item_name, quantity, unit_measure, threshold, unit_cost, status) 
                 VALUES (%s, %s, %s, %s, %s, %s)"""
        values = (stock.item_name, stock.quantity, stock.unit_measure, stock.threshold, stock.unit_cost, stock.status)
        cursor.execute(sql, values)
        new_id = cursor.lastrowid # Grabs the newly created inventory_id
        db.commit()
        return {"status": "success", "message": f"Inventory record '{stock.item_name}' created with ID: {new_id}"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()
        db.close()

# --- 2. ADMIN ONLY: UPDATE INVENTORY (Receive Stock) ---
# Changed URL parameter from item_id to inventory_id
@router.put("/inventory/receive/{inventory_id}", tags=["inventory"], dependencies=[Depends(verify_role(["Admin"]))])
def receive_stock(inventory_id: int, data: InventoryUpdate):
    db = pull_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Changed WHERE clause to target inventory_id
        sql = "UPDATE inventory SET quantity = quantity + %s, unit_cost = %s WHERE inventory_id = %s"
        cursor.execute(sql, (data.quantity, data.unit_cost, inventory_id))
        db.commit()

        cursor.execute("SELECT quantity, threshold FROM inventory WHERE inventory_id = %s", (inventory_id,))
        item = cursor.fetchone()

        is_low = False
        if item and item['quantity'] <= item['threshold']:
            is_low = True

        return {
            "status": "success",
            "new_total": item['quantity'] if item else 0,
            "low_stock_alert": is_low
        }
    finally:
        cursor.close()
        db.close()

# --- 3. ADMIN ONLY: REPORT/RETURN ITEM ---
@router.post("/inventory/return/{inventory_id}", tags=["inventory"], dependencies=[Depends(verify_role(["Admin"]))])
def return_bad_stock(inventory_id: int, quantity: float, reason: str):
    db = pull_db()
    cursor = db.cursor()
    try:
        # Logic to handle return goes here. Just updating the success message for now.
        return {"status": "success", "message": f"Return logged for inventory ID {inventory_id}. Reason: {reason}"}
    finally:
        cursor.close()
        db.close()

# --- 4. ADMIN & CASHIER ONLY: TRIGGER ALERT (The View) ---
@router.get("/inventory/alerts", tags=["inventory"])
def get_low_stock_list(current_user=Depends(verify_role(["Admin", "Cashier"]))):
    db = pull_db()
    cursor = db.cursor(dictionary=True)
    try:
        sql = "SELECT * FROM inventory WHERE quantity <= threshold"
        cursor.execute(sql)
        return {"status": "success", "low_stock_items": cursor.fetchall()}
    finally:
        cursor.close()
        db.close()

# --- 5. GET ALL INVENTORY ---
@router.get("/inventory", tags=["inventory"])
def get_all_inventory():
    db = pull_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM inventory")
        return cursor.fetchall()
    finally:
        cursor.close()
        db.close()