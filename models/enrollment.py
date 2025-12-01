from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, PrimaryKeyConstraint
from user import Base


class Enrollment(Base):
    __tablename__ = "enrollments"

    member_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False, index=True)
    registration_date = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        PrimaryKeyConstraint('member_id', 'class_id', name='pk_enrollment'),
    )

