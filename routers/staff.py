from fastapi import APIRouter, HTTPException
from database import pull_db
from schemas.models import StaffUpdateSchema, ShiftSchema
from datetime import date

router = APIRouter()

# --- 1. STAFF PROFILE MANAGEMENT (Employees Table) ---

@router.put("/staff/profile/{employee_id}", tags=["staff"])
def update_staff_info(employee_id: int, data: StaffUpdateSchema):
    db = pull_db()
    cursor = db.cursor()
    try:
        # Updates Name, Contact, and Salary in the Employees table
        sql = """UPDATE Employees 
                 SET first_name = %s, last_name = %s, phone_number = %s, salary = %s 
                 WHERE employee_id = %s"""
        cursor.execute(sql, (data.first_name, data.last_name, data.phone_number, data.salary, employee_id))
        db.commit()
        return {"status": "success", "message": "Staff profile updated."}
    finally:
        cursor.close()
        db.close()

# --- 2. ATTENDANCE & SCHEDULING (Shift Table) ---

# This handles the "Assign/Edit Shifts" block in your flowchart
@router.post("/staff/shifts", tags=["staff"])
def create_shift_record(data: ShiftSchema):
    db = pull_db()
    cursor = db.cursor()
    try:
        # Uses the fields exactly as named in your ERD
        sql = """INSERT INTO Shift (employee_id, start_time, end_time, date_shift) 
                 VALUES (%s, %s, %s, %s)"""
        cursor.execute(sql, (data.employee_id, data.start_time, data.end_time, data.date_shift))
        db.commit()
        return {"status": "success", "message": "Work shift recorded."}
    finally:
        cursor.close()
        db.close()

# This handles the "Display Daily Login" block
@router.get("/staff/attendance/today", tags=["staff"])
def get_today_attendance():
    db = pull_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Joins Employees and Shift to see WHO is working WHEN
        sql = """
        SELECT e.first_name, e.last_name, s.start_time, s.end_time
        FROM Employees e
        JOIN Shift s ON e.employee_id = s.employee_id
        WHERE s.date_shift = CURRENT_DATE
        """
        cursor.execute(sql)
        return {"status": "success", "attendance": cursor.fetchall()}
    finally:
        cursor.close()
        db.close()

# --- 3. REPORTING ---

# This handles the "Export Staff Sheet Details" block
@router.get("/staff/report/full", tags=["staff"])
def export_staff_sheet():
    db = pull_db()
    cursor = db.cursor(dictionary=True)
    try:
        # A master list of all staff, their roles, and their contact info
        sql = """
        SELECT e.employee_id, e.first_name, e.last_name, r.role_name, e.salary, e.phone_number
        FROM Employees e
        JOIN Roles r ON e.role_id = r.role_id
        """
        cursor.execute(sql)
        return {"status": "success", "staff_data": cursor.fetchall()}
    finally:
        cursor.close()
        db.close()