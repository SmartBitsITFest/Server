import uuid
from typing import Optional
from pydantic import BaseModel, Field


class Product(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    name: str = Field(...)
    description: str = Field(...)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "name": "Llama",
                "description": "A product that helps you with your daily tasks"
            }
        }
    
class ProductUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Llama",
                "description": "A product that helps you with your daily tasks"
            }
        }