from pydantic import BaseModel, ConfigDict
from typing import List
from schemas.offer import OfferResponse


class OfferWithAppCount(OfferResponse):
    applications_count: int

    model_config = ConfigDict(from_attributes=True)


class CompanyDashboardResponse(BaseModel):
    entreprise_id: str
    nom_entreprise: str
    offres: List[OfferWithAppCount]
    total_candidatures: int

    model_config = ConfigDict(from_attributes=True)
