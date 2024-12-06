import logging
from datetime import datetime

from fastapi import HTTPException, APIRouter

from database.database import SessionLocal
from database.models.models import Product, OwnedProduct
from schemas.product import OwnedProductCreate

router = APIRouter()


@router.post("/api/owned_products")
async def add_owned_product(data: OwnedProductCreate):
    session = SessionLocal()

    product = session.query(Product).filter_by(id_url=data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found in the database")

    try:
        buy_date = datetime.fromisoformat(data.buy_date)  # Ensure date is valid ISO format
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    owned_product = OwnedProduct(
        product_id=data.product_id,
        owned_qty=data.owned_qty,
        buy_price=data.buy_price,
        buy_date=buy_date,
        buy_availability=data.buy_availability
    )

    try:
        session.add(owned_product)
        session.commit()
        session.refresh(owned_product)
    except Exception as e:
        session.rollback()
        logging.error(f"Error adding owned product: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add owned product: {str(e)}")

    return {"message": "Owned product successfully added", "owned_product": owned_product}
