from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    
    class Config:
        from_attributes = True  # Updated for Pydantic V2


class SampleCreate(BaseModel):
    name: str = Field(..., description="Sample name/identifier")
    taxonomy: str = Field(..., description="Taxonomic classification")
    abundance: float = Field(..., ge=0, le=100, description="Relative abundance (0-100%)")
    location: str = Field(..., description="Sample location or source")


class SampleOut(BaseModel):
    id: int
    name: str
    taxonomy: str
    abundance: float
    location: str
    user_id: int
    
    class Config:
        from_attributes = True  # Updated for Pydantic V2