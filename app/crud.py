from sqlalchemy.orm import Session
from .models import User
from .schemas import UserCreateModel, UserResponseModel
import logging

# Nutzer erstellen
def create_user(db: Session, user: UserCreateModel):
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    db_user = User(name=user.username)
    if(user.password):
        db_user.set_password(user.password)  # Passwörter werden in der User-Klasse behandelt
    db.add(db_user)
    db.commit()
    return db_user

# Nutzer nach Name suchen
def get_user_by_name(db: Session, username: str):
    return db.query(User).filter(User.name == username).first()

# Erhalte die Anzahl aller Nutzer
def get_amout_of_users(db: Session):
    return db.query(User).count()

# Passwortüberprüfung
def verify_user_password(user: User, password: str) -> bool:
    return user.verify_password(password)

# Erhalte einen Nutzer
def get_user_with_id(db: Session, id: int) -> UserResponseModel:
    return db.query(User).where(User.id == id)