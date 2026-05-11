from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.schemas import (
    BiographyCreate, BiographyUpdate, BiographyResponse, BiographyListItem,
    BiographyDetailResponse, BiographyListResponse, PersonBriefForBiography
)
from app.services import BiographyService, FamilyService, PersonService
from app.routers.auth import get_current_active_user

router = APIRouter(prefix="/biographies", tags=["人物传记"])


def person_to_brief(person) -> PersonBriefForBiography:
    """将Person对象转为简要信息"""
    return PersonBriefForBiography(
        id=person.id,
        name=person.name,
        gender=person.gender,
        birth_date=str(person.birth_date) if person.birth_date else None,
        death_date=str(person.death_date) if person.death_date else None,
        photo_url=person.photo_url,
        branch_name=person.branch_name,
        generation_number=person.generation_number
    )


@router.get("/family/{family_id}", response_model=BiographyListResponse)
async def list_family_biographies(
    family_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """获取家族的人物传记列表"""
    family = await FamilyService.get_family_by_id(db, family_id)
    if not family:
        raise HTTPException(status_code=404, detail="家族不存在")

    if not family.is_public:
        role = await FamilyService.get_user_role_in_family(db, family_id, current_user.id)
        if not role:
            raise HTTPException(status_code=403, detail="您没有权限访问此家族")

    biographies, total = await BiographyService.get_biographies_by_family(
        db, family_id, skip=skip, limit=limit, search=search
    )

    items = []
    for bio in biographies:
        person = bio.person
        items.append(BiographyListItem(
            id=bio.id,
            title=bio.title,
            person=person_to_brief(person),
            summary=bio.summary,
            views_count=bio.views_count,
            is_published=bio.is_published,
            created_by=bio.created_by,
            created_at=bio.created_at,
            updated_at=bio.updated_at
        ))

    return {"total": total, "items": items}


@router.post("", response_model=BiographyResponse, status_code=status.HTTP_201_CREATED)
async def create_biography(
    bio_data: BiographyCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """创建人物传记"""
    # 验证人员存在
    person = await PersonService.get_person_by_id(db, bio_data.person_id)
    if not person:
        raise HTTPException(status_code=404, detail="成员不存在")

    # 检查家族权限
    family = await FamilyService.get_family_by_id(db, bio_data.family_id)
    if not family:
        raise HTTPException(status_code=404, detail="家族不存在")

    role = await FamilyService.get_user_role_in_family(db, bio_data.family_id, current_user.id)
    if not role:
        raise HTTPException(status_code=403, detail="您没有权限创建传记")

    # 检查是否已有传记
    existing = await BiographyService.get_biography_by_person(db, bio_data.person_id)
    if existing:
        raise HTTPException(status_code=400, detail="该成员已有传记")

    try:
        bio = await BiographyService.create_biography(db, bio_data, current_user.id)
        await db.commit()
        return BiographyResponse.model_validate(bio)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{biography_id}", response_model=BiographyDetailResponse)
async def get_biography(
    biography_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """获取传记详情"""
    bio = await BiographyService.get_biography_by_id(db, biography_id)
    if not bio:
        raise HTTPException(status_code=404, detail="传记不存在")

    # 访问权限检查
    family = await FamilyService.get_family_by_id(db, bio.family_id)
    if not family.is_public:
        role = await FamilyService.get_user_role_in_family(db, bio.family_id, current_user.id)
        if not role:
            raise HTTPException(status_code=403, detail="您没有权限查看此传记")

    # 增加浏览次数
    await BiographyService.increment_views(db, bio)
    await db.commit()

    person = bio.person
    return BiographyDetailResponse(
        id=bio.id,
        title=bio.title,
        subtitle=bio.subtitle,
        summary=bio.summary,
        content=bio.content,
        achievements=bio.achievements,
        portrait_url=bio.portrait_url,
        is_published=bio.is_published,
        views_count=bio.views_count + 1,
        person=person_to_brief(person),
        created_by=bio.created_by,
        created_at=bio.created_at,
        updated_at=bio.updated_at
    )


@router.put("/{biography_id}", response_model=BiographyResponse)
async def update_biography(
    biography_id: int,
    bio_update: BiographyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """更新传记"""
    bio = await BiographyService.get_biography_by_id(db, biography_id)
    if not bio:
        raise HTTPException(status_code=404, detail="传记不存在")

    role = await FamilyService.get_user_role_in_family(db, bio.family_id, current_user.id)
    if not role:
        raise HTTPException(status_code=403, detail="您没有权限编辑此传记")

    try:
        updated = await BiographyService.update_biography(db, bio, bio_update)
        await db.commit()
        return BiographyResponse.model_validate(updated)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{biography_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_biography(
    biography_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """删除传记"""
    bio = await BiographyService.get_biography_by_id(db, biography_id)
    if not bio:
        raise HTTPException(status_code=404, detail="传记不存在")

    role = await FamilyService.get_user_role_in_family(db, bio.family_id, current_user.id)
    if not role:
        raise HTTPException(status_code=403, detail="您没有权限删除此传记")

    await BiographyService.delete_biography(db, bio)
    await db.commit()
    return None


@router.get("/eligible-persons/{family_id}")
async def get_eligible_persons(
    family_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """获取可以创建传记的人员列表"""
    role = await FamilyService.get_user_role_in_family(db, family_id, current_user.id)
    if not role:
        raise HTTPException(status_code=403, detail="您没有权限查看此家族信息")

    persons = await BiographyService.get_eligible_persons(db, family_id)

    return [
        {
            "id": p.id,
            "name": p.name,
            "gender": p.gender,
            "birth_date": str(p.birth_date) if p.birth_date else None,
            "death_date": str(p.death_date) if p.death_date else None,
            "photo_url": p.photo_url,
            "branch_name": p.branch_name,
            "generation_number": p.generation_number
        }
        for p in persons
    ]


@router.get("/by-person/{person_id}", response_model=BiographyDetailResponse)
async def get_biography_by_person(
    person_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """根据人员ID获取传记"""
    bio = await BiographyService.get_biography_by_person(db, person_id)
    if not bio:
        raise HTTPException(status_code=404, detail="该成员暂未创建传记")

    family = await FamilyService.get_family_by_id(db, bio.family_id)
    if not family.is_public:
        role = await FamilyService.get_user_role_in_family(db, bio.family_id, current_user.id)
        if not role:
            raise HTTPException(status_code=403, detail="您没有权限查看此传记")

    # 增加浏览次数
    await BiographyService.increment_views(db, bio)
    await db.commit()

    person = bio.person
    return BiographyDetailResponse(
        id=bio.id,
        title=bio.title,
        subtitle=bio.subtitle,
        summary=bio.summary,
        content=bio.content,
        achievements=bio.achievements,
        portrait_url=bio.portrait_url,
        is_published=bio.is_published,
        views_count=bio.views_count + 1,
        person=person_to_brief(person),
        created_by=bio.created_by,
        created_at=bio.created_at,
        updated_at=bio.updated_at
    )
