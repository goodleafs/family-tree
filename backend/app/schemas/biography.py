from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class BiographyBase(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    subtitle: Optional[str] = Field(None, max_length=300)
    summary: Optional[str] = None
    content: str = Field(..., min_length=1)
    achievements: Optional[str] = None
    portrait_url: Optional[str] = None
    is_published: bool = True

class BiographyCreate(BiographyBase):
    person_id: int
    family_id: int

class BiographyUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    subtitle: Optional[str] = Field(None, max_length=300)
    summary: Optional[str] = None
    content: Optional[str] = None
    achievements: Optional[str] = None
    portrait_url: Optional[str] = None
    is_published: Optional[bool] = None

class BiographyResponse(BiographyBase):
    id: int
    person_id: int
    family_id: int
    views_count: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PersonBriefForBiography(BaseModel):
    """人员简要信息（用于传记列表）"""
    id: int
    name: str
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    death_date: Optional[str] = None
    photo_url: Optional[str] = None
    branch_name: Optional[str] = None
    generation_number: Optional[int] = None

class BiographyListItem(BaseModel):
    """传记列表项"""
    id: int
    title: Optional[str]
    person: PersonBriefForBiography
    summary: Optional[str]
    views_count: int
    is_published: bool
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BiographyDetailResponse(BaseModel):
    """传记详情（包含人员信息）"""
    id: int
    title: Optional[str]
    subtitle: Optional[str]
    summary: Optional[str]
    content: str
    achievements: Optional[str]
    portrait_url: Optional[str]
    is_published: bool
    views_count: int
    person: PersonBriefForBiography
    created_by: int
    created_at: datetime
    updated_at: datetime

class BiographyListResponse(BaseModel):
    total: int
    items: List[BiographyListItem]
