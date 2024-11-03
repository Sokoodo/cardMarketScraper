import os
from dotenv import load_dotenv
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()  # Carica le variabili d'ambiente dal file .env

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://sokoodo:Mn105371@localhost:5432/cardmarket_scraper_db")

Base = declarative_base()
