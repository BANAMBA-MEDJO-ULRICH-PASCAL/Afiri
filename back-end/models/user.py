"""
models/user.py — Modèles SQLAlchemy pour les utilisateurs.
Contient : RoleEnum, Utilisateur, ProfilEtudiant, Entreprise
"""

import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from database import Base


class RoleEnum(str, enum.Enum):
    etudiant = "etudiant"
    entreprise = "entreprise"
    admin = "admin"


class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    mot_de_passe = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.etudiant)
    est_actif = Column(Boolean, default=True)
    date_inscription = Column(DateTime, default=datetime.utcnow)

    profil_etudiant = relationship("ProfilEtudiant", back_populates="utilisateur", uselist=False)
    entreprise = relationship("Entreprise", back_populates="utilisateur", uselist=False)


class ProfilEtudiant(Base):
    __tablename__ = "profils_etudiants"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    utilisateur_id = Column(String, ForeignKey("utilisateurs.id"), nullable=False, unique=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    formation = Column(String(255))
    universite = Column(String(255))
    competences = Column(Text)
    experiences = Column(Text)
    projets = Column(Text)
    cv_lien = Column(String(500))
    lien_partage = Column(String(100), unique=True, default=lambda: str(uuid.uuid4())[:8])
    date_mise_a_jour = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    utilisateur = relationship("Utilisateur", back_populates="profil_etudiant")
    candidatures = relationship("Candidature", back_populates="etudiant")


class Entreprise(Base):
    __tablename__ = "entreprises"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    utilisateur_id = Column(String, ForeignKey("utilisateurs.id"), nullable=False, unique=True)
    nom = Column(String(255), nullable=False)
    secteur = Column(String(255))
    description = Column(Text)
    site_web = Column(String(500))
    localisation = Column(String(255))
    date_creation = Column(DateTime, default=datetime.utcnow)

    utilisateur = relationship("Utilisateur", back_populates="entreprise")
    offres = relationship("OffreEmploi", back_populates="entreprise")
