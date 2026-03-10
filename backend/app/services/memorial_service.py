from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.models import MemorialHall, WorshipRecord, Person, User
from app.schemas import MemorialHallCreate, MemorialHallUpdate, OfferingItem

class MemorialService:
    @staticmethod
    async def get_memorial_hall_by_id(db: AsyncSession, hall_id: int) -> Optional[MemorialHall]:
        """根据ID获取灵堂"""
        result = await db.execute(
            select(MemorialHall)
            .where(MemorialHall.id == hall_id)
            .options(
                selectinload(MemorialHall.person),
                selectinload(MemorialHall.creator)
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_memorial_hall_by_person(db: AsyncSession, person_id: int) -> Optional[MemorialHall]:
        """根据逝者ID获取灵堂"""
        result = await db.execute(
            select(MemorialHall).where(MemorialHall.person_id == person_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_memorial_halls(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        family_id: Optional[int] = None
    ) -> tuple[List[MemorialHall], int]:
        """获取灵堂列表"""
        query = select(MemorialHall).options(
            selectinload(MemorialHall.person),
            selectinload(MemorialHall.creator)
        )
        count_query = select(func.count(MemorialHall.id))
        
        if family_id:
            query = query.where(MemorialHall.family_id == family_id)
            count_query = count_query.where(MemorialHall.family_id == family_id)
        
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        query = query.offset(skip).limit(limit).order_by(MemorialHall.created_at.desc())
        result = await db.execute(query)
        halls = result.scalars().all()
        
        return list(halls), total
    
    @staticmethod
    async def create_memorial_hall(
        db: AsyncSession,
        person_id: int,
        family_id: int,
        created_by: int,
        offerings: Optional[List[OfferingItem]] = None
    ) -> MemorialHall:
        """创建灵堂"""
        # 默认贡品
        default_offerings = [
            {"name": "鲜花", "icon": "🌸"},
            {"name": "水果", "icon": "🍎"},
            {"name": "糕点", "icon": "🥮"}
        ]
        
        hall = MemorialHall(
            person_id=person_id,
            family_id=family_id,
            created_by=created_by,
            offerings=[o.dict() if isinstance(o, OfferingItem) else o for o in (offerings or default_offerings)],
            incense_count=0,
            worship_count=0
        )
        db.add(hall)
        await db.flush()
        return hall
    
    @staticmethod
    async def update_memorial_hall(
        db: AsyncSession,
        hall: MemorialHall,
        update_data: MemorialHallUpdate
    ) -> MemorialHall:
        """更新灵堂"""
        if update_data.offerings is not None:
            hall.offerings = [o.dict() if isinstance(o, OfferingItem) else o for o in update_data.offerings]
        if update_data.is_active is not None:
            hall.is_active = update_data.is_active
        await db.flush()
        return hall
    
    @staticmethod
    async def delete_memorial_hall(db: AsyncSession, hall: MemorialHall) -> None:
        """删除灵堂"""
        await db.delete(hall)
        await db.flush()
    
    @staticmethod
    async def add_worship_record(
        db: AsyncSession,
        hall_id: int,
        user_id: Optional[int],
        worship_type: str,
        message: Optional[str] = None
    ) -> WorshipRecord:
        """添加祭拜记录"""
        record = WorshipRecord(
            memorial_hall_id=hall_id,
            user_id=user_id,
            worship_type=worship_type,
            message=message
        )
        db.add(record)
        
        # 更新灵堂统计
        hall = await MemorialService.get_memorial_hall_by_id(db, hall_id)
        if hall:
            hall.worship_count += 1
            if worship_type == "incense":
                hall.incense_count += 1
        
        await db.flush()
        return record
    
    @staticmethod
    async def get_worship_records(
        db: AsyncSession,
        hall_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[WorshipRecord], int]:
        """获取祭拜记录列表"""
        query = select(WorshipRecord).where(WorshipRecord.memorial_hall_id == hall_id).options(
            selectinload(WorshipRecord.user)
        )
        count_query = select(func.count(WorshipRecord.id)).where(WorshipRecord.memorial_hall_id == hall_id)
        
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        query = query.offset(skip).limit(limit).order_by(WorshipRecord.created_at.desc())
        result = await db.execute(query)
        records = result.scalars().all()
        
        return list(records), total
    
    @staticmethod
    async def get_eligible_persons(db: AsyncSession, family_id: int) -> List[Person]:
        """获取可以布置灵堂的逝者列表（有death_date且没有灵堂的）"""
        # 获取已有灵堂的person_id列表
        existing_halls = await db.execute(
            select(MemorialHall.person_id).where(MemorialHall.family_id == family_id)
        )
        existing_person_ids = {r[0] for r in existing_halls.all()}
        
        # 查询有death_date且没有灵堂的成员
        query = select(Person).where(
            and_(
                Person.family_id == family_id,
                Person.death_date != None,
                Person.id.notin_(existing_person_ids) if existing_person_ids else True
            )
        )
        result = await db.execute(query)
        return list(result.scalars().all())
