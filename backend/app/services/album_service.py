from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import date
from app.models import Album, Photo
from app.schemas import AlbumCreate, AlbumUpdate, PhotoCreate, PhotoUpdate


class AlbumService:
    @staticmethod
    async def get_album_by_id(db: AsyncSession, album_id: int) -> Optional[Album]:
        """根据ID获取相册"""
        result = await db.execute(
            select(Album)
            .where(Album.id == album_id)
            .options(selectinload(Album.photos))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_albums_by_family(
        db: AsyncSession,
        family_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Album], int]:
        """获取家族相册列表"""
        query = select(Album).where(Album.family_id == family_id)
        count_query = select(func.count(Album.id)).where(Album.family_id == family_id)

        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(Album.sort_order, Album.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        albums = result.scalars().all()

        return list(albums), total

    @staticmethod
    async def get_album_photo_count(db: AsyncSession, album_id: int) -> int:
        """获取相册中的照片数量"""
        result = await db.execute(
            select(func.count(Photo.id)).where(Photo.album_id == album_id)
        )
        return result.scalar() or 0

    @staticmethod
    async def create_album(db: AsyncSession, album_data: AlbumCreate, created_by: int) -> Album:
        """创建相册"""
        album = Album(
            family_id=album_data.family_id,
            name=album_data.name,
            description=album_data.description,
            sort_order=album_data.sort_order,
            created_by=created_by
        )
        db.add(album)
        await db.flush()
        return album

    @staticmethod
    async def update_album(db: AsyncSession, album: Album, update_data: AlbumUpdate | dict) -> Album:
        """更新相册"""
        if isinstance(update_data, dict):
            update_dict = update_data
        else:
            update_dict = update_data.model_dump(exclude_unset=True)

        for field, value in update_dict.items():
            setattr(album, field, value)
        await db.flush()
        return album

    @staticmethod
    async def delete_album(db: AsyncSession, album: Album) -> None:
        """删除相册"""
        await db.delete(album)
        await db.flush()

    # ---- Photo methods ----

    @staticmethod
    async def get_photo_by_id(db: AsyncSession, photo_id: int) -> Optional[Photo]:
        """根据ID获取照片"""
        result = await db.execute(select(Photo).where(Photo.id == photo_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_photos_by_album(
        db: AsyncSession,
        album_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[Photo], int]:
        """获取相册中的照片列表"""
        query = select(Photo).where(Photo.album_id == album_id)
        count_query = select(func.count(Photo.id)).where(Photo.album_id == album_id)

        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(Photo.taken_date.desc().nullslast(), Photo.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        photos = result.scalars().all()

        return list(photos), total

    @staticmethod
    async def get_photos_by_family(
        db: AsyncSession,
        family_id: int,
        skip: int = 0,
        limit: int = 50,
        year: Optional[int] = None
    ) -> tuple[List[Photo], int]:
        """获取家族的所有照片（可按年份筛选）"""
        query = select(Photo).where(Photo.family_id == family_id)
        count_query = select(func.count(Photo.id)).where(Photo.family_id == family_id)

        if year is not None:
            query = query.where(Photo.taken_year == year)
            count_query = count_query.where(Photo.taken_year == year)

        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(Photo.taken_date.desc().nullslast(), Photo.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        photos = result.scalars().all()

        return list(photos), total

    @staticmethod
    async def get_photo_timeline(db: AsyncSession, family_id: int) -> Dict[str, Any]:
        """获取照片时间轴数据"""
        # 获取所有有年份的照片
        result = await db.execute(
            select(Photo).where(
                and_(
                    Photo.family_id == family_id,
                    Photo.taken_year != None
                )
            ).order_by(Photo.taken_year.desc(), Photo.taken_month.desc())
        )
        photos = result.scalars().all()

        # 按年份分组
        timeline: Dict[int, List[Photo]] = {}
        years_set: set = set()
        for photo in photos:
            if photo.taken_year:
                if photo.taken_year not in timeline:
                    timeline[photo.taken_year] = []
                timeline[photo.taken_year].append(photo)
                years_set.add(photo.taken_year)

        years = sorted(list(years_set), reverse=True)
        total = sum(len(v) for v in timeline.values())

        return {
            "total": total,
            "years": years,
            "timeline": [{"year": year, "photos": timeline[year]} for year in years]
        }

    @staticmethod
    async def create_photo(
        db: AsyncSession,
        family_id: int,
        uploader_id: int,
        url: str,
        thumbnail_url: Optional[str] = None,
        album_id: Optional[int] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        taken_date: Optional[date] = None,
        file_size: Optional[int] = None
    ) -> Photo:
        """创建照片记录"""
        taken_year = taken_date.year if taken_date else None
        taken_month = taken_date.month if taken_date else None

        photo = Photo(
            album_id=album_id,
            family_id=family_id,
            title=title,
            description=description,
            url=url,
            thumbnail_url=thumbnail_url,
            taken_date=taken_date,
            taken_year=taken_year,
            taken_month=taken_month,
            file_size=file_size,
            uploader_id=uploader_id
        )
        db.add(photo)

        # 如果没有指定专辑，或者该相册还没有封面，设置此照片为封面
        if album_id:
            album = await AlbumService.get_album_by_id(db, album_id)
            if album and not album.cover_url:
                album.cover_url = url

        await db.flush()
        return photo

    @staticmethod
    async def update_photo(db: AsyncSession, photo: Photo, update_data: PhotoUpdate | dict) -> Photo:
        """更新照片信息"""
        if isinstance(update_data, dict):
            update_dict = update_data
        else:
            update_dict = update_data.model_dump(exclude_unset=True)

        # 如果更新拍摄日期，同步更新年份月份
        if "taken_date" in update_dict:
            td = update_dict["taken_date"]
            if td:
                photo.taken_year = td.year if hasattr(td, 'year') else None
                photo.taken_month = td.month if hasattr(td, 'month') else None

        for field, value in update_dict.items():
            setattr(photo, field, value)
        await db.flush()
        return photo

    @staticmethod
    async def delete_photo(db: AsyncSession, photo: Photo) -> None:
        """删除照片"""
        await db.delete(photo)
        await db.flush()
