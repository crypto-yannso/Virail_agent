import logging
import os
import socket
from typing import Dict, Optional, Tuple
from praw import Reddit
from dotenv import load_dotenv
from ..auth.session_manager import SessionManager
from ..models.oauth import SocialPlatform

logger = logging.getLogger(__name__)

class RedditApi:
    def __init__(self, session_manager: SessionManager):
        load_dotenv()
        self.session_manager = session_manager
        self.client = None
        self.redirect_uri = "http://localhost:8080"
        self._init_client()
        
    def _init_client(self):
        """Initialise le client Reddit"""
        try:
            self.client = Reddit(
                client_id=os.getenv("REDDIT_CLIENT_ID"),
                client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                redirect_uri=self.redirect_uri,
                user_agent=os.getenv("REDDIT_USER_AGENT")
            )
            logger.info("Client Reddit initialisé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du client Reddit : {str(e)}")
            raise
            
    def get_auth_url(self) -> Tuple[str, Dict]:
        """Obtient l'URL d'authentification et le state"""
        try:
            scopes = ['identity', 'submit', 'read', 'edit', 'history']
            state = self.session_manager.generate_state()
            auth_url = self.client.auth.url(scopes, state, 'permanent')
            
            logger.info(f"URL d'authentification générée : {auth_url}")
            return auth_url, {"state": state}
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de l'URL d'auth : {str(e)}")
            raise
            
    def handle_callback(self, code: str, state: str, stored_state: Dict) -> Dict[str, str]:
        """Gère le callback OAuth"""
        try:
            if state != stored_state["state"]:
                raise ValueError("État invalide - possible tentative de CSRF")
                
            refresh_token = self.client.auth.authorize(code)
            
            logger.info("Authentification Reddit réussie")
            return {
                "status": "success",
                "refresh_token": refresh_token
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la gestion du callback : {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
            
    async def create_post(self, subreddit: str, title: str, content: str, flair_id: Optional[str] = None) -> Dict[str, str]:
        """Crée un nouveau post Reddit"""
        try:
            if not self.client:
                raise ValueError("Client Reddit non initialisé")
                
            # Nettoyer le nom du subreddit
            subreddit = subreddit.replace('r/', '')
            
            # Créer le post
            submission = self.client.subreddit(subreddit).submit(
                title=title,
                selftext=content,
                flair_id=flair_id
            )
            
            logger.info(f"Post créé avec succès dans r/{subreddit}")
            return {
                "status": "success",
                "post_id": submission.id,
                "post_url": submission.url
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du post : {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
            
    async def delete_post(self, post_id: str) -> Dict[str, str]:
        """Supprime un post Reddit"""
        try:
            if not self.client:
                raise ValueError("Client Reddit non initialisé")
                
            submission = self.client.submission(id=post_id)
            submission.delete()
            
            logger.info(f"Post {post_id} supprimé avec succès")
            return {
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du post : {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
            
    def get_subreddit_flairs(self, subreddit: str) -> list:
        """Récupère les flairs disponibles pour un subreddit"""
        try:
            subreddit_obj = self.client.subreddit(subreddit)
            return list(subreddit_obj.flair.link_templates.user_selectable())
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des flairs : {str(e)}")
            return [] 