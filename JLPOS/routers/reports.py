from fastapi import APIRouter, Query
from database import pull_db
from datetime import date

router = APIRouter()

# 1. SALES REPORT BY DATE RANGE
@router.get("/reports/sales", tags=["reports"])
def get_sales_report(start_date: str, end_date: str):
    db = pull_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Pulls every payment within a specific window
        sql = """
        SELECT p.payment_id, p.amount, p.payment_method, p.payment_date, o.order_id
        FROM Payment p
        JOIN `Order` o ON p.order_id = o.order_id
        WHERE DATE(p.payment_date) BETWEEN %s AND %s
        ORDER BY p.payment_date ASC
        """
        cursor.execute(sql, (start_date, end_date))
        return {"status": "success", "period": f"{start_date} to {end_date}", "data": cursor.fetchall()}
    finally:
        cursor.close()
        db.close()

# 2. STAFF PERFORMANCE / PAYROLL REPORT
@router.get("/reports/staff-hours", tags=["reports"])
def get_staff_hours_report(start_date: str, end_date: str):
    db = pull_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Calculates total hours worked per employee using the Shift table
        sql = """
        SELECT 
            e.first_name, 
            e.last_name, 
            e.salary,
            COUNT(s.shift_id) as total_shifts,
            SUM(TIMESTAMPDIFF(HOUR, s.start_time, s.end_time)) as total_hours
        FROM Employees e
        JOIN Shift s ON e.employee_id = s.employee_id
        WHERE s.date_shift BETWEEN %s AND %s
        GROUP BY e.employee_id
        """
        cursor.execute(sql, (start_date, end_date))
        return {"status": "success", "data": cursor.fetchall()}
    finally:
        cursor.close()
        db.close()

# 3. INVENTORY AUDIT REPORT
@router.get("/reports/inventory-audit", tags=["reports"])
def get_inventory_audit():
    db = pull_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Shows current stock vs. threshold for a "State of the Kitchen" printout
        sql = "SELECT item_name, quantity, threshold, unit_cost FROM Inventory"
        cursor.execute(sql)
        return {"status": "success", "data": cursor.fetchall()}
    finally:
        cursor.close()
        db.close()