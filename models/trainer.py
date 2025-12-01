from datetime import datetime, time
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as OrmSession
from user import User
from member import Member
from fitness_class import FitnessClass
from trainer_availability import TrainerAvailability


class Trainer(User):
    __mapper_args__ = {
        "polymorphic_identity": "trainer",
    }

    @classmethod
    def create(cls, db: "OrmSession", name: str, email: str) -> "Trainer":
        if not name or not email:
            raise ValueError("Name and email are required.")
        existing = db.query(cls).filter(cls.email == email).first()
        if existing is not None:
            raise ValueError("Email already registered")
        trainer = cls(name=name, email=email)
        db.add(trainer)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            if "users.email" in str(exc.orig) or "UNIQUE constraint failed: users.email" in str(exc.orig):
                raise ValueError("Email already registered")
            raise

        db.refresh(trainer)
        return trainer

    def set_availability(
        self,
        db: "OrmSession",
        day_of_week: int,
        start_time: time,
        end_time: time,
    ) -> TrainerAvailability:
        return TrainerAvailability.create_window(
            db=db,
            trainer_id=self.id,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
        )

    def get_schedule(
        self,
        db: "OrmSession",
    ) -> list[FitnessClass]:
        query = db.query(FitnessClass).filter(FitnessClass.trainer_id == self.id)
        return query.order_by(FitnessClass.day_of_week, FitnessClass.start_time).all()

    def lookup_member(
        self,
        db: "OrmSession",
        name: str,
    ) -> Member | None:
        member = (
            db.query(Member)
            .filter(func.lower(Member.name) == func.lower(name))
            .first()
        )
        return member

    def get_availability(
        self,
        db: "OrmSession",
    ) -> list[TrainerAvailability]:
        return (
            db.query(TrainerAvailability)
            .filter(TrainerAvailability.trainer_id == self.id)
            .order_by(TrainerAvailability.day_of_week, TrainerAvailability.start_time)
            .all()
        )