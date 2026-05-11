from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pathlib import Path
import traceback

from app.database import get_db
from app.schemas import (
    DocumentCreate, DocumentUpdate, DocumentResponse, DocumentListResponse,
    DocumentOverviewResponse
)
from app.services import DocumentService, FamilyService
from app.routers.auth import get_current_active_user
from app.utils import save_upload_file, delete_file

router = APIRouter(prefix="/documents", tags=["文献库"])


@router.get("/family/{family_id}", response_model=DocumentListResponse)
async def list_family_documents(
    family_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """获取家族的文献列表"""
    family = await FamilyService.get_family_by_id(db, family_id)
    if not family:
        raise HTTPException(status_code=404, detail="家族不存在")

    if not family.is_public:
        role = await FamilyService.get_user_role_in_family(db, family_id, current_user.id)
        if not role:
            raise HTTPException(status_code=403, detail="您没有权限访问此家族")

    documents, total = await DocumentService.get_documents_by_family(
        db, family_id, skip=skip, limit=limit, category=category, search=search
    )

    return {"total": total, "items": [DocumentResponse.model_validate(d) for d in documents]}


@router.get("/family/{family_id}/overview", response_model=DocumentOverviewResponse)
async def get_document_overview(
    family_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """获取文献库概览（分类统计）"""
    family = await FamilyService.get_family_by_id(db, family_id)
    if not family:
        raise HTTPException(status_code=404, detail="家族不存在")

    if not family.is_public:
        role = await FamilyService.get_user_role_in_family(db, family_id, current_user.id)
        if not role:
            raise HTTPException(status_code=403, detail="您没有权限访问此家族")

    overview = await DocumentService.get_document_overview(db, family_id)
    return DocumentOverviewResponse(**overview)


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    family_id: int = Query(...),
    title: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    document_date: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """上传文献（支持PDF和图片）"""
    try:
        family = await FamilyService.get_family_by_id(db, family_id)
        if not family:
            raise HTTPException(status_code=404, detail="家族不存在")

        role = await FamilyService.get_user_role_in_family(db, family_id, current_user.id)
        if not role:
            raise HTTPException(status_code=403, detail="您没有权限上传文献")

        if not title:
            title = file.filename or "未命名文献"

        # 保存文件
        file_path = save_upload_file(file, subfolder="documents", validate_type="document")

        # 确定文件类型
        content_type = file.content_type or ""
        if content_type.startswith("image/"):
            file_type = "image"
        elif content_type == "application/pdf":
            file_type = "pdf"
        elif "word" in content_type:
            file_type = "doc"
        else:
            file_type = "other"

        file_ext = Path(file.filename).suffix.lower() if file.filename else None

        doc_data = DocumentCreate(
            family_id=family_id,
            title=title,
            description=description,
            author=author,
            document_date=document_date,
            tags=tags,
            category=category or "other"
        )

        doc = await DocumentService.create_document(
            db=db,
            document_data=doc_data,
            uploader_id=current_user.id,
            file_url=file_path,
            file_type=file_type,
            file_size=file.size,
            file_ext=file_ext
        )
        await db.commit()

        return DocumentResponse.model_validate(doc)
    except HTTPException:
        raise
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """获取文献详情"""
    doc = await DocumentService.get_document_by_id(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="文献不存在")

    family = await FamilyService.get_family_by_id(db, doc.family_id)
    if not family.is_public:
        role = await FamilyService.get_user_role_in_family(db, doc.family_id, current_user.id)
        if not role:
            raise HTTPException(status_code=403, detail="您没有权限访问此文献")

    return DocumentResponse.model_validate(doc)


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    doc_update: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """更新文献信息"""
    doc = await DocumentService.get_document_by_id(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="文献不存在")

    role = await FamilyService.get_user_role_in_family(db, doc.family_id, current_user.id)
    if not role:
        raise HTTPException(status_code=403, detail="您没有权限编辑此文献")

    try:
        updated = await DocumentService.update_document(db, doc, doc_update)
        await db.commit()
        return DocumentResponse.model_validate(updated)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """删除文献"""
    doc = await DocumentService.get_document_by_id(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="文献不存在")

    role = await FamilyService.get_user_role_in_family(db, doc.family_id, current_user.id)
    if not role:
        raise HTTPException(status_code=403, detail="您没有权限删除此文献")

    # 删除物理文件
    if doc.file_url:
        delete_file(doc.file_url)

    await DocumentService.delete_document(db, doc)
    await db.commit()
    return None
