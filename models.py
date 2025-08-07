from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Ingredient(Base):
    __tablename__ = "ingredients"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    unit = Column(String)
    quantity = Column(Float)
    minStock = Column(Float)
    cost = Column(Float)

class StockMovement(Base):
    __tablename__ = "stock_movements"
    id = Column(String, primary_key=True, index=True, default=lambda: str(int(func.random()*1e10)))
    ingredientId = Column(String, ForeignKey("ingredients.id"))
    type = Column(String)
    quantity = Column(Float)
    previousQuantity = Column(Float)
    newQuantity = Column(Float)
    reason = Column(String)
    userId = Column(String)
    date = Column(DateTime(timezone=True), server_default=func.now())