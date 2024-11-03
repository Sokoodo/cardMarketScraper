from models.models import Product, Scrape, ProductData, PriceHistory
from sqlalchemy.orm import Session
from datetime import datetime


def save_product_data(session: Session, product_url: str, data: dict):
    """
    Salva i dati di scraping nel database per un prodotto specifico.
    """
    # Verifica se il prodotto esiste già nel database
    product = session.query(Product).filter_by(url=product_url).first()

    if not product:
        product = Product(
            url=product_url,
            name=data['name'],
            image_url=data['image_url']
        )
        session.add(product)
        session.commit()

    # Crea un nuovo record di scrape
    scrape = Scrape(
        product_id=product.id,
        scrape_date=datetime.utcnow()
    )
    session.add(scrape)
    session.commit()

    # Salva i dettagli del prezzo e delle copie disponibili
    product_data = ProductData(
        scrape_id=scrape.id,
        copies_available=data['copies_available'],
        price_min=data['price_min'],
        price_max=data['price_max'],
        price_avg=data['price_avg']
    )
    session.add(product_data)

    # Salva la cronologia dei prezzi
    price_history = PriceHistory(
        product_id=product.id,
        date=datetime.utcnow(),
        price_min=data['price_min'],
        price_max=data['price_max'],
        price_avg=data['price_avg']
    )
    session.add(price_history)

    # Conferma tutte le modifiche
    session.commit()
