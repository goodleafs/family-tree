from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional, Dict, Any
from app.models import Document
from app.schemas import DocumentCreate, DocumentUpdate


class DocumentService:
    @staticmethod
    async def get_document_by_id(db: AsyncSession, document_id: int) -> Optional[Document]:
        """根据ID获取文献"""
        result = await db.execute(select(Document).where(Document.id == document_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_documents_by_family(
        db: AsyncSession,
        family_id: int,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[Document], int]:
        """获取家族的文献列表"""
        query = select(Document).where(Document.family_id == family_id)
        count_query = select(func.count(Document.id)).where(Document.family_id == family_id)

        if category:
            query = query.where(Document.category == category)
            count_query = count_query.where(Document.category == category)

        if search:
            search_filter = Document.title.contains(search) | Document.description.contains(search)
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(Document.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        documents = result.scalars().all()

        return list(documents), total

    @staticmethod
    async def get_document_categories(db: AsyncSession, family_id: int) -> List[Dict[str, Any]]:
        """获取家族的文献分类统计"""
        from sqlalchemy import text
        result = await db.execute(
            text("""
                SELECT category, COUNT(*) as count 
                FROM documents 
                WHERE family_id = :family_id AND category IS NOT NULL
                GROUP BY category 
                ORDER BY count DESC
            """),
            {"family_id": family_id}
        )
        rows = result.all()
        return [{"category": row.category, "count": row.count} for row in rows]

    @staticmethod
    async def get_document_overview(db: AsyncSession, family_id: int) -> Dict[str, Any]:
        """获取文献库概览"""
        # 总数
        total_result = await db.execute(
            select(func.count(Document.id)).where(Document.family_id == family_id)
        )
        total = total_result.scalar() or 0

        # 分类统计
        categories = await DocumentService.get_document_categories(db, family_id)

        # PDF数量
        pdf_result = await db.execute(
            select(func.count(Document.id)).where(
                Document.family_id == family_id,
                Document.file_type == "pdf"
            )
        )
        pdf_count = pdf_result.scalar() or 0

        # 图片数量
        img_result = await db.execute(
            select(func.count(Document.id)).where(
                Document.family_id == family_id,
                Document.file_type == "image"
            )
        )
        image_count = img_result.scalar() or 0

        return {
            "total": total,
            "pdf_count": pdf_count,
            "image_count": image_count,
            "categories": categories
        }

    @staticmethod
    async def create_document(
        db: AsyncSession,
        document_data: DocumentCreate,
        uploader_id: int,
        file_url: str,
        file_type: str,
        file_size: Optional[int] = None,
        file_ext: Optional[str] = None
    ) -> Document:
        """创建文献记录"""
        doc = Document(
            family_id=document_data.family_id,
            title=document_data.title,
            description=document_data.description,
            file_type=file_type,
            file_url=file_url,
            file_size=file_size,
            file_ext=file_ext,
            author=document_data.author,
            document_date=document_data.document_date,
            tags=document_data.tags,
            category=document_data.category,
            uploader_id=uploader_id
        )
        db.add(doc)
        await db.flush()
        return doc

    @staticmethod
    async def update_document(
        db: AsyncSession,
        document: Document,
        update_data: DocumentUpdate | dict
    ) -> Document:
        """更新文献信息"""
        if isinstance(update_data, dict):
            update_dict = update_data
        else:
            update_dict = update_data.model_dump(exclude_unset=True)

        for field, value in update_dict.items():
            setattr(document, field, value)
        await db.flush()
        return document

    @staticmethod
    async def delete_document(db: AsyncSession, document: Document) -> None:
        """删除文献"""
        await db.delete(document)
        await db.flush()
