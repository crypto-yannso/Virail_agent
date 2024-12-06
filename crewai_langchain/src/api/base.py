from abc import ABC, abstractmethod
from typing import Dict, Optional

class SocialMediaAPI(ABC):
    def __init__(self):
        self.headers = None
        self.user_data = None
    
    @abstractmethod
    async def _initialize_client(self) -> bool:
        pass
        
    @abstractmethod
    async def _validate_credentials(self) -> bool:
        pass
        
    @abstractmethod
    async def authenticate_user(self) -> bool:
        pass
        
    @abstractmethod
    async def get_user_id(self) -> str:
        pass