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
        sql = """INSERT INTO Inventory(item_id, quantity, threshold, unit_cost, status) 
                 VALUES (%s, %s, %s, %s, %s)"""
        values = (stock.item_id, stock.quantity, stock.threshold, stock.unit_cost, stock.status)
        cursor.execute(sql, values)
        db.commit()
        return {"status": "success", "message": f"Inventory record created for item {stock.item_id}"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()
        db.close()


# --- 2. ADMIN ONLY: UPDATE INVENTORY (Receive Stock) ---
@router.put("/inventory/receive/{item_id}", tags=["inventory"], dependencies=[Depends(verify_role(["Admin"]))])
def receive_stock(item_id: int, data: InventoryUpdate):
    db = pull_db()
    cursor = db.cursor(dictionary=True)
    try:
        sql = "UPDATE Inventory SET quantity = quantity + %s, unit_cost = %s WHERE item_id = %s"
        cursor.execute(sql, (data.quantity, data.unit_cost, item_id))
        db.commit()

        cursor.execute("SELECT quantity, threshold FROM Inventory WHERE item_id = %s", (item_id,))
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
@router.post("/inventory/return/{item_id}", tags=["inventory"], dependencies=[Depends(verify_role(["Admin"]))])
def return_bad_stock(item_id: int, quantity: float, reason: str):
    db = pull_db()
    cursor = db.cursor()
    try:
        return {"status": "success", "message": f"Return logged for item {item_id}. Reason: {reason}"}
    finally:
        cursor.close()
        db.close()


# --- 4. ADMIN & CASHIER ONLY: TRIGGER ALERT (The View) ---
# 'Staff' has been removed from this list.
@router.get("/inventory/alerts", tags=["inventory"])
def get_low_stock_list(current_user=Depends(verify_role(["Admin", "Cashier"]))):
    db = pull_db()
    cursor = db.cursor(dictionary=True)
    try:
        sql = "SELECT * FROM Inventory WHERE quantity <= threshold"
        cursor.execute(sql)
        return {"status": "success", "low_stock_items": cursor.fetchall()}
    finally:
        cursor.close()
        db.close()
@router.get("/inventory", tags=["inventory"])
def get_all_inventory():
    db = pull_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Inventory")
        return cursor.fetchall()
    finally:
        cursor.close()
        db.close()