from fastapi import APIRouter
from database import pull_db
from schemas.models import MenuSchema

router = APIRouter()

@router.post("/menu", tags=["menu"])
def create_menu(inputs: MenuSchema):
    db = pull_db()
    cursor = db.cursor()
    try:
        sql = """INSERT INTO Menu (item_name, description, price, category_id, available) VALUES (%s, %s, %s,%s,%s)"""
        values = (inputs.item_name, inputs.description, inputs.price, inputs.category_id, inputs.available)
        cursor.execute(sql, values)
        new_id = cursor.lastrowid
        db.commit()

        return {"Item_id": new_id, "status": "Added to the menu"}
    except Exception as e:
        return {"Status": "Error", "Message": str(e)}
    finally:
        cursor.close()
        db.close()

@router.get("/menu", tags=["menu"])
def get_menu():
        db = pull_db()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM Menu")
            results = cursor.fetchall()
            return results
        except Exception as e:
            return {"Status": "Error", "Message": str(e)}
        finally:
            cursor.close()
            db.close()