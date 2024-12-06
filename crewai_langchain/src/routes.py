from fastapi import APIRouter, Depends, HTTPException
from .auth import OAuthManager
from .models import SocialPlatform

router = APIRouter()

@router.get("/auth/{platform}/connect")
async def connect_platform(platform: SocialPlatform, user_id: str):
    try:
        auth_url = await oauth_manager.get_auth_url(platform.value, user_id)
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/auth/{platform}/callback")
async def oauth_callback(platform: SocialPlatform, code: str, state: str):
    try:
        token = await oauth_manager.handle_callback(platform.value, code, state)
        return {"status": "success", "platform": platform.value}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 