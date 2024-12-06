import aiohttp
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class MediumClient:
    def __init__(self):
        self.base_url = "https://api.medium.com/v1"
        self.integration_token: Optional[str] = None
        self.user_id: Optional[str] = None

    async def connect(self, integration_token: str) -> bool:
        """Connecte le client avec un integration token"""
        self.integration_token = integration_token
        return await self.validate_connection()

    async def validate_connection(self) -> bool:
        """Valide la connexion et récupère l'user_id"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.integration_token}"}
                async with session.get(f"{self.base_url}/me", headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.user_id = data["data"]["id"]
                        return True
                    return False
        except Exception as e:
            logger.error(f"Erreur de validation: {e}")
            return False

    async def create_post(self, title: str, content: str, tags: list[str], status: str = "draft") -> bool:
        """Crée un article sur Medium"""
        if not self.user_id or not self.integration_token:
            raise ValueError("Client non connecté")

        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.integration_token}"}
                data = {
                    "title": title,
                    "contentFormat": "markdown",
                    "content": content,
                    "tags": tags,
                    "publishStatus": status
                }

                url = f"{self.base_url}/users/{self.user_id}/posts"
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 201:
                        return True
                    logger.error(f"Erreur création article: {await response.text()}")
                    return False

        except Exception as e:
            logger.error(f"Erreur de création: {e}")
            return False 