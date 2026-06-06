from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from models.user import Utilisateur, ProfilEtudiant, RoleEnum
from models.application import Candidature, StatutCandidature
from models.offer import OffreEmploi
from schemas.candidature import CandidatureCreate, CandidatureResponse, CandidatureStatusUpdate
from security import get_current_user

router = APIRouter(
    prefix="/candidatures",
    tags=["Candidatures"]
)


@router.post("/", response_model=CandidatureResponse, status_code=status.HTTP_201_CREATED)
def postuler(
    donnees: CandidatureCreate,
    db: Session = Depends(get_db),
    utilisateur_courant: Utilisateur = Depends(get_current_user)
):
    if utilisateur_courant.role != RoleEnum.etudiant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les étudiants peuvent postuler à une offre."
        )

    profil = db.query(ProfilEtudiant).filter(
        ProfilEtudiant.utilisateur_id == utilisateur_courant.id
    ).first()
    if not profil:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous devez d'abord créer votre profil avant de postuler."
        )

    offre = db.query(OffreEmploi).filter(OffreEmploi.id == donnees.offre_id).first()
    if not offre:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette offre n'existe pas."
        )

    if offre.date_expiration and offre.date_expiration < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette offre est expirée, vous ne pouvez plus y postuler."
        )

    deja_candidat = db.query(Candidature).filter(
        Candidature.etudiant_id == profil.id,
        Candidature.offre_id == donnees.offre_id
    ).first()

    if deja_candidat:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous avez déjà postulé à cette offre."
        )

    # CORRECTION : utiliser "statut" (pas "status") — correspond au modèle SQLAlchemy
    nouvelle_candidature = Candidature(
        etudiant_id=profil.id,
        offre_id=donnees.offre_id,
        lettre_motivation=donnees.lettre_motivation,
        statut=StatutCandidature.en_attente,
        date_candidature=datetime.utcnow()
    )

    db.add(nouvelle_candidature)
    db.commit()
    db.refresh(nouvelle_candidature)
    return nouvelle_candidature


# IMPORTANT : /moi doit être déclaré AVANT /{candidature_id} pour éviter les conflits de routing
@router.get("/moi", response_model=List[CandidatureResponse])
def mes_candidatures(
    db: Session = Depends(get_db),
    utilisateur_courant: Utilisateur = Depends(get_current_user)
):
    if utilisateur_courant.role != RoleEnum.etudiant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Réservé aux étudiants."
        )

    profil = db.query(ProfilEtudiant).filter(
        ProfilEtudiant.utilisateur_id == utilisateur_courant.id
    ).first()

    if not profil:
        return []  # Pas de profil = pas de candidatures

    candidatures = db.query(Candidature).filter(
        Candidature.etudiant_id == profil.id
    ).order_by(Candidature.date_candidature.desc()).all()

    return candidatures


@router.get("/offre/{offre_id}", response_model=List[CandidatureResponse])
def candidatures_par_offre(
    offre_id: str,
    db: Session = Depends(get_db),
    utilisateur_courant: Utilisateur = Depends(get_current_user)
):
    if utilisateur_courant.role != RoleEnum.entreprise:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Réservé aux entreprises."
        )

    entreprise = utilisateur_courant.entreprise
    if not entreprise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil entreprise introuvable."
        )

    offre = db.query(OffreEmploi).filter(
        OffreEmploi.id == offre_id,
        OffreEmploi.entreprise_id == entreprise.id
    ).first()

    if not offre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offre non trouvée ou vous n'êtes pas propriétaire de cette offre."
        )

    candidatures = db.query(Candidature).filter(
        Candidature.offre_id == offre_id
    ).all()

    return candidatures


@router.put("/{candidature_id}/statut", response_model=CandidatureResponse)
def modifier_statut_candidature(
    candidature_id: str,
    donnees_statut: CandidatureStatusUpdate,
    db: Session = Depends(get_db),
    utilisateur_courant: Utilisateur = Depends(get_current_user)
):
    if utilisateur_courant.role != RoleEnum.entreprise:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Réservé aux entreprises."
        )

    candidature = db.query(Candidature).filter(Candidature.id == candidature_id).first()
    if not candidature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidature non trouvée."
        )

    entreprise = utilisateur_courant.entreprise
    offre = db.query(OffreEmploi).filter(
        OffreEmploi.id == candidature.offre_id,
        OffreEmploi.entreprise_id == entreprise.id
    ).first()

    if not offre:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à modifier cette candidature."
        )

    statuts_valides = ["en_attente", "acceptee", "refusee"]
    if donnees_statut.statut not in statuts_valides:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Statut invalide. Valeurs acceptées : {', '.join(statuts_valides)}"
        )

    candidature.statut = StatutCandidature(donnees_statut.statut)
    db.commit()
    db.refresh(candidature)
    return candidature
