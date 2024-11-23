# schemas/product.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class OwnedProductCreate(BaseModel):
    product_id: str
    owned_qty: int
    buy_price: float
    buy_date: str
    buy_availability: int


class ScrapeDataBase(BaseModel):
    scrape_date: datetime
    total_availability: int
    detailed_availability: int
    min_price: float
    max_price: float
    avg_price: float


class Config:
    orm_mode = True


class ProductBase(BaseModel):
    product_name: str
    title: str
    subtitle: Optional[str]
    image: Optional[bytes]
    product_type: str
    set_name: Optional[str]
    card_number: Optional[str]
    language: str
    condition: Optional[str]
    tcg_name: str
    pokemon_species: Optional[str]
    current_min_price: float
    current_availability: float


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id_url: str  # Ensure id_url is included in the response
    scrapes: List[ScrapeDataBase]  # Include related scrapes

    class Config:
        orm_mode = True
