import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from security import get_current_user
from models.quiz import QuizResultat
from models.user import Utilisateur
from schemas.quiz import QuizSubmit, QuizSubmitResponse, QuizResultResponse


router = APIRouter(
    prefix="/quiz",
    tags=["Quiz d'orientation"]
)

# Dictionnaire de suggestions par domaine
SUGGESTIONS_PAR_DOMAINE = {
    "informatique": [
        "Développeur logiciel",
        "Data Analyst",
        "Administrateur réseau",
        "Cybersécurité"
    ],
    "math": [
        "Data Scientist",
        "Statisticien"
    ],
    "gestion": [
        "Comptable",
        "Gestionnaire de projet"
    ],
    "biologie": [
        "Vétérinaire",
        "Médecin chercheur",
        "Laborantin biologie"
    ],
    "chimie": [
        "Chimiste chercheur",
        "Enseignant de chimie"
    ],
    "physique": [
        "Physicien chercheur",
        "Mécanicien engin d'usine",
        "Enseignant de physique"
    ],
    "lettres": [
        "Enseignant de français",
        "Journaliste"
    ],
    "finance": [
        "Analyste financier",
        "Comptable",
        "Contrôleur de gestion"
    ],
    "droit": [
        "Juriste d'entreprise",
        "Avocat",
        "Notaire"
    ],
    "marketing": [
        "Chargé de communication",
        "Community manager",
        "Consultant marketing"
    ],
}

SUGGESTIONS_PAR_DEFAUT = [
    "Encadreur / Conseiller",
    "Assistant d'Administration",
    "Gestionnaire"
]


# ─────────────────────────────────────────────────────────────────
# POST /quiz/envoyer
# ─────────────────────────────────────────────────────────────────

@router.post("/envoyer", response_model=QuizSubmitResponse)
def submit_quiz(
    data: QuizSubmit,
    db: Session = Depends(get_db),
    utilisateur_courant: Utilisateur = Depends(get_current_user)
):
    domaine = data.reponses.get("filiere", "").lower()
    suggestions = SUGGESTIONS_PAR_DOMAINE.get(domaine, SUGGESTIONS_PAR_DEFAUT)

    quiz = QuizResultat(
        utilisateur_id=utilisateur_courant.id,
        reponses=json.dumps(data.reponses),
        suggestions=json.dumps(suggestions)
    )

    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    return {
        "answer": "Réponses enregistrées avec succès",
        "quiz_id": quiz.id
    }


# ─────────────────────────────────────────────────────────────────
# GET /quiz/resultats/{quiz_id}
# ─────────────────────────────────────────────────────────────────

@router.get("/resultats/{quiz_id}", response_model=QuizResultResponse)
def get_resultats(
    quiz_id: str,
    db: Session = Depends(get_db),
    utilisateur_courant: Utilisateur = Depends(get_current_user)
):
    quiz = db.query(QuizResultat).filter(QuizResultat.id == quiz_id).first()

    if not quiz:
        raise HTTPException(status_code=404, detail="Résultat introuvable.")

    if quiz.utilisateur_id != utilisateur_courant.id:
        raise HTTPException(
            status_code=403,
            detail="Vous ne pouvez consulter que vos propres résultats."
        )

    return {
        "id": quiz.id,
        "utilisateur_id": quiz.utilisateur_id,
        "suggestions": json.loads(quiz.suggestions),
        "date_quiz": quiz.date_quiz
    }


# ─────────────────────────────────────────────────────────────────
# GET /quiz/mon-dernier
# Raccourci : récupère le dernier quiz de l'utilisateur connecté
# ─────────────────────────────────────────────────────────────────

@router.get("/mon-dernier", response_model=QuizResultResponse)
def get_mon_dernier_quiz(
    db: Session = Depends(get_db),
    utilisateur_courant: Utilisateur = Depends(get_current_user)
):
    quiz = db.query(QuizResultat).filter(
        QuizResultat.utilisateur_id == utilisateur_courant.id
    ).order_by(QuizResultat.date_quiz.desc()).first()

    if not quiz:
        raise HTTPException(status_code=404, detail="Aucun quiz trouvé pour cet utilisateur.")

    return {
        "id": quiz.id,
        "utilisateur_id": quiz.utilisateur_id,
        "suggestions": json.loads(quiz.suggestions),
        "date_quiz": quiz.date_quiz
    }
