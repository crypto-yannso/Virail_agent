from abc import ABC, abstractmethod
from typing import Dict, Any
from .models import ContentOutput, PostStats

class SocialMediaAPI(ABC):
    def __init__(self, credentials: Dict[str, str]):
        self.credentials = credentials
        self._validate_credentials()
        self._initialize_client()
    
    @abstractmethod
    def _validate_credentials(self) -> None:
        """Valide les identifiants requis pour l'API."""
        pass
    
    @abstractmethod
    def _initialize_client(self) -> None:
        """Initialise le client API."""
        pass
    
    @abstractmethod
    async def publish(self, content: ContentOutput, metadata: Dict[str, Any]) -> bool:
        """Publie le contenu sur la plateforme."""
        pass
    
    @abstractmethod
    async def get_post_stats(self, post_id: str) -> PostStats:
        """Récupère les statistiques d'un post."""
        pass 