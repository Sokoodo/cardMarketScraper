import asyncio
import random
import logging
from datetime import datetime

from fastapi import HTTPException, FastAPI, Query
from urllib.parse import unquote
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from database import SessionLocal
from models.models import Product, ScrapeData, OwnedProduct
from schemas.product import OwnedProductCreate
from scraping.db_operations import save_product_data
from scraping.scraper import fetch_product_data
from utilities.common import get_url_partial_params, encode_product_image, get_product_urls

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, set this for development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)


@app.get("/api/programmaticScraping")  # TESTARE FUNZIONAMENTO IL 22/11
async def programmatic_scraping():
    session = SessionLocal()
    try:
        product_urls = get_product_urls(session)

        if not product_urls:
            raise HTTPException(status_code=404, detail="No product URLs found.")

        return await scrape_bulk_products(product_urls)
    finally:
        session.close()


@app.post("/api/scrape")
async def scrape_product(product_url: str):
    session = SessionLocal()
    try:
        partial_params = get_url_partial_params(product_url)
        product_data = fetch_product_data(partial_params)
        save_product_data(session, product_data)

        return {"message": f"Salvataggio di {product_data['title']} avvenuto con successo!"}

    except HTTPException as e:
        raise e

    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

    finally:
        session.close()


@app.post("/api/scrape_bulk")
async def scrape_bulk_products(product_urls: List[str]):
    session = SessionLocal()
    results = []
    try:
        for product_url in product_urls:
            try:
                partial_params = get_url_partial_params(product_url)
                product_data = fetch_product_data(partial_params)

                save_product_data(session, product_data)
                results.append({"product_url": product_url, "status": "success",
                                "message": f"Salvataggio di {product_data['title']} avvenuto con successo!"})
            except HTTPException as e:
                results.append({"product_url": product_url, "status": "error", "message": str(e.detail)})
            except Exception as e:
                results.append(
                    {"product_url": product_url, "status": "error", "message": "An unexpected error occurred"})
            await asyncio.sleep(random.uniform(2, 6))

        return {"results": results}
    finally:
        session.close()


@app.get("/api/products/product_detail")
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


@app.get("/api/products/singlesPokemon")
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


@app.get("/api/products/sealedPokemon")
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


@app.post("/api/owned_products")
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






# EXAMPLE FOR BULKING SCRAPING
# [
#         "https://www.cardmarket.com/it/Pokemon/Products/Singles/Brilliant-Stars/Sylveon-V-BRSTG14?language=5&minCondition=2",
#         "https://www.cardmarket.com/it/Pokemon/Products/Booster-Boxes/Twilight-Masquerade-Booster-Box?language=5&minCondition=2"
# ]

# tcg = "Pokemon"
# product_category = "Booster-Boxes"
# product = "Scarlet-Violet-Booster-Box"
# language = "5"
# condition = "2"
# product_category = "Singles"
# product = "Brilliant-Stars/Sylveon-VMAX-BRSTG15"
# language = "5"
# condition = "2"

# url = f"https://www.cardmarket.com/it/{tcg}/Products/{product_category}/{product}?language={language}&minCondition={condition}"
# partial_params = ProductPartialParams(url, product, product_category, language, condition, tcg)
#
# product_data = fetch_product_data(partial_params)
# db = SessionLocal()
# save_product_data(db, product_data)
# db.close()
