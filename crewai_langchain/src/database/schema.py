from sqlalchemy import create_engine, Column, String, DateTime, ForeignKey, Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    tokens = relationship("OAuthToken", back_populates="user")

class OAuthToken(Base):
    __tablename__ = 'oauth_tokens'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'))
    platform = Column(String)
    access_token = Column(String)
    refresh_token = Column(String)
    expires_at = Column(DateTime)
    scopes = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="tokens") 