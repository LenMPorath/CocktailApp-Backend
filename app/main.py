#main.py
import logging
from fastapi import FastAPI
from app.db import models
from app.db.database import engine
from fastapi.middleware.cors import CORSMiddleware
from app.routes import iam, recipes
from app.core.config import APP_ENV 

# Datenbank erstellen (falls nicht existiert)
models.Base.metadata.create_all(bind=engine)

# Logger konfigurieren
log_level = logging.DEBUG if APP_ENV == "dev" else logging.ERROR
logging.getLogger().setLevel(log_level)

app = FastAPI(
    title="Len's Cocktail API",
    description="Dies ist eine API für meine Cocktail-App.",
    version="0.0.1",
    docs_url="/swagger"
)

# Fügen Sie die CORS-Middleware hinzu
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(iam.router)
app.include_router(recipes.router)