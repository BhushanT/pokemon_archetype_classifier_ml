from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Construct database URL from environment variables
database_url = f"mysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(database_url)

Base = declarative_base()

class Team(Base):
    __tablename__ = 'teams'
    
    team_id = Column(Integer, primary_key=True)
    team_name = Column(String(100))
    playstyle = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    team_hp = Column(Integer, nullable=True)
    team_offense = Column(Integer, nullable=True)
    team_defense = Column(Integer, nullable=True)
    team_spdef = Column(Integer, nullable=True)
    team_speed = Column(Integer, nullable=True)
    recovery_moves = Column(Integer, nullable=True)
    defensive_items = Column(Integer, nullable=True)
    # Relationship to TeamPokemon
    pokemon = relationship("TeamPokemon", back_populates="team")

class Pokemon(Base):
    __tablename__ = 'pokemon'
    
    pokemon_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    type1 = Column(String(20), nullable=False)
    type2 = Column(String(20))
    base_hp = Column(Integer, nullable=False)
    base_attack = Column(Integer, nullable=False)
    base_defense = Column(Integer, nullable=False)
    base_sp_attack = Column(Integer, nullable=False)
    base_sp_defense = Column(Integer, nullable=False)
    base_speed = Column(Integer, nullable=False)
    # Relationship to TeamPokemon
    teams = relationship("TeamPokemon", back_populates="pokemon")

class Move(Base):
    __tablename__ = 'moves'
    
    move_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)
    category = Column(String(20))  # Physical, Special, or Status
    power = Column(Integer)
    accuracy = Column(Integer)
    pp = Column(Integer)
    is_recovery = Column(Boolean, default=False)
    is_hazard = Column(Boolean, default=False)

class TeamPokemon(Base):
    __tablename__ = 'team_pokemon'
    
    team_pokemon_id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.team_id'))
    pokemon_id = Column(Integer, ForeignKey('pokemon.pokemon_id'))
    move1_id = Column(Integer, ForeignKey('moves.move_id'))
    move2_id = Column(Integer, ForeignKey('moves.move_id'))
    move3_id = Column(Integer, ForeignKey('moves.move_id'))
    move4_id = Column(Integer, ForeignKey('moves.move_id'))
    item_id = Column(Integer, ForeignKey('items.item_id'))
    hp = Column(Integer, default=0)
    attack = Column(Integer, default=0)
    defense = Column(Integer, default=0)
    sp_attack = Column(Integer, default=0)
    sp_defense = Column(Integer, default=0)
    speed = Column(Integer, default=0)
    
    # Relationships
    team = relationship("Team", back_populates="pokemon")
    pokemon = relationship("Pokemon", back_populates="teams")
    move1 = relationship("Move", foreign_keys=[move1_id])
    move2 = relationship("Move", foreign_keys=[move2_id])
    move3 = relationship("Move", foreign_keys=[move3_id])
    move4 = relationship("Move", foreign_keys=[move4_id])
    item = relationship("Item")

class Item(Base):
    __tablename__ = 'items'
    
    item_id = Column(Integer, primary_key=True)
    item_name = Column(String(100), nullable=False)
    is_defensive = Column(Boolean, default=False)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

new_user = Team(team_name='Team Sandy')
session.add(new_user)
session.commit()

all_users = session.query(Team).all()

user = session.query(Team).filter_by(team_name='Team Sandy').first()
print(user)

session.close()