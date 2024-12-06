from pydantic import BaseModel
from typing import List, Dict

class UserInputs(BaseModel):
    tone: str
    style: str
    keywords: List[str]
    target_audience: str
    platform_params: Dict = {}