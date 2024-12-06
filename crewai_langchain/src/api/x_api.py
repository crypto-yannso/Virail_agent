import logging
import os
import tweepy
from typing import Optional, Dict, Any, Tuple
from ..auth.session_manager import SessionManager
from ..models.oauth import SocialPlatform

logger = logging.getLogger(__name__)

class XApi:
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
        self.client = None
        self.auth = None
        self._init_auth()
        
    def _init_auth(self):
        """Initialise l'authentification OAuth"""
        try:
            self.auth = tweepy.OAuth1UserHandler(
                os.getenv("X_CONSUMER_KEY"),
                os.getenv("X_CONSUMER_SECRET"),
                callback="http://127.0.0.1:5000/callback"
            )
            logger.info("Authentification X initialisée avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de l'auth X : {str(e)}")
            raise
            
    def get_auth_url(self) -> Tuple[str, Dict]:
        """Obtient l'URL d'authentification et le request token"""
        try:
            auth_url = self.auth.get_authorization_url()
            request_token = self.auth.request_token
            logger.info(f"URL d'authentification générée : {auth_url}")
            return auth_url, request_token
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de l'URL d'auth : {str(e)}")
            raise
            
    def handle_callback(self, oauth_token: str, oauth_verifier: str, request_token: Dict) -> Tuple[str, str]:
        """Gère le callback OAuth et retourne les tokens d'accès"""
        try:
            # Restaurer le request token
            self.auth.request_token = request_token
            
            # Obtenir les tokens d'accès
            access_token, access_token_secret = self.auth.get_access_token(oauth_verifier)
            
            # Initialiser le client avec les tokens obtenus
            self.client = tweepy.Client(
                consumer_key=os.getenv("X_CONSUMER_KEY"),
                consumer_secret=os.getenv("X_CONSUMER_SECRET"),
                access_token=access_token,
                access_token_secret=access_token_secret,
                wait_on_rate_limit=True
            )
            
            logger.info("Tokens d'accès obtenus avec succès")
            return access_token, access_token_secret
            
        except Exception as e:
            logger.error(f"Erreur lors de la gestion du callback : {str(e)}")
            raise
        
    async def post_tweet(self, user_id: str, content: str) -> bool:
        """Publie un tweet"""
        try:
            if not self.client:
                logger.error("Client X non initialisé - authentification requise")
                return False
                
            # Vérification de la longueur du tweet
            if len(content) > 280:
                logger.error("Tweet trop long (max 280 caractères)")
                return False
                
            # Publication du tweet
            response = self.client.create_tweet(text=content)
            tweet_id = response.data['id']
            logger.info(f"Tweet publié avec succès (ID: {tweet_id})")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la publication du tweet : {str(e)}")
            return False
            
    async def delete_tweet(self, tweet_id: str) -> bool:
        """Supprime un tweet"""
        try:
            if not self.client:
                logger.error("Client X non initialisé - authentification requise")
                return False
                
            self.client.delete_tweet(tweet_id)
            logger.info(f"Tweet {tweet_id} supprimé avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du tweet : {str(e)}")
            return False