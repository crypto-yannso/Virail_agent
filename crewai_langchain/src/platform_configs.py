from typing import Dict, Any

PLATFORM_CONFIGS: Dict[str, Dict[str, Any]] = {
    "reddit_writer": {
        "name": "Reddit",
        "max_length": 40000,
        "prompt_template": """Tu es un expert en rédaction pour Reddit.
        
        Contexte:
        - Subreddit: {target_audience}
        - Style: {style}
        - Mots-clés: {keywords}
        - Tâche: {task}
        
        Instructions spécifiques:
        1. Respecte le format Markdown de Reddit
        2. Adapte le ton au subreddit
        3. Encourage la discussion
        """,
        "output_requirements": {
            "tone_match": True,
            "keyword_presence": True,
            "length_valid": True
        },
        "platform_specifics": {
            "supports_formatting": True,
            "supports_media": True,
            "allowed_media_types": ["image", "video", "link"],
            "special_features": {
                "markdown_support": True,
                "flair_support": True
            },
            "rate_limits": {
                "posts_per_day": 50
            }
        }
    }
    # Ajoutez d'autres plateformes ici
}