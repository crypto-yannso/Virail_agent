from langchain_openai import ChatOpenAI
from crewai import Agent, Task, Crew, Process
from typing import Dict, List, Tuple

class RedditContentGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7
        )
        
    def generate_reddit_content(self, task: str, subreddit: str, parameters: Dict) -> Tuple[str, str]:
        """Génère du contenu pour Reddit avec CrewAI"""
        
        # Créer les agents
        title_writer = Agent(
            role='Rédacteur de Titres Reddit',
            goal='Créer des titres accrocheurs et pertinents pour Reddit',
            backstory="""Expert en création de titres viraux pour Reddit.
            Vous savez comment créer des titres qui attirent l'attention tout en
            respectant les règles de chaque subreddit.""",
            llm=self.llm,
            verbose=True
        )
        
        content_writer = Agent(
            role='Rédacteur de Contenu Reddit',
            goal='Créer du contenu détaillé et engageant pour Reddit',
            backstory="""Expert en rédaction de posts Reddit.
            Vous savez comment structurer le contenu, utiliser le formatage Markdown,
            et encourager les discussions constructives.""",
            llm=self.llm,
            verbose=True
        )
        
        editor = Agent(
            role='Éditeur Reddit',
            goal='Optimiser et affiner le contenu pour maximiser l\'impact',
            backstory="""Éditeur expérimenté spécialisé dans l'optimisation de contenu
            pour Reddit. Vous connaissez les meilleures pratiques de chaque subreddit
            et savez comment maximiser l'engagement.""",
            llm=self.llm,
            verbose=True
        )
        
        # Créer les tâches
        title_task = Task(
            description=f"""
            Créer un titre accrocheur pour r/{subreddit}
            
            Consignes :
            - Ton : {parameters.get('tone', 'neutre')}
            - Mots-clés : {parameters.get('keywords', [])}
            - Public cible : {parameters.get('target_audience', 'général')}
            - Longueur maximale : 300 caractères
            - Le titre doit être clair et informatif
            - Éviter le clickbait excessif
            
            Sujet : {task}
            """,
            agent=title_writer,
            expected_output="Un titre optimisé pour Reddit"
        )
        
        content_task = Task(
            description=f"""
            Créer le contenu détaillé du post pour r/{subreddit}
            
            Consignes :
            - Style : {parameters.get('style', 'informatif')}
            - Ton : {parameters.get('tone', 'neutre')}
            - Mots-clés : {parameters.get('keywords', [])}
            - Public cible : {parameters.get('target_audience', 'général')}
            - Utiliser le formatage Markdown approprié
            - Structurer le contenu de manière claire
            - Inclure des sources si pertinent
            - Encourager la discussion
            
            Sujet : {task}
            """,
            agent=content_writer,
            expected_output="Un post Reddit détaillé et formaté"
        )
        
        editing_task = Task(
            description=f"""
            Optimiser le titre et le contenu pour r/{subreddit}
            
            Consignes :
            - Vérifier la cohérence entre le titre et le contenu
            - Optimiser le formatage Markdown
            - Vérifier le respect des règles du subreddit
            - Maximiser le potentiel d'engagement
            - S'assurer que les mots-clés sont bien intégrés
            - Vérifier le ton et le style
            
            Subreddit : r/{subreddit}
            """,
            agent=editor,
            expected_output="Un post Reddit final optimisé"
        )
        
        # Créer et exécuter le crew
        crew = Crew(
            agents=[title_writer, content_writer, editor],
            tasks=[title_task, content_task, editing_task],
            process=Process.sequential,
            verbose=True
        )
        
        try:
            # Obtenir le résultat de l'agent
            result = crew.kickoff()
            
            # Convertir CrewOutput en string avant de le split
            result_str = str(result)
            
            # Maintenant on peut faire le split
            parts = result_str.split("\n\n")
            
            # Extraire le titre et le contenu du résultat
            # Le format attendu est : "TITRE: [titre]\n\nCONTENU: [contenu]"
            title = parts[0].replace("TITRE: ", "").strip()
            content = parts[1].replace("CONTENU: ", "").strip()
            return title, content
        except Exception as e:
            raise ValueError(f"Format de sortie invalide : {str(e)}") 