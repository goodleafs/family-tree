from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.database import get_db
from app.schemas import (
    FamilyCreate, FamilyUpdate, FamilyResponse, FamilyListResponse,
    FamilyMemberCreate, FamilyMemberResponse
)
from app.services import FamilyService, AuthService
from app.routers.auth import get_current_active_user

router = APIRouter(prefix="/families", tags=["家族管理"])

@router.get("", response_model=FamilyListResponse)
async def list_families(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: Optional = Depends(get_current_active_user)
):
    """获取家族列表"""
    # 检查是否为超级管理员
    is_superuser = False
    user_id = None
    if current_user:
        user_id = current_user.id
        is_superuser = await FamilyService.is_superuser(db, current_user.id)
    
    families, total = await FamilyService.get_families(
        db, skip=skip, limit=limit, search=search, 
        user_id=user_id, is_superuser=is_superuser
    )
    
    # 获取每个家族的统计数据
    family_responses = []
    for family in families:
        stats = await FamilyService.get_family_stats(db, family.id)
        family_dict = {
            **family.__dict__,
            "member_count": stats["member_count"],
            "person_count": stats["person_count"]
        }
        family_responses.append(FamilyResponse.model_validate(family_dict))
    
    return {"total": total, "items": family_responses}

@router.post("", response_model=FamilyResponse, status_code=status.HTTP_201_CREATED)
async def create_family(
    family_data: FamilyCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """创建家族"""
    try:
        family = await FamilyService.create_family(db, family_data, current_user.id)
        await db.commit()
        
        # 获取统计信息
        stats = await FamilyService.get_family_stats(db, family.id)
        family_dict = {
            **family.__dict__,
            "member_count": stats["member_count"],
            "person_count": stats["person_count"]
        }
        
        return FamilyResponse.model_validate(family_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{family_id}", response_model=FamilyResponse)
async def get_family(
    family_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional = Depends(get_current_active_user)
):
    """获取家族详情"""
    family = await FamilyService.get_family_by_id(db, family_id)
    if not family:
        raise HTTPException(status_code=404, detail="家族不存在")
    
    # 检查访问权限
    if not family.is_public:
        if not current_user:
            raise HTTPException(status_code=403, detail="该家族为私密家族")
        role = await FamilyService.get_user_role_in_family(db, family_id, current_user.id)
        if not role:
            raise HTTPException(status_code=403, detail="您没有权限访问此家族")
    
    stats = await FamilyService.get_family_stats(db, family_id)
    family_dict = {
        **family.__dict__,
        "member_count": stats["member_count"],
        "person_count": stats["person_count"]
    }
    
    return FamilyResponse.model_validate(family_dict)

@router.put("/{family_id}", response_model=FamilyResponse)
async def update_family(
    family_id: int,
    family_update: FamilyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """更新家族信息"""
    family = await FamilyService.get_family_by_id(db, family_id)
    if not family:
        raise HTTPException(status_code=404, detail="家族不存在")
    
    is_superuser = await FamilyService.is_superuser(db, current_user.id)
    can_edit = await FamilyService.can_edit_family(db, family_id, current_user.id)
    
    if not is_superuser and family.creator_id != current_user.id and not can_edit:
        raise HTTPException(status_code=403, detail="您没有权限编辑此家族")
    
    try:
        updated_family = await FamilyService.update_family(db, family, family_update)
        await db.commit()
        
        stats = await FamilyService.get_family_stats(db, family_id)
        family_dict = {
            **updated_family.__dict__,
            "member_count": stats["member_count"],
            "person_count": stats["person_count"]
        }
        
        return FamilyResponse.model_validate(family_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{family_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_family(
    family_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """删除家族"""
    family = await FamilyService.get_family_by_id(db, family_id)
    if not family:
        raise HTTPException(status_code=404, detail="家族不存在")
    
    is_superuser = await FamilyService.is_superuser(db, current_user.id)
    if not is_superuser and family.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="只有家族创建者或超级管理员可以删除家族")
    
    await FamilyService.delete_family(db, family)
    await db.commit()
    return None

@router.get("/{family_id}/members", response_model=List[dict])
async def get_family_members(
    family_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """获取家族成员列表（包含角色信息）"""
    family = await FamilyService.get_family_by_id(db, family_id)
    if not family:
        raise HTTPException(status_code=404, detail="家族不存在")
    
    if not family.is_public:
        role = await FamilyService.get_user_role_in_family(db, family_id, current_user.id)
        if not role:
            raise HTTPException(status_code=403, detail="您没有权限访问此家族")
    
    members = await FamilyService.get_family_members_with_users(db, family_id)
    return members

@router.post("/{family_id}/members")
async def add_family_member(
    family_id: int,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """添加家族成员（将系统用户添加到家族）"""
    family = await FamilyService.get_family_by_id(db, family_id)
    if not family:
        raise HTTPException(status_code=404, detail="家族不存在")
    
    user_id = data.get("user_id")
    role = data.get("role", "member")
    
    if not user_id:
        raise HTTPException(status_code=400, detail="需要指定用户ID")
    
    if role not in ["admin", "family_admin", "editor", "member"]:
        raise HTTPException(status_code=400, detail="无效的角色类型")
    
    # 检查是否有权限添加成员
    can_manage = await FamilyService.can_manage_family_members(db, family_id, current_user.id)
    if not can_manage:
        raise HTTPException(status_code=403, detail="您没有权限添加家族成员")
    
    # 检查用户是否存在
    user = await FamilyService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查用户是否已经是家族成员
    existing_role = await FamilyService.get_user_role_in_family(db, family_id, user_id)
    if existing_role:
        raise HTTPException(status_code=400, detail="该用户已经是家族成员")
    
    # 添加成员
    member = await FamilyService.add_family_member(db, family_id, user_id, role)
    await db.commit()
    
    return {
        "message": "添加成员成功",
        "member": {
            "id": member.id,
            "user_id": member.user_id,
            "family_id": member.family_id,
            "role": member.role,
            "username": user.username,
            "email": user.email,
            "avatar_url": user.avatar_url,
            "is_superuser": user.is_superuser,
            "created_at": member.created_at
        }
    }

@router.delete("/{family_id}/members/{user_id}")
async def remove_family_member(
    family_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """移除家族成员"""
    family = await FamilyService.get_family_by_id(db, family_id)
    if not family:
        raise HTTPException(status_code=404, detail="家族不存在")
    
    # 检查是否有权限移除成员
    can_manage = await FamilyService.can_manage_family_members(db, family_id, current_user.id)
    if not can_manage:
        raise HTTPException(status_code=403, detail="您没有权限移除家族成员")
    
    # 不能移除自己
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能移除自己")
    
    # 移除成员
    success = await FamilyService.remove_family_member(db, family_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="该用户不是此家族成员")
    
    await db.commit()
    return {"message": "移除成员成功"}

@router.put("/{family_id}/members/{user_id}/role")
async def update_member_role(
    family_id: int,
    user_id: int,
    role: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """更新家族成员角色"""
    family = await FamilyService.get_family_by_id(db, family_id)
    if not family:
        raise HTTPException(status_code=404, detail="家族不存在")
    
    if role not in ["admin", "family_admin", "editor", "member"]:
        raise HTTPException(status_code=400, detail="无效的角色类型")
    
    can_set = await FamilyService.can_set_family_admin(db, family_id, current_user.id)
    if not can_set:
        raise HTTPException(status_code=403, detail="您没有权限设置家族管理员")
    
    member = await FamilyService.update_member_role(db, family_id, user_id, role)
    if not member:
        raise HTTPException(status_code=404, detail="该用户不是此家族成员")
    
    await db.commit()
    return {"message": "角色更新成功", "role": role}
