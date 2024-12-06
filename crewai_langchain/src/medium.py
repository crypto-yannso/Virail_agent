import aiohttp
import logging
from typing import Optional, Dict, Any
from .api.base import SocialMediaAPI
from .auth.session_manager import SessionManager
from .models import ContentOutput
from .auth.medium_auth import MediumAuthManager

logger = logging.getLogger(__name__)

class MediumAPI(SocialMediaAPI):
    def __init__(self, session_manager: SessionManager):
        super().__init__()
        self.session_manager = session_manager
        self.auth_manager = MediumAuthManager()
        self.base_url = "https://api.medium.com/v1"
        
    async def _get_headers(self, token: OAuthToken) -> Dict:
        """Génère les headers pour les requêtes API"""
        return {
            "Authorization": f"Bearer {token.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def _get_user_info(self, token: OAuthToken) -> Optional[Dict]:
        """Récupère les informations de l'utilisateur"""
        try:
            headers = await self._get_headers(token)
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(f"{self.base_url}/me") as response:
                    if response.status == 200:
                        return await response.json()
                    logger.error(f"Erreur récupération user info: {await response.text()}")
                    return None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération user info: {e}")
            return None
    
    async def authenticate_user(self, user_id: str, auth_data: Dict) -> bool:
        """Authentifie un utilisateur via OAuth"""
        try:
            success = await self.session_manager.authenticate_platform(
                user_id=user_id,
                platform="medium",
                auth_data=auth_data
            )
            
            if success:
                token = await self.session_manager.get_valid_token(user_id, "medium")
                if token:
                    return bool(await self._get_user_info(token))
            return False
            
        except Exception as e:
            logger.error(f"Erreur d'authentification: {e}")
            return False
    
    async def get_user_id(self, token: OAuthToken) -> Optional[str]:
        """Récupère l'ID de l'utilisateur"""
        user_info = await self._get_user_info(token)
        if user_info:
            return user_info.get("data", {}).get("id")
        return None
        
    async def publish_content(self, user_id: str, content: ContentOutput, metadata: Dict) -> bool:
        """Publie du contenu sur Medium"""
        try:
            # Vérifie la session
            session = await self.session_manager.get_session(user_id)
            if not session or not session.platforms.get("medium"):
                raise ValueError("Utilisateur non authentifié sur Medium")
                
            # Récupère le token
            token = await self.session_manager.token_store.get_valid_token(user_id, "medium")
            if not token:
                raise ValueError("Token expiré ou invalide")
                
            headers = await self._get_headers(token)
            
            # Prépare les données pour la publication
            post_data = {
                "title": metadata.get("title", "Sans titre"),
                "contentFormat": "markdown",
                "content": content.content,
                "tags": metadata.get("tags", []),
                "publishStatus": metadata.get("status", "draft")
            }
            
            # Publie sur Medium
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.post(f"{self.base_url}/users/{user_id}/posts", json=post_data) as response:
                    if response.status == 201:
                        return True
                    logger.error(f"Erreur de publication: {await response.text()}")
                    return False
                    
        except Exception as e:
            logger.error(f"Erreur lors de la publication: {e}")
            return False
            
    async def get_user_publications(self, user_id: str) -> Optional[Dict]:
        """Récupère les publications de l'utilisateur"""
        try:
            token = await self.session_manager.token_store.get_valid_token(user_id, "medium")
            if not token:
                raise ValueError("Token invalide")
                
            headers = await self._get_headers(token)
            
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(f"{self.base_url}/users/{user_id}/publications") as response:
                    if response.status == 200:
                        return await response.json()
                    logger.error(f"Erreur récupération publications: {await response.text()}")
                    return None
                    
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des publications: {e}")
            return None