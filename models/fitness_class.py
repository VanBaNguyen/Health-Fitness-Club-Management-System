from datetime import time
from sqlalchemy import Column, Integer, String, Time, ForeignKey
from sqlalchemy.orm import relationship, Session as OrmSession
from user import Base, User
from room import Room
from trainer_availability import TrainerAvailability


class FitnessClass(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    trainer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True, index=True)
    day_of_week = Column(Integer, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    capacity = Column(Integer, nullable=True)

    trainer = relationship("User")
    room = relationship("Room")

    @classmethod
    def schedule(
        cls,
        db: "OrmSession",
        name: str,
        trainer_id: int,
        day_of_week: int,
        start_time: time,
        end_time: time,
        room_id: int | None = None,
        capacity: int | None = None,
    ) -> "FitnessClass":
        if end_time <= start_time:
            raise ValueError("end_time must be after start_time")
        
        if not (1 <= day_of_week <= 7):
            raise ValueError("day_of_week must be between 1 and 7")

        availability = (
            db.query(TrainerAvailability)
            .filter(
                TrainerAvailability.trainer_id == trainer_id,
                TrainerAvailability.day_of_week == day_of_week,
                TrainerAvailability.start_time <= start_time,
                TrainerAvailability.end_time >= end_time,
            )
            .first()
        )

        if availability is None:
            raise ValueError("Trainer is not available for the requested time window.")

        conflict_class = (
            db.query(cls)
            .filter(
                cls.trainer_id == trainer_id,
                cls.day_of_week == day_of_week,
                cls.start_time < end_time,
                cls.end_time > start_time,
            )
            .first()
        )

        if conflict_class is not None:
            raise ValueError("Trainer is already assigned to another class in that time window.")

        if room_id is not None:
            room_conflict_class = (
                db.query(cls)
                .filter(
                    cls.room_id == room_id,
                    cls.day_of_week == day_of_week,
                    cls.start_time < end_time,
                    cls.end_time > start_time,
                )
                .first()
            )

            if room_conflict_class is not None:
                raise ValueError("Room is booked for another class in that time window.")

        obj = cls(
            name=name,
            trainer_id=trainer_id,
            room_id=room_id,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            capacity=capacity,
        )

        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @classmethod
    def update_schedule(
        cls,
        db: "OrmSession",
        class_id: int,
        *,
        name: str | None = None,
        trainer_id: int | None = None,
        room_id: int | None = None,
        day_of_week: int | None = None,
        start_time: time | None = None,
        end_time: time | None = None,
        capacity: int | None = None,
    ) -> "FitnessClass":
        obj = db.query(cls).filter(cls.id == class_id).first()
        if obj is None:
            raise ValueError("Class not found")

        new_name = name if name is not None else obj.name
        new_trainer_id = trainer_id if trainer_id is not None else obj.trainer_id
        new_room_id = room_id if room_id is not None else obj.room_id
        new_day_of_week = day_of_week if day_of_week is not None else obj.day_of_week
        new_start_time = start_time if start_time is not None else obj.start_time
        new_end_time = end_time if end_time is not None else obj.end_time
        new_capacity = capacity if capacity is not None else obj.capacity

        if new_end_time <= new_start_time:
            raise ValueError("end_time must be after start_time")
        
        if not (1 <= new_day_of_week <= 7):
            raise ValueError("day_of_week must be between 1 and 7")

        availability = (
            db.query(TrainerAvailability)
            .filter(
                TrainerAvailability.trainer_id == new_trainer_id,
                TrainerAvailability.day_of_week == new_day_of_week,
                TrainerAvailability.start_time <= new_start_time,
                TrainerAvailability.end_time >= new_end_time,
            )
            .first()
        )

        if availability is None:
            raise ValueError("Trainer is not available for the requested time window.")

        conflict_class = (
            db.query(cls)
            .filter(
                cls.id != obj.id,
                cls.trainer_id == new_trainer_id,
                cls.day_of_week == new_day_of_week,
                cls.start_time < new_end_time,
                cls.end_time > new_start_time,
            )
            .first()
        )

        if conflict_class is not None:
            raise ValueError("Trainer is already assigned to another class in that time window.")

        if new_room_id is not None:
            room_conflict_class = (
                db.query(cls)
                .filter(
                    cls.id != obj.id,
                    cls.room_id == new_room_id,
                    cls.day_of_week == new_day_of_week,
                    cls.start_time < new_end_time,
                    cls.end_time > new_start_time,
                )
                .first()
            )

            if room_conflict_class is not None:
                raise ValueError("Room is booked for another class in that time window.")

        obj.name = new_name
        obj.trainer_id = new_trainer_id
        obj.room_id = new_room_id
        obj.day_of_week = new_day_of_week
        obj.start_time = new_start_time
        obj.end_time = new_end_time
        obj.capacity = new_capacity

        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
