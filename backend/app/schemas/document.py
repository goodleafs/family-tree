from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DocumentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    author: Optional[str] = Field(None, max_length=100)
    document_date: Optional[str] = Field(None, max_length=50)
    tags: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)

class DocumentCreate(DocumentBase):
    family_id: int

class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    author: Optional[str] = Field(None, max_length=100)
    document_date: Optional[str] = Field(None, max_length=50)
    tags: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)

class DocumentResponse(DocumentBase):
    id: int
    family_id: int
    file_type: str
    file_url: str
    file_size: Optional[int]
    file_ext: Optional[str]
    uploader_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    total: int
    items: List[DocumentResponse]

class DocumentCategoryCount(BaseModel):
    """分类统计"""
    category: str
    count: int

class DocumentOverviewResponse(BaseModel):
    total: int
    categories: List[DocumentCategoryCount]
