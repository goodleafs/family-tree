from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class FamilyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    surname: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    history: Optional[str] = None
    family_motto: Optional[str] = None
    generation_names: Optional[List[str]] = None
    is_public: bool = False

class FamilyCreate(FamilyBase):
    pass

class FamilyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    surname: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    history: Optional[str] = None
    family_motto: Optional[str] = None
    generation_names: Optional[List[str]] = None
    is_public: Optional[bool] = None

class FamilyResponse(FamilyBase):
    id: int
    creator_id: int
    created_at: datetime
    updated_at: datetime
    member_count: Optional[int] = 0
    person_count: Optional[int] = 0
    
    class Config:
        from_attributes = True

class FamilyMemberBase(BaseModel):
    family_id: int
    user_id: int
    role: str = "member"  # admin, editor, member

class FamilyMemberCreate(FamilyMemberBase):
    pass

class FamilyMemberUpdate(BaseModel):
    role: str

class FamilyMemberResponse(FamilyMemberBase):
    id: int
    created_at: datetime
    username: Optional[str] = None
    
    class Config:
        from_attributes = True

class FamilyListResponse(BaseModel):
    total: int
    items: List[FamilyResponse]
