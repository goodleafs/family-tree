from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from app.models import Family, FamilyMember, Person, User
from app.schemas import FamilyCreate, FamilyUpdate, FamilyMemberCreate

class FamilyService:
    @staticmethod
    async def get_family_by_id(db: AsyncSession, family_id: int) -> Optional[Family]:
        """根据ID获取家族"""
        result = await db.execute(select(Family).where(Family.id == family_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_families(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        user_id: Optional[int] = None,
        is_superuser: bool = False
    ) -> tuple[List[Family], int]:
        """获取家族列表
        
        Args:
            db: 数据库会话
            skip: 跳过数量
            limit: 限制数量
            search: 搜索关键词
            user_id: 当前用户ID（用于权限过滤）
            is_superuser: 是否为超级管理员
        """
        if is_superuser:
            # 超级管理员可以看到所有家族
            query = select(Family)
            count_query = select(func.count(Family.id)).select_from(Family)
            
            # 搜索过滤
            if search:
                query = query.where(
                    Family.name.contains(search) | 
                    Family.surname.contains(search) |
                    Family.description.contains(search)
                )
                count_query = count_query.where(
                    Family.name.contains(search) | 
                    Family.surname.contains(search) |
                    Family.description.contains(search)
                )
            
            total_result = await db.execute(count_query)
            total = total_result.scalar() or 0
            
            query = query.order_by(Family.created_at.desc()).offset(skip).limit(limit)
            result = await db.execute(query)
            families = result.scalars().all()
            
            return list(families), total
        
        else:
            # 普通用户：只能看到公开家族 + 自己创建的家族 + 自己是成员的家族
            accessible_family_ids = set()
            
            # 1. 获取所有公开家族
            public_query = select(Family.id).where(Family.is_public == True)
            if search:
                public_query = public_query.where(
                    Family.name.contains(search) | 
                    Family.surname.contains(search) |
                    Family.description.contains(search)
                )
            public_result = await db.execute(public_query)
            accessible_family_ids.update([r[0] for r in public_result.all()])
            
            # 2. 获取用户创建的家族
            if user_id:
                created_query = select(Family.id).where(Family.creator_id == user_id)
                if search:
                    created_query = created_query.where(
                        Family.name.contains(search) | 
                        Family.surname.contains(search) |
                        Family.description.contains(search)
                    )
                created_result = await db.execute(created_query)
                accessible_family_ids.update([r[0] for r in created_result.all()])
                
                # 3. 获取用户是成员的家族
                member_query = select(FamilyMember.family_id).where(
                    FamilyMember.user_id == user_id
                )
                member_result = await db.execute(member_query)
                member_family_ids = [r[0] for r in member_result.all()]
                
                if member_family_ids:
                    member_families_query = select(Family.id).where(
                        Family.id.in_(member_family_ids)
                    )
                    if search:
                        member_families_query = member_families_query.where(
                            Family.name.contains(search) | 
                            Family.surname.contains(search) |
                            Family.description.contains(search)
                        )
                    member_families_result = await db.execute(member_families_query)
                    accessible_family_ids.update([r[0] for r in member_families_result.all()])
            
            total = len(accessible_family_ids)
            
            # 分页获取家族详情
            if accessible_family_ids:
                # 转换为列表并排序（按ID降序，这样最新的在前面）
                sorted_ids = sorted(list(accessible_family_ids), reverse=True)
                
                # 分页
                paginated_ids = sorted_ids[skip:skip + limit]
                
                # 获取家族详情
                if paginated_ids:
                    detail_query = select(Family).where(Family.id.in_(paginated_ids))
                    detail_result = await db.execute(detail_query)
                    families = list(detail_result.scalars().all())
                    # 保持排序
                    families_dict = {f.id: f for f in families}
                    families = [families_dict[id] for id in paginated_ids if id in families_dict]
                else:
                    families = []
            else:
                families = []
            
            return families, total
    
    @staticmethod
    async def create_family(db: AsyncSession, family_data: FamilyCreate, creator_id: int) -> Family:
        """创建家族"""
        db_family = Family(
            name=family_data.name,
            surname=family_data.surname,
            description=family_data.description,
            history=family_data.history,
            family_motto=family_data.family_motto,
            generation_names=family_data.generation_names,
            creator_id=creator_id,
            is_public=family_data.is_public
        )
        db.add(db_family)
        await db.flush()
        
        # 自动将创建者设为管理员
        member = FamilyMember(
            family_id=db_family.id,
            user_id=creator_id,
            role="admin"
        )
        db.add(member)
        await db.flush()
        
        return db_family
    
    @staticmethod
    async def update_family(db: AsyncSession, family: Family, update_data: FamilyUpdate) -> Family:
        """更新家族信息"""
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(family, field, value)
        await db.flush()
        return family
    
    @staticmethod
    async def delete_family(db: AsyncSession, family: Family) -> None:
        """删除家族"""
        await db.delete(family)
        await db.flush()
    
    @staticmethod
    async def get_user_role_in_family(db: AsyncSession, family_id: int, user_id: int) -> Optional[str]:
        """获取用户在家族中的角色"""
        result = await db.execute(
            select(FamilyMember.role).where(
                and_(
                    FamilyMember.family_id == family_id,
                    FamilyMember.user_id == user_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_family_stats(db: AsyncSession, family_id: int) -> dict:
        """获取家族统计信息"""
        member_count = await db.execute(
            select(func.count(FamilyMember.id)).where(FamilyMember.family_id == family_id)
        )
        person_count = await db.execute(
            select(func.count(Person.id)).where(Person.family_id == family_id)
        )
        
        return {
            "member_count": member_count.scalar(),
            "person_count": person_count.scalar()
        }
    
    @staticmethod
    async def is_superuser(db: AsyncSession, user_id: int) -> bool:
        """检查用户是否为超级管理员"""
        result = await db.execute(
            select(User.is_superuser).where(User.id == user_id)
        )
        return result.scalar_one_or_none() or False
    
    @staticmethod
    async def can_edit_family(db: AsyncSession, family_id: int, user_id: int) -> bool:
        """检查用户是否有编辑家族信息的权限"""
        if await FamilyService.is_superuser(db, user_id):
            return True
        role = await FamilyService.get_user_role_in_family(db, family_id, user_id)
        return role in ["admin", "editor"]
    
    @staticmethod
    async def can_manage_family_members(db: AsyncSession, family_id: int, user_id: int) -> bool:
        """检查用户是否有管理家族成员的权限（增删改）"""
        if await FamilyService.is_superuser(db, user_id):
            return True
        role = await FamilyService.get_user_role_in_family(db, family_id, user_id)
        return role in ["admin", "family_admin"]
    
    @staticmethod
    async def can_delete_family_members(db: AsyncSession, family_id: int, user_id: int) -> bool:
        """检查用户是否有删除家族成员的权限"""
        if await FamilyService.is_superuser(db, user_id):
            return True
        role = await FamilyService.get_user_role_in_family(db, family_id, user_id)
        return role in ["admin", "family_admin"]
    
    @staticmethod
    async def can_set_family_admin(db: AsyncSession, family_id: int, user_id: int) -> bool:
        """检查用户是否有设置家族管理员的权限"""
        if await FamilyService.is_superuser(db, user_id):
            return True
        role = await FamilyService.get_user_role_in_family(db, family_id, user_id)
        return role == "admin"
    
    @staticmethod
    async def get_family_members_with_users(db: AsyncSession, family_id: int) -> List[dict]:
        """获取家族成员列表（包含用户信息）"""
        result = await db.execute(
            select(FamilyMember, User)
            .join(User, FamilyMember.user_id == User.id)
            .where(FamilyMember.family_id == family_id)
        )
        members = []
        for fm, user in result.all():
            members.append({
                "id": fm.id,
                "family_id": fm.family_id,
                "user_id": fm.user_id,
                "role": fm.role,
                "created_at": fm.created_at,
                "username": user.username,
                "email": user.email,
                "avatar_url": user.avatar_url,
                "is_superuser": user.is_superuser
            })
        return members
    
    @staticmethod
    async def update_member_role(db: AsyncSession, family_id: int, user_id: int, new_role: str) -> Optional[FamilyMember]:
        """更新家族成员角色"""
        result = await db.execute(
            select(FamilyMember).where(
                and_(
                    FamilyMember.family_id == family_id,
                    FamilyMember.user_id == user_id
                )
            )
        )
        member = result.scalar_one_or_none()
        if member:
            member.role = new_role
            await db.flush()
        return member
    
    @staticmethod
    async def add_family_member(db: AsyncSession, family_id: int, user_id: int, role: str = "member") -> FamilyMember:
        """添加家族成员"""
        member = FamilyMember(
            family_id=family_id,
            user_id=user_id,
            role=role
        )
        db.add(member)
        await db.flush()
        return member
    
    @staticmethod
    async def remove_family_member(db: AsyncSession, family_id: int, user_id: int) -> bool:
        """移除家族成员"""
        result = await db.execute(
            select(FamilyMember).where(
                and_(
                    FamilyMember.family_id == family_id,
                    FamilyMember.user_id == user_id
                )
            )
        )
        member = result.scalar_one_or_none()
        if member:
            await db.delete(member)
            await db.flush()
            return True
        return False
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
