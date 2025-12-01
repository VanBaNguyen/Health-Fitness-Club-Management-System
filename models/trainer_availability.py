from datetime import time
from sqlalchemy import Column, Integer, Time, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, Session as OrmSession
from user import Base, User


class TrainerAvailability(Base):
    __tablename__ = "trainer_availability"

    id = Column(Integer, primary_key=True, index=True)
    trainer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    day_of_week = Column(Integer, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    trainer = relationship("User")

    __table_args__ = (
        UniqueConstraint("trainer_id", "day_of_week", "start_time", "end_time", name="uq_trainer_availability_exact"),
    )

    @classmethod
    def create_window(
        cls,
        db: "OrmSession",
        trainer_id: int,
        day_of_week: int,
        start_time: time,
        end_time: time,
    ) -> "TrainerAvailability":
        if end_time <= start_time:
            raise ValueError("end_time must be after start_time")
        
        if not (1 <= day_of_week <= 7):
            raise ValueError("day_of_week must be between 1 and 7")

        overlap = (
            db.query(cls)
            .filter(
                cls.trainer_id == trainer_id,
                cls.day_of_week == day_of_week,
                cls.start_time < end_time,
                cls.end_time > start_time,
            )
            .first()
        )

        if overlap is not None:
            raise ValueError("Availability window overlaps with an existing window.")

        window = cls(
            trainer_id=trainer_id,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
        )
        db.add(window)
        db.commit()
        db.refresh(window)
        return window
