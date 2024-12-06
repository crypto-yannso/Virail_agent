import tweepy
from typing import Dict, Any
import logging
from .models import ContentOutput, PostStats
from .api import SocialMediaAPI

logger = logging.getLogger(__name__)

class XAPI(SocialMediaAPI):
    def _validate_credentials(self) -> None:
        """Valide que les identifiants requis pour l'API X sont présents."""
        required = [
            'integration_token',
            'api_key_secret',
            'access_token',
            'access_token_secret'
        ]
        missing = [cred for cred in required if cred not in self.credentials]
        if missing:
            raise ValueError(f"Identifiants manquants pour X: {missing}")
    
    def _initialize_client(self) -> None:
        auth = tweepy.OAuthHandler(
            self.credentials['integration_token'],
            self.credentials['api_key_secret']
        )
        auth.set_access_token(
            self.credentials['access_token'],
            self.credentials['access_token_secret']
        )
        self.client = tweepy.Client(auth)
    
    async def publish(self, content: ContentOutput, metadata: Dict[str, Any]) -> bool:
        try:
            tweet = self.client.create_tweet(
                text=content.content,
                media_ids=metadata.get('media_ids', [])
            )
            return bool(tweet.id)
        except Exception as e:
            logger.error(f"Erreur lors de la publication sur X: {e}")
            return False

    async def get_post_stats(self, post_id: str) -> PostStats:
        try:
            tweet = self.client.get_tweet(post_id, tweet_fields=['public_metrics'])
            metrics = tweet.data.public_metrics
            return PostStats(
                views=metrics.get('impression_count', 0),
                likes=metrics.get('like_count', 0),
                comments=metrics.get('reply_count', 0)
            )
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des stats: {e}")
            return PostStats() 