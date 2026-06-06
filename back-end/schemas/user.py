from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from models.user import RoleEnum


class UserBase(BaseModel):
    email: EmailStr
    role: RoleEnum = RoleEnum.etudiant


class UserCreate(UserBase):
    mot_de_passe: str


class UserResponse(UserBase):
    id: str
    est_actif: bool
    date_inscription: datetime

    model_config = ConfigDict(from_attributes=True)
