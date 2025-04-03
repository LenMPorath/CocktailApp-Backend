# db/crud/iam.py
from sqlalchemy.orm import Session
from app.db.models import User
from app.schemas.iam import UserModel, UserResponseModel, UserEditModel
from fastapi import HTTPException

# Nutzer erstellen
def create_user(db: Session, userModel: UserModel):

    if db.query(User).where(User.name == userModel.username).first() is not None:
        raise HTTPException(status_code=409, detail="Query: Nutzer existiert bereits")
    
    if db.query(User).first() is None:
        user = User(name=userModel.username, is_admin=True)
    else:
        user = User(name=userModel.username)

    user.set_password(userModel.password)

    db.add(user)
    db.commit()
    return user

# Nutzer nach Name suchen
def get_user_by_name(db: Session, username: str):
    return db.query(User).filter(User.name == username).first()

# Erhalte die Anzahl aller Nutzer
def get_amout_of_users(db: Session):
    return db.query(User).count()

# Passwortüberprüfung
def verify_user_password(user: User, password: str) -> bool:
    return user.verify_password(password)

def update_user_by_name(db: Session, userEditModel: UserEditModel):
    user = db.query(User).where(User.id == userEditModel.id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Query: Nutzer nicht gefunden")
    
    if db.query(User).where(User.name == userEditModel.new_username).first() is not None:
        raise HTTPException(status_code=409, detail="Query: Nutzer existiert bereits")
    
    if userEditModel.new_username is not None:
        user.name = userEditModel.new_username

    if userEditModel.new_password is not None:
        user.set_password(userEditModel.new_password)

    db.commit()
    return user

# Erhalte einen Nutzer
def get_user_with_id(db: Session, id: int) -> UserResponseModel:
    user = db.query(User).where(User.id == id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Query: Nutzer nicht gefunden")
    return UserResponseModel(
        id=user.id,
        username=user.name,
        favourites=[favourite.recipe_id for favourite in user.favorites]
    )