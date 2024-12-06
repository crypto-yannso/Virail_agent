from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class PlatformCredentials(BaseModel):
    integration_token: str
    user_id: str

class ContentValidation(BaseModel):
    tone_match: bool = False
    keyword_presence: bool = False
    length_valid: bool = False
    format_valid: bool = False  # Ajout de l'attribut format_valid
    platform_specific_rules: Dict[str, bool] = Field(default_factory=dict)

class PostStats(BaseModel):
    views: int = 0
    likes: int = 0
    comments: int = 0

class PerformanceMetrics(BaseModel):
    engagement_rate: float = 0.0
    reach: int = 0
    conversion_rate: float = 0.0
    metrics: Dict[str, Any] = Field(default_factory=dict)

class ContentAnalysis(BaseModel):
    sentiment_score: float = 0.0
    readability_score: float = 0.0
    seo_score: float = 0.0
    keyword_density: Dict[str, float] = Field(default_factory=dict)
    performance: PerformanceMetrics = Field(default_factory=PerformanceMetrics)
    platform_metrics: Dict[str, Any] = Field(default_factory=dict)

class PublishingSchedule(BaseModel):
    publish_time: datetime
    retry_strategy: Dict[str, Any] = Field(default_factory=dict)

class PlatformConfig(BaseModel):
    name: str
    credentials: Optional[PlatformCredentials] = None
    max_length: int
    prompt_template: str
    output_requirements: Dict[str, bool]
    platform_specifics: Dict[str, Any]

class UserInputs(BaseModel):
    tone: str
    style: str
    keywords: List[str]
    target_audience: str
    platform_params: Dict[str, Any]

class ContentOutput(BaseModel):
    content: str
    validation: ContentValidation
    metadata: Dict[str, Any] = Field(default_factory=dict)
    platform_data: Dict[str, Any] = Field(default_factory=dict)