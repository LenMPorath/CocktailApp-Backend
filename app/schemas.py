from typing import List
from pydantic import BaseModel

# Schema für Login-Anfragen
class AuthRequestModel(BaseModel):
    username: str
    password: str
    guest: bool

# Schema für Login-Antwort
class AuthResponseModel(BaseModel):
    message: str
    username: str = None

class RefreshRequest(BaseModel):
    refresh_token: str

# Schema für die Erstellung eines neuen Benutzers
class UserCreateModel(BaseModel):
    username: str
    password: str = None

# Basisschema des Nutzers
class UserModel(BaseModel):
    id: int

# Schema zum Verändern des Nutzers
class EditUserModel(UserModel):
    newUsername: str = None

# Schema um das Passwort zu verändern
class ChangePasswordModel(AuthRequestModel):
    newPassword: str

# Schema für Benutzerantworten
class UserResponseModel(UserModel):
    username: str
    favourites: List[int]
    class Config:
        orm_mode = True