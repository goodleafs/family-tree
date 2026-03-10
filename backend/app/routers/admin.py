from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List

from app.database import get_db
from app.models import User
from app.schemas import UserResponse
from app.services import FamilyService
from app.routers.auth import get_current_active_user

router = APIRouter(prefix="/admin", tags=["超级管理员"])

async def require_superuser(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """要求超级管理员权限"""
    is_superuser = await FamilyService.is_superuser(db, current_user.id)
    if not is_superuser:
        raise HTTPException(status_code=403, detail="需要超级管理员权限")
    return current_user

@router.get("/users", response_model=dict)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_superuser)
):
    """获取用户列表（仅超级管理员）"""
    query = select(User)
    count_query = select(func.count(User.id))
    
    if search:
        query = query.where(
            User.username.contains(search) | 
            User.email.contains(search)
        )
        count_query = count_query.where(
            User.username.contains(search) | 
            User.email.contains(search)
        )
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
    result = await db.execute(query)
    users = result.scalars().all()
    
    return {
        "total": total,
        "items": [UserResponse.model_validate(u) for u in users]
    }

@router.put("/users/{user_id}/superuser", response_model=UserResponse)
async def toggle_superuser(
    user_id: int,
    is_superuser: bool,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_superuser)
):
    """设置/取消超级管理员（仅超级管理员）"""
    user = await FamilyService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能修改自己的超级管理员状态")
    
    user.is_superuser = is_superuser
    await db.commit()
    await db.refresh(user)
    
    return UserResponse.model_validate(user)

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_superuser)
):
    """获取用户详情（仅超级管理员）"""
    user = await FamilyService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return UserResponse.model_validate(user)

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: dict,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_superuser)
):
    """更新用户信息（仅超级管理员）"""
    user = await FamilyService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 允许更新的字段
    allowed_fields = ['email', 'phone']
    for field in allowed_fields:
        if field in user_update:
            setattr(user, field, user_update[field])
    
    await db.commit()
    await db.refresh(user)
    
    return UserResponse.model_validate(user)

@router.post("/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_superuser)
):
    """重置用户密码（仅超级管理员）"""
    from app.utils.auth import get_password_hash
    
    user = await FamilyService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    new_password = data.get('new_password')
    if not new_password or len(new_password) < 6:
        raise HTTPException(status_code=400, detail="密码长度至少6位")
    
    # 重置密码
    user.hashed_password = get_password_hash(new_password)
    await db.commit()
    
    return {"message": "密码重置成功"}