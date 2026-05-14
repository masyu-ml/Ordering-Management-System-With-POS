from fastapi import APIRouter, Depends
from database import pull_db
from datetime import date, timedelta
from routers.auth import verify_role
router = APIRouterrouter = APIRouter(
    dependencies=[Depends(verify_role(["Admin"]))]
)


# --- FLOWCHART: COMPUTE KPIs (Revenue, Profit, Growth) ---
@router.get("/analytics/dashboard/kpis", tags=["analytics"])
def get_dashboard_kpis():
    db = pull_db()
    cursor = db.cursor(dictionary=True)
    try:
        # 1. TODAY'S REVENUE
        cursor.execute("SELECT SUM(amount) as revenue FROM Payment WHERE DATE(payment_date) = CURRENT_DATE")
        today_rev = cursor.fetchone()['revenue'] or 0.0

        # 2. YESTERDAY'S REVENUE (For "Growth" Logic)
        cursor.execute(
            "SELECT SUM(amount) as revenue FROM Payment WHERE DATE(payment_date) = CURRENT_DATE - INTERVAL 1 DAY")
        yesterday_rev = cursor.fetchone()['revenue'] or 0.0

        # 3. TODAY'S EXPENSES
        cursor.execute("SELECT SUM(amount) as expenses FROM Expenses WHERE DATE(date_logged) = CURRENT_DATE")
        today_exp = cursor.fetchone()['expenses'] or 0.0

        # KPI Calculation
        net_profit = float(today_rev) - float(today_exp)

        # Growth Logic: ((Today - Yesterday) / Yesterday) * 100
        growth_percent = 0
        if yesterday_rev > 0:
            growth_percent = ((float(today_rev) - float(yesterday_rev)) / float(yesterday_rev)) * 100

        return {
            "status": "success",
            "kpis": {
                "revenue": today_rev,
                "expenses": today_exp,
                "net_profit": net_profit,
                "growth_percentage": round(growth_percent, 2)
            }
        }
    finally:
        cursor.close()
        db.close()


# --- FLOWCHART: APPLY VISUALIZATION TECHNIQUES (Data for Pie Chart) ---
@router.get("/analytics/dashboard/pie-chart", tags=["analytics"])
def get_category_distribution():
    db = pull_db()
    cursor = db.cursor(dictionary=True)
    try:
        # This groups sales by Category so the frontend can draw a Pie Chart
        sql = """
        SELECT c.category_name, SUM(od.quantity * od.unit_price) as value
        FROM Order_Details od
        JOIN Menu m ON od.item_id = m.item_id
        JOIN Category c ON m.category_id = c.category_id
        GROUP BY c.category_name
        """
        cursor.execute(sql)
        return {"status": "success", "chart_data": cursor.fetchall()}
    finally:
        cursor.close()
        db.close()


# --- FLOWCHART: REPORT (PDF) DATA ---
# This provides the raw data that a PDF library would use to generate the report
@router.get("/analytics/report/export", tags=["analytics"])
def get_report_data():
    db = pull_db()
    cursor = db.cursor(dictionary=True)
    try:
        # A detailed list of every transaction today for the PDF report
        sql = """
        SELECT p.payment_id, p.amount, p.payment_method, p.payment_date 
        FROM Payment p 
        WHERE DATE(p.payment_date) = CURRENT_DATE
        """
        cursor.execute(sql)
        return {"status": "success", "transactions": cursor.fetchall()}
    finally:
        cursor.close()
        db.close()