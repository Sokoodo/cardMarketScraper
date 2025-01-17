import logging

from fastapi import HTTPException, Query, APIRouter
from urllib.parse import unquote

from sqlalchemy import func

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

        latest_scrape = all_scrapes[0] if all_scrapes else None  # Takes the last scrape by date
        latest_min_price = latest_scrape.min_price if latest_scrape else None
        latest_availability = latest_scrape.detailed_availability if latest_scrape else None

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
            "current_min_price": latest_min_price,
            "current_availability": latest_availability,
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
        # Subquery to get the latest scrape date for each product
        latest_scrapes = (
            session.query(
                ScrapeData.product_id_url,
                func.max(ScrapeData.scrape_date).label("latest_date")
            )
            .group_by(ScrapeData.product_id_url)
            .subquery()
        )

        # Join Product with the subquery and ScrapeData to fetch the latest scrape info
        products_with_scrapes = (
            session.query(
                Product,
                ScrapeData.min_price.label("current_min_price"),
                ScrapeData.detailed_availability.label("current_availability"),
            )
            .join(latest_scrapes, Product.id_url == latest_scrapes.c.product_id_url)
            .join(
                ScrapeData,
                (ScrapeData.product_id_url == latest_scrapes.c.product_id_url)
                & (ScrapeData.scrape_date == latest_scrapes.c.latest_date),
            )
            .filter(Product.product_type == "Singles", Product.tcg_name == "Pokemon")
            .order_by(ScrapeData.min_price.desc())
            .all()
        )

        results = [
            {
                "id_url": product.id_url,
                "title": product.title,
                "image": encode_product_image(product.image),
                "language": product.language,
                "in_my_collection": product.in_my_collection,
                "set_name": product.set_name,
                "current_min_price": current_min_price,
                "current_availability": current_availability,
            }
            for product, current_min_price, current_availability in products_with_scrapes
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
        latest_scrapes = (
            session.query(
                ScrapeData.product_id_url,
                func.max(ScrapeData.scrape_date).label("latest_date")
            )
            .group_by(ScrapeData.product_id_url)
            .subquery()
        )

        products_with_scrapes = (
            session.query(
                Product,
                ScrapeData.min_price.label("current_min_price"),
                ScrapeData.detailed_availability.label("current_availability"),
            )
            .join(latest_scrapes, Product.id_url == latest_scrapes.c.product_id_url)
            .join(
                ScrapeData,
                (ScrapeData.product_id_url == latest_scrapes.c.product_id_url)
                & (ScrapeData.scrape_date == latest_scrapes.c.latest_date),
            )
            .filter(Product.product_type != "Singles", Product.tcg_name == "Pokemon")
            .order_by(ScrapeData.min_price.asc())
            .all()
        )

        results = [
            {
                "id_url": product.id_url,
                "title": product.title,
                "image": encode_product_image(product.image),
                "language": product.language,
                "in_my_collection": product.in_my_collection,
                "current_min_price": current_min_price,
                "current_availability": current_availability,
            }
            for product, current_min_price, current_availability in products_with_scrapes
        ]

        return results
    except Exception as e:
        logging.error(f"Error fetching singles Pokemon products: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching singles Pokemon products.")
    finally:
        session.close()
