from typing import Dict, List, Tuple
import spacy
from textblob import TextBlob
from readability import Readability

class EnhancedContentValidator:
    def __init__(self):
        self.nlp = spacy.load("fr_core_news_sm")
        
    def validate_content(self, content: str, requirements: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        validations = {}
        
        # Analyse du ton
        if requirements.get("tone"):
            validations["tone"] = self._validate_tone(content, requirements["tone"])
        
        # Analyse de la lisibilité
        if requirements.get("readability"):
            validations["readability"] = self._validate_readability(content)
        
        # Validation des mots-clés
        if requirements.get("keywords"):
            validations["keywords"] = self._validate_keywords(
                content, 
                requirements["keywords"]
            )
        
        # Validation spécifique à la plateforme
        if requirements.get("platform_rules"):
            validations["platform"] = self._validate_platform_rules(
                content, 
                requirements["platform_rules"]
            )
        
        # Vérification globale
        is_valid = all(validations.values())
        
        return is_valid, validations
    
    def _validate_tone(self, content: str, expected_tone: str) -> bool:
        blob = TextBlob(content)
        sentiment = blob.sentiment.polarity
        
        tone_ranges = {
            "professional": (0.1, 0.5),
            "friendly": (0.3, 0.8),
            "formal": (-0.1, 0.3),
            "casual": (0.2, 0.7)
        }
        
        if expected_tone in tone_ranges:
            min_val, max_val = tone_ranges[expected_tone]
            return min_val <= sentiment <= max_val
        return True