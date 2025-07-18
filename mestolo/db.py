from enum import Enum
import os

import pandas as pd

from sqlalchemy import (Boolean, Column, DateTime, Float, Integer, String,
                        create_engine, TEXT, ForeignKey, Enum as SQLEnum, text, inspect)
from sqlalchemy.orm import Session, declarative_base, Mapped, mapped_column

Base = declarative_base()

def get_database_name():
    return os.environ.get("MESTOLO_DATABASE", "sqlite:///mestolo.db")

def run_query(query):
    engine = create_engine(get_database_name())
    with engine.connect() as conn, conn.begin():
        return pd.read_sql_query(query, conn)

def create_session():
    engine = create_engine(get_database_name())
    if not inspect(engine).has_table("recipes"):  # it's incomplete and needs filling
        Base.metadata.create_all(engine)
    return Session(engine)

class RecipeDB(Base):
    __tablename__ = "recipes"
    name = Column(String(128), nullable=False, primary_key=True)
    inputs = Column(TEXT, nullable=False)
    outputs = Column(TEXT, nullable=False)
    cadence_seconds = Column(Float, nullable=False)
    lookback_length_seconds = Column(Float, nullable=False)
    priority = Column(Float, nullable=False)

RecipeRunState = Enum("RecipeRunState", ["scheduled", "failed", "cooked", "cancelled", "cooking"])

class RecipeRunDB(Base):
    __tablename__ = 'recipe_runs'

    id = Column(Integer, primary_key=True)
    recipe_name: Mapped[String(128)] = mapped_column(ForeignKey("recipes.name"))
    last_update = Column(DateTime, nullable=False)
    status = Column(SQLEnum(RecipeRunState), nullable=False)
    input_values = Column(TEXT, nullable=True)
    output_values = Column(TEXT, nullable=True)
    schedule_time = Column(DateTime, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)


# class NodeDB(Base):
#     __tablename__ = "nodes"
#     id = Column(Integer, primary_key=True)
#     name = Column(String(64), nullable=False)
#     start_time = Column(DateTime, nullable=True)
#     end_time = Column(DateTime, nullable=True)
#     state = Column(Integer, nullable=False)
#     count = Column(Integer, nullable=True)
#     posx = Column(Float, nullable=True)
#     posy = Column(Float, nullable=True)
#
#     def to_ingredient_constraint(self):
#         return IngredientConstraint(self.name, DateTimeInterval(self.start_time, self.end_time), self.count)
#
#
# class EdgesDB(Base):
#     __tablename__ = "edges"
#     id = Column(Integer, primary_key=True)
#     source = Column(Integer, nullable=False)
#     sink = Column(Integer, nullable=False)
#     active = Column(Boolean, nullable=False, default=True)
#
#
# class ScheduledIngredientDB(Base):
#     __tablename__ = "scheduled_ingredient"
#     id = Column(Integer, primary_key=True)
#     schedule_time = Column(DateTime, nullable=False)
#     current_priority = Column(Float, nullable=False)
#     recipe = Column(String(64), nullable=False)
#     node = Column(Integer, nullable=False)
#     active = Column(Boolean, nullable=False, default=True)
