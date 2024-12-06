from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from .models import ContentOutput

class SocialMediaAPI(ABC):
    def __init__(self, api_credentials: Dict[str, str]):
        self.credentials = api_credentials
        self._validate_credentials()
        self._initialize_client()
    
    @abstractmethod
    def _validate_credentials(self) -> None:
        pass
    
    @abstractmethod
    def _initialize_client(self) -> None:
        pass
    
    @abstractmethod
    async def publish(self, content: ContentOutput, metadata: Dict[str, Any]) -> bool:
        pass
    
    @abstractmethod
    async def get_post_stats(self, post_id: str) -> Dict[str, Any]:
        pass