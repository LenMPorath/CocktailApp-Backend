from fastapi import FastAPI, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from app import models
from app.database import get_db, engine
from fastapi.middleware.cors import CORSMiddleware
from .utils import create_access_token, create_refresh_token, verify_token
from datetime import timedelta
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
from .crud import create_user, get_amout_of_users, get_user_with_id, verify_user_password, get_user_by_name
from .schemas import AuthRequestModel, AuthResponseModel, ChangePasswordModel, RefreshRequest, UserCreateModel

# Datenbank erstellen (falls nicht existiert)
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Fügen Sie die CORS-Middleware hinzu
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Hier können Sie spezifische Ursprünge angeben, z.B. ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # Erlaubt alle HTTP-Methoden, z.B. GET, POST
    allow_headers=["*"],  # Erlaubt alle Header
)

@app.post("/login")
async def login(login_data: AuthRequestModel, db = Depends(get_db)):
    if(login_data.guest):
        if (get_user_by_name(db, login_data.username)):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Nutzer "{login_data.username}" existiert bereits')
        user = create_user(db, UserCreateModel(username=login_data.username))
        access_token = create_access_token({"sub": user.name}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        refresh_token = create_refresh_token({"sub": user.name})

        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    else:
        user = get_user_by_name(db, login_data.username)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Ungültige Anmeldeinformationen (Nutzername oder Passwort ist falsch)")

        # Authentifiziere den Benutzer und hole seine Daten
        if not verify_user_password(user, login_data.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Ungültige Anmeldeinformationen (Nutzername oder Passwort ist falsch)")

        access_token = create_access_token({"sub": user.name}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        refresh_token = create_refresh_token({"sub": user.name})

        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    

@app.get("/protected")
async def protectedRoute(authorization: str = Header(None)):
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalider Token")
    return {"message": "Zugang gestattet"}

@app.get("/getUserAmount")
async def getUserAmount(db = Depends(get_db)):
    return get_amout_of_users(db)

@app.post("/createUser")
async def createUser(register_data: UserCreateModel, db = Depends(get_db)):
    user = create_user(db, register_data)
    return AuthResponseModel(message="Nutzer wurde erstellt")

@app.patch("/changePassword")
async def changePassword(auth_data: ChangePasswordModel, db = Depends(get_db)):
    print("changePasswordController")

@app.delete("/deleteUser")
async def deleteUser(auth_data: ChangePasswordModel):
    print("deleteUserController")

@app.get("/getUser")
async def getUser(id: int):
    return get_user_with_id(id)

@app.post("/refresh")
async def refresh_token(refresh_request: RefreshRequest):
    payload = verify_token(refresh_request.refresh_token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalider Refresh Token")

    # Stelle sicher, dass der Token einem bestehenden Benutzer gehört und gültig ist
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalides Token payload")

    # Erstelle einen neuen Access-Token
    new_access_token = create_access_token({"sub": username}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": new_access_token}