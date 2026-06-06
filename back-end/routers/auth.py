"""
routers/auth.py — Endpoints d'authentification.
Contient : inscription, connexion, /me.
Note : get_current_user est défini dans security.py et importé par tous les routers.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from database import get_db
from models.user import Utilisateur, RoleEnum
from security import hash_password, verify_password, create_access_token, get_current_user


router = APIRouter(prefix="/auth", tags=["Authentification"])


# ─────────────────────────────────────────────────────────────────
# SCHEMAS LOCAUX
# ─────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    email: EmailStr
    mot_de_passe: str
    role: RoleEnum = RoleEnum.etudiant


class UserResponse(BaseModel):
    id: str
    email: str
    role: RoleEnum

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


# ─────────────────────────────────────────────────────────────────
# POST /auth/register
# Inscription d'un nouvel utilisateur
# ─────────────────────────────────────────────────────────────────

@router.post("/register", response_model=UserResponse, status_code=201)
def inscription(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Crée un nouveau compte utilisateur.
    Vérifie que l'email n'est pas déjà utilisé,
    hache le mot de passe avant de sauvegarder en BDD.
    """
    existing_user = db.query(Utilisateur).filter(
        Utilisateur.email == user_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est déjà utilisé."
        )

    new_user = Utilisateur(
        email=user_data.email,
        mot_de_passe=hash_password(user_data.mot_de_passe),
        role=user_data.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# ─────────────────────────────────────────────────────────────────
# POST /auth/login
# Connexion — retourne un token JWT si les identifiants sont corrects
# ─────────────────────────────────────────────────────────────────

@router.post("/login", response_model=Token)
def connexion(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authentifie un utilisateur avec email + mot de passe.
    Retourne un token JWT à inclure dans toutes les requêtes protégées.

    Convention OAuth2 : le champ s'appelle "username" dans le formulaire
    même si on y met un email — c'est le standard.
    """
    user = db.query(Utilisateur).filter(
        Utilisateur.email == form_data.username
    ).first()

    if not user or not verify_password(form_data.password, user.mot_de_passe):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.est_actif:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ce compte a été désactivé. Contactez l'administrateur."
        )

    access_token = create_access_token(data={
        "sub": user.email,
        "role": user.role
    })

    return {"access_token": access_token, "token_type": "bearer"}


# ─────────────────────────────────────────────────────────────────
# GET /auth/me
# Retourne les infos de l'utilisateur actuellement connecté
# ─────────────────────────────────────────────────────────────────

@router.get("/me", response_model=UserResponse)
def me(utilisateur_courant: Utilisateur = Depends(get_current_user)):
    """
    Retourne les informations de l'utilisateur dont le token est fourni.
    Utile pour vérifier si un token est encore valide.
    """
    return utilisateur_courant
