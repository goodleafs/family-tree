from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class OfferingItem(BaseModel):
    """贡品项目"""
    name: str
    icon: str
    
class MemorialHallCreate(BaseModel):
    """创建灵堂"""
    person_id: int
    offerings: Optional[List[OfferingItem]] = None
    
class MemorialHallUpdate(BaseModel):
    """更新灵堂"""
    offerings: Optional[List[OfferingItem]] = None
    is_active: Optional[bool] = None
    
class PersonBrief(BaseModel):
    """逝者简要信息"""
    id: int
    name: str
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    death_date: Optional[str] = None
    photo_url: Optional[str] = None
    
class CreatorBrief(BaseModel):
    """创建者简要信息"""
    id: int
    username: str
    
class WorshipRecordResponse(BaseModel):
    """祭拜记录响应"""
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    worship_type: str
    message: Optional[str] = None
    created_at: datetime
    
class MemorialHallResponse(BaseModel):
    """灵堂响应"""
    id: int
    person: PersonBrief
    offerings: List[OfferingItem]
    incense_count: int
    worship_count: int
    is_active: bool
    creator: CreatorBrief
    created_at: datetime
    
class MemorialHallListItem(BaseModel):
    """灵堂列表项"""
    id: int
    person: PersonBrief
    worship_count: int
    is_active: bool
    creator: CreatorBrief
    created_at: datetime
    
class WorshipRequest(BaseModel):
    """祭拜请求"""
    worship_type: str = "kowtow"  # kowtow, incense, offering
    message: Optional[str] = None
    
class WorshipResponse(BaseModel):
    """祭拜响应"""
    message: str
    worship_count: int
    
class MemorialHallListResponse(BaseModel):
    """灵堂列表响应"""
    total: int
    items: List[MemorialHallListItem]
