from pydantic import BaseModel
from typing import Optional

class MenuSchema(BaseModel):
    item_name: str
    description: Optional[str] = None
    price: float
    category_id: Optional[int] = None
    available: bool = True

class InventorySchema(BaseModel):
    item_name: str
    quantity: float
    unit_measure: str
    threshold: float
    unit_cost: float
    status: bool = True

class InventoryUpdate(BaseModel):
    quantity: float
    unit_cost: float

class OrderDetailSchema(BaseModel):
    item_id: int
    quantity: int
    unit_price: float
    notes: Optional[str] = None

class OrderSchema(BaseModel):
    status: str
    items: list[OrderDetailSchema]
    payment_method: str
    amount_paid: float
    discount_amount: float = 0.0

class RoleSchema(BaseModel):
    role_name: str
    permissions: Optional[str] = None

class UserSchema(BaseModel):
    username: str
    password: str
    is_active: bool = True

class EmployeeSchema(BaseModel):
    user_id: Optional[int] = None
    role_id: int
    first_name: str
    last_name: str
    phone_number: str

class LoginSchema(BaseModel):
    username: str
    password: str

class RecipeCreateSchema(BaseModel):
    item_id: int
    inventory_id: int
    quantity: float
    unit_measure: str
    prep_notes: Optional[str] = None

class ExpenseSchema(BaseModel):
    description: str  # This is the "TYPE" from your flowchart
    amount: float     # The "AMOUNT"
    category: str     # Extra organization (e.g., 'Utilities', 'Repair')
    employee_id: int  # Who is logging this?

class UserUpdateSchema(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class EmployeeUpdateSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    role_id: Optional[int] = None

class RoleUpdateSchema(BaseModel):
    role_name: Optional[str] = None
    permissions: Optional[str] = None

class StaffUpdateSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    salary: Optional[float] = None

class ShiftSchema(BaseModel):
    employee_id: int
    start_time: str # Format: "HH:MM:SS"
    end_time: str
    date_shift: str # Format: "YYYY-MM-DD"

class CategorySchema(BaseModel):
    category_name: str
    description: Optional[str] = None