from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Optional
from .oauth import SocialPlatform

class ValidationResult(BaseModel):
    format_valid: bool
    length_valid: bool
    keyword_presence: bool

class ContentOutput(BaseModel):
    content: str
    validation: ValidationResult
    metadata: Dict
    platform_data: Dict = {}