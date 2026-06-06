from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.user import Utilisateur, ProfilEtudiant, RoleEnum
from models.quiz import QuizResultat
from schemas.profiles import ProfilCreate, ProfilUpdate, ProfilResponse, ProfilCompletionResponse
from security import get_current_user
from utils.profile_completion import calculer_completion

router = APIRouter(
    prefix="/profils",
    tags=["Profils étudiants"]
)


@router.post("/", response_model=ProfilResponse, status_code=status.HTTP_201_CREATED)
def creer_profil(
    donnees_profil: ProfilCreate,
    db: Session = Depends(get_db),
    utilisateur_courant: Utilisateur = Depends(get_current_user)
):
    if utilisateur_courant.role != RoleEnum.etudiant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les étudiants peuvent créer un profil étudiant."
        )

    profil_existant = db.query(ProfilEtudiant).filter(
        ProfilEtudiant.utilisateur_id == utilisateur_courant.id
    ).first()
    if profil_existant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous avez déjà un profil étudiant. Veuillez le mettre à jour."
        )

    nouveau_profil = ProfilEtudiant(
        utilisateur_id=utilisateur_courant.id,
        nom=donnees_profil.nom,
        prenom=donnees_profil.prenom,
        formation=donnees_profil.formation,
        universite=donnees_profil.universite,
        competences=donnees_profil.competences,
        experiences=donnees_profil.experiences,
        projets=donnees_profil.projets,
        cv_lien=donnees_profil.cv_lien
    )
    db.add(nouveau_profil)
    db.commit()
    db.refresh(nouveau_profil)
    return nouveau_profil


@router.get("/moi", response_model=ProfilResponse)
def obtenir_mon_profil(
    db: Session = Depends(get_db),
    utilisateur_courant: Utilisateur = Depends(get_current_user)
):
    profil = db.query(ProfilEtudiant).filter(
        ProfilEtudiant.utilisateur_id == utilisateur_courant.id
    ).first()
    if not profil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vous n'avez pas encore créé de profil étudiant."
        )
    return profil


@router.put("/moi", response_model=ProfilResponse)
def mettre_a_jour_mon_profil(
    donnees_profil: ProfilUpdate,
    db: Session = Depends(get_db),
    utilisateur_courant: Utilisateur = Depends(get_current_user)
):
    profil = db.query(ProfilEtudiant).filter(
        ProfilEtudiant.utilisateur_id == utilisateur_courant.id
    ).first()
    if not profil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vous n'avez pas encore créé de profil étudiant."
        )

    # .model_dump() remplace .dict() en Pydantic v2
    champs_a_modifier = donnees_profil.model_dump(exclude_unset=True)
    for champ, valeur in champs_a_modifier.items():
        setattr(profil, champ, valeur)

    db.commit()
    db.refresh(profil)
    return profil


@router.get("/moi/completion", response_model=ProfilCompletionResponse)
def obtenir_completion_profil(
    db: Session = Depends(get_db),
    utilisateur_courant: Utilisateur = Depends(get_current_user),
):
    profil = db.query(ProfilEtudiant).filter(
        ProfilEtudiant.utilisateur_id == utilisateur_courant.id
    ).first()
    if not profil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vous n'avez pas encore créé de profil étudiant.",
        )

    quiz = db.query(QuizResultat).filter(
        QuizResultat.utilisateur_id == utilisateur_courant.id
    ).order_by(QuizResultat.date_quiz.desc()).first()

    return calculer_completion(profil, quiz)


@router.get("/{profil_id}", response_model=ProfilResponse)
def obtenir_profil_public(
    profil_id: str,
    db: Session = Depends(get_db),
):
    profil = db.query(ProfilEtudiant).filter(ProfilEtudiant.id == profil_id).first()
    if not profil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil étudiant non trouvé."
        )
    return profil
