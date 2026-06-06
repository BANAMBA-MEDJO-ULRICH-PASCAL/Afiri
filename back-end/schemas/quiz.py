from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Dict, Any, List


class QuizSubmit(BaseModel):
    reponses: Dict[str, Any]
    # utilisateur_id retiré — il viendra du token JWT via get_current_user


class QuizSubmitResponse(BaseModel):
    answer: str
    quiz_id: str


class QuizResultResponse(BaseModel):
    id: str
    utilisateur_id: str
    suggestions: List[str]    # List[str] (json.loads est fait dans le router)
    date_quiz: datetime

    model_config = ConfigDict(from_attributes=True)
