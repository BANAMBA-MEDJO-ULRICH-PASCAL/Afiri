"""Helpers pour le profil étudiant."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.user import Utilisateur, ProfilEtudiant, RoleEnum


def obtenir_ou_creer_profil(db: Session, utilisateur: Utilisateur) -> ProfilEtudiant:
    """Retourne le profil étudiant, ou en crée un minimal si absent."""
    profil = db.query(ProfilEtudiant).filter(
        ProfilEtudiant.utilisateur_id == utilisateur.id
    ).first()

    if profil:
        return profil

    if utilisateur.role != RoleEnum.etudiant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil étudiant introuvable.",
        )

    email_part = utilisateur.email.split("@")[0].replace(".", " ").replace("_", " ")
    parts = email_part.split()
    prenom = parts[0].capitalize() if parts else "Etudiant"
    nom = parts[-1].capitalize() if len(parts) > 1 else "Afiri"

    profil = ProfilEtudiant(
        utilisateur_id=utilisateur.id,
        nom=nom,
        prenom=prenom,
    )
    db.add(profil)
    db.commit()
    db.refresh(profil)
    return profil
