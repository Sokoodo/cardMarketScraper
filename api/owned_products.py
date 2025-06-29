import logging
from datetime import datetime

from fastapi import HTTPException, APIRouter
from sqlalchemy import func

from database.database import SessionLocal
from database.models.models import Product, OwnedProduct, ScrapeData
from schemas.product import OwnedProductCreate
from utilities.common import encode_product_image

router = APIRouter()


@router.post("/add_owned_products")
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


@router.get("/get_owned_products")
def get_owned_products():
    session = SessionLocal()
    try:
        logging.info("Starting query to fetch owned products")

        latest_scrapes = (
            session.query(
                ScrapeData.product_id_url,
                func.max(ScrapeData.scrape_date).label("latest_date")
            )
            .group_by(ScrapeData.product_id_url)
            .subquery()
        )

        products_with_owned_entries = (
            session.query(
                Product,
                func.count(OwnedProduct.owned_product_id).label("owned_entries_number"),
                ScrapeData.min_price.label("current_min_price"),
                ScrapeData.detailed_availability.label("current_availability"),
            )
            .join(OwnedProduct, Product.id_url == OwnedProduct.product_id)
            .outerjoin(
                latest_scrapes,
                Product.id_url == latest_scrapes.c.product_id_url
            )
            .outerjoin(
                ScrapeData,
                (ScrapeData.product_id_url == latest_scrapes.c.product_id_url)
                & (ScrapeData.scrape_date == latest_scrapes.c.latest_date),
            )
            .group_by(
                Product.id_url,
                ScrapeData.min_price,
                ScrapeData.detailed_availability,
                Product.product_name,
                Product.title,
                Product.subtitle,
                Product.image,
                Product.product_type,
                Product.set_name,
                Product.card_number,
                Product.language,
                Product.condition,
                Product.tcg_name,
                Product.pokemon_species,
                Product.in_my_collection,
            )
            .order_by(ScrapeData.min_price.desc())
            .all()
        )
        logging.info(f"Query returned {len(products_with_owned_entries)} results")

        if not products_with_owned_entries:
            logging.warning("No owned products found in the database")
            raise HTTPException(status_code=404, detail="No owned products found")

        result = []
        for product, owned_entries_number, current_min_price, current_availability in products_with_owned_entries:
            result.append({
                "id_url": product.id_url,
                "title": product.title,
                "image": encode_product_image(product.image),
                "language": product.language,
                "set_name": product.set_name,
                "in_my_collection": product.in_my_collection,
                "owned_entries_number": owned_entries_number,
                "current_min_price": current_min_price,
                "current_availability": current_availability,
            })

        logging.info("Returning processed result")
        return result

    except Exception as e:
        logging.error(f"Error in get_owned_products: {e}")
        raise HTTPException(status_code=500, detail="An error occurred")
    finally:
        session.close()
