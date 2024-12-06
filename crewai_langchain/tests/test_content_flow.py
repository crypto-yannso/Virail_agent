import os
import asyncio
import webbrowser
from aiohttp import web
from dotenv import load_dotenv
from datetime import datetime

from src.models.oauth import SocialPlatform
from src.auth.session_manager import SessionManager
from src.api.x_api import XApi
from src.content_generator import ContentGenerator

# Charger les variables d'environnement
load_dotenv()

# Variables globales pour stocker les données OAuth
request_token = None
oauth_verifier = None
oauth_event = None

async def handle_callback(request):
    """Gère le callback OAuth de X"""
    global oauth_verifier, oauth_event
    
    # Récupérer les paramètres
    oauth_verifier = request.query.get('oauth_verifier')
    
    # Notifier que nous avons reçu le callback
    oauth_event.set()
    
    return web.Response(text="Authentification réussie ! Vous pouvez fermer cette fenêtre.")

async def run_server():
    """Démarre le serveur web"""
    app = web.Application()
    app.router.add_get('/callback', handle_callback)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '127.0.0.1', 5000)
    await site.start()
    return runner

async def test_content_flow():
    """Test du flux complet : génération de contenu et publication"""
    global request_token, oauth_event
    
    try:
        print("\n=== Démarrage du test de flux complet ===")
        
        # 1. Génération du contenu
        print("\n1. Génération du contenu...")
        generator = ContentGenerator()
        topic = "L'impact de l'Intelligence Artificielle sur notre futur"
        content = generator.generate_social_content(
            topic=topic,
            tone="conversationnel et optimiste",
            max_length=280
        )
        print(f"\nContenu généré :\n{content}")
        
        # Demander confirmation à l'utilisateur
        response = input("\nVoulez-vous publier ce contenu sur X ? (o/n) : ")
        if response.lower() != 'o':
            print("Publication annulée.")
            return
            
        # 2. Publication sur X
        print("\n2. Configuration de la connexion X...")
        
        # Initialiser le gestionnaire de session
        session_manager = SessionManager()
        
        # Créer une instance de XApi
        x_api = XApi(session_manager)
        
        # Démarrer le serveur web
        runner = await run_server()
        
        # Créer un événement pour la synchronisation
        oauth_event = asyncio.Event()
        
        # Obtenir l'URL d'authentification
        auth_url, request_token = x_api.get_auth_url()
        print(f"\n3. Ouverture automatique de l'URL d'authentification...")
        webbrowser.open(auth_url)
        
        # Attendre le callback
        print("\n4. En attente de l'authentification...")
        await oauth_event.wait()
        
        # Gérer le callback
        access_token, access_token_secret = x_api.handle_callback(
            request_token['oauth_token'],
            oauth_verifier,
            request_token
        )
        print("\n✅ Authentification réussie !")
        
        # Publication du contenu
        print("\n5. Publication du contenu...")
        success = await x_api.post_tweet("test_user", content)
        
        if not success:
            raise Exception("La publication du tweet a échoué")
            
        print("\n✅ Tweet publié avec succès")
        print("\n=== Test terminé avec succès ! ===")
        
        # Arrêter le serveur
        await runner.cleanup()
        
    except Exception as e:
        print(f"\n❌ Erreur lors du test: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_content_flow()) 