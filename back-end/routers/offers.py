from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models.offer import OffreEmploi
from models.user import Utilisateur, RoleEnum, Entreprise
from schemas.offer import OfferCreate, OfferResponse
from security import get_current_user

router = APIRouter(
    prefix="/offres",
    tags=["Offres d'emploi"]
)


@router.post("/", response_model=OfferResponse, status_code=status.HTTP_201_CREATED)
def create_offer(
    offer_data: OfferCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    Créer une nouvelle offre d'emploi. Réservé aux entreprises.
    """
    if current_user.role != RoleEnum.entreprise:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seules les entreprises peuvent créer des offres"
        )

    entreprise = db.query(Entreprise).filter(Entreprise.utilisateur_id == current_user.id).first()
    if not entreprise:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profil entreprise introuvable"
        )

    new_offer = OffreEmploi(
        entreprise_id=entreprise.id,
        titre=offer_data.titre,
        description=offer_data.description,
        localisation=offer_data.localisation,
        type_contrat=offer_data.type_contrat,
        domaine=offer_data.domaine,
        est_active=offer_data.est_active,
        date_expiration=offer_data.date_expiration
    )
    db.add(new_offer)
    db.commit()
    db.refresh(new_offer)
    return new_offer


@router.get("/", response_model=List[OfferResponse])
def get_offers(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Lister toutes les offres d'emploi actives (accessible à tous).
    Permet un filtrage optionnel par recherche textuelle sur le titre.
    """
    query = db.query(OffreEmploi).filter(OffreEmploi.est_active == True)
    if search:
        query = query.filter(OffreEmploi.titre.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()


@router.get("/{id}", response_model=OfferResponse)
def get_offer(id: str, db: Session = Depends(get_db)):
    """
    Voir le détail d'une offre spécifique.
    """
    offer = db.query(OffreEmploi).filter(OffreEmploi.id == id).first()
    if not offer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offre introuvable")
    return offer


@router.put("/{id}", response_model=OfferResponse)
def update_offer(
    id: str,
    offer_data: OfferCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    Modifier une offre d'emploi. Réservé à l'entreprise propriétaire.
    """
    offer = db.query(OffreEmploi).filter(OffreEmploi.id == id).first()
    if not offer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offre introuvable")

    if current_user.role != RoleEnum.entreprise:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")

    entreprise = db.query(Entreprise).filter(Entreprise.utilisateur_id == current_user.id).first()
    if not entreprise or offer.entreprise_id != entreprise.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez modifier que vos propres offres"
        )

    for key, value in offer_data.model_dump().items():
        setattr(offer, key, value)

    db.commit()
    db.refresh(offer)
    return offer


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_offer(
    id: str,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    Supprimer une offre d'emploi. Réservé à l'entreprise propriétaire.
    """
    offer = db.query(OffreEmploi).filter(OffreEmploi.id == id).first()
    if not offer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offre introuvable")

    if current_user.role != RoleEnum.entreprise:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")

    entreprise = db.query(Entreprise).filter(Entreprise.utilisateur_id == current_user.id).first()
    if not entreprise or offer.entreprise_id != entreprise.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez supprimer que vos propres offres"
        )

    db.delete(offer)
    db.commit()
    return None
