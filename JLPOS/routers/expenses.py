from fastapi import APIRouter, HTTPException, Depends
from database import pull_db
from schemas.models import ExpenseSchema
from routers.auth import verify_role
router = APIRouter(
    dependencies=[Depends(verify_role(["Admin"]))]
)

# --- FLOWCHART STEP: SAVE TO EXPENSE RECORDS ---
@router.post("/expenses", tags=["expenses"])
def log_new_expense(data: ExpenseSchema):
    db = pull_db()
    cursor = db.cursor()
    try:
        sql = """INSERT INTO Expenses (description, amount, category, employee_id) 
                 VALUES (%s, %s, %s, %s)"""
        cursor.execute(sql, (data.description, data.amount, data.category, data.employee_id))
        db.commit()
        return {"status": "success", "message": "Expense record saved successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Validation Failed: {str(e)}")
    finally:
        cursor.close()
        db.close()

# --- FLOWCHART STEP: EXPENSE REPORT ---
@router.get("/expenses/report", tags=["expenses"])
def get_expense_report():
    db = pull_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Pulls the most recent expenses so the manager can see the "Report"
        sql = "SELECT * FROM Expenses ORDER BY date_logged DESC LIMIT 50"
        cursor.execute(sql)
        results = cursor.fetchall()
        return {"status": "success", "expense_report": results}
    finally:
        cursor.close()
        db.close()