from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Document(Base):
    """文献/文档模型"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    file_type = Column(String(50), nullable=False)  # pdf, image, doc, txt
    file_url = Column(String(255), nullable=False)
    file_size = Column(BigInteger, nullable=True)
    file_ext = Column(String(20), nullable=True)  # 文件扩展名
    author = Column(String(100), nullable=True)  # 文献作者
    document_date = Column(String(50), nullable=True)  # 文献日期（原文中的日期）
    tags = Column(String(500), nullable=True)  # 标签，逗号分隔
    category = Column(String(50), nullable=True)  # 分类: genealogy/老谱, contract/契约, writing/著作, other/其他
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    family = relationship("Family", back_populates="documents")
    uploader = relationship("User", back_populates="uploaded_documents")

    def __repr__(self):
        return f"<Document {self.title}>"
