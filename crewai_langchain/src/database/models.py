from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class OAuthToken(Base):
    __tablename__ = 'oauth_tokens'
    
    id = Column(String, primary_key=True)
    user_id = Column(String)
    platform = Column(String)
    access_token = Column(String)
    refresh_token = Column(String)
    expires_at = Column(DateTime)
    scopes = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow) 