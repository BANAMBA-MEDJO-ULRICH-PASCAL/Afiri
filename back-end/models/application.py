"""
models/application.py — Modèle SQLAlchemy pour les candidatures.
"""

import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from database import Base


class StatutCandidature(str, enum.Enum):
    en_attente = "en_attente"
    acceptee = "acceptee"
    refusee = "refusee"


class Candidature(Base):
    __tablename__ = "candidatures"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    etudiant_id = Column(String, ForeignKey("profils_etudiants.id"), nullable=False)
    offre_id = Column(String, ForeignKey("offres_emploi.id"), nullable=False)
    lettre_motivation = Column(Text, nullable=True)
    statut = Column(Enum(StatutCandidature), default=StatutCandidature.en_attente)
    date_candidature = Column(DateTime, default=datetime.utcnow)

    etudiant = relationship("ProfilEtudiant", back_populates="candidatures")
    offre = relationship("OffreEmploi", back_populates="candidatures")
