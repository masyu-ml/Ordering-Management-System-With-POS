from fastapi import APIRouter, HTTPException
from database import pull_db

# This line is CRITICAL for main.py to "see" the routes
router = APIRouter()

# 1. DISPLAY ORDER ON KDS SCREEN
@router.get("/kitchen/pending", tags=["kitchen"])
def get_pending_orders():
    db = pull_db()
    cursor = db.cursor(dictionary=True)
    try:
        sql = """
        SELECT 
            o.order_id, 
            o.order_time, 
            m.item_name, 
            od.quantity, 
            od.notes 
        FROM `Order` o
        JOIN Order_Details od ON o.order_id = od.order_id
        JOIN Menu m ON od.item_id = m.item_id
        WHERE o.status = 1 
        ORDER BY o.order_time ASC
        """
        cursor.execute(sql)
        return {"status": "success", "pending_tickets": cursor.fetchall()}
    finally:
        cursor.close()
        db.close()


# 2. CLEAR ORDER -> ORDER COMPLETE (The "YES" Path)
@router.put("/kitchen/complete/{order_id}", tags=["kitchen"])
def mark_order_completed(order_id: int):
    db = pull_db()
    cursor = db.cursor()
    try:
        # Added backticks around `Order` here:
        sql = "UPDATE `Order` SET status = 0 WHERE order_id = %s"
        cursor.execute(sql, (order_id,))
        db.commit()
        return {"status": "success", "message": f"Order #{order_id} cleared as COMPLETED."}
    finally:
        cursor.close()
        db.close()


# 3. CANCEL ORDER (The "NO" Path)
@router.put("/kitchen/cancel/{order_id}", tags=["kitchen"])
def mark_order_canceled(order_id: int):
    db = pull_db()
    cursor = db.cursor()
    try:
        # Added backticks around `Order` here:
        sql = "UPDATE `Order` SET status = 2 WHERE order_id = %s"
        cursor.execute(sql, (order_id,))
        db.commit()
        return {"status": "success", "message": f"Order #{order_id} has been CANCELED."}
    finally:
        cursor.close()
        db.close()