#routes/recipes.py
from fastapi import APIRouter
router = APIRouter(prefix="/recipes", tags=["recipes"])