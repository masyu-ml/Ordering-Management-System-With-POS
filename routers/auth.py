from fastapi import APIRouter, HTTPException, Depends, Header
from database import pull_db
from schemas.models import UserSchema, EmployeeSchema, LoginSchema
from datetime import datetime
import hashlib

router = APIRouter()
def hash_password(password: str) -> str:
    """Converts a plain-text password into a SHA-256 hash."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks if the typed password matches the stored hash."""
    return hash_password(plain_password) == hashed_password


# --- 2. LOGIN LOGIC ---
@router.post("/login", tags=["security"])
def login(credentials: LoginSchema):
    db = pull_db()
    cursor = db.cursor(dictionary=True)
    try:
        # 1. Fetch user by username ONLY
        sql = """
        SELECT u.user_id, u.username, u.password, e.first_name, r.role_name 
        FROM Users u
        JOIN Employees e ON u.user_id = e.user_id
        JOIN Roles r ON e.role_id = r.role_id
        WHERE u.username = %s AND u.is_active = TRUE
        """
        cursor.execute(sql, (credentials.username,))
        user_data = cursor.fetchone()

        # 2. Check if user exists AND if the hash matches
        if not user_data or not verify_password(credentials.password, user_data['password']):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        # 3. Log the login time (Your existing code)
        update_sql = "UPDATE Users SET last_login = %s WHERE user_id = %s"
        cursor.execute(update_sql, (datetime.now(), user_data['user_id']))
        db.commit()

        return {
            "status": "success",
            "message": f"Welcome back, {user_data['first_name']}",
            "data": {
                "user_id": user_data['user_id'],
                "username": user_data['username'],
                "role": user_data['role_name']
            }
        }
    finally:
        cursor.close()
        db.close()

# --- 3. SECURITY GATEKEEPER (DEPENDENCY) ---
# This is used by other routers to restrict access
def verify_role(allowed_roles: list):
    # Change 'user_id' to 'requester_id' here
    def role_checker(requester_id: int = Header(..., alias="user-id")):
        db = pull_db()
        cursor = db.cursor(dictionary=True, buffered=True)

        try:
            sql = """
                SELECT r.role_name FROM Users u
                JOIN Employees e ON u.user_id = e.user_id
                JOIN Roles r ON e.role_id = r.role_id
                WHERE u.user_id = %s
            """
            # Use 'requester_id' in the execute statement
            cursor.execute(sql, (requester_id,))

            user_data = cursor.fetchone()

            if not user_data or user_data['role_name'] not in allowed_roles:
                raise HTTPException(status_code=403, detail=f"Access Denied: Requires {allowed_roles} permissions")

            return requester_id  # Return the new name

        finally:
            cursor.close()
            db.close()

    return role_checker