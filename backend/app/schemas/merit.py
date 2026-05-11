from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class MeritDonorBase(BaseModel):
    donor_name: str = Field(..., min_length=1, max_length=100)
    amount: float = Field(..., gt=0)
    donation_date: Optional[date] = None
    remarks: Optional[str] = None
    sort_order: int = 0

class MeritDonorCreate(MeritDonorBase):
    family_id: int

class MeritDonorUpdate(BaseModel):
    donor_name: Optional[str] = Field(None, min_length=1, max_length=100)
    amount: Optional[float] = Field(None, gt=0)
    donation_date: Optional[date] = None
    remarks: Optional[str] = None
    sort_order: Optional[int] = None

class MeritDonorResponse(MeritDonorBase):
    id: int
    family_id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MeritDonorListResponse(BaseModel):
    total: int
    total_amount: float
    items: List[MeritDonorResponse]
