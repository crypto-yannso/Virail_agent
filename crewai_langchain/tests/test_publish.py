import asyncio
import sys
from pathlib import Path

# Ajout du chemin racine au PYTHONPATH
root_dir = Path(__file__).parent.parent.absolute()
sys.path.append(str(root_dir))

from src.main import VirailManager 
from src.models import UserInputs
from src.medium import MediumAPI
from datetime import datetime

async def test_autonomous_publishing():
    # Initialiser l'API Medium
    medium_api = await MediumAPI.initialize()
    if not medium_api:
        print("❌ Impossible d'initialiser l'API Medium")
        return
        
    manager = VirailManager(medium_api=medium_api)
    
    # Test avec Medium
    platform = "medium"
    task = "Write 20 words about AI trends in 2024"
    user_inputs = UserInputs(
        tone="professional", 
        style="technical",
        keywords=["AI", "trends", "2024", "machine learning"],
        target_audience="tech professionals",
        platform_params={
            "publication": "Towards Data Science",
            "tags": ["Artificial Intelligence", "Technology Trends"]
        }
    )

    try:
        print("Génération du contenu...")
        content = await manager.create_content(platform, task, user_inputs)
        
        print("\n=== Contenu Généré ===")
        print(content.content)
        print("\n=== Validation ===") 
        print(f"Format valide: {content.validation.format_valid}")
        print(f"Longueur valide: {content.validation.length_valid}")
        print(f"Mots-clés présents: {content.validation.keyword_presence}")
        
        if input("\nVoulez-vous publier ce contenu? (y/n): ").lower() == 'y':
            success = await manager.publish_content(
                platform=platform,
                content=content,
                metadata={
                    "scheduled_time": datetime.now(),
                    "tags": user_inputs.platform_params["tags"]
                }
            )
            print(f"Publication {'réussie' if success else 'échouée'}")
    except Exception as e:
        print(f"Erreur: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_autonomous_publishing())