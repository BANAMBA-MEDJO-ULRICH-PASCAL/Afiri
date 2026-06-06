"""Calcul du pourcentage de complétion du profil étudiant."""

import json
from typing import Optional

from models.user import ProfilEtudiant
from models.quiz import QuizResultat


def _quiz_status(quiz: Optional[QuizResultat]) -> dict:
    if not quiz:
        return {"termine": False, "ignore": False, "partiel": False}

    try:
        reponses = json.loads(quiz.reponses)
    except (json.JSONDecodeError, TypeError):
        return {"termine": False, "ignore": False, "partiel": False}

    return {
        "termine": bool(reponses.get("complete")),
        "ignore": bool(reponses.get("skipped")),
        "partiel": bool(reponses.get("partial")),
    }


def calculer_completion(profil: ProfilEtudiant, quiz: Optional[QuizResultat]) -> dict:
    quiz_info = _quiz_status(quiz)

    items = [
        {
            "key": "quiz",
            "label": "Passer le quiz d'orientation",
            "done": quiz_info["termine"] or quiz_info["partiel"],
        },
        {
            "key": "competences",
            "label": "Ajouter tes compétences",
            "done": bool(profil.competences and profil.competences.strip()),
        },
        {
            "key": "experiences",
            "label": "Ajouter tes expériences",
            "done": bool(profil.experiences and profil.experiences.strip()),
        },
        {
            "key": "projets",
            "label": "Ajouter tes projets",
            "done": bool((getattr(profil, "projets", None) or "").strip()),
        },
    ]

    pourcentage = sum(25 for item in items if item["done"])
    complet = pourcentage >= 100

    quiz_termine = quiz_info["termine"]
    quiz_ignore = quiz_info["ignore"]

    peut_recommander = (quiz_termine and not quiz_ignore) or pourcentage >= 25

    manquants = [item["label"] for item in items if not item["done"]]
    if complet:
        conseil = "Profil complet — tu es prêt à matcher les meilleures offres !"
    elif manquants:
        conseil = f"Pour compléter ton profil : {manquants[0]}."
    else:
        conseil = "Complète ton profil pour de meilleures recommandations."

    return {
        "pourcentage": pourcentage,
        "complet": complet,
        "peut_recommander": peut_recommander,
        "quiz_termine": quiz_termine,
        "quiz_ignore": quiz_ignore,
        "items": items,
        "conseil": conseil,
    }
