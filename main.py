from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, schemas
from database import SessionLocal, engine

# Crea las tablas en la base de datos
models.Base.metadata.create_all(bind=engine)

# Instancia de FastAPI
app = FastAPI()

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto a tu dominio en producción si es necesario
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencia para obtener la sesión de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint raíz
@app.get("/")
def root():
    return {"message": "API de Ingredientes funcionando. Visita /docs"}

# Obtener todos los ingredientes
@app.get("/ingredients", response_model=list[schemas.Ingredient])
def get_ingredients(db: Session = Depends(get_db)):
    return db.query(models.Ingredient).all()

# Crear un nuevo ingrediente
@app.post("/ingredients", response_model=schemas.Ingredient)
def create_ingredient(ingredient: schemas.IngredientCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Ingredient).filter(models.Ingredient.id == ingredient.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="El ingrediente ya existe")

    db_ingredient = models.Ingredient(**ingredient.dict())
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient

# Actualizar stock de un ingrediente
@app.post("/ingredients/update", response_model=schemas.StockMovement)
def update_ingredient_stock(update: schemas.StockUpdate, db: Session = Depends(get_db)):
    ingredient = db.query(models.Ingredient).filter(models.Ingredient.id == update.ingredientId).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado")

    previous_quantity = ingredient.quantity
    new_quantity = previous_quantity + update.quantity

    if new_quantity < 0:
        raise HTTPException(status_code=400, detail="El stock no puede quedar negativo")

    ingredient.quantity = new_quantity
    db.commit()

    movement = models.StockMovement(
        ingredientId=update.ingredientId,
        type="manual_add" if update.quantity > 0 else "manual_subtract",
        quantity=update.quantity,
        previousQuantity=previous_quantity,
        newQuantity=new_quantity,
        reason=update.reason,
        userId=update.userId,
    )
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return movement
