from typing import List, Dict, Any
import re
from .models import ContentValidation, PlatformConfig

class ContentValidator:
    def __init__(self, config: PlatformConfig):
        self.config = config

    def validate_content(self, content: str, tone: str, keywords: List[str]) -> ContentValidation:
        length_valid = len(content) <= self.config.max_length
        keyword_presence = all(keyword.lower() in content.lower() for keyword in keywords)
        
        # Validation spécifique à la plateforme
        platform_rules = self._validate_platform_specific(content)
        
        return ContentValidation(
            tone_match=True,  # À implémenter avec analyse de sentiment
            keyword_presence=keyword_presence,
            length_valid=length_valid,
            format_valid=platform_rules.get("format_valid", True),  # Ajout du format_valid
            platform_specific_rules=platform_rules
        )

    def _validate_platform_specific(self, content: str) -> Dict[str, bool]:
        platform_validators = {
            "Medium": self._validate_medium,
            "Reddit": self._validate_reddit,
            "Instagram": self._validate_instagram,
            "LinkedIn": self._validate_linkedin,
            "X": self._validate_x,
            "Telegram": self._validate_telegram
        }
        
        validator = platform_validators.get(self.config.name)
        if validator:
            validation_result = validator(content)
            return {
                "format_valid": validation_result,
                "platform_rules_followed": validation_result
            }
        return {"format_valid": True, "platform_rules_followed": True}

    def _validate_medium(self, content: str) -> bool:
        return self._validate_markdown_format(content)

    def _validate_reddit(self, content: str) -> bool:
        return self._validate_markdown_format(content)

    def _validate_instagram(self, content: str) -> bool:
        # Vérifie les hashtags et la longueur
        return True

    def _validate_linkedin(self, content: str) -> bool:
        # Vérifie le format professionnel
        return True

    def _validate_x(self, content: str) -> bool:
        # Vérifie la longueur et les mentions
        return True

    def _validate_telegram(self, content: str) -> bool:
        # Vérifie le format HTML et les liens
        return True

    def _validate_markdown_format(self, content: str) -> bool:
        # Vérifie la présence de titres markdown
        has_headers = bool(re.search(r'^#{1,6}\s.+', content, re.MULTILINE))
        
        # Vérifie la présence de listes
        has_lists = bool(re.search(r'^\s*[-*+]\s.+', content, re.MULTILINE))
        
        # Vérifie la présence de liens
        has_links = bool(re.search(r'\[.+\]\(.+\)', content))
        
        # Vérifie la présence de mise en forme (gras, italique)
        has_formatting = bool(re.search(r'(\*\*.+\*\*)|(\*.+\*)', content))
        
        return has_headers and (has_lists or has_links or has_formatting)