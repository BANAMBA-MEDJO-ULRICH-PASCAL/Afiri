"""
security.py — Gestion de la sécurité : hachage des mots de passe,
création/décodage des tokens JWT, et récupération de l'utilisateur connecté.
"""

import os
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_db
from models.user import Utilisateur

load_dotenv()


# ─────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "Afiri-cle-secrete-dev-changer-en-production-2024"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 jours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# tokenUrl doit correspondre exactement à l'endpoint de connexion dans auth.py
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ─────────────────────────────────────────────────────────────────────────
# HACHAGE DES MOTS DE PASSE
# ─────────────────────────────────────────────────────────────────────────

def hash_password(plain_password: str) -> str:
    """
    Transforme un mot de passe lisible en hash bcrypt non réversible.
    Exemple : "monmdp123" → "$2b$12$eImiTXuW..."
    On ne stocke JAMAIS le mot de passe original en base de données.
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie si un mot de passe en clair correspond au hash stocké.
    bcrypt recrée le hash et compare — sans jamais décoder l'original.
    Retourne True si correct, False sinon.
    """
    return pwd_context.verify(plain_password, hashed_password)


# ─────────────────────────────────────────────────────────────────────────
# TOKENS JWT
# ─────────────────────────────────────────────────────────────────────────

def create_access_token(data: dict) -> str:
    """
    Crée un token JWT signé avec la SECRET_KEY.
    Le token contient les données passées + une date d'expiration.

    Utilisation dans auth.py :
        token = create_access_token({"sub": utilisateur.email, "role": utilisateur.role})

    "sub" (subject) est une convention JWT — on y stocke l'email de l'utilisateur.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """
    Décode et vérifie un token JWT.
    - Si le token est valide et non expiré : retourne son contenu (dict)
    - Si invalide ou expiré : retourne None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# ─────────────────────────────────────────────────────────────────────────
# RÉCUPÉRATION DE L'UTILISATEUR CONNECTÉ
# ─────────────────────────────────────────────────────────────────────────

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Utilisateur:
    """
    Dépendance FastAPI utilisée par tous les routers protégés.

    Elle fait trois choses dans l'ordre :
    1. Extrait le token JWT de l'en-tête "Authorization: Bearer <token>"
    2. Décode le token et récupère l'email stocké dans "sub"
    3. Charge et retourne l'utilisateur depuis la base de données

    Si quelque chose échoue (token absent, expiré, utilisateur inexistant,
    compte désactivé), elle lève automatiquement une erreur HTTP qui
    arrête la requête avant même d'entrer dans l'endpoint.

    Utilisation dans n'importe quel router :
        utilisateur_courant: Utilisateur = Depends(get_current_user)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré. Veuillez vous reconnecter.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    # auth.py stocke l'email dans "sub" lors de la création du token
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    utilisateur = db.query(Utilisateur).filter(
        Utilisateur.email == email
    ).first()

    if utilisateur is None:
        raise credentials_exception

    if not utilisateur.est_actif:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ce compte a été désactivé."
        )

    return utilisateur
