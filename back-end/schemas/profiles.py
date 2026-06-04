from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ProfilCreate(BaseModel):
    nom: str
    prenom: str
    formation: Optional[str] = None
    universite: Optional[str] = None
    competences: Optional[str] = None
    experiences: Optional[str] = None
    cv_lien: Optional[str] = None


class ProfilUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    formation: Optional[str] = None
    universite: Optional[str] = None
    competences: Optional[str] = None
    experiences: Optional[str] = None
    cv_lien: Optional[str] = None


class ProfilResponse(BaseModel):
    id: str
    utilisateur_id: str
    nom: str
    prenom: str
    formation: Optional[str] = None
    universite: Optional[str] = None
    competences: Optional[str] = None
    experiences: Optional[str] = None
    cv_lien: Optional[str] = None
    lien_partage: str
    date_mise_a_jour: datetime

    model_config = ConfigDict(from_attributes=True)
