import os
from sqlalchemy import Boolean, Column, DateTime, Integer, Float, Enum, ForeignKey, String
from sqlalchemy.orm import relationship
from .database import Base
from .enums import UnitEnum
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    password_hash = Column(String, nullable=True)
    salt = Column(String, nullable=True)

    orders = relationship("Order", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")

    def set_password(self, password: str):
        """Generiert einen Salt, hasht das Passwort und speichert den Hash."""
        self.salt = os.urandom(16).hex()
        self.password_hash = pwd_context.hash(password + self.salt)

    def verify_password(self, password: str) -> bool:
        """Verifiziert, ob das Passwort korrekt ist."""
        return pwd_context.verify(password + self.salt, self.password_hash)

class Session(Base):
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True, index=True)
    session_token = Column(String, unique=True, index=True)
    session_start = Column(DateTime)
    session_end = Column(DateTime)
    include_prices = Column(Boolean, default=False)

    orders = relationship("Order", back_populates="session")

class Recipe(Base):
    __tablename__ = 'recipes'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    img_path = Column(String)

    ingredients = relationship("RecipeIngredient", back_populates="recipe")
    orders = relationship("Order", back_populates="recipe")
    favorites = relationship("Favorite", back_populates="recipe")

class Ingredient(Base):
    __tablename__ = 'ingredients'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    kcal = Column(Float)
    is_alcohol = Column(Boolean)
    img_path = Column(String)

    recipe_ingredients = relationship("RecipeIngredient", back_populates="ingredient")
    inventory_ingredients = relationship("InventoryIngredient", back_populates="ingredient")

class RecipeIngredient(Base):
    __tablename__ = 'recipe_ingredients'

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'))
    unit = Column(Enum(UnitEnum))
    amount = Column(Float)

    recipe = relationship("Recipe", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="recipe_ingredients")

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    session_id = Column(Integer, ForeignKey('sessions.id'))
    order_time = Column(DateTime)
    additional_info = Column(String, nullable=True)
    finished = Column(Boolean, default=False)

    user = relationship("User", back_populates="orders")
    recipe = relationship("Recipe", back_populates="orders")
    session = relationship("Session", back_populates="orders")

class Favorite(Base):
    __tablename__ = 'favorites'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    recipe_id = Column(Integer, ForeignKey('recipes.id'))

    user = relationship("User", back_populates="favorites")
    recipe = relationship("Recipe", back_populates="favorites")

class Inventory(Base):
    __tablename__ = 'inventories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    ingredients = relationship("InventoryIngredient", back_populates="inventory")

class InventoryIngredient(Base):
    __tablename__ = 'inventory_ingredients'

    id = Column(Integer, primary_key=True, index=True)
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'))
    inventory_id = Column(Integer, ForeignKey('inventories.id'))
    unit = Column(Enum(UnitEnum))
    amount = Column(Float)

    ingredient = relationship("Ingredient", back_populates="inventory_ingredients")
    inventory = relationship("Inventory", back_populates="ingredients")
