from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import logging
import re
from .models import ContentAnalysis, PerformanceMetrics, PlatformConfig
from langchain_community.callbacks.utils import import_textstat

logger = logging.getLogger(__name__)

class ContentAnalyzer:
    def __init__(self, config: PlatformConfig):
        self.config = config

    async def analyze_content(self, content: str) -> ContentAnalysis:
        try:
            return ContentAnalysis(
                topic_relevance=self._analyze_topic_relevance(content),
                sentiment_analysis=self._analyze_sentiment(content),
                readability_score=self._calculate_readability(content),
                keyword_density=self._analyze_keywords(content),
                content_quality_score=self._calculate_quality_score(content),
                viral_potential=self._predict_viral_potential(content)
            )
        except Exception as e:
            logger.error(f"Error analyzing content: {e}")
            raise

    def _analyze_topic_relevance(self, content: str) -> Dict[str, float]:
        # Analyse basique des thèmes
        topics = {
            "technology": 0.0,
            "business": 0.0,
            "science": 0.0
        }
        words = content.lower().split()
        
        for word in words:
            if word in ["ai", "technology", "software"]:
                topics["technology"] += 0.1
            elif word in ["business", "market", "industry"]:
                topics["business"] += 0.1
            elif word in ["research", "study", "discovery"]:
                topics["science"] += 0.1

        return {k: min(v, 1.0) for k, v in topics.items()}

    def _analyze_sentiment(self, content: str) -> Dict[str, float]:
        # Analyse simplifiée des sentiments
        return {
            "positive": 0.7,
            "neutral": 0.2,
            "negative": 0.1
        }

    def _calculate_readability(self, content: str) -> float:
        textstat = import_textstat()
        # Retourne un score normalisé entre 0 et 1
        flesch_score = textstat.flesch_reading_ease(content)
        # Normalisation du score Flesch (qui va de 0 à 100)
        return max(0.0, min(1.0, flesch_score / 100))

    def _analyze_keywords(self, content: str) -> Dict[str, float]:
        words = content.lower().split()
        word_count = {}
        for word in words:
            if len(word) > 3:  # Ignore les mots courts
                word_count[word] = word_count.get(word, 0) + 1
        total_words = len(words)
        return {k: v/total_words for k, v in word_count.items()}

    def _calculate_quality_score(self, content: str) -> float:
        # Score basé sur plusieurs facteurs
        factors = {
            "length": min(1.0, len(content) / 1000),
            "formatting": 0.8 if re.search(r'#{1,6}\s.+', content) else 0.4,
            "links": 0.7 if re.search(r'\[.+\]\(.+\)', content) else 0.3
        }
        return sum(factors.values()) / len(factors)

    def _predict_viral_potential(self, content: str) -> float:
        # Prédiction simplifiée
        return 0.6

    def _calculate_engagement_potential(self, content: str) -> float:
        # Logique simplifiée pour commencer
        return 0.8

    def _calculate_platform_fit(self, content: str) -> float:
        return 0.9 