from fastapi import APIRouter, HTTPException

import logging

from database.database import SessionLocal
from utilities.common import get_total_current_price, get_total_bought_price

router = APIRouter()

print("Statistics router loaded")


@router.get("/total_singles_current_price")
async def get_total_singles_current_price():
    session = SessionLocal()
    try:
        logging.info("Fetching total current price for Singles")
        total_price = get_total_current_price(session, "Singles")
        return total_price
    except Exception as e:
        logging.error(f"Error fetching singles Pokemon products: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching singles Pokemon products.")
    finally:
        session.close()


@router.get("/total_singles_bought_price")
async def get_total_singles_bought_price():
    session = SessionLocal()
    try:
        logging.info("Fetching total bought price for Singles")
        total_price = get_total_bought_price(session, "Singles")
        return total_price
    except Exception as e:
        logging.error(f"Error fetching singles Pokemon products: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching singles Pokemon products.")
    finally:
        session.close()
