import pytest
from crewai_langchain.src.main import VirailManager
from crewai_langchain.src.models import UserInputs
from flask import Flask, session
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration de Flask pour les tests
app = Flask(__name__)
app.secret_key = 'test_secret_key'

@pytest.mark.asyncio
async def test_complete_x_flow():
    """Test le flux complet de génération et publication sur X"""
    
    with app.test_request_context():
        logger.info("=== Démarrage du test de flux X ===")
        
        # Initialisation du manager
        manager = VirailManager()
        
        try:
            # Étape 1: Authentification X
            logger.info("Étape 1: Test de l'authentification X")
            auth_result = manager.get_x_auth_url()
            assert auth_result["status"] == "success", "Échec de l'obtention de l'URL d'auth"
            assert "auth_url" in auth_result, "URL d'auth manquante"
            
            # Simulation du callback OAuth
            request_token = session.get('request_token')
            assert request_token, "Token de requête manquant"
            
            callback_result = manager.handle_x_callback("fake_verifier", request_token)
            assert callback_result["status"] == "success", "Échec du callback OAuth"
            
            # Étape 2: Génération du contenu
            logger.info("Étape 2: Génération du contenu")
            task = "Créer un tweet engageant sur les dernières tendances en IA"
            user_inputs = UserInputs(
                tone="conversationnel",
                style="informatif",
                keywords=["IA", "innovation", "tech"],
                target_audience="tech enthusiasts"
            )
            
            content = await manager.create_content(task, user_inputs)
            assert content is not None, "Échec de la génération de contenu"
            assert content.content, "Contenu généré vide"
            
            # Vérification du contenu
            assert len(content.content) <= 280, "Contenu trop long pour X"
            assert any(keyword.lower() in content.content.lower() 
                      for keyword in user_inputs.keywords), "Mots-clés manquants"
            
            # Étape 3: Publication sur X
            logger.info("Étape 3: Publication sur X")
            publish_result = await manager.publish_to_x(content.content)
            assert publish_result["status"] == "success", "Échec de la publication"
            assert "tweet_id" in publish_result, "ID du tweet manquant"
            assert "tweet_url" in publish_result, "URL du tweet manquante"
            
            tweet_id = publish_result["tweet_id"]
            logger.info(f"Tweet publié: {publish_result['tweet_url']}")
            
            # Étape 4: Suppression du tweet de test
            logger.info("Étape 4: Nettoyage - Suppression du tweet")
            delete_result = await manager.delete_from_x(tweet_id)
            assert delete_result["status"] == "success", "Échec de la suppression"
            
            logger.info("=== Test de flux X terminé avec succès ===")
            
        except Exception as e:
            logger.error(f"Test échoué: {str(e)}")
            raise