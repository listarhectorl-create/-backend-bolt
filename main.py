from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "API de Ingredientes funcionando. Visita /docs"}

@app.get("/ingredients", response_model=list[schemas.Ingredient])
def get_ingredients(db: Session = Depends(get_db)):
    return db.query(models.Ingredient).all()

@app.post("/ingredients", response_model=schemas.Ingredient)
def create_ingredient(ingredient: schemas.IngredientCreate, db: Session = Depends(get_db)):
    db_ingredient = models.Ingredient(**ingredient.dict())
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient

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
