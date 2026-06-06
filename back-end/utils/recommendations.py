"""Moteur de recommandation d'offres basé sur le quiz et le profil."""

import json
from typing import List, Optional

from models.offer import OffreEmploi
from models.user import ProfilEtudiant, Entreprise
from models.quiz import QuizResultat

TYPE_TO_DOMAINE = {
    "dev": "Informatique",
    "design": "Marketing",
    "data": "Informatique",
    "project": "Gestion",
    "marketing": "Marketing",
    "support": "Informatique",
}

DOMAINE_KEYWORDS = {
    "informatique": ["python", "javascript", "java", "react", "sql", "web", "mobile", "data", "réseau", "dev"],
    "marketing": ["marketing", "seo", "communication", "community", "social", "design", "figma"],
    "finance": ["finance", "comptab", "analyse", "excel", "banque"],
    "gestion": ["gestion", "projet", "agile", "coordination"],
    "droit": ["droit", "jurid", "contrat"],
}


def _domaine_from_quiz(quiz: Optional[QuizResultat]) -> Optional[str]:
    if not quiz:
        return None
    try:
        reponses = json.loads(quiz.reponses)
    except (json.JSONDecodeError, TypeError):
        return None

    if reponses.get("skipped"):
        return None

    filiere = reponses.get("filiere", "")
    if filiere:
        return filiere.capitalize() if filiere.lower() != "informatique" else "Informatique"

    quiz_type = reponses.get("type", "")
    return TYPE_TO_DOMAINE.get(quiz_type)


def _score_offer(offer: OffreEmploi, entreprise_nom: str, profil: ProfilEtudiant, domaine_cible: Optional[str]) -> int:
    score = 0
    titre = (offer.titre or "").lower()
    desc = (offer.description or "").lower()
    domaine = (offer.domaine or "").lower()
    competences = (profil.competences or "").lower()

    if domaine_cible and domaine == domaine_cible.lower():
        score += 40

    for mot in competences.replace(",", " ").split():
        mot = mot.strip().lower()
        if len(mot) > 2 and (mot in titre or mot in desc):
            score += 15

    for mots in DOMAINE_KEYWORDS.values():
        for mot in mots:
            if mot in competences and (mot in titre or mot in desc or mot in domaine):
                score += 8

    if offer.type_contrat and offer.type_contrat.lower() == "stage":
        score += 5

    return score


def recommander_offres(
    offres: List[OffreEmploi],
    entreprises: dict,
    profil: ProfilEtudiant,
    quiz: Optional[QuizResultat],
    limit: int = 8,
) -> List[dict]:
    domaine_cible = _domaine_from_quiz(quiz)

    scored = []
    for offre in offres:
        ent = entreprises.get(offre.entreprise_id)
        nom_entreprise = ent.nom if ent else "Entreprise"
        score = _score_offer(offre, nom_entreprise, profil, domaine_cible)
        if domaine_cible and offre.domaine and offre.domaine.lower() == domaine_cible.lower():
            score += 20
        scored.append((score, offre, nom_entreprise))

    scored.sort(key=lambda x: x[0], reverse=True)

    if all(s == 0 for s, _, _ in scored):
        scored.sort(key=lambda x: x[1].date_publication, reverse=True)

    result = []
    for score, offre, nom_entreprise in scored[:limit]:
        result.append({
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
            "entreprise_nom": nom_entreprise,
            "score": score,
        })
    return result
