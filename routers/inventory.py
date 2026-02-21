from fastapi import APIRouter
from database import pull_db
from schemas.models import InventorySchema

router = APIRouter()

@router.post("/inventory", tags=["inventory"])
def create_inventory(stock: InventorySchema):
    db = pull_db()
    cursor = db.cursor()

    sql = """INSERT INTO Inventory(item_id, quantity, threshold,unit_cost, status) VALUES (%s, %s, %s, %s, %s)"""
    values = (stock.item_id, stock.quantity, stock.threshold, stock.unit_cost, stock.status)

    try:
        cursor.execute(sql, values)
        db.commit()
        return {"status": "success", "message": f"Inventory item set for item {stock.item_id}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()
        db.close()

