from fastapi import FastAPI, Depends
from . import models, database

app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)

# Testendpunkt
@app.get("/")
def read_root():
    return {"Hello World"}
