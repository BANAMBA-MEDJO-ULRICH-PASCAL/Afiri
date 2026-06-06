"""
main.py — Point d'entrée de l'application Afiri Backend.
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from database import engine, Base

from models import user
from models import offer
from models import application
from models import quiz

from routers import auth
from routers import analytics
from routers import seed
from routers import offers
from routers import companies
from routers import profiles
from routers import applications
from routers import quiz as quiz_router

Base.metadata.create_all(bind=engine)

# Migration légère SQLite : ajoute la colonne projets si absente
from sqlalchemy import text, inspect

def _migrate_columns():
    inspector = inspect(engine)
    if "profils_etudiants" in inspector.get_table_names():
        cols = {c["name"] for c in inspector.get_columns("profils_etudiants")}
        if "projets" not in cols:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE profils_etudiants ADD COLUMN projets TEXT"))

_migrate_columns()

# ── Auto-seed : si aucun admin n'existe en BDD, on peuple avec les données de test ──
from database import SessionLocal
from models.user import Utilisateur, RoleEnum
from models.offer import OffreEmploi
from models.user import Entreprise
from datetime import datetime, timedelta
import random

def _ensure_minimum_offers(db):
    """Ajoute les offres manquantes si la BDD en contient moins que le seed."""
    from routers.seed import OFFRES_DATA
    count = db.query(OffreEmploi).count()
    if count >= len(OFFRES_DATA):
        return
    entreprise_ids = [e.id for e in db.query(Entreprise).all()]
    if not entreprise_ids:
        return
    titres_existants = {o.titre for o in db.query(OffreEmploi).all()}
    for i, data in enumerate(OFFRES_DATA):
        if data["titre"] in titres_existants:
            continue
        offre = OffreEmploi(
            entreprise_id=entreprise_ids[i % len(entreprise_ids)],
            titre=data["titre"],
            description=data["description"],
            localisation=data["localisation"],
            type_contrat=data["type_contrat"],
            domaine=data["domaine"],
            est_active=True,
            date_expiration=datetime.utcnow() + timedelta(days=random.randint(15, 60)),
        )
        db.add(offre)
    db.commit()

_session = SessionLocal()
try:
    admin_existe = _session.query(Utilisateur).filter(
        Utilisateur.role == RoleEnum.admin
    ).first()
    if not admin_existe:
        seed.seed_database(db=_session)
    else:
        _ensure_minimum_offers(_session)
finally:
    _session.close()

app = FastAPI(
    title="Afiri API",
    description="API Backend de la plateforme Afiri — Connexion étudiant/emploi",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(analytics.router)
app.include_router(seed.router)
app.include_router(offers.router)
app.include_router(companies.router)
app.include_router(profiles.router)
app.include_router(applications.router)
app.include_router(quiz_router.router)

# Montage du dossier static/ pour servir dashboard.html et autres fichiers statiques
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def accueil():
    """Endpoint de vérification — confirme que l'API tourne correctement."""
    return {"message": "Bienvenue sur l'API Afiri 🚀"}


@app.get("/dashboard", response_class=HTMLResponse, tags=["Dashboard"])
def dashboard():
    """Sert le tableau de bord analytique admin."""
    try:
        with open("static/dashboard.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Fichier dashboard.html introuvable dans le dossier static/</h1>",
            status_code=404
        )
