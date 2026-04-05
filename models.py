from pydantic import BaseModel , field_validator , Field
from typing import Optional

class BusinessListData(BaseModel):
    name: str
    url: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    street: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    telephone: Optional[str] = None
    opening_hours: Optional[str|list] = None
    location_name: Optional[str] = None
    state_code: Optional[str] = None

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
    extra_links: Optional[str] | list= None
    extra_phone: Optional[str] | list = None
    
    @field_validator('*', mode='before')
    @classmethod
    def empty_to_none(cls , v):
        if v != "N/A":
            return v
        return None
    
class ConfigJson(BaseModel):
    page_per_request: int = Field(gt=0 , strict=True, le=100,  description="amount of pages to run" , default=1)
    rate_min : float = Field(ge=0 , strict=True, description="minimum rate per requests" , default=1) # rate per requests gonna get randomize between rate_min and rate_max 
    rate_max : float = Field(gt=0 , strict=True, description="maximum rate per requests" , default=1) 
    max_attempt : int = Field(ge=0 , strict=True, description="amount of attempts for request" , default=0)
    attempt_duration : float =  Field(ge=0 , strict=True, description="how long to wait per requests" , default=0)
    write_business_insight_on_loop: bool = Field(strict=True, description="loop on 'write_business_insight' till null" , default=False)
    write_business_insight_loop_cooldown : float =  Field(ge=0 ,strict=True , description="how long to wait per loop" , default=0)
    redo_on_fail_page: bool = Field(strict=True, description="redo on the return fail page" , default=False)
    redo_on_fail_page_attempt: int = Field(ge=0 , strict=True, description="redo on the return fail page's attempt" , default=0)
    category: list[str] = Field(min_length=1, description = "category of business to iterate example  plumbing / dentist , etc.")
    location: list[str] = Field(min_length=1, description="location to iterate example NYC / Sydney etc.")
    headers: dict = Field(min_length=1, strict=True , description="headers that would be use in the request **SHOULD INCLUDE COOKIES")
    amount_write_business_insight: int = Field(strict=True,gt=0,description="amount of page to run on inner extraction",default=10) 
    


        