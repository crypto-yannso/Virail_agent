import aiohttp
import logging
from typing import Optional, Dict, Any
from .api.base import SocialMediaAPI
from .auth.session_manager import SessionManager
from .models import ContentOutput
from .models.auth import OAuthToken
from .models.oauth import SocialPlatform, UserProfile

logger = logging.getLogger(__name__)

class MediumAPI(SocialMediaAPI):
    def __init__(self, session_manager: SessionManager):
        super().__init__()
        self.session_manager = session_manager
        self.base_url = "https://api.medium.com/v1"
        
    async def _initialize_client(self) -> bool:
        """Initialise le client avec les credentials"""
        try:
            session = await self.session_manager.get_session(self.user_data["id"])
            if not session:
                return False
            return await self._validate_credentials()
        except Exception as e:
            logger.error(f"Erreur d'initialisation: {e}")
            return False
            
    async def _validate_credentials(self) -> bool:
        """Valide les credentials"""
        try:
            if not self.user_data or "id" not in self.user_data:
                return False
                
            token = await self.session_manager.token_store.get_valid_token(
                self.user_data["id"], 
                SocialPlatform.MEDIUM
            )
            if not token:
                return False
                
            headers = await self._get_headers(token)
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(f"{self.base_url}/me") as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Erreur de validation: {e}")
            return False
            
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
        """Authentifie un utilisateur sur Medium"""
        try:
            success = await self.session_manager.authenticate_platform(
                user_id=user_id,
                platform=SocialPlatform.MEDIUM,
                auth_data=auth_data
            )
            
            if not success:
                return False
                
            token = await self.session_manager.token_store.get_valid_token(
                user_id, 
                SocialPlatform.MEDIUM
            )
            if not token:
                return False
                
            user_info = await self._get_user_info(token)
            if user_info:
                self.user_data = user_info.get("data", {})
                return True
            return False
            
        except Exception as e:
            logger.error(f"Erreur lors de l'authentification: {e}")
            return False
    
    async def get_user_id(self) -> Optional[str]:
        """Récupère l'ID de l'utilisateur"""
        if not self.user_data:
            return None
        return self.user_data.get("id")
        
    async def publish_content(self, user_id: str, content: ContentOutput, metadata: Dict) -> bool:
        """Publie du contenu sur Medium"""
        try:
            session = await self.session_manager.get_session(user_id)
            if not session or not session.platforms.get(SocialPlatform.MEDIUM):
                raise ValueError("Utilisateur non authentifié sur Medium")
                
            token = await self.session_manager.token_store.get_valid_token(
                user_id, 
                SocialPlatform.MEDIUM
            )
            if not token:
                raise ValueError("Token expiré ou invalide")
                
            headers = await self._get_headers(token)
            
            post_data = {
                "title": metadata.get("title", "Sans titre"),
                "contentFormat": "markdown",
                "content": content.content,
                "tags": metadata.get("tags", []),
                "publishStatus": metadata.get("status", "draft"),
                "notifyFollowers": metadata.get("notify_followers", True)
            }
            
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.post(
                    f"{self.base_url}/users/{user_id}/posts", 
                    json=post_data
                ) as response:
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
            token = await self.session_manager.token_store.get_valid_token(
                user_id, 
                SocialPlatform.MEDIUM
            )
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

class VirailManager:
    def __init__(self, medium_api: MediumAPI):
        self.medium_api = medium_api

    async def authenticate_user(self, user_id: str, platform: SocialPlatform, auth_data: Dict) -> bool:
        return await self.medium_api.authenticate_user(user_id, auth_data)

    async def publish_content(self, user_id: str, content: ContentOutput, metadata: Dict) -> bool:
        return await self.medium_api.publish_content(user_id, content, metadata)

    async def get_user_publications(self, user_id: str) -> Optional[Dict]:
        return await self.medium_api.get_user_publications(user_id)