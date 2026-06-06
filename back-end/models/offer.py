"""
models/offer.py — Modèle SQLAlchemy pour les offres d'emploi/stage.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from database import Base


class OffreEmploi(Base):
    __tablename__ = "offres_emploi"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    entreprise_id = Column(String, ForeignKey("entreprises.id"), nullable=False)
    titre = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    localisation = Column(String(255))
    type_contrat = Column(String(100))        # Ex: "Stage", "CDI", "CDD"
    domaine = Column(String(255))             # Ex: "Informatique", "Finance"
    est_active = Column(Boolean, default=True)
    date_publication = Column(DateTime, default=datetime.utcnow)
    date_expiration = Column(DateTime, nullable=True)

    entreprise = relationship("Entreprise", back_populates="offres")
    candidatures = relationship("Candidature", back_populates="offre")
