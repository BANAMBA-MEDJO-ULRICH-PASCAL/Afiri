# routers/analytics.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from security import get_current_user
from models.user import Utilisateur, RoleEnum
from models.offer import OffreEmploi
from models.application import Candidature


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics / Admin Dashboard"]
)


def _verifier_admin(utilisateur_courant: Utilisateur):
    """Vérifie que l'utilisateur est bien un admin. Lève 403 sinon."""
    if utilisateur_courant.role != RoleEnum.admin:
        raise HTTPException(
            status_code=403,
            detail="Accès réservé aux administrateurs."
        )


@router.get("/users/count", summary="Nombre total d'utilisateurs inscrits")
def get_users_count(
    db: Session = Depends(get_db),
    utilisateur_courant: Utilisateur = Depends(get_current_user)
):
    _verifier_admin(utilisateur_courant)
    try:
        count = db.query(Utilisateur).count()
        return {"total_utilisateurs": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur : {str(e)}")


@router.get("/users/breakdown", summary="Répartition étudiants vs entreprises")
def get_users_breakdown(
    db: Session = Depends(get_db),
    utilisateur_courant: Utilisateur = Depends(get_current_user)
):
    _verifier_admin(utilisateur_courant)
    try:
        etudiants = db.query(Utilisateur).filter(
            Utilisateur.role == RoleEnum.etudiant
        ).count()

        entreprises = db.query(Utilisateur).filter(
            Utilisateur.role == RoleEnum.entreprise
        ).count()

        return {
            "etudiants": etudiants,
            "entreprises": entreprises
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur : {str(e)}")


@router.get("/offers/count", summary="Nombre d'offres actives")
def get_offers_count(
    db: Session = Depends(get_db),
    utilisateur_courant: Utilisateur = Depends(get_current_user)
):
    _verifier_admin(utilisateur_courant)
    try:
        offres_actives = db.query(OffreEmploi).filter(
            OffreEmploi.est_active == True
        ).count()
        return {"offres_actives": offres_actives}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur : {str(e)}")


@router.get("/applications/count", summary="Nombre total de candidatures")
def get_applications_count(
    db: Session = Depends(get_db),
    utilisateur_courant: Utilisateur = Depends(get_current_user)
):
    _verifier_admin(utilisateur_courant)
    try:
        count = db.query(Candidature).count()
        return {"total_candidatures": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur : {str(e)}")


@router.get("/offers/top-secteurs", summary="Top 5 des domaines avec le plus d'offres")
def get_top_secteurs(
    db: Session = Depends(get_db),
    utilisateur_courant: Utilisateur = Depends(get_current_user)
):
    _verifier_admin(utilisateur_courant)
    try:
        resultats = db.query(
            OffreEmploi.domaine,
            func.count(OffreEmploi.id).label("nombre_offres")
        ).filter(
            OffreEmploi.domaine != None
        ).group_by(
            OffreEmploi.domaine
        ).order_by(
            func.count(OffreEmploi.id).desc()
        ).limit(5).all()

        return {
            "top_secteurs": [
                {"domaine": domaine, "nombre_offres": count}
                for domaine, count in resultats
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur : {str(e)}")
