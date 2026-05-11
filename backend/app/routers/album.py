from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import traceback

from app.database import get_db
from app.schemas import (
    AlbumCreate, AlbumUpdate, AlbumResponse, AlbumDetailResponse, AlbumListResponse,
    PhotoResponse, PhotoListResponse, AlbumTimelineResponse
)
from app.services import AlbumService, FamilyService
from app.routers.auth import get_current_active_user
from app.utils import save_upload_file, delete_file

router = APIRouter(prefix="/albums", tags=["家族相册"])


@router.get("/family/{family_id}", response_model=AlbumListResponse)
async def list_family_albums(
    family_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """获取家族的相册列表"""
    family = await FamilyService.get_family_by_id(db, family_id)
    if not family:
        raise HTTPException(status_code=404, detail="家族不存在")

    if not family.is_public:
        role = await FamilyService.get_user_role_in_family(db, family_id, current_user.id)
        if not role:
            raise HTTPException(status_code=403, detail="您没有权限访问此家族")

    albums, total = await AlbumService.get_albums_by_family(db, family_id, skip=skip, limit=limit)

    # 为每个相册添加photo_count
    items = []
    for album in albums:
        photo_count = await AlbumService.get_album_photo_count(db, album.id)
        album_dict = {
            **{c.name: getattr(album, c.name) for c in album.__table__.columns},
            "photo_count": photo_count
        }
        items.append(AlbumResponse.model_validate(album_dict))

    return {"total": total, "items": items}


@router.post("", response_model=AlbumResponse, status_code=status.HTTP_201_CREATED)
async def create_album(
    album_data: AlbumCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """创建相册"""
    family = await FamilyService.get_family_by_id(db, album_data.family_id)
    if not family:
        raise HTTPException(status_code=404, detail="家族不存在")

    role = await FamilyService.get_user_role_in_family(db, album_data.family_id, current_user.id)
    if not role:
        raise HTTPException(status_code=403, detail="您没有权限在此家族创建相册")

    try:
        album = await AlbumService.create_album(db, album_data, current_user.id)
        await db.commit()
        return AlbumResponse(
            id=album.id,
            family_id=album.family_id,
            name=album.name,
            description=album.description,
            cover_url=album.cover_url,
            sort_order=album.sort_order,
            created_by=album.created_by,
            created_at=album.created_at,
            updated_at=album.updated_at,
            photo_count=0
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{album_id}", response_model=AlbumDetailResponse)
async def get_album(
    album_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """获取相册详情（含照片列表）"""
    album = await AlbumService.get_album_by_id(db, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="相册不存在")

    family = await FamilyService.get_family_by_id(db, album.family_id)
    if not family.is_public:
        role = await FamilyService.get_user_role_in_family(db, album.family_id, current_user.id)
        if not role:
            raise HTTPException(status_code=403, detail="您没有权限访问此相册")

    photo_count = await AlbumService.get_album_photo_count(db, album_id)
    return AlbumDetailResponse(
        id=album.id,
        family_id=album.family_id,
        name=album.name,
        description=album.description,
        cover_url=album.cover_url,
        sort_order=album.sort_order,
        created_by=album.created_by,
        created_at=album.created_at,
        updated_at=album.updated_at,
        photo_count=photo_count,
        photos=[PhotoResponse.model_validate(p) for p in album.photos]
    )


@router.put("/{album_id}", response_model=AlbumResponse)
async def update_album(
    album_id: int,
    album_update: AlbumUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """更新相册信息"""
    album = await AlbumService.get_album_by_id(db, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="相册不存在")

    role = await FamilyService.get_user_role_in_family(db, album.family_id, current_user.id)
    if not role:
        raise HTTPException(status_code=403, detail="您没有权限编辑此相册")

    try:
        updated = await AlbumService.update_album(db, album, album_update)
        await db.commit()
        photo_count = await AlbumService.get_album_photo_count(db, album_id)
        return AlbumResponse(
            id=updated.id,
            family_id=updated.family_id,
            name=updated.name,
            description=updated.description,
            cover_url=updated.cover_url,
            sort_order=updated.sort_order,
            created_by=updated.created_by,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
            photo_count=photo_count
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{album_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_album(
    album_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """删除相册"""
    album = await AlbumService.get_album_by_id(db, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="相册不存在")

    role = await FamilyService.get_user_role_in_family(db, album.family_id, current_user.id)
    if not role:
        raise HTTPException(status_code=403, detail="您没有权限删除此相册")

    await AlbumService.delete_album(db, album)
    await db.commit()
    return None


# ---- Photo endpoints ----

@router.get("/{album_id}/photos", response_model=PhotoListResponse)
async def list_album_photos(
    album_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """获取相册中的照片列表"""
    album = await AlbumService.get_album_by_id(db, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="相册不存在")

    family = await FamilyService.get_family_by_id(db, album.family_id)
    if not family.is_public:
        role = await FamilyService.get_user_role_in_family(db, album.family_id, current_user.id)
        if not role:
            raise HTTPException(status_code=403, detail="您没有权限访问此相册")

    photos, total = await AlbumService.get_photos_by_album(db, album_id, skip=skip, limit=limit)
    return {"total": total, "items": [PhotoResponse.model_validate(p) for p in photos]}


@router.post("/{album_id}/photos", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def upload_album_photo(
    album_id: int,
    file: UploadFile = File(...),
    title: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    taken_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """上传照片到相册"""
    try:
        album = await AlbumService.get_album_by_id(db, album_id)
        if not album:
            raise HTTPException(status_code=404, detail="相册不存在")

        role = await FamilyService.get_user_role_in_family(db, album.family_id, current_user.id)
        if not role:
            raise HTTPException(status_code=403, detail="您没有权限上传照片")

        # 保存文件
        from datetime import date
        file_path = save_upload_file(file, subfolder="albums", validate_type="image")

        # 生成缩略图URL
        from pathlib import Path
        file_name = Path(file_path).name
        thumb_url = f"/uploads/albums/thumb_{file_name}"

        # 解析拍摄日期
        parsed_date = None
        if taken_date:
            try:
                parsed_date = date.fromisoformat(taken_date)
            except ValueError:
                pass

        photo = await AlbumService.create_photo(
            db=db,
            family_id=album.family_id,
            uploader_id=current_user.id,
            url=file_path,
            thumbnail_url=thumb_url,
            album_id=album_id,
            title=title,
            description=description,
            taken_date=parsed_date,
            file_size=file.size
        )
        await db.commit()

        return PhotoResponse.model_validate(photo)
    except HTTPException:
        raise
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.put("/photos/{photo_id}", response_model=PhotoResponse)
async def update_photo(
    photo_id: int,
    photo_update: dict,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """更新照片信息"""
    photo = await AlbumService.get_photo_by_id(db, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="照片不存在")

    role = await FamilyService.get_user_role_in_family(db, photo.family_id, current_user.id)
    if not role:
        raise HTTPException(status_code=403, detail="您没有权限编辑此照片")

    try:
        updated = await AlbumService.update_photo(db, photo, photo_update)
        await db.commit()
        return PhotoResponse.model_validate(updated)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """删除照片"""
    photo = await AlbumService.get_photo_by_id(db, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="照片不存在")

    role = await FamilyService.get_user_role_in_family(db, photo.family_id, current_user.id)
    if not role:
        raise HTTPException(status_code=403, detail="您没有权限删除此照片")

    # 删除物理文件
    if photo.url:
        delete_file(photo.url)
    if photo.thumbnail_url:
        delete_file(photo.thumbnail_url)

    await AlbumService.delete_photo(db, photo)
    await db.commit()
    return None


# ---- Timeline endpoint ----

@router.get("/family/{family_id}/timeline", response_model=AlbumTimelineResponse)
async def get_photo_timeline(
    family_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """获取家族照片时间轴"""
    family = await FamilyService.get_family_by_id(db, family_id)
    if not family:
        raise HTTPException(status_code=404, detail="家族不存在")

    if not family.is_public:
        role = await FamilyService.get_user_role_in_family(db, family_id, current_user.id)
        if not role:
            raise HTTPException(status_code=403, detail="您没有权限访问此家族")

    timeline_data = await AlbumService.get_photo_timeline(db, family_id)
    return AlbumTimelineResponse(**timeline_data)
