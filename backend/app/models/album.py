from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Album(Base):
    """相册模型"""
    __tablename__ = "albums"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    cover_url = Column(String(255), nullable=True)  # 封面照片URL
    sort_order = Column(Integer, default=0)  # 排序
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    family = relationship("Family", back_populates="albums")
    creator = relationship("User", back_populates="created_albums")
    photos = relationship("Photo", back_populates="album", cascade="all, delete-orphan",
                          order_by="Photo.taken_date.desc()")

    def __repr__(self):
        return f"<Album {self.name}>"


class Photo(Base):
    """照片模型"""
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    album_id = Column(Integer, ForeignKey("albums.id"), nullable=True)  # 可为空（未归类照片）
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    title = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    url = Column(String(255), nullable=False)
    thumbnail_url = Column(String(255), nullable=True)
    taken_date = Column(Date, nullable=True)  # 拍摄日期
    taken_year = Column(Integer, nullable=True)  # 拍摄年份（用于时间轴）
    taken_month = Column(Integer, nullable=True)
    file_size = Column(Integer, nullable=True)
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    album = relationship("Album", back_populates="photos")
    family = relationship("Family", back_populates="photos")
    uploader = relationship("User", back_populates="uploaded_photos")

    def __repr__(self):
        return f"<Photo {self.title or self.url}>"
