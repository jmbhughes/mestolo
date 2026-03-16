import logging
import multiprocessing as mp
import time
import random
import json

from sqlalchemy import Column, DateTime, Integer, create_engine, TEXT, String, ForeignKey, inspect, Float, Boolean
from sqlalchemy.orm import declarative_base, Session, mapped_column, Mapped

from mestolo.util import get_callable_from_path

DB_NAME = "sqlite:///mestolo.db"  # TODO don't hardcode

Base = declarative_base()

logger = logging.getLogger()

def get_database_session():
    """Sets up a session to connect to the database"""
    engine = create_engine(DB_NAME)
    if not inspect(engine).has_table("recipes"):  # it's incomplete and needs filling
        Base.metadata.create_all(engine)
    session = Session(engine)
    return engine, session

class RecipeDB(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True)
    path = Column(String(128), nullable=False)
    name = Column(String(128), nullable=False)

class RecipeRunDB(Base):
    __tablename__ = "recipe_runs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    scheduled_time = Column(DateTime, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    parameters = Column(TEXT, nullable=True)
    recipe: Mapped[Integer] = mapped_column(ForeignKey("recipes.id"))

    def run(self, q: mp.Queue) -> None:
        logger.info(f"Running {self.id} RecipeRun.")
        recipe = self.grab_recipe()
        parameters = json.loads(self.parameters)
        fn = get_callable_from_path(recipe.path, recipe.name)
        fn(**parameters)
        q.put(self.id)

    def grab_recipe(self) -> RecipeDB:
        _, session = get_database_session()
        return session.query(RecipeDB).filter(RecipeDB.id == self.recipe).one()

class ResourceUseDB(Base):
    __tablename__ = "resource_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    memory = Column(Float)
    cpu = Column(Float)
    time = Column(DateTime, nullable=False)
    error = Column(Boolean)
    run_id: Mapped[Integer] = mapped_column(ForeignKey("recipe_runs.id"))