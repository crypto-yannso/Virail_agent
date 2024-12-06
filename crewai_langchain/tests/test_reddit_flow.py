import os
import sys
import pytest
import asyncio
import webbrowser
from aiohttp import web
from dotenv import load_dotenv
from datetime import datetime

# Ajouter le chemin du package parent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.auth.session_manager import SessionManager
from src.api.reddit_api import RedditApi
from src.content_generator_reddit import RedditContentGenerator

# Charger les variables d'environnement
load_dotenv()

# Variables globales pour le callback OAuth
oauth_code = None
oauth_state = None
oauth_event = None

async def handle_callback(request):
    """Gère le callback OAuth de Reddit"""
    global oauth_code, oauth_state, oauth_event
    
    # Récupérer les paramètres
    oauth_code = request.query.get('code')
    oauth_state = request.query.get('state')
    
    # Notifier que nous avons reçu le callback
    oauth_event.set()
    
    return web.Response(text="Authentification réussie ! Vous pouvez fermer cette fenêtre.")

async def run_server():
    """Démarre le serveur web"""
    app = web.Application()
    app.router.add_get('/', handle_callback)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8090)
    await site.start()
    return runner

async def test_reddit_flow():
    """Test du flux complet : génération de contenu et publication sur Reddit"""
    try:
        print("\n=== Démarrage du test de flux Reddit ===")
        
        # 1. Initialisation des composants
        session_manager = SessionManager()
        reddit_api = RedditApi(session_manager)
        generator = RedditContentGenerator()
        
        # 2. Authentification Reddit
        print("\n1. Configuration de la connexion Reddit...")
        
        # Démarrer le serveur web
        runner = await run_server()
        
        # Créer un événement pour la synchronisation
        global oauth_event
        oauth_event = asyncio.Event()
        
        # Obtenir l'URL d'authentification
        auth_url, state = reddit_api.get_auth_url()
        print(f"\n2. Ouverture automatique de l'URL d'authentification...")
        webbrowser.open(auth_url)
        
        # Attendre le callback
        print("\n3. En attente de l'authentification...")
        await oauth_event.wait()
        
        # Gérer le callback
        result = reddit_api.handle_callback(oauth_code, oauth_state, state)
        assert result["status"] == "success", "Échec de l'authentification"
        print("\n✅ Authentification réussie !")
        
        # 3. Génération du contenu
        print("\n4. Génération du contenu...")
        task = "Créer un post sur l'impact de l'IA dans notre quotidien"
        parameters = {
            "tone": "conversationnel",
            "style": "informatif",
            "keywords": ["IA", "technologie", "futur"],
            "target_audience": "tech enthusiasts"
        }
        
        title, content = generator.generate_reddit_content(
            task=task,
            subreddit="Futurology",
            parameters=parameters
        )
        
        print(f"\nTitre généré : {title}")
        print(f"\nContenu généré : {content[:200]}...")
        
        # Ajouter un timestamp pour éviter les doublons
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = f"{content}\n\n---\nPublié le : {timestamp}"
        
        # 4. Publication sur Reddit
        print("\n5. Publication sur Reddit...")
        result = await reddit_api.create_post("test", title, content)
        
        assert result["status"] == "success", "Échec de la publication"
        post_id = result["post_id"]
        post_url = result["post_url"]
        
        print(f"\n✅ Post publié avec succès !")
        print(f"URL du post : {post_url}")
        
        # 5. Nettoyage - Suppression du post de test
        print("\n6. Nettoyage - Suppression du post...")
        delete_result = await reddit_api.delete_post(post_id)
        assert delete_result["status"] == "success", "Échec de la suppression"
        
        print("\n✅ Post supprimé avec succès")
        print("\n=== Test terminé avec succès ! ===")
        
        # Arrêter le serveur
        await runner.cleanup()
        
    except Exception as e:
        print(f"\n❌ Erreur lors du test : {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_reddit_flow()) 