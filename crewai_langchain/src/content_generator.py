import os
from langchain_openai import ChatOpenAI
from crewai import Agent, Task, Crew, Process
from typing import Dict, List

class ContentGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7
        )
        
    def generate_social_content(self, topic: str, tone: str = "professionnel", max_length: int = 280) -> str:
        """Génère du contenu pour les réseaux sociaux avec CrewAI"""
        
        # Créer les agents
        writer = Agent(
            role='Rédacteur Social Media',
            goal='Créer du contenu engageant et viral pour les réseaux sociaux',
            backstory="""Expert en création de contenu viral pour les réseaux sociaux.
            Vous savez comment créer des messages qui génèrent de l'engagement tout en
            restant pertinents et informatifs.""",
            llm=self.llm,
            verbose=True
        )
        
        editor = Agent(
            role='Éditeur Social Media',
            goal='Optimiser et affiner le contenu pour maximiser l\'impact',
            backstory="""Éditeur expérimenté spécialisé dans l'optimisation de contenu
            pour les réseaux sociaux. Vous savez comment rendre un message plus percutant
            tout en respectant les contraintes de longueur.""",
            llm=self.llm,
            verbose=True
        )
        
        # Créer les tâches
        writing_task = Task(
            description=f"""
            Créer un post pour X (Twitter) sur le sujet : {topic}
            
            Consignes :
            - Ton : {tone}
            - Longueur maximale : {max_length} caractères
            - Inclure des emojis pertinents
            - Utiliser des hashtags appropriés
            - Le message doit être engageant et encourager l'interaction
            """,
            agent=writer,
            expected_output="Un tweet engageant et optimisé"
        )
        
        editing_task = Task(
            description=f"""
            Optimiser le post X (Twitter) pour maximiser son impact.
            
            Consignes :
            - Vérifier que la longueur ne dépasse pas {max_length} caractères
            - Améliorer le choix des mots pour plus d'impact
            - Optimiser le placement des emojis et hashtags
            - S'assurer que le ton correspond à : {tone}
            """,
            agent=editor,
            expected_output="Un tweet final optimisé prêt à être publié"
        )
        
        # Créer et exécuter le crew
        crew = Crew(
            agents=[writer, editor],
            tasks=[writing_task, editing_task],
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff()
        return result 