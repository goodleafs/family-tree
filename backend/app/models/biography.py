from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class PersonBiography(Base):
    """人物传记模型 - 为家族名人提供独立、丰富的传记页面"""
    __tablename__ = "person_biographies"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=False, unique=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    title = Column(String(200), nullable=True)  # 传记标题，如"XX公传"
    subtitle = Column(String(300), nullable=True)  # 副标题
    summary = Column(Text, nullable=True)  # 传记摘要/导语
    content = Column(Text, nullable=False)  # 传记正文（支持HTML格式富文本）
    achievements = Column(Text, nullable=True)  # 主要成就/贡献
    portrait_url = Column(String(255), nullable=True)  # 传记专用肖像照
    is_published = Column(Boolean, default=True)
    views_count = Column(Integer, default=0)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    person = relationship("Person", back_populates="biography_entry")
    family = relationship("Family", back_populates="biographies")
    creator = relationship("User", back_populates="created_biographies")

    def __repr__(self):
        return f"<PersonBiography person_id={self.person_id}>"
