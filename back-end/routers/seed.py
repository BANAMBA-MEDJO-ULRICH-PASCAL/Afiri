"""
routers/seed.py — Endpoint pour peupler la base de données avec des données de test.
Toutes les données créées ici utilisent des emails reconnaissables (@test.cm)
pour pouvoir les nettoyer facilement sans toucher aux vraies données.
Mot de passe universel pour tous les comptes de test : CareerTest2026
"""

import json
import random
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.user import Utilisateur, ProfilEtudiant, Entreprise, RoleEnum
from models.offer import OffreEmploi
from models.application import Candidature, StatutCandidature
from models.quiz import QuizResultat
from security import hash_password


router = APIRouter(
    prefix="/seed",
    tags=["Données de test"]
)

MOT_DE_PASSE_TEST = hash_password("CareerTest2026")


ETUDIANTS_DATA = [
    {"email": "alice.mbarga@test.cm",  "nom": "Mbarga",   "prenom": "Alice",   "formation": "Licence Informatique",   "universite": "Université de Yaoundé I",  "competences": "Python, JavaScript, SQL"},
    {"email": "boris.nkodo@test.cm",   "nom": "Nkodo",    "prenom": "Boris",   "formation": "Master Data Science",    "universite": "ENSP Yaoundé",              "competences": "Python, R, Machine Learning"},
    {"email": "claire.fomo@test.cm",   "nom": "Fomo",     "prenom": "Claire",  "formation": "Licence Gestion",        "universite": "Université de Douala",      "competences": "Comptabilité, Excel, SAP"},
    {"email": "david.nguele@test.cm",  "nom": "Nguele",   "prenom": "David",   "formation": "Master Finance",         "universite": "IAI Cameroun",              "competences": "Finance, Analyse financière"},
    {"email": "emma.bella@test.cm",    "nom": "Bella",    "prenom": "Emma",    "formation": "Licence Droit",          "universite": "Université de Yaoundé II",  "competences": "Droit des affaires, Rédaction"},
    {"email": "felix.tala@test.cm",    "nom": "Tala",     "prenom": "Félix",   "formation": "Licence Informatique",   "universite": "IAI Cameroun",              "competences": "Java, Spring Boot, MySQL"},
    {"email": "grace.essono@test.cm",  "nom": "Essono",   "prenom": "Grace",   "formation": "Master Marketing",       "universite": "Université de Douala",      "competences": "Marketing digital, SEO"},
    {"email": "hugo.manga@test.cm",    "nom": "Manga",    "prenom": "Hugo",    "formation": "Licence Électronique",   "universite": "ENSP Yaoundé",              "competences": "Arduino, Électronique, C++"},
]

ENTREPRISES_DATA = [
    {"email": "rh@orange.test.cm",       "nom": "Orange Cameroun",    "secteur": "Télécommunications", "localisation": "Douala",  "description": "Opérateur télécom leader au Cameroun"},
    {"email": "recrutement@mtn.test.cm", "nom": "MTN Cameroun",       "secteur": "Télécommunications", "localisation": "Douala",  "description": "Réseau mobile panafricain"},
    {"email": "drh@camtel.test.cm",      "nom": "CAMTEL",             "secteur": "Informatique",       "localisation": "Yaoundé", "description": "Opérateur télécoms public du Cameroun"},
    {"email": "talent@afriland.test.cm", "nom": "Afriland First Bank", "secteur": "Finance",           "localisation": "Yaoundé", "description": "Banque panafricaine basée au Cameroun"},
]

OFFRES_DATA = [
    {"titre": "Stage Développeur Full Stack",   "description": "Développez des apps web modernes au sein de notre équipe tech.",    "localisation": "Douala",  "type_contrat": "Stage", "domaine": "Informatique"},
    {"titre": "Stage Data Analyst",             "description": "Analysez les données clients et produisez des rapports stratégiques.", "localisation": "Douala",  "type_contrat": "Stage", "domaine": "Informatique"},
    {"titre": "CDI Ingénieur Réseau",           "description": "Gérez et optimisez notre infrastructure réseau nationale.",           "localisation": "Yaoundé", "type_contrat": "CDI",   "domaine": "Informatique"},
    {"titre": "Stage Chargé de Communication",  "description": "Créez du contenu et gérez nos réseaux sociaux.",                     "localisation": "Douala",  "type_contrat": "Stage", "domaine": "Marketing"},
    {"titre": "CDD Gestionnaire de Projet",     "description": "Pilotez nos projets de transformation digitale.",                    "localisation": "Yaoundé", "type_contrat": "CDD",   "domaine": "Gestion"},
    {"titre": "Stage Analyste Financier",       "description": "Participez à l'analyse des risques et la gestion de portefeuille.",  "localisation": "Yaoundé", "type_contrat": "Stage", "domaine": "Finance"},
    {"titre": "CDI Développeur Mobile",         "description": "Développez nos applications mobiles iOS et Android.",                "localisation": "Douala",  "type_contrat": "CDI",   "domaine": "Informatique"},
    {"titre": "Stage Juriste d'Entreprise",     "description": "Assistez le département juridique dans la rédaction de contrats.",   "localisation": "Yaoundé", "type_contrat": "Stage", "domaine": "Droit"},
    {"titre": "Stage Marketing Digital",        "description": "Lancez des campagnes publicitaires en ligne.",                       "localisation": "Douala",  "type_contrat": "Stage", "domaine": "Marketing"},
    {"titre": "CDI Comptable",                  "description": "Gérez la comptabilité générale et analytique.",                      "localisation": "Yaoundé", "type_contrat": "CDI",   "domaine": "Finance"},
]


@router.post("/", summary="Peupler la BDD avec des données de test réalistes")
def seed_database(db: Session = Depends(get_db)):
    """
    Crée des données de test réalistes pour la démo et les graphiques.
    - Nettoie d'abord les données de test précédentes (@test.cm)
    - Crée un compte admin : admin@Afiri.cm / CareerTest2026
    - Crée 8 étudiants, 4 entreprises, 10 offres, ~20 candidatures, 5 quiz
    """

    # ── Étape 1 : Nettoyer les anciennes données de test ──────────────────
    tous_emails_test = (
        [e["email"] for e in ETUDIANTS_DATA]
        + [e["email"] for e in ENTREPRISES_DATA]
        + ["admin@Afiri.cm"]
    )

    utilisateurs_existants = db.query(Utilisateur).filter(
        Utilisateur.email.in_(tous_emails_test)
    ).all()
    ids_utilisateurs = [u.id for u in utilisateurs_existants]

    if ids_utilisateurs:
        db.query(QuizResultat).filter(
            QuizResultat.utilisateur_id.in_(ids_utilisateurs)
        ).delete(synchronize_session=False)

        profils_ids = [
            p.id for p in db.query(ProfilEtudiant).filter(
                ProfilEtudiant.utilisateur_id.in_(ids_utilisateurs)
            ).all()
        ]
        if profils_ids:
            db.query(Candidature).filter(
                Candidature.etudiant_id.in_(profils_ids)
            ).delete(synchronize_session=False)

        entreprises_ids = [
            e.id for e in db.query(Entreprise).filter(
                Entreprise.utilisateur_id.in_(ids_utilisateurs)
            ).all()
        ]
        if entreprises_ids:
            offres_ids = [
                o.id for o in db.query(OffreEmploi).filter(
                    OffreEmploi.entreprise_id.in_(entreprises_ids)
                ).all()
            ]
            if offres_ids:
                db.query(Candidature).filter(
                    Candidature.offre_id.in_(offres_ids)
                ).delete(synchronize_session=False)
            db.query(OffreEmploi).filter(
                OffreEmploi.entreprise_id.in_(entreprises_ids)
            ).delete(synchronize_session=False)

        db.query(ProfilEtudiant).filter(
            ProfilEtudiant.utilisateur_id.in_(ids_utilisateurs)
        ).delete(synchronize_session=False)
        db.query(Entreprise).filter(
            Entreprise.utilisateur_id.in_(ids_utilisateurs)
        ).delete(synchronize_session=False)
        db.query(Utilisateur).filter(
            Utilisateur.id.in_(ids_utilisateurs)
        ).delete(synchronize_session=False)

    db.commit()

    # ── Étape 2 : Compte admin ────────────────────────────────────────────
    admin = Utilisateur(
        email="admin@Afiri.cm",
        mot_de_passe=hash_password("CareerTest2026"),
        role=RoleEnum.admin
    )
    db.add(admin)
    db.commit()

    # ── Étape 3 : Étudiants + Profils ─────────────────────────────────────
    profil_ids = []

    for data in ETUDIANTS_DATA:
        user = Utilisateur(
            email=data["email"],
            mot_de_passe=MOT_DE_PASSE_TEST,
            role=RoleEnum.etudiant
        )
        db.add(user)
        db.flush()

        profil = ProfilEtudiant(
            utilisateur_id=user.id,
            nom=data["nom"],
            prenom=data["prenom"],
            formation=data["formation"],
            universite=data["universite"],
            competences=data["competences"],
        )
        db.add(profil)
        db.flush()
        profil_ids.append(profil.id)

    db.commit()

    # ── Étape 4 : Entreprises ─────────────────────────────────────────────
    entreprise_ids = []

    for data in ENTREPRISES_DATA:
        user = Utilisateur(
            email=data["email"],
            mot_de_passe=MOT_DE_PASSE_TEST,
            role=RoleEnum.entreprise
        )
        db.add(user)
        db.flush()

        entreprise = Entreprise(
            utilisateur_id=user.id,
            nom=data["nom"],
            secteur=data["secteur"],
            description=data["description"],
            localisation=data["localisation"]
        )
        db.add(entreprise)
        db.flush()
        entreprise_ids.append(entreprise.id)

    db.commit()

    # ── Étape 5 : Offres d'emploi ─────────────────────────────────────────
    offre_ids = []

    for i, data in enumerate(OFFRES_DATA):
        offre = OffreEmploi(
            entreprise_id=entreprise_ids[i % len(entreprise_ids)],
            titre=data["titre"],
            description=data["description"],
            localisation=data["localisation"],
            type_contrat=data["type_contrat"],
            domaine=data["domaine"],
            est_active=True,
            date_expiration=datetime.utcnow() + timedelta(days=random.randint(15, 60))
        )
        db.add(offre)
        db.flush()
        offre_ids.append(offre.id)

    db.commit()

    # ── Étape 6 : Candidatures ────────────────────────────────────────────
    statuts = [
        StatutCandidature.en_attente,
        StatutCandidature.en_attente,
        StatutCandidature.acceptee,
        StatutCandidature.refusee,
    ]
    paires_utilisees = set()
    candidatures_count = 0

    for profil_id in profil_ids:
        offres_choisies = random.sample(offre_ids, min(random.randint(2, 3), len(offre_ids)))

        for offre_id in offres_choisies:
            paire = (profil_id, offre_id)
            if paire not in paires_utilisees:
                candidature = Candidature(
                    etudiant_id=profil_id,
                    offre_id=offre_id,
                    statut=random.choice(statuts),
                    date_candidature=datetime.utcnow() - timedelta(days=random.randint(1, 20))
                )
                db.add(candidature)
                paires_utilisees.add(paire)
                candidatures_count += 1

    db.commit()

    # ── Étape 7 : Résultats de quiz ───────────────────────────────────────
    ids_etudiants_test = [
        u.id for u in db.query(Utilisateur).filter(
            Utilisateur.email.in_([e["email"] for e in ETUDIANTS_DATA[:5]])
        ).all()
    ]

    domaines_quiz = ["informatique", "gestion", "finance", "math", "lettres"]
    for i, uid in enumerate(ids_etudiants_test):
        reponses = {
            "filiere": domaines_quiz[i % len(domaines_quiz)],
            "experience": random.choice(["moins de 1 an", "1 à 2 ans", "plus de 2 ans"])
        }
        suggestions = ["Développeur logiciel", "Data Analyst", "Chef de projet"]
        db.add(QuizResultat(
            utilisateur_id=uid,
            reponses=json.dumps(reponses),
            suggestions=json.dumps(suggestions)
        ))

    db.commit()

    return {
        "message": "✅ Données de test créées avec succès !",
        "acces_dashboard": "http://localhost:8000/dashboard",
        "compte_admin": {
            "email": "admin@Afiri.cm",
            "mot_de_passe": "CareerTest2026",
            "role": "admin"
        },
        "résumé": {
            "étudiants": len(ETUDIANTS_DATA),
            "entreprises": len(ENTREPRISES_DATA),
            "offres": len(OFFRES_DATA),
            "candidatures": candidatures_count,
            "quiz": len(ids_etudiants_test),
        }
    }
