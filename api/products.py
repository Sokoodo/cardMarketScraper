import logging

from fastapi import HTTPException, Query, APIRouter
from urllib.parse import unquote
from database.database import SessionLocal
from database.models.models import Product, ScrapeData
from utilities.common import encode_product_image

router = APIRouter()


@router.get("/product_detail")
async def get_product_details(id_url: str = Query(..., alias="id_url")):
    session = SessionLocal()
    try:
        decoded_id_url = unquote(id_url)
        logging.info(f"Decoded id_url: {decoded_id_url}")
        product = session.query(Product).filter(Product.id_url == decoded_id_url).first()

        if not product:
            logging.error(f"Product not found for id_url: {decoded_id_url}")
            raise HTTPException(status_code=404, detail="Product not found")

        all_scrapes = (
            session.query(ScrapeData)
            .filter_by(product_id_url=decoded_id_url)
            .order_by(ScrapeData.scrape_date.desc())
            .all()
        )

        product_data = {
            "id_url": product.id_url,
            "product_name": product.product_name,
            "title": product.title,
            "subtitle": product.subtitle,
            "image": encode_product_image(product.image),
            "product_type": product.product_type,
            "set_name": product.set_name,
            "card_number": product.card_number,
            "language": product.language,
            "condition": product.condition,
            "tcg_name": product.tcg_name,
            "pokemon_species": product.pokemon_species,
            "current_min_price": product.current_min_price,
            "current_availability": product.current_availability,
            "in_my_collection": product.in_my_collection,
            "historical_scrape_data": [
                {
                    "scrape_date": scrape.scrape_date,
                    "avg_price": scrape.avg_price,
                    "min_price": scrape.min_price,
                    "max_price": scrape.max_price,
                    "detailed_availability": scrape.detailed_availability,
                    "total_availability": scrape.total_availability,
                }
                for scrape in all_scrapes
            ],
        }

        return product_data

    except Exception as e:
        logging.error(f"Error fetching product details: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching the product details.")
    finally:
        session.close()


@router.get("/singlesPokemon")
async def get_singles_pokemon():
    session = SessionLocal()
    try:
        products = (
            session.query(Product)
            .filter(Product.product_type == "Singles", Product.tcg_name == "Pokemon")
            .order_by(Product.current_min_price.desc())  # Order by current_min_price, descending
            .all()
        )
        results = [
            {
                "id_url": product.id_url,
                "title": product.title,
                "image": encode_product_image(product.image),
                "language": product.language,
                "current_min_price": product.current_min_price,
                "current_availability": product.current_availability,
                "in_my_collection": product.in_my_collection
            }
            for product in products
        ]

        return results
    except Exception as e:
        logging.error(f"Error fetching singles Pokemon products: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching singles Pokemon products.")
    finally:
        session.close()


@router.get("/sealedPokemon")
async def get_sealed_pokemon():
    session = SessionLocal()
    try:
        products = (
            session.query(Product)
            .filter(Product.product_type != "Singles", Product.tcg_name == "Pokemon")
            .order_by(Product.current_min_price.asc())  # Order by current_min_price, ascending
            .all()
        )
        results = [
            {
                "id_url": product.id_url,
                "title": product.title,
                "image": encode_product_image(product.image),
                "language": product.language,
                "current_min_price": product.current_min_price,
                "current_availability": product.current_availability,
                "in_my_collection": product.in_my_collection
            }
            for product in products
        ]

        return results
    except Exception as e:
        logging.error(f"Error fetching singles Pokemon products: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching singles Pokemon products.")
    finally:
        session.close()
