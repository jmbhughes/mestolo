import pandas as pd
from sqlalchemy import (Boolean, Column, DateTime, Float, Integer, String,
                        create_engine)
from sqlalchemy.orm import Session, declarative_base

from mestolo.datetime import DateTimeInterval
from mestolo.ingredients import IngredientConstraint

Base = declarative_base()
DATABASE_NAME = "sqlite:///database.db"

def run_query(query):
    engine = create_engine(DATABASE_NAME)
    with engine.connect() as conn, conn.begin():
        return pd.read_sql_query(query, conn)

def create_db():
    engine = create_engine(DATABASE_NAME)
    # with engine.connect() as connection:
    #     connection.execute(text('CREATE DATABASE IF NOT EXISTS mestolo;'))
    Base.metadata.create_all(engine)

def create_session():
    engine = create_engine(DATABASE_NAME)
    return Session(engine)

class NodeDB(Base):
    __tablename__ = "nodes"
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    state = Column(Integer, nullable=False)
    posx = Column(Float, nullable=True)
    posy = Column(Float, nullable=True)

    def to_ingredient_constraint(self):
        return IngredientConstraint(self.name, DateTimeInterval(self.start_time, self.end_time))

class EdgesDB(Base):
    __tablename__ = "edges"
    id = Column(Integer, primary_key=True)
    source = Column(Integer, nullable=False)
    sink = Column(Integer, nullable=False)
    active = Column(Boolean, nullable=False, default=True)


class ScheduledIngredientDB(Base):
    __tablename__ = "scheduled_ingredient"
    id = Column(Integer, primary_key=True)
    schedule_time = Column(DateTime, nullable=False)
    current_priority = Column(Float, nullable=False)
    recipe = Column(String(64), nullable=False)
    node = Column(Integer, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
