from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class MemorialHall(Base):
    """灵堂模型"""
    __tablename__ = "memorial_halls"
    
    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=False, unique=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 灵堂布置
    offerings = Column(JSON, default=list)  # 贡品列表 [{"name": "水果", "icon": "🍎"}]
    incense_count = Column(Integer, default=0)  # 香火数量
    
    # 统计
    worship_count = Column(Integer, default=0)  # 祭拜人数
    
    # 状态
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    person = relationship("Person", back_populates="memorial_hall")
    family = relationship("Family", back_populates="memorial_halls")
    creator = relationship("User", back_populates="created_memorial_halls")
    worship_records = relationship("WorshipRecord", back_populates="memorial_hall", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MemorialHall person_id={self.person_id}>"

class WorshipRecord(Base):
    """祭拜记录模型"""
    __tablename__ = "worship_records"
    
    id = Column(Integer, primary_key=True, index=True)
    memorial_hall_id = Column(Integer, ForeignKey("memorial_halls.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 可为空，支持匿名祭拜
    
    # 祭拜信息
    worship_type = Column(String(20), default="kowtow")  # kowtow-叩拜, incense-上香, offering-献贡
    message = Column(Text, nullable=True)  # 留言
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    memorial_hall = relationship("MemorialHall", back_populates="worship_records")
    user = relationship("User", back_populates="worship_records")
    
    def __repr__(self):
        return f"<WorshipRecord hall_id={self.memorial_hall_id} user_id={self.user_id}>"
