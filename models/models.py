from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    product_type = Column(String, nullable=False)
    set_name = Column(String, nullable=True)
    card_number = Column(String, nullable=True)
    product_subtype = Column(String, nullable=True)
    language = Column(String, nullable=True)

    scrapes = relationship("Scrape", back_populates="product")
    price_history = relationship("PriceHistory", back_populates="product")


class Scrape(Base):
    __tablename__ = 'scrapes'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    scrape_date = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="scrapes")
    product_data = relationship("ProductData", back_populates="scrape")


class ProductData(Base):
    __tablename__ = 'product_data'

    id = Column(Integer, primary_key=True)
    scrape_id = Column(Integer, ForeignKey('scrapes.id'), nullable=False)
    condition = Column(String, nullable=True)
    copies_available = Column(Integer, nullable=True)
    price_min = Column(Float, nullable=True)
    price_max = Column(Float, nullable=True)
    price_avg = Column(Float, nullable=True)

    scrape = relationship("Scrape", back_populates="product_data")


class PriceHistory(Base):
    __tablename__ = 'price_history'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)  # Collegamento al prodotto
    date = Column(DateTime, default=datetime.utcnow, nullable=False)  # Data e ora dello scrape per il prezzo
    price_min = Column(Float, nullable=True)  # Prezzo minimo al momento dello scrape
    price_max = Column(Float, nullable=True)  # Prezzo massimo al momento dello scrape
    price_avg = Column(Float, nullable=True)  # Prezzo medio al momento dello scrape

    # Relazione con la tabella Product
    product = relationship("Product", back_populates="price_history")
