from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging
from typing import Optional, Dict
from pathlib import Path
from .models import Base, OAuthToken
import uuid

class DatabaseManager:
    def __init__(self, db_url: str = None):
        if db_url is None:
            data_dir = Path(__file__).parent.parent.parent / "data"
            data_dir.mkdir(exist_ok=True)
            db_url = f"sqlite:///{data_dir}/oauth.db"
        
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.logger = logging.getLogger(__name__)

    async def save_token(self, user_id: str, platform: str, token_data: Dict) -> bool:
        session = self.Session()
        try:
            token = OAuthToken(
                id=str(uuid.uuid4()),
                user_id=user_id,
                platform=platform,
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token"),
                expires_at=token_data["expires_at"],
                scopes=",".join(token_data["scopes"])
            )
            session.add(token)
            session.commit()
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde du token: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    async def get_token(self, user_id: str, platform: str) -> Optional[Dict]:
        session = self.Session()
        try:
            token = session.query(OAuthToken).filter_by(
                user_id=user_id,
                platform=platform
            ).first()
            
            if token:
                return {
                    "access_token": token.access_token,
                    "refresh_token": token.refresh_token,
                    "expires_at": token.expires_at,
                    "scopes": token.scopes.split(",")
                }
            return None
        finally:
            session.close() 