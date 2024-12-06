import os
import sys
import asyncio
import webbrowser
from aiohttp import web
from dotenv import load_dotenv
from datetime import datetime

# Ajouter le chemin du package parent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

async def test_full_flow():
    """Test du flux complet : génération de contenu et publication sur X"""
    try:
        print("\n=== Démarrage du test de flux complet ===")
        
        # 1. Initialisation des composants
        session_manager = SessionManager()
        x_api = XApi(session_manager)
        generator = ContentGenerator()
        
        # 2. Génération du contenu
        print("\n1. Génération du contenu...")
        topic = "L'impact de l'Intelligence Artificielle sur notre quotidien"
        content = generator.generate_social_content(
            topic=topic,
            tone="conversationnel et optimiste",
            max_length=280
        )
        print(f"\nContenu généré :\n{content}")
        
        # 3. Ajout d'un timestamp pour éviter les doublons
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = f"{content}\n\nPublié le : {timestamp}"
        
        # 4. Authentification sur X
        print("\n2. Configuration de la connexion X...")
        
        # Démarrer le serveur web
        runner = await run_server()
        
        # Créer un événement pour la synchronisation
        global oauth_event
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
        
        # 5. Publication sur X
        print("\n5. Publication du contenu...")
        success = await x_api.post_tweet("test_user", content)
        
        if success:
            print("\n✅ Tweet publié avec succès !")
        else:
            print("\n❌ Erreur lors de la publication du tweet")
            
        print("\n=== Test terminé ===")
        
        # Arrêter le serveur
        await runner.cleanup()
        
    except Exception as e:
        print(f"\n❌ Erreur lors du test : {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_full_flow()) 