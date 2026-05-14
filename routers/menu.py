from fastapi import APIRouter
from database import pull_db
from schemas.models import MenuSchema, RecipeCreateSchema, CategorySchema

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
@router.put("/menu/{item_id}", tags=["menu"])
def update_menu_item(item_id: int, inputs: MenuSchema):
    db = pull_db()
    cursor = db.cursor()
    try:
        sql = "UPDATE Menu SET item_name=%s, description=%s, price=%s, category_id=%s, available=%s WHERE item_id=%s"
        cursor.execute(sql, (inputs.item_name, inputs.description, inputs.price, inputs.category_id, inputs.available, item_id))
        db.commit()
        return {"status": "success", "message": "Item updated"}
    finally:
        cursor.close()
        db.close()

@router.delete("/menu/{item_id}", tags=["menu"])
def delete_menu_item(item_id: int):
    db = pull_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM Menu WHERE item_id = %s", (item_id,))
        db.commit()
        return {"status": "success", "message": "Item deleted from menu"}
    finally:
        cursor.close()
        db.close()

@router.post("/recipe", tags=["recipe"])
def add_recipe_requirement(data: RecipeCreateSchema):
    db = pull_db()
    cursor = db.cursor()
    try:
        sql = """INSERT INTO Recipe (item_id, inventory_id, quantity, unit_measure, prep_notes) 
                 VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(sql, (data.item_id, data.inventory_id, data.quantity, data.unit_measure, data.prep_notes))
        db.commit()
        return {"status": "success", "message": "Ingredient added to recipe"}
    finally:
        cursor.close()
        db.close()

@router.get("/recipe/{menu_item_id}", tags=["recipe"])
def view_recipe(menu_item_id: int):
    db = pull_db()
    cursor = db.cursor(dictionary=True)
    try:
        # This join shows the Admin exactly what ingredients are in a dish
        sql = """
            SELECT r.recipe_id, i.item_id as inv_id, r.quantity, r.unit_measure 
            FROM Recipe r
            JOIN Inventory i ON r.inventory_id = i.item_id
            WHERE r.item_id = %s
        """
        cursor.execute(sql, (menu_item_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        db.close()

@router.post("/menu/categories", tags=["menu"])
def create_category(data: CategorySchema):
    db = pull_db()
    cursor = db.cursor()
    try:
        # The database handles the category_id automatically (Auto-Increment)
        sql = "INSERT INTO Category (category_name, description) VALUES (%s, %s)"
        cursor.execute(sql, (data.category_name, data.description))
        db.commit()
        return {"status": "success", "message": f"Category '{data.category_name}' created successfully."}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()
        db.close()
@router.get("/menu/categories", tags=["menu"])
def get_categories():
    db = pull_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Pulls from the exact table name shown in your database screenshot
        cursor.execute("SELECT * FROM Category")
        results = cursor.fetchall()
        return results
    except Exception as e:
        return {"Status": "Error", "Message": str(e)}
    finally:
        cursor.close()
        db.close()