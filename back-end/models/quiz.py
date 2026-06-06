"""
models/quiz.py — Modèle SQLAlchemy pour les résultats du quiz d'orientation.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base


class QuizResultat(Base):
    __tablename__ = "quiz_resultats"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    utilisateur_id = Column(String, ForeignKey("utilisateurs.id"), nullable=False)
    reponses = Column(Text, nullable=False)       # Stocké en JSON string
    suggestions = Column(Text, nullable=False)    # Liste de métiers suggérés en JSON string
    date_quiz = Column(DateTime, default=datetime.utcnow)

    utilisateur = relationship("Utilisateur")
