from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import products, owned_products, scraping

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(owned_products.router, prefix="/api/owned_products", tags=["Owned Products"])
app.include_router(scraping.router, prefix="/api/scraping", tags=["Scraping"])


@app.get("/")
async def root():
    return {"message": "Welcome to the API!"}

# EXAMPLE FOR BULKING SCRAPING
# [
#         "https://www.cardmarket.com/it/Pokemon/Products/Singles/Brilliant-Stars/Sylveon-V-BRSTG14?language=5&minCondition=2",
#         "https://www.cardmarket.com/it/Pokemon/Products/Booster-Boxes/Twilight-Masquerade-Booster-Box?language=5&minCondition=2"
# ]

# tcg = "Pokemon"
# product_category = "Booster-Boxes"
# product = "Scarlet-Violet-Booster-Box"
# language = "5"
# condition = "2"
# product_category = "Singles"
# product = "Brilliant-Stars/Sylveon-VMAX-BRSTG15"
# language = "5"
# condition = "2"

# url = f"https://www.cardmarket.com/it/{tcg}/Products/{product_category}/{product}?language={language}&minCondition={condition}"
# partial_params = ProductPartialParams(url, product, product_category, language, condition, tcg)
#
# product_data = fetch_product_data(partial_params)
# db = SessionLocal()
# save_product_data(db, product_data)
# db.close()
