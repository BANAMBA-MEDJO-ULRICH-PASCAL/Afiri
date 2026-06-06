from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class ProfilCreate(BaseModel):
    nom: str
    prenom: str
    formation: Optional[str] = None
    universite: Optional[str] = None
    competences: Optional[str] = None
    experiences: Optional[str] = None
    projets: Optional[str] = None
    cv_lien: Optional[str] = None


class ProfilUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    formation: Optional[str] = None
    universite: Optional[str] = None
    competences: Optional[str] = None
    experiences: Optional[str] = None
    projets: Optional[str] = None
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
    projets: Optional[str] = None
    cv_lien: Optional[str] = None
    lien_partage: str
    date_mise_a_jour: datetime

    model_config = ConfigDict(from_attributes=True)


class ProfilCompletionItem(BaseModel):
    key: str
    label: str
    done: bool


class ProfilCompletionResponse(BaseModel):
    pourcentage: int
    complet: bool
    peut_recommander: bool
    quiz_termine: bool
    quiz_ignore: bool
    items: List[ProfilCompletionItem]
    conseil: str
