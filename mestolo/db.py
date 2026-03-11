import logging
import multiprocessing as mp
import time
import random

from sqlalchemy import Column, DateTime, Integer, create_engine, TEXT, String, ForeignKey, inspect, Float, Boolean
from sqlalchemy.orm import declarative_base, Session, mapped_column, Mapped

DB_NAME = "sqlite:////Users/mhughes/repos/mestolo/mestolo/mestolo.db"  # TODO don't hardcode

Base = declarative_base()

logger = logging.getLogger()

import numpy as np

def numpy_pi(number_of_samples):
    # Generate all random points at once
    xs = np.random.random(size=number_of_samples)
    ys = np.random.random(size=number_of_samples)

    # Compute squared distances without square root
    r_squareds = xs ** 2 + ys ** 2

    # Count points inside unit circle
    within_circle_count = np.sum(r_squareds < 1)

    return within_circle_count / number_of_samples * 4

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
        time.sleep(random.randint(1, 15))
        # TODO: actually run recipe
        numpy_pi(np.random.randint(1E8, 1E9))
        q.put(self.id)




class ResourceUseDB(Base):
    __tablename__ = "resource_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    memory = Column(Float)
    cpu = Column(Float)
    time = Column(DateTime, nullable=False)
    error = Column(Boolean)
    run_id: Mapped[Integer] = mapped_column(ForeignKey("recipe_runs.id"))