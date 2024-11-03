from scraping.scraper import fetch_product_data

# @app.get("/")
# async def root():
#     return {"message": "Hello World"}
#
#
# @app.get("/hello/{name}")
# async def say_hello(name: str):
#     return {"message": f"Hello {name}"}

url = "https://www.cardmarket.com/it/Pokemon/Products/Booster-Boxes/Scarlet-Violet-Booster-Box?language=5&minCondition=2"
data = fetch_product_data(url)
