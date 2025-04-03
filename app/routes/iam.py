# routes/iam.py
from fastapi import APIRouter, Depends, HTTPException, Header, status
from fastapi.responses import JSONResponse
from datetime import timedelta
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.db.database import get_db
from app.db.crud.iam import create_user, get_user_by_name, verify_user_password, get_amout_of_users, get_user_with_id, update_user_by_name
from app.schemas.iam import RefreshRequest, UserModel, UserEditModel, UserResponseModel

router = APIRouter(prefix="/iam", tags=["iam"])

@router.get("/getUserAmount")
async def getUserAmount(db = Depends(get_db)):
    return get_amout_of_users(db)

@router.get("/getUser")
async def getUser(id: int, db = Depends(get_db)):
    user: UserResponseModel = get_user_with_id(db, id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nutzer nicht gefunden")
    return user
    
@router.get("/protected")
async def protectedRoute(authorization: str = Header(None)):
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalider Token")
    return JSONResponse(content={"message": "Zugang gestattet"})

@router.post("/createUser")
async def createUser(register_data: UserModel, db = Depends(get_db)):
    user = create_user(db, register_data)
    return UserResponseModel(username= user.name,message="Nutzer wurde erstellt")

@router.post("/refresh")
async def refresh_token(request: RefreshRequest):
    refresh_token = request.refresh_token
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Kein Refresh-Token vorhanden")

    payload = verify_token(refresh_token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Ungültiger Refresh-Token")

    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalides Token payload")

    new_access_token = create_access_token({"sub": username}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    response = JSONResponse(content={"message": "Token aktualisiert"})
    response.set_cookie(key="access_token", value=new_access_token, httponly=True, secure=True, samesite="Strict")
    return response


@router.post("/login")
async def login(login_data: UserModel, db=Depends(get_db)):
    user = get_user_by_name(db, login_data.username)
    if not user or not verify_user_password(user, login_data.password):
        raise HTTPException(status_code=401, detail="Ungültige Anmeldeinformationen")

    access_token = create_access_token({"sub": user.name}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_refresh_token({"sub": user.name})

    response = JSONResponse(content={"message": "Login erfolgreich"})
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite="Strict")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="Strict")
    return response

@router.patch("/editUser")
async def editUser(data: UserEditModel, db = Depends(get_db)):
    user = update_user_by_name(db, data.username)
    return UserModel(username= user.name,message="Nutzer wurde erstellt")

@router.delete("/deleteUser")
async def deleteUser(auth_data: UserModel, db = Depends(get_db)):
    print("deleteUserController")