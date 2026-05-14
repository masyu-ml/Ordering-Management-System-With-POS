from fastapi import APIRouter, HTTPException, Depends
from database import pull_db
from schemas.models import OrderSchema
from routers.auth import verify_role

router = APIRouter()

VAT_RATE = 0.12

# --- 1. THE POS CHECKOUT (Admin & Cashier) ---
@router.post("/checkout", tags=["pos"], dependencies=[Depends(verify_role(["Admin", "Cashier"]))])
def create_order(payload: OrderSchema):
    db = pull_db()
    cursor = db.cursor()

    try:
        # --- PHASE ONE: MATH & RECIPE VERIFICATION ---
        subtotal = 0.0

        for item in payload.items:
            # Check if this Menu Item has a Recipe
            cursor.execute("SELECT inventory_id, quantity FROM Recipe WHERE item_id = %s", (item.item_id,))
            recipe_items = cursor.fetchall()

            if recipe_items:
                # Level B Logic: Verify all ingredients in the recipe
                for inv_id, qty_per_unit in recipe_items:
                    total_needed = qty_per_unit * item.quantity
                    cursor.execute("SELECT quantity FROM Inventory WHERE item_id = %s", (inv_id,))
                    inv_result = cursor.fetchone()

                    if not inv_result:
                        raise Exception(f"Ingredient ID {inv_id} for '{item.item_id}' not found in inventory.")
                    if inv_result[0] < total_needed:
                        raise Exception(f"Insufficient stock for Ingredient ID {inv_id}. Need {total_needed}.")
            else:
                # Level A Fallback: Check for 1:1 match in Inventory
                cursor.execute("SELECT quantity FROM Inventory WHERE item_id = %s", (item.item_id,))
                result = cursor.fetchone()

                if not result:
                    raise Exception(f"Item ID {item.item_id} not found in inventory or recipe.")
                if result[0] < item.quantity:
                    raise Exception(f"Insufficient stock for item ID {item.item_id}.")

            subtotal += (item.quantity * item.unit_price)

        # --- PHASE TWO: CALCULATE DISCOUNTS AND TAXES ---
        discounted_subtotal = max(0.0, subtotal - payload.discount_amount)
        vat_amount = discounted_subtotal * VAT_RATE
        grand_total = discounted_subtotal + vat_amount

        if payload.amount_paid < grand_total:
            raise Exception(f"Insufficient payment. Total is {grand_total:.2f}.")

        # --- PHASE THREE: DATABASE INSERTS & DEDUCTION ---
        sql_order = """INSERT INTO `Order` 
                       (status, subtotal, discount_amount, vat_rate, vat_amount, grand_total) 
                       VALUES (%s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql_order, (payload.status, subtotal, payload.discount_amount, VAT_RATE, vat_amount, grand_total))
        new_order_id = cursor.lastrowid

        for item in payload.items:
            # Check for Recipe again to perform actual deduction
            cursor.execute("SELECT inventory_id, quantity FROM Recipe WHERE item_id = %s", (item.item_id,))
            recipe_items = cursor.fetchall()

            if recipe_items:
                # Deduct multiple ingredients based on recipe
                for inv_id, qty_per_unit in recipe_items:
                    deduction_amount = qty_per_unit * item.quantity
                    sql_update_stock = "UPDATE Inventory SET quantity = quantity - %s WHERE item_id = %s"
                    cursor.execute(sql_update_stock, (deduction_amount, inv_id))
            else:
                # Deduct 1:1 if no recipe exists
                sql_update_stock = "UPDATE Inventory SET quantity = quantity - %s WHERE item_id = %s"
                cursor.execute(sql_update_stock, (item.quantity, item.item_id))

            # Record Line Item in Order_Details
            sql_details = """INSERT INTO Order_Details (order_id, item_id, quantity, unit_price, notes) 
                             VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(sql_details, (new_order_id, item.item_id, item.quantity, item.unit_price, item.notes))

        # Record Payment
        sql_payment = "INSERT INTO Payment (order_id, amount, payment_method) VALUES (%s, %s, %s)"
        cursor.execute(sql_payment, (new_order_id, payload.amount_paid, payload.payment_method))

        db.commit()
        return {
            "status": "success",
            "order_id": new_order_id,
            "receipt": {
                "subtotal": round(subtotal, 2),
                "vat_12": round(vat_amount, 2),
                "grand_total": round(grand_total, 2),
                "change_due": round(payload.amount_paid - grand_total, 2)
            }
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        db.close()

# --- 2. SALES REPORTS (Admin Only) ---
@router.get("/orders", tags=["reports"], dependencies=[Depends(verify_role(["Admin"]))])
def get_sales_report():
    db = pull_db()
    cursor = db.cursor(dictionary=True)

    try:
        sql = """
        SELECT 
            o.order_id, o.order_time, o.status, 
            SUM(od.quantity * od.unit_price) as total_bill,
            COUNT(od.item_id) as items_count
        FROM `Order` o
        JOIN Order_Details od ON o.order_id = od.order_id
        GROUP BY o.order_id
        ORDER BY o.order_time DESC
        """
        cursor.execute(sql)
        orders = cursor.fetchall()
        total_revenue = sum(order['total_bill'] for order in orders) if orders else 0

        return {
            "status": "success",
            "total_revenue": total_revenue,
            "total_orders": len(orders),
            "sales_history": orders
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()
        db.close()