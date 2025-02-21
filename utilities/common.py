import base64
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs
from fastapi import HTTPException

from database.models.models import Product


@dataclass
class ProductPartialParams:
    url: str
    product_name: str
    product_type: str
    language: str
    condition: str
    tcg_name: str


def encode_product_image(image_binary: bytes) -> str | None:
    if image_binary:
        return base64.b64encode(image_binary).decode('utf-8')
    return None


def get_url_partial_params(product_url: str):
    try:
        parsed_url = urlparse(product_url)
        path_parts = parsed_url.path.strip('/').split('/')

        tcg = path_parts[1]
        product_category = path_parts[3]
        if product_category == "Singles":
            product = f"{path_parts[4]}/{path_parts[5]}"
        else:
            product = path_parts[4]

        query_params = parse_qs(parsed_url.query)
        language = query_params.get("language", [""])[0]
        condition = query_params.get("minCondition", ["2"])[0]

        partial_params = ProductPartialParams(product_url, product, product_category, language, condition, tcg)
        return partial_params
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid URL format")


def get_product_urls(sess):
    products = sess.query(Product.id_url).all()  # Make sure `Product.id_url` is the correct column for URLs
    return [product[0] for product in products]


def get_product_urls_by_product_type(sess, product_type: str):
    """
    Get product URLs from the database filtered by product type.
    """
    if product_type == "Singles":
        products = sess.query(Product.id_url).filter(Product.product_type == "Singles").all()
    else:
        products = sess.query(Product.id_url).filter(Product.product_type != "Singles").all()
    return [product[0] for product in products]
