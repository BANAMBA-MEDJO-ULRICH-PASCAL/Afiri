from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from database import get_db
from models.user import Utilisateur, RoleEnum, Entreprise
from models.offer import OffreEmploi
from models.application import Candidature
from schemas.company import CompanyDashboardResponse
from security import get_current_user

router = APIRouter(
    prefix="/entreprises",
    tags=["Entreprises"]
)


@router.get("/dashboard", response_model=CompanyDashboardResponse)
def get_company_dashboard(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    Tableau de bord de l'entreprise :
    Retourne ses offres publiées et le nombre de candidatures reçues par offre.
    """
    if current_user.role != RoleEnum.entreprise:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux entreprises"
        )

    entreprise = db.query(Entreprise).filter(
        Entreprise.utilisateur_id == current_user.id
    ).first()
    if not entreprise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil entreprise introuvable"
        )

    results = db.query(
        OffreEmploi,
        func.count(Candidature.id).label("applications_count")
    ).outerjoin(
        Candidature, OffreEmploi.id == Candidature.offre_id
    ).filter(
        OffreEmploi.entreprise_id == entreprise.id
    ).group_by(OffreEmploi.id).all()

    offres_response = []
    total_candidatures = 0

    for offre, count in results:
        offre_dict = {
            "id": offre.id,
            "entreprise_id": offre.entreprise_id,
            "titre": offre.titre,
            "description": offre.description,
            "localisation": offre.localisation,
            "type_contrat": offre.type_contrat,
            "domaine": offre.domaine,
            "est_active": offre.est_active,
            "date_publication": offre.date_publication,
            "date_expiration": offre.date_expiration,
            "applications_count": count
        }
        offres_response.append(offre_dict)
        total_candidatures += count

    return {
        "entreprise_id": entreprise.id,
        "nom_entreprise": entreprise.nom,
        "offres": offres_response,
        "total_candidatures": total_candidatures
    }
