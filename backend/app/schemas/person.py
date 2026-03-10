from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

class PersonBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    gender: Optional[str] = Field(None, pattern="^(male|female)$")
    birth_date: Optional[date] = None
    death_date: Optional[date] = None
    birthplace: Optional[str] = Field(None, max_length=100)
    residence: Optional[str] = Field(None, max_length=100)
    occupation: Optional[str] = Field(None, max_length=100)
    education: Optional[str] = Field(None, max_length=100)
    biography: Optional[str] = None
    achievements: Optional[str] = None
    photo_url: Optional[str] = None
    branch_name: Optional[str] = Field(None, max_length=50)
    generation_number: Optional[int] = None

class PersonCreate(PersonBase):
    family_id: int

class PersonUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    gender: Optional[str] = Field(None, pattern="^(male|female)$")
    birth_date: Optional[date] = None
    death_date: Optional[date] = None
    birthplace: Optional[str] = Field(None, max_length=100)
    residence: Optional[str] = Field(None, max_length=100)
    occupation: Optional[str] = Field(None, max_length=100)
    education: Optional[str] = Field(None, max_length=100)
    biography: Optional[str] = None
    achievements: Optional[str] = None
    photo_url: Optional[str] = None
    branch_name: Optional[str] = Field(None, max_length=50)
    generation_number: Optional[int] = None

class PersonResponse(PersonBase):
    id: int
    family_id: int
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PersonListResponse(BaseModel):
    total: int
    items: List[PersonResponse]

class RelationshipBase(BaseModel):
    person_id: int
    relative_id: int
    relation_type: str = Field(..., pattern="^(father|mother|spouse|child)$")
    is_primary: bool = True
    marriage_date: Optional[date] = None
    divorce_date: Optional[date] = None

class RelationshipCreate(RelationshipBase):
    pass

class RelationshipUpdate(BaseModel):
    is_primary: Optional[bool] = None
    marriage_date: Optional[date] = None
    divorce_date: Optional[date] = None

class RelationshipResponse(RelationshipBase):
    id: int
    created_at: datetime
    person_name: Optional[str] = None
    relative_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class TreeNode(BaseModel):
    id: int
    name: str
    gender: Optional[str]
    birth_date: Optional[date]
    death_date: Optional[date]
    photo_url: Optional[str]
    generation_number: Optional[int]
    children: List['TreeNode'] = []
    spouses: List['TreeNode'] = []
    
    class Config:
        from_attributes = True

TreeNode.model_rebuild()

class FamilyTreeResponse(BaseModel):
    root: TreeNode
    total_generations: int
    total_members: int
