from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# ⚙️ Cargar URL de la base de datos desde Render
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://usuario:contraseña@localhost/db")

# 🔌 Conexión a la base de datos
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 🧱 Modelo SQLAlchemy
class IngredientModel(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    quantity = Column(Integer)

# 🛠️ Crear tablas
Base.metadata.create_all(bind=engine)

# 📦 Esquema de entrada/salida con Pydantic
class Ingredient(BaseModel):
    name: str
    quantity: int

class StockUpdate(BaseModel):
    updates: List[Ingredient] = Field(...)

# 🚀 Instancia de FastAPI
app = FastAPI()

# ✅ Ruta principal
@app.get("/")
def read_root():
    return {"message": "API en funcionamiento"}

# 📥 Obtener ingredientes desde DB
@app.get("/ingredients", response_model=List[Ingredient])
def get_ingredients():
    db = SessionLocal()
    try:
        ingredients = db.query(IngredientModel).all()
        return [Ingredient(name=i.name, quantity=i.quantity) for i in ingredients]
    finally:
        db.close()

# 🔄 Actualizar ingredientes
@app.post("/ingredients/update")
def update_ingredients(stock_update: StockUpdate):
    db = SessionLocal()
    try:
        for item in stock_update.updates:
            ingredient = db.query(IngredientModel).filter_by(name=item.name).first()
            if ingredient:
                ingredient.quantity += item.quantity
            else:
                new_ingredient = IngredientModel(name=item.name, quantity=item.quantity)
                db.add(new_ingredient)
        db.commit()
        return {"message": "Ingredientes actualizados exitosamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar: {str(e)}")
    finally:
        db.close()
