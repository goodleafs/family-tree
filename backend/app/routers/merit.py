from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.schemas import MeritDonorCreate, MeritDonorUpdate, MeritDonorResponse, MeritDonorListResponse
from app.services import MeritService, FamilyService
from app.routers.auth import get_current_active_user

router = APIRouter(prefix="/merit", tags=["功德榜"])


@router.get("/family/{family_id}", response_model=MeritDonorListResponse)
async def list_merit_donors(
    family_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """获取家族功德榜"""
    family = await FamilyService.get_family_by_id(db, family_id)
    if not family:
        raise HTTPException(status_code=404, detail="家族不存在")

    if not family.is_public:
        role = await FamilyService.get_user_role_in_family(db, family_id, current_user.id)
        if not role:
            raise HTTPException(status_code=403, detail="您没有权限访问此家族")

    donors, total, total_amount = await MeritService.get_donors_by_family(db, family_id, skip=skip, limit=limit)
    return {"total": total, "total_amount": total_amount, "items": [MeritDonorResponse.model_validate(d) for d in donors]}


@router.post("", response_model=MeritDonorResponse, status_code=status.HTTP_201_CREATED)
async def create_merit_donor(
    data: MeritDonorCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """添加捐款记录"""
    family = await FamilyService.get_family_by_id(db, data.family_id)
    if not family:
        raise HTTPException(status_code=404, detail="家族不存在")

    role = await FamilyService.get_user_role_in_family(db, data.family_id, current_user.id)
    if not role:
        raise HTTPException(status_code=403, detail="您没有权限添加捐款记录")

    try:
        donor = await MeritService.create_donor(db, data, current_user.id)
        await db.commit()
        return MeritDonorResponse.model_validate(donor)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{donor_id}", response_model=MeritDonorResponse)
async def get_merit_donor(
    donor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """获取捐款记录详情"""
    donor = await MeritService.get_donor_by_id(db, donor_id)
    if not donor:
        raise HTTPException(status_code=404, detail="记录不存在")

    family = await FamilyService.get_family_by_id(db, donor.family_id)
    if not family.is_public:
        role = await FamilyService.get_user_role_in_family(db, donor.family_id, current_user.id)
        if not role:
            raise HTTPException(status_code=403, detail="您没有权限查看")

    return MeritDonorResponse.model_validate(donor)


@router.put("/{donor_id}", response_model=MeritDonorResponse)
async def update_merit_donor(
    donor_id: int,
    update_data: MeritDonorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """更新捐款记录"""
    donor = await MeritService.get_donor_by_id(db, donor_id)
    if not donor:
        raise HTTPException(status_code=404, detail="记录不存在")

    role = await FamilyService.get_user_role_in_family(db, donor.family_id, current_user.id)
    if not role:
        raise HTTPException(status_code=403, detail="您没有权限编辑")

    try:
        updated = await MeritService.update_donor(db, donor, update_data)
        await db.commit()
        return MeritDonorResponse.model_validate(updated)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{donor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_merit_donor(
    donor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """删除捐款记录"""
    donor = await MeritService.get_donor_by_id(db, donor_id)
    if not donor:
        raise HTTPException(status_code=404, detail="记录不存在")

    role = await FamilyService.get_user_role_in_family(db, donor.family_id, current_user.id)
    if not role:
        raise HTTPException(status_code=403, detail="您没有权限删除")

    await MeritService.delete_donor(db, donor)
    await db.commit()
    return None
