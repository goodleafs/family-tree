from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.database import get_db
from app.schemas import (
    MemorialHallCreate, MemorialHallUpdate, MemorialHallResponse, MemorialHallListItem,
    MemorialHallListResponse, WorshipRequest, WorshipResponse, WorshipRecordResponse,
    OfferingItem, PersonBrief, CreatorBrief
)
from app.services import MemorialService, FamilyService
from app.routers.auth import get_current_active_user

router = APIRouter(prefix="/memorial", tags=["祭拜管理"])

@router.get("/halls", response_model=MemorialHallListResponse)
async def list_memorial_halls(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    family_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """获取灵堂列表"""
    halls, total = await MemorialService.get_memorial_halls(
        db, skip=skip, limit=limit, family_id=family_id
    )
    
    items = []
    for hall in halls:
        items.append(MemorialHallListItem(
            id=hall.id,
            person=PersonBrief(
                id=hall.person.id,
                name=hall.person.name,
                gender=hall.person.gender,
                birth_date=str(hall.person.birth_date) if hall.person.birth_date else None,
                death_date=str(hall.person.death_date) if hall.person.death_date else None,
                photo_url=hall.person.photo_url
            ),
            worship_count=hall.worship_count,
            is_active=hall.is_active,
            creator=CreatorBrief(
                id=hall.creator.id,
                username=hall.creator.username
            ),
            created_at=hall.created_at
        ))
    
    return {"total": total, "items": items}

@router.get("/halls/{hall_id}", response_model=MemorialHallResponse)
async def get_memorial_hall(
    hall_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """获取灵堂详情"""
    hall = await MemorialService.get_memorial_hall_by_id(db, hall_id)
    if not hall:
        raise HTTPException(status_code=404, detail="灵堂不存在")
    
    return MemorialHallResponse(
        id=hall.id,
        person=PersonBrief(
            id=hall.person.id,
            name=hall.person.name,
            gender=hall.person.gender,
            birth_date=str(hall.person.birth_date) if hall.person.birth_date else None,
            death_date=str(hall.person.death_date) if hall.person.death_date else None,
            photo_url=hall.person.photo_url
        ),
        offerings=[OfferingItem(**o) for o in hall.offerings],
        incense_count=hall.incense_count,
        worship_count=hall.worship_count,
        is_active=hall.is_active,
        creator=CreatorBrief(
            id=hall.creator.id,
            username=hall.creator.username
        ),
        created_at=hall.created_at
    )

@router.post("/halls", response_model=MemorialHallResponse, status_code=status.HTTP_201_CREATED)
async def create_memorial_hall(
    data: MemorialHallCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """创建灵堂"""
    # 检查该逝者是否已有灵堂
    existing = await MemorialService.get_memorial_hall_by_person(db, data.person_id)
    if existing:
        raise HTTPException(status_code=400, detail="该逝者已有灵堂")
    
    # 获取逝者信息
    from app.services import PersonService
    person = await PersonService.get_person_by_id(db, data.person_id)
    if not person:
        raise HTTPException(status_code=404, detail="逝者不存在")
    
    if not person.death_date:
        raise HTTPException(status_code=400, detail="只能为有逝世日期的成员布置灵堂")
    
    # 检查权限
    can_manage = await FamilyService.can_manage_family_members(db, person.family_id, current_user.id)
    if not can_manage:
        raise HTTPException(status_code=403, detail="您没有权限为此家族布置灵堂")
    
    hall = await MemorialService.create_memorial_hall(
        db=db,
        person_id=data.person_id,
        family_id=person.family_id,
        created_by=current_user.id,
        offerings=data.offerings
    )
    await db.commit()
    
    # 重新查询以获取完整关系数据
    hall = await MemorialService.get_memorial_hall_by_id(db, hall.id)
    
    return MemorialHallResponse(
        id=hall.id,
        person=PersonBrief(
            id=hall.person.id,
            name=hall.person.name,
            gender=hall.person.gender,
            birth_date=str(hall.person.birth_date) if hall.person.birth_date else None,
            death_date=str(hall.person.death_date) if hall.person.death_date else None,
            photo_url=hall.person.photo_url
        ),
        offerings=[OfferingItem(**o) for o in hall.offerings],
        incense_count=hall.incense_count,
        worship_count=hall.worship_count,
        is_active=hall.is_active,
        creator=CreatorBrief(
            id=hall.creator.id,
            username=hall.creator.username
        ),
        created_at=hall.created_at
    )

@router.put("/halls/{hall_id}", response_model=MemorialHallResponse)
async def update_memorial_hall(
    hall_id: int,
    data: MemorialHallUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """更新灵堂"""
    hall = await MemorialService.get_memorial_hall_by_id(db, hall_id)
    if not hall:
        raise HTTPException(status_code=404, detail="灵堂不存在")
    
    # 检查权限
    can_manage = await FamilyService.can_manage_family_members(db, hall.family_id, current_user.id)
    if not can_manage:
        raise HTTPException(status_code=403, detail="您没有权限修改此灵堂")
    
    hall = await MemorialService.update_memorial_hall(db, hall, data)
    await db.commit()
    
    # 重新查询以获取完整关系数据
    hall = await MemorialService.get_memorial_hall_by_id(db, hall.id)
    
    return MemorialHallResponse(
        id=hall.id,
        person=PersonBrief(
            id=hall.person.id,
            name=hall.person.name,
            gender=hall.person.gender,
            birth_date=str(hall.person.birth_date) if hall.person.birth_date else None,
            death_date=str(hall.person.death_date) if hall.person.death_date else None,
            photo_url=hall.person.photo_url
        ),
        offerings=[OfferingItem(**o) for o in hall.offerings],
        incense_count=hall.incense_count,
        worship_count=hall.worship_count,
        is_active=hall.is_active,
        creator=CreatorBrief(
            id=hall.creator.id,
            username=hall.creator.username
        ),
        created_at=hall.created_at
    )

@router.delete("/halls/{hall_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memorial_hall(
    hall_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """删除灵堂"""
    hall = await MemorialService.get_memorial_hall_by_id(db, hall_id)
    if not hall:
        raise HTTPException(status_code=404, detail="灵堂不存在")
    
    # 检查权限
    can_manage = await FamilyService.can_manage_family_members(db, hall.family_id, current_user.id)
    if not can_manage:
        raise HTTPException(status_code=403, detail="您没有权限删除此灵堂")
    
    await MemorialService.delete_memorial_hall(db, hall)
    await db.commit()
    return None

@router.post("/halls/{hall_id}/worship", response_model=WorshipResponse)
async def worship(
    hall_id: int,
    data: WorshipRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """祭拜"""
    hall = await MemorialService.get_memorial_hall_by_id(db, hall_id)
    if not hall:
        raise HTTPException(status_code=404, detail="灵堂不存在")
    
    if not hall.is_active:
        raise HTTPException(status_code=400, detail="该灵堂已停用")
    
    record = await MemorialService.add_worship_record(
        db=db,
        hall_id=hall_id,
        user_id=current_user.id,
        worship_type=data.worship_type,
        message=data.message
    )
    await db.commit()
    
    # 重新获取hall以获取最新统计
    hall = await MemorialService.get_memorial_hall_by_id(db, hall_id)
    
    return WorshipResponse(
        message="祭拜成功",
        worship_count=hall.worship_count
    )

@router.get("/halls/{hall_id}/records", response_model=List[WorshipRecordResponse])
async def list_worship_records(
    hall_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """获取祭拜记录"""
    hall = await MemorialService.get_memorial_hall_by_id(db, hall_id)
    if not hall:
        raise HTTPException(status_code=404, detail="灵堂不存在")
    
    records, _ = await MemorialService.get_worship_records(db, hall_id, skip, limit)
    
    result = []
    for record in records:
        result.append(WorshipRecordResponse(
            id=record.id,
            user_id=record.user_id,
            username=record.user.username if record.user else None,
            worship_type=record.worship_type,
            message=record.message,
            created_at=record.created_at
        ))
    
    return result

@router.get("/eligible-persons/{family_id}")
async def get_eligible_persons(
    family_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """获取可以布置灵堂的逝者列表"""
    # 检查权限
    role = await FamilyService.get_user_role_in_family(db, family_id, current_user.id)
    if not role:
        raise HTTPException(status_code=403, detail="您没有权限查看此家族信息")
    
    persons = await MemorialService.get_eligible_persons(db, family_id)
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "gender": p.gender,
            "birth_date": str(p.birth_date) if p.birth_date else None,
            "death_date": str(p.death_date) if p.death_date else None,
            "photo_url": p.photo_url
        }
        for p in persons
    ]
