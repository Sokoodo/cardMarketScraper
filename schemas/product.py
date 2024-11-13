from pydantic import BaseModel


class ProductBase(BaseModel):
    name: str
    current_price: float


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: str

    class Config:
        orm_mode = True
