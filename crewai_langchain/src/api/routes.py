from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import OAuth2AuthorizationCodeBearer
from ..auth.oauth_manager import OAuthManager
from ..database.manager import DatabaseManager
from typing import Optional
import jwt

router = APIRouter()
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="auth/login",
    tokenUrl="auth/token"
)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Optional[str]:
    try:
        payload = jwt.decode(token, "your-secret-key", algorithms=["HS256"])
        return payload.get("sub")
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Token invalide"
        )

@router.get("/auth/{platform}/connect")
async def connect_platform(
    platform: str,
    current_user: str = Depends(get_current_user)
):
    try:
        auth_url = await oauth_manager.get_auth_url(platform, current_user)
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{platform}/callback")
async def oauth_callback(
    platform: SocialPlatform,
    code: str,
    state: str
):
    token = await oauth_manager.handle_callback(platform, code, state)
    return {"status": "success", "platform": platform} 