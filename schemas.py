from pydantic import BaseModel
from datetime import datetime

# Esquema para crear un ingrediente (sin el id obligatorio)
class IngredientCreate(BaseModel):
    id: str
    name: str
    unit: str
    quantity: float
    minStock: float
    cost: float

# Esquema para respuesta de ingrediente (con orm_mode)
class Ingredient(IngredientCreate):
    class Config:
        orm_mode = True

# Movimiento de stock (respuesta)
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

# Entrada para actualizar stock
class StockUpdate(BaseModel):
    ingredientId: str
    quantity: float
    reason: str
    userId: str
