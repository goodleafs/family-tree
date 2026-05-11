from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Optional, Dict, Any
from app.models import MeritDonor
from app.schemas import MeritDonorCreate, MeritDonorUpdate


class MeritService:
    @staticmethod
    async def get_donor_by_id(db: AsyncSession, donor_id: int) -> Optional[MeritDonor]:
        result = await db.execute(select(MeritDonor).where(MeritDonor.id == donor_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_donors_by_family(
        db: AsyncSession,
        family_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[MeritDonor], int, float]:
        """获取功德榜列表，按金额降序排列"""
        count_query = select(func.count(MeritDonor.id)).where(MeritDonor.family_id == family_id)
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        sum_query = select(func.coalesce(func.sum(MeritDonor.amount), 0)).where(MeritDonor.family_id == family_id)
        sum_result = await db.execute(sum_query)
        total_amount = float(sum_result.scalar() or 0)

        query = (
            select(MeritDonor)
            .where(MeritDonor.family_id == family_id)
            .order_by(desc(MeritDonor.sort_order), desc(MeritDonor.amount), MeritDonor.created_at)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        donors = result.scalars().all()

        return list(donors), total, total_amount

    @staticmethod
    async def create_donor(db: AsyncSession, data: MeritDonorCreate, created_by: int) -> MeritDonor:
        donor = MeritDonor(
            family_id=data.family_id,
            donor_name=data.donor_name,
            amount=data.amount,
            donation_date=data.donation_date,
            remarks=data.remarks,
            sort_order=data.sort_order,
            created_by=created_by
        )
        db.add(donor)
        await db.flush()
        return donor

    @staticmethod
    async def update_donor(db: AsyncSession, donor: MeritDonor, update_data: MeritDonorUpdate | dict) -> MeritDonor:
        if isinstance(update_data, dict):
            update_dict = update_data
        else:
            update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(donor, field, value)
        await db.flush()
        return donor

    @staticmethod
    async def delete_donor(db: AsyncSession, donor: MeritDonor) -> None:
        await db.delete(donor)
        await db.flush()
