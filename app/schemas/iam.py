#schemas/iam.py
from pydantic import BaseModel
from typing import List, Optional

class RefreshRequest(BaseModel):
    refresh_token: str

# Schema für die Erstellung eines neuen Benutzers
class UserModel(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None

# Schema zum Verändern des Nutzers
class UserEditModel(UserModel):
    username: str = None
    password: str = None
    new_username: Optional[str] = None
    new_password: Optional[str] = None

# Schema für Benutzerantworten
class UserResponseModel(UserModel):
    message: str = None
    favourites: List[int]