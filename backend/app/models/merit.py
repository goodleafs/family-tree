from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class MeritDonor(Base):
    """功德榜捐款记录"""
    __tablename__ = "merit_donors"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    donor_name = Column(String(100), nullable=False)  # 捐款人姓名
    amount = Column(Float, nullable=False)  # 捐款金额
    donation_date = Column(Date, nullable=True)  # 捐款日期
    remarks = Column(Text, nullable=True)  # 备注
    sort_order = Column(Integer, default=0)  # 排序权重（越大越靠前）
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    family = relationship("Family", back_populates="merit_donors")
    creator = relationship("User", back_populates="created_merit_donors")

    def __repr__(self):
        return f"<MeritDonor {self.donor_name} {self.amount}>"
