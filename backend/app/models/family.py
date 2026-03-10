from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Family(Base):
    __tablename__ = "families"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    surname = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    history = Column(Text, nullable=True)
    family_motto = Column(Text, nullable=True)
    generation_names = Column(JSON, nullable=True)  # 字辈排列
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    creator = relationship("User", back_populates="created_families")
    members = relationship("FamilyMember", back_populates="family")
    persons = relationship("Person", back_populates="family")
    memorial_halls = relationship("MemorialHall", back_populates="family")
    
    def __repr__(self):
        return f"<Family {self.name}>"

class FamilyMember(Base):
    __tablename__ = "family_members"
    
    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(20), default="member")  # admin, family_admin, editor, member
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    family = relationship("Family", back_populates="members")
    user = relationship("User", back_populates="family_memberships")
    
    __table_args__ = (
        UniqueConstraint('family_id', 'user_id', name='unique_family_member'),
    )
    
    def __repr__(self):
        return f"<FamilyMember family={self.family_id} user={self.user_id}>"
