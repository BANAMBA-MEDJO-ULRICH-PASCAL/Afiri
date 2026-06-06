"""
database.py — Configuration de la connexion à la base de données SQLite.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./Afiri.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Création du moteur de connexion
engine = create_engine(
    DATABASE_URL, connect_args=connect_args
)

# Fabrique de sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe de base pour tous les modèles
Base = declarative_base()


def get_db():
    """
    Dépendance FastAPI : fournit une session BDD pour chaque requête.
    Utilisation dans un router :
        db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
