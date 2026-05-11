from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class PhotoBase(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    taken_date: Optional[date] = None

class PhotoCreate(PhotoBase):
    album_id: Optional[int] = None
    family_id: int

class PhotoUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    taken_date: Optional[date] = None
    album_id: Optional[int] = None

class PhotoResponse(PhotoBase):
    id: int
    album_id: Optional[int]
    family_id: int
    url: str
    thumbnail_url: Optional[str]
    taken_year: Optional[int]
    taken_month: Optional[int]
    file_size: Optional[int]
    uploader_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class AlbumBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    sort_order: int = 0

class AlbumCreate(AlbumBase):
    family_id: int

class AlbumUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    cover_url: Optional[str] = None
    sort_order: Optional[int] = None

class AlbumResponse(AlbumBase):
    id: int
    family_id: int
    cover_url: Optional[str]
    created_by: int
    created_at: datetime
    updated_at: datetime
    photo_count: Optional[int] = 0

    class Config:
        from_attributes = True

class AlbumDetailResponse(AlbumResponse):
    photos: List[PhotoResponse] = []

class AlbumListResponse(BaseModel):
    total: int
    items: List[AlbumResponse]

class PhotoListResponse(BaseModel):
    total: int
    items: List[PhotoResponse]

class TimelineGroup(BaseModel):
    """时间轴分组"""
    year: int
    photos: List[PhotoResponse]

class AlbumTimelineResponse(BaseModel):
    """相册时间轴响应"""
    total: int
    years: List[int]
    timeline: List[TimelineGroup]
