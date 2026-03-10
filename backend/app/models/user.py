from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True)
    phone = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    avatar_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    created_families = relationship("Family", back_populates="creator")
    family_memberships = relationship("FamilyMember", back_populates="user")
    created_persons = relationship("Person", back_populates="creator")
    created_memorial_halls = relationship("MemorialHall", back_populates="creator")
    worship_records = relationship("WorshipRecord", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}>"
