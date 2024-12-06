from datetime import datetime

from fastapi import HTTPException

from database.models.models import Product, ScrapeData
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def save_product_data(session: Session, product_data: dict):
    try:
        product = session.query(Product).filter_by(id_url=product_data['id_url']).first()

        if not product:
            product = Product(
                id_url=product_data['id_url'],
                product_name=product_data['product_name'],
                title=product_data['title'],
                subtitle=product_data['subtitle'],
                image=product_data['image'],
                product_type=product_data['product_type'],
                set_name=product_data['set_name'],
                card_number=product_data['card_number'],
                language=product_data['language'],
                condition=product_data['condition'],
                tcg_name=product_data['tcg_name'],
                pokemon_species=product_data['pokemon_species'],
                current_min_price=product_data['min_price'],
                current_availability=product_data['detailed_availability'],
                in_my_collection=False
            )
            session.add(product)
            session.commit()
            logger.info("New product added to the database with ID: %s", product_data['id_url'])
        elif product.current_min_price != product_data['min_price'] and product.current_availability != product_data[
            'detailed_availability']:
            # Update only current_min_price and current_availability if the product exists
            product.current_min_price = product_data['min_price']
            product.current_availability = product_data['detailed_availability']
            session.commit()
            logger.info("Existing product updated with new min_price and availability for ID: %s",
                        product_data['id_url'])
        else:
            logger.info("Existing product not Updated: %s", product_data['id_url'])

        scrape_data = ScrapeData(
            product_id_url=product_data['id_url'],
            scrape_date=datetime.utcnow(),
            total_availability=product_data['total_availability'],
            detailed_availability=product_data['detailed_availability'],
            min_price=product_data['min_price'],
            max_price=product_data['max_price'],
            avg_price=product_data['avg_price']
        )
        session.add(scrape_data)
        session.commit()
        logger.info("Scrape data saved successfully for product ID: %s", product_data['id_url'])

    except SQLAlchemyError as e:
        session.rollback()
        logger.error("An error occurred while saving product data: %s", str(e))
        raise HTTPException(status_code=500, detail="An error occurred while saving data to the database")
    finally:
        # Close the session if you’re not using a session manager
        session.close()
