from pydantic import BaseModel , field_validator
from typing import Optional

class BusinessListData(BaseModel):
    name: str
    url: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    street: Optional[str] = None
    locality: Optional[str] = None
    region: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    telephone: Optional[str] = None
    opening_hours: Optional[str] = None

    @field_validator('*', mode='before')
    @classmethod
    def empty_to_none(cls , v):
        if v != "N/A":
            return v
        return None
    

class BusinessInsightData(BaseModel):
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    payment: Optional[str] = None
    language: Optional[str] = None
    extra_links: Optional[str] = None
    extra_phone: Optional[str] = None
    
    @field_validator('*', mode='before')
    @classmethod
    def empty_to_none(cls , v):
        if v != "N/A":
            return v
        return None
    
class Config_json(BaseModel):
    page_per_request: int = 0
    rate_min : int
    rate_max : int
    max_attempt : int
    failed_attempt_duration : float
    word_randomizer: bool
    categories: list
    locations: list
    enable: bool
    csv_export: bool
    json_export: bool
    database_export: bool