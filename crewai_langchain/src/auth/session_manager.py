from typing import Optional, Dict
import random
import string
from datetime import datetime
from ..models.auth import OAuthToken, UserSession
from ..models.oauth import SocialPlatform

class TokenStore:
    def __init__(self):
        self._tokens: Dict[str, Dict[SocialPlatform, OAuthToken]] = {}
        
    async def store_token(self, token: OAuthToken) -> None:
        """Stocke un token pour un utilisateur et une plateforme"""
        if token.user_id not in self._tokens:
            self._tokens[token.user_id] = {}
        self._tokens[token.user_id][token.platform] = token
        
    async def get_valid_token(self, user_id: str, platform: SocialPlatform) -> Optional[OAuthToken]:
        """Récupère un token valide pour un utilisateur et une plateforme"""
        if user_id not in self._tokens or platform not in self._tokens[user_id]:
            return None
            
        token = self._tokens[user_id][platform]
        if token.expires_at <= datetime.now():
            return None
            
        return token

class SessionManager:
    def __init__(self):
        self.token_store = TokenStore()
        self._sessions: Dict[str, UserSession] = {}
        
    def generate_state(self, length: int = 32) -> str:
        """Génère un état aléatoire pour OAuth"""
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
