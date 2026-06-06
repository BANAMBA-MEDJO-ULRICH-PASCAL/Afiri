from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class CandidatureCreate(BaseModel):
    offre_id: str
    lettre_motivation: Optional[str] = None


class CandidatureStatusUpdate(BaseModel):
    statut: str  # "en_attente", "acceptee", "refusee"


class CandidatureResponse(BaseModel):
    id: str
    etudiant_id: str
    offre_id: str
    lettre_motivation: Optional[str] = None
    statut: str
    date_candidature: datetime

    model_config = ConfigDict(from_attributes=True)
