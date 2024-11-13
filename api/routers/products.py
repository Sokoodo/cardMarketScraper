# app/api/routers/cards.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models import models
from schemas import card
from database import get_db

router = APIRouter(
    prefix="/cards",
    tags=["cards"]
)


@router.get("/", response_model=List[card.CardResponse])
async def get_cards(db: Session = Depends(get_db)):
    return db.query(models.Product).all()


@router.get("/{card_id}", response_model=card.CardResponse)
async def get_card(card_id: int, db: Session = Depends(get_db)):
    card = db.query(models.Product).filter(models.Product.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card


@router.post("/", response_model=card.CardResponse, status_code=status.HTTP_201_CREATED)
async def create_card(card: card.CardCreate, db: Session = Depends(get_db)):
    db_card = models.Product(name=card.name, current_price=card.current_price)
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card


@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(card_id: string, db: Session = Depends(get_db)):
    card = db.query(models.Product).filter(models.Product.id_url == card_id).first()
    if card:
        db.delete(card)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Card not found")
