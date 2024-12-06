from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, LargeBinary, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Product(Base):
    __tablename__ = 'products'

    id_url = Column(String, primary_key=True)
    product_name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    subtitle = Column(String, nullable=True)
    image = Column(LargeBinary, nullable=True)
    product_type = Column(String, nullable=False)
    set_name = Column(String, nullable=True)
    card_number = Column(String, nullable=True)
    language = Column(String, nullable=False)
    condition = Column(String, nullable=True)
    tcg_name = Column(String, nullable=False)
    pokemon_species = Column(String, nullable=True)
    current_min_price = Column(Float, nullable=False)
    current_availability = Column(Float, nullable=False)
    in_my_collection = Column(Boolean, default=False, nullable=False)

    scrapes = relationship("ScrapeData", back_populates="product")
    owned_products = relationship("OwnedProduct", back_populates="product")


class OwnedProduct(Base):
    __tablename__ = 'owned_products'

    owned_product_id = Column(Integer, primary_key=True)
    product_id = Column(String, ForeignKey('products.id_url'), nullable=False)
    owned_qty = Column(Integer, nullable=False)
    buy_price = Column(Float, nullable=False)
    buy_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    buy_availability = Column(Integer, nullable=False)

    product = relationship("Product", back_populates="owned_products")


class ScrapeData(Base):
    __tablename__ = 'scrapes'

    scrape_id = Column(Integer, primary_key=True)
    product_id_url = Column(String, ForeignKey('products.id_url'), nullable=False)
    scrape_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    total_availability = Column(Integer, nullable=False)
    detailed_availability = Column(Integer, nullable=False)
    min_price = Column(Float, nullable=False)
    max_price = Column(Float, nullable=False)
    avg_price = Column(Float, nullable=False)

    product = relationship("Product", back_populates="scrapes")
