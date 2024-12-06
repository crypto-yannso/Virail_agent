from typing import Dict, Any
from abc import ABC, abstractmethod
import logging
from .models import ContentOutput, PublishingSchedule, PlatformConfig
from .medium import MediumAPI
from .x import XAPI
import asyncio
from .auth.oauth_manager import OAuthManager

logger = logging.getLogger(__name__)

class SocialMediaPublisher(ABC):
    @abstractmethod
    async def publish(self, content: ContentOutput, metadata: Dict[str, Any]) -> bool:
        pass

class MediumPublisher(SocialMediaPublisher):
    def __init__(self, config: PlatformConfig):
        self.api = MediumAPI(config.credentials.dict())  # Convertit en dict
    
    async def publish(self, content: ContentOutput, metadata: Dict[str, Any]) -> bool:
        return await self.api.publish(content, metadata)

class XPublisher(SocialMediaPublisher):
    def __init__(self, config: PlatformConfig):
        self.api = XAPI(config.credentials.dict())
    
    async def publish(self, content: ContentOutput, metadata: Dict[str, Any]) -> bool:
        return await self.api.publish(content, metadata)

class PublisherFactory:
    @staticmethod
    def create_publisher(platform: str, config: PlatformConfig) -> SocialMediaPublisher:
        publishers = {
            "medium": MediumPublisher,
            "x": XPublisher,
        }
        
        if platform not in publishers:
            raise ValueError(f"Plateforme non supportée: {platform}")
            
        return publishers[platform](config)

class PublishingManager:
    def __init__(self, config: PlatformConfig, oauth_manager: OAuthManager):
        self.config = config
        self.oauth_manager = oauth_manager
    
    async def schedule_publish(self, content: ContentOutput, schedule: PublishingSchedule) -> bool:
        """Planifie et exécute la publication avec retry."""
        max_attempts = schedule.retry_strategy.get('max_attempts', 3)
        delay = schedule.retry_strategy.get('delay_between_attempts', 60)
        
        for attempt in range(max_attempts):
            try:
                success = await self.publish(content, content.metadata)
                if success:
                    return True
                    
                if attempt < max_attempts - 1:
                    logger.warning(f"Tentative {attempt + 1} échouée, nouvelle tentative dans {delay} secondes")
                    await asyncio.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Erreur lors de la tentative {attempt + 1}: {e}")
                if attempt < max_attempts - 1:
                    await asyncio.sleep(delay)
                    
        return False

    async def publish(self, content: ContentOutput, metadata: Dict[str, Any], user_id: str) -> bool:
        try:
            # Vérifie le token OAuth
            token = await self.oauth_manager.get_valid_token(
                user_id=user_id,
                platform=self.config.name.lower()
            )
            
            if not token:
                raise ValueError("Token d'authentification invalide ou expiré")
            
            # Met à jour les credentials avec le token OAuth
            credentials = {
                **self.config.credentials.dict(),
                "access_token": token.access_token
            }
            
            platform = self.config.name.lower()
            config_with_credentials = PlatformConfig(
                name=self.config.name,
                credentials=credentials,
                max_length=self.config.max_length,
                prompt_template=self.config.prompt_template,
                output_requirements=self.config.output_requirements,
                platform_specifics=self.config.platform_specifics
            )
            
            publisher = PublisherFactory.create_publisher(platform, config_with_credentials)
            return await publisher.publish(content, metadata)
        except Exception as e:
            logger.error(f"Erreur lors de la publication sur {platform}: {e}")
            return False