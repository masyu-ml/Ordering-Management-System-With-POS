from fastapi import APIRouter, Depends
from database import pull_db
from schemas.models import UserSchema, EmployeeSchema, UserUpdateSchema, EmployeeUpdateSchema, RoleUpdateSchema, RoleSchema
from routers.auth import verify_role, hash_password
router = APIRouter(
    dependencies=[Depends(verify_role(["Admin"]))]
)


# --- FLOWCHART: MANAGE USER ACCOUNTS (ADD) ---
@router.post("/admin/users", tags=["administration"])
def create_user_and_profile(user: UserSchema, profile: EmployeeSchema):
    db = pull_db()
    cursor = db.cursor()
    try:
        # SECURE: Hash it!
        hashed_pass = hash_password(user.password)

        # 1. Save User Account with hashed password
        sql_user = "INSERT INTO Users (username, password, is_active) VALUES (%s, %s, %s)"
        cursor.execute(sql_user, (user.username, hashed_pass, user.is_active))
        user_id = cursor.lastrowid

        # 2. Save Employee Profile (Name, Phone)
        sql_emp = """INSERT INTO Employees (user_id, role_id, first_name, last_name, phone_number) 
                     VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(sql_emp, (user_id, profile.role_id, profile.first_name, profile.last_name, profile.phone_number))

        db.commit()
        return {"status": "success", "message": "User and Profile created successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        db.close()


# --- FLOWCHART: ADD/EDIT/DELETE USER (EDIT) ---
@router.put("/admin/users/{user_id}", tags=["administration"])
def edit_user_account(user_id: int, user_data: UserUpdateSchema, emp_data: EmployeeUpdateSchema):
    db = pull_db()
    cursor = db.cursor()
    try:
        # Update Users table if data provided
        if user_data.username:
            cursor.execute("UPDATE Users SET username=%s WHERE user_id=%s", (user_data.username, user_id))

        # Update Employees table (Profile) if data provided
        if emp_data.first_name:
            cursor.execute("UPDATE Employees SET first_name=%s, last_name=%s WHERE user_id=%s",
                           (emp_data.first_name, emp_data.last_name, user_id))

        db.commit()
        return {"status": "success", "message": "Account updated."}
    finally:
        cursor.close()
        db.close()


# --- FLOWCHART: MODIFY ROLES AND PERMISSION ---
@router.put("/admin/roles/{role_id}", tags=["administration"])
def update_role_permissions(role_id: int, data: RoleUpdateSchema):
    db = pull_db()
    cursor = db.cursor()
    try:
        sql = "UPDATE Roles SET role_name=%s, permissions=%s WHERE role_id=%s"
        cursor.execute(sql, (data.role_name, data.permissions, role_id))
        db.commit()
        return {"status": "success", "message": "Role permissions modified."}
    finally:
        cursor.close()
        db.close()


# --- FETCH ROLES (For the Decision Block) ---
@router.get("/admin/roles", tags=["administration"])
def get_all_roles():
    db = pull_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Roles")
    return cursor.fetchall()