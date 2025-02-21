from fastapi import APIRouter
import asyncio
import random
import logging

from fastapi import HTTPException
from typing import List
from database.database import SessionLocal
from database.db_operations import save_product_data
from scraping.scraper import fetch_product_data
from utilities.common import get_url_partial_params, get_product_urls, get_product_urls_by_product_type

router = APIRouter()


@router.get("/programmatic_scraping")
async def programmatic_scraping():
    session = SessionLocal()
    try:
        product_urls = get_product_urls(session)
        if not product_urls:
            raise HTTPException(status_code=404, detail="No product URLs found.")
        return await scrape_bulk_products(product_urls)
    finally:
        session.close()


@router.get("/programmatic_scraping_singles")
async def scrape_singles():
    """
    Scrapes only Singles products.
    """
    session = SessionLocal()
    try:
        product_urls = get_product_urls_by_product_type(session, "Singles")
        if not product_urls:
            raise HTTPException(status_code=404, detail="No Singles products found.")
        return await scrape_bulk_products(product_urls)
    finally:
        session.close()


@router.get("/programmatic_scraping_sealed")
async def scrape_sealed():
    """
    Scrapes only Sealed products.
    """
    session = SessionLocal()
    try:
        product_urls = get_product_urls_by_product_type(session, "Sealed")
        if not product_urls:
            raise HTTPException(status_code=404, detail="No Sealed products found.")
        return await scrape_bulk_products(product_urls)
    finally:
        session.close()


@router.post("/scrape")
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


@router.post("/scrape_bulk")
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
            await asyncio.sleep(random.uniform(1, 2))

        return {"results": results}
    finally:
        session.close()
