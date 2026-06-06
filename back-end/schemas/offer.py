from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class OfferBase(BaseModel):
    titre: str
    description: str
    localisation: Optional[str] = None
    type_contrat: Optional[str] = None
    domaine: Optional[str] = None
    est_active: bool = True


class OfferCreate(OfferBase):
    date_expiration: Optional[datetime] = None


class OfferUpdate(BaseModel):
    titre: Optional[str] = None
    description: Optional[str] = None
    localisation: Optional[str] = None
    type_contrat: Optional[str] = None
    domaine: Optional[str] = None
    est_active: Optional[bool] = None
    date_expiration: Optional[datetime] = None


class OfferResponse(OfferBase):
    id: str
    entreprise_id: str
    date_publication: datetime
    date_expiration: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
