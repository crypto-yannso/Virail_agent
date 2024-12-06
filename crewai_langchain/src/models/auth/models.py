from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Optional
from ..oauth import SocialPlatform

class OAuthToken(BaseModel):
    platform: SocialPlatform
    access_token: str
    refresh_token: Optional[str]
    expires_at: datetime
    scopes: list[str] = []
    user_id: str
    platform_user_id: Optional[str] = None

class UserSession(BaseModel):
    user_id: str
    created_at: datetime = datetime.now()
    last_activity: datetime = datetime.now()
    platforms: Dict[SocialPlatform, bool] = {}