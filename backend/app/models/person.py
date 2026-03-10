from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Person(Base):
    __tablename__ = "persons"
    
    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    name = Column(String(50), nullable=False)
    gender = Column(String(10), nullable=True)  # male, female
    birth_date = Column(Date, nullable=True)
    death_date = Column(Date, nullable=True)
    birthplace = Column(String(100), nullable=True)
    residence = Column(String(100), nullable=True)
    occupation = Column(String(100), nullable=True)
    education = Column(String(100), nullable=True)
    biography = Column(Text, nullable=True)
    achievements = Column(Text, nullable=True)
    photo_url = Column(String(255), nullable=True)
    branch_name = Column(String(50), nullable=True)  # 支系/房系
    generation_number = Column(Integer, nullable=True)  # 世代
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    family = relationship("Family", back_populates="persons")
    creator = relationship("User", back_populates="created_persons")
    memorial_hall = relationship("MemorialHall", back_populates="person", uselist=False)
    relationships_as_person = relationship(
        "Relationship", 
        foreign_keys="Relationship.person_id",
        back_populates="person"
    )
    relationships_as_relative = relationship(
        "Relationship",
        foreign_keys="Relationship.relative_id", 
        back_populates="relative"
    )
    
    def __repr__(self):
        return f"<Person {self.name}>"

class Relationship(Base):
    __tablename__ = "relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=False)
    relative_id = Column(Integer, ForeignKey("persons.id"), nullable=False)
    relation_type = Column(String(20), nullable=False)  # father, mother, spouse, child
    is_primary = Column(Boolean, default=True)  # 是否主要配偶
    marriage_date = Column(Date, nullable=True)
    divorce_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    person = relationship(
        "Person",
        foreign_keys=[person_id],
        back_populates="relationships_as_person"
    )
    relative = relationship(
        "Person", 
        foreign_keys=[relative_id],
        back_populates="relationships_as_relative"
    )
    
    def __repr__(self):
        return f"<Relationship {self.person_id} -{self.relation_type}-> {self.relative_id}>"
