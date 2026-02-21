from pydantic import BaseModel
from typing import Optional

class MenuSchema(BaseModel):
    item_name: str
    description: Optional[str] = None
    price: float
    category_id: Optional[int] = None
    available: bool = True

class InventorySchema(BaseModel):
    item_id: int
    quantity: int
    threshold: int
    unit_cost: float
    status: bool = True

class OrderDetailSchema(BaseModel):
    item_id: int
    quantity: int
    unit_price: float
    notes: Optional[str] = None

class OrderSchema(BaseModel):
    status: bool = True

    items: list[OrderDetailSchema]