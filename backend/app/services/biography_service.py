from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.models import PersonBiography, Person
from app.schemas import BiographyCreate, BiographyUpdate


class BiographyService:
    @staticmethod
    async def get_biography_by_id(db: AsyncSession, biography_id: int) -> Optional[PersonBiography]:
        """根据ID获取传记"""
        result = await db.execute(
            select(PersonBiography)
            .where(PersonBiography.id == biography_id)
            .options(selectinload(PersonBiography.person))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_biography_by_person(db: AsyncSession, person_id: int) -> Optional[PersonBiography]:
        """根据人员ID获取传记"""
        result = await db.execute(
            select(PersonBiography)
            .where(PersonBiography.person_id == person_id)
            .options(selectinload(PersonBiography.person))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_biographies_by_family(
        db: AsyncSession,
        family_id: int,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None
    ) -> tuple[List[PersonBiography], int]:
        """获取家族的传记列表"""
        query = select(PersonBiography).where(PersonBiography.family_id == family_id).options(
            selectinload(PersonBiography.person)
        )
        count_query = select(func.count(PersonBiography.id)).where(PersonBiography.family_id == family_id)

        if search:
            # 搜索传记标题或关联的人员名称
            search_filter = PersonBiography.title.contains(search)
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(PersonBiography.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        biographies = result.scalars().all()

        return list(biographies), total

    @staticmethod
    async def create_biography(
        db: AsyncSession,
        bio_data: BiographyCreate,
        created_by: int
    ) -> PersonBiography:
        """创建传记"""
        bio = PersonBiography(
            person_id=bio_data.person_id,
            family_id=bio_data.family_id,
            title=bio_data.title,
            subtitle=bio_data.subtitle,
            summary=bio_data.summary,
            content=bio_data.content,
            achievements=bio_data.achievements,
            portrait_url=bio_data.portrait_url,
            is_published=bio_data.is_published,
            created_by=created_by
        )
        db.add(bio)
        await db.flush()
        return bio

    @staticmethod
    async def update_biography(
        db: AsyncSession,
        biography: PersonBiography,
        update_data: BiographyUpdate | dict
    ) -> PersonBiography:
        """更新传记"""
        if isinstance(update_data, dict):
            update_dict = update_data
        else:
            update_dict = update_data.model_dump(exclude_unset=True)

        for field, value in update_dict.items():
            setattr(biography, field, value)
        await db.flush()
        return biography

    @staticmethod
    async def delete_biography(db: AsyncSession, biography: PersonBiography) -> None:
        """删除传记"""
        await db.delete(biography)
        await db.flush()

    @staticmethod
    async def increment_views(db: AsyncSession, biography: PersonBiography) -> None:
        """增加浏览次数"""
        biography.views_count += 1
        await db.flush()

    @staticmethod
    async def get_eligible_persons(db: AsyncSession, family_id: int) -> List[Person]:
        """获取可以创建传记的人员列表（尚未有传记的）"""
        # 获取已有传记的person_id列表
        existing = await db.execute(
            select(PersonBiography.person_id).where(PersonBiography.family_id == family_id)
        )
        existing_ids = {r[0] for r in existing.all()}

        query = select(Person).where(
            and_(
                Person.family_id == family_id,
                Person.id.notin_(existing_ids) if existing_ids else True
            )
        )
        result = await db.execute(query)
        return list(result.scalars().all())
