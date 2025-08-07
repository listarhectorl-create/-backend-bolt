from pydantic import BaseModel
from datetime import datetime

class Ingredient(BaseModel):
    id: str
    name: str
    unit: str
    quantity: float
    minStock: float
    cost: float

    class Config:
        orm_mode = True

class StockMovement(BaseModel):
    id: str
    ingredientId: str
    type: str
    quantity: float
    previousQuantity: float
    newQuantity: float
    reason: str
    userId: str
    date: datetime

    class Config:
        orm_mode = True

class StockUpdate(BaseModel):
    ingredientId: str
    quantity: float
    reason: str
    userId: str