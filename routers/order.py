from fastapi import APIRouter, HTTPException
from database import pull_db
from schemas.models import OrderSchema

router = APIRouter()

@router.post("/checkout", tags=["checkout"])
def create_order(payload: OrderSchema):
    db = pull_db()
    cursor = db.cursor()

    try:
        sql_order = """INSERT INTO `Order` (status) VALUES (%s)"""
        cursor.execute(sql_order, (payload.status,))
        new_order_id = cursor.lastrowid

        for item in payload.items:

            cursor.execute("SELECT quantity FROM Inventory WHERE item_id = %s", (item.item_id,))
            result = cursor.fetchone()

            if not result:
                raise Exception(f"Item ID {item.item_id} not found in inventory.")

            current_stock = result[0]

            if current_stock < item.quantity:
                raise Exception(f"Insufficient stock for item ID {item.item_id}. Available: {current_stock}, Requested: {item.quantity}")

            sql_update_stock = """UPDATE Inventory SET quantity = quantity - %s WHERE item_id = %s"""
            cursor.execute(sql_update_stock, (item.quantity, item.item_id))

            sql_details = """INSERT INTO Order_Details (order_id, item_id, quantity, unit_price, notes) VALUES (%s, %s, %s, %s, %s)"""

            detail_values = (new_order_id, item.item_id, item.quantity, item.unit_price, item.notes)
            cursor.execute(sql_details, detail_values)

        db.commit()
        return{"status": "success", "order_id": new_order_id, "message": "Order placed and stock updated."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        db.close()

@router.get("/checkout", tags=["reports"])
def get_sale_report():
    