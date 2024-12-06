import asyncio
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent.absolute()
sys.path.append(str(root_dir))

from src.database.manager import DatabaseManager
from src.auth.oauth_manager import OAuthManager
from datetime import datetime, timedelta

async def test_oauth_connection():
    # Initialisation
    db_manager = DatabaseManager()
    oauth_manager = OAuthManager(db_manager)
    
    # Test avec Medium
    platform = "medium"
    user_id = "test_user_123"
    
    try:
        # Simuler un token pour le test
        test_token = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_at": datetime.utcnow() + timedelta(hours=1),
            "scopes": ["basicProfile", "publishPost"]
        }
        
        # Sauvegarder le token
        success = await db_manager.save_token(user_id, platform, test_token)
        print(f"\nToken sauvegardé: {success}")
        
        # Vérifier le token
        token = await oauth_manager.get_valid_token(user_id, platform)
        print(f"Token récupéré: {token is not None}")
        
    except Exception as e:
        print(f"Erreur: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_oauth_connection()) 