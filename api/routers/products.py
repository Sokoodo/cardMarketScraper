from fastapi import APIRouter, HTTPException
from urllib.parse import urlparse, parse_qs

from scraping.scraper import fetch_product_data
from utilities.common import ProductPartialParams

router = APIRouter(
    prefix="/products",
    tags=["products"]
)


def get_url_partial_params(product_url: str):
    try:
        parsed_url = urlparse(product_url)
        path_parts = parsed_url.path.strip('/').split('/')

        tcg = path_parts[1]
        product_category = path_parts[3]
        if product_category == "Singles":
            product = path_parts[4] + "/" + path_parts[5]
        else:
            product = path_parts[4]

        query_params = parse_qs(parsed_url.query)
        language = query_params.get("language", [""])[0]
        condition = query_params.get("minCondition", [""])[0]

        partial_params = ProductPartialParams(product_url, product, product_category, language, condition, tcg)
        return partial_params
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid URL format")


@router.post("/api/scrape")
async def scrape_product(product_url: str):
    # Extract variables from the URL
    try:
        partial_params = get_url_partial_params(product_url)
    except HTTPException as e:
        return e

    # Start the scraping process with extracted data
    result = fetch_product_data(partial_params)

    # Return the scraping result
    return result
