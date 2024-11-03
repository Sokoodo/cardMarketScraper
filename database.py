from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL, Base

# Creiamo l'engine
engine = create_engine(DATABASE_URL)

# Crea una SessionLocal per ogni richiesta
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Funzione per ottenere la connessione al database (Dependency Injection di FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
