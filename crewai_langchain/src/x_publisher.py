import os
import yaml
import tweepy
import logging
from typing import Dict, Optional
from flask import session

logger = logging.getLogger(__name__)

class XPublisher:
    def __init__(self):
        self.consumer_key = os.getenv('X_CONSUMER_KEY')
        self.consumer_secret = os.getenv('X_CONSUMER_SECRET')
        self._client = None
        self._auth = None
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Charge la configuration depuis x.yaml"""
        try:
            with open('config/x.yaml', 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Erreur lors du chargement de la config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """Retourne la configuration par défaut"""
        return {
            "api": {
                "oauth": {
                    "callback_url": "http://127.0.0.1:5001/callback"
                }
            },
            "content": {
                "max_length": 280
            },
            "error_handling": {
                "max_retries": 3,
                "retry_delay": 5
            }
        }

    def _get_auth_handler(self):
        """Crée et retourne un gestionnaire OAuth"""
        if not all([self.consumer_key, self.consumer_secret]):
            raise ValueError("Clés d'API X manquantes dans les variables d'environnement")
        
        callback_url = self.config["api"]["oauth"]["callback_url"]
        return tweepy.OAuth1UserHandler(
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            callback=callback_url
        )

    def _validate_content(self, content: str) -> bool:
        """Valide le contenu selon les règles de X"""
        max_length = self.config["content"]["max_length"]
        if len(content) > max_length:
            raise ValueError(f"Contenu trop long (max {max_length} caractères)")
        return True

    def get_auth_url(self) -> Dict[str, str]:
        """Obtient l'URL d'authentification pour X"""
        try:
            self._auth = self._get_auth_handler()
            auth_url = self._auth.get_authorization_url()
            session['request_token'] = self._auth.request_token
            return {
                "status": "success",
                "auth_url": auth_url
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'obtention de l'URL d'auth: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    def handle_callback(self, oauth_verifier: str, request_token: Dict) -> Dict[str, str]:
        """Gère le callback OAuth et initialise le client"""
        try:
            self._auth = self._get_auth_handler()
            self._auth.request_token = request_token
            
            access_token, access_token_secret = self._auth.get_access_token(oauth_verifier)
            
            self._client = tweepy.Client(
                consumer_key=self.consumer_key,
                consumer_secret=self.consumer_secret,
                access_token=access_token,
                access_token_secret=access_token_secret
            )
            
            return {"status": "success"}
        except Exception as e:
            logger.error(f"Erreur lors du callback OAuth: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def publish_tweet(self, content: str) -> Dict[str, str]:
        """Publie un tweet et retourne son ID"""
        if not self._client:
            return {
                "status": "error",
                "error": "Client non initialisé. Authentification requise."
            }
            
        try:
            # Validation du contenu
            self._validate_content(content)
            
            response = self._client.create_tweet(text=content)
            tweet_id = response.data['id']
            tweet_url = f"https://twitter.com/user/status/{tweet_id}"
            
            logger.info(f"Tweet publié avec succès: {tweet_url}")
            return {
                "status": "success",
                "tweet_id": tweet_id,
                "tweet_url": tweet_url
            }
        except ValueError as ve:
            logger.error(f"Erreur de validation: {str(ve)}")
            return {
                "status": "error",
                "error": str(ve)
            }
        except Exception as e:
            logger.error(f"Erreur lors de la publication du tweet: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def delete_tweet(self, tweet_id: str) -> Dict[str, str]:
        """Supprime un tweet"""
        if not self._client:
            return {
                "status": "error",
                "error": "Client non initialisé. Authentification requise."
            }
            
        try:
            self._client.delete_tweet(tweet_id)
            logger.info(f"Tweet {tweet_id} supprimé avec succès")
            return {"status": "success"}
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du tweet: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            } 