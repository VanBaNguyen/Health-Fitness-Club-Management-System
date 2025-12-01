from datetime import datetime
from sqlalchemy import Column, Float, Integer, String, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as OrmSession
from user import User
from fitness_class import FitnessClass
from enrollment import Enrollment


class Member(User):
    __mapper_args__ = {
        "polymorphic_identity": "member",
    }

    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    weight_goal = Column(Float, nullable=True)
    current_weight = Column(Float, nullable=True)

    @classmethod
    def create(
        cls,
        db: "OrmSession",
        name: str,
        email: str,
        age: int | None = None,
        gender: str | None = None,
        weight_goal: float | None = None,
        current_weight: float | None = None,
    ) -> "Member":
        existing = db.query(cls).filter(cls.email == email).first()
        if existing is not None:
            raise ValueError("Email already registered")
        
        member_obj = cls(
            name=name,
            email=email,
            age=age,
            gender=gender,
            weight_goal=weight_goal,
            current_weight=current_weight,
        )
        db.add(member_obj)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            if "users.email" in str(exc.orig) or "UNIQUE constraint failed: users.email" in str(exc.orig):
                raise ValueError("Email already registered")
            raise

        db.refresh(member_obj)
        return member_obj

    def update_profile(
        self,
        db: "OrmSession",
        name: str | None = None,
        age: int | None = None,
        gender: str | None = None,
        weight_goal: float | None = None,
        current_weight: float | None = None,
    ) -> "Member":
        if name is not None:
            self.name = name
        if age is not None:
            self.age = age
        if gender is not None:
            self.gender = gender
        if weight_goal is not None:
            self.weight_goal = weight_goal
        if current_weight is not None:
            self.current_weight = current_weight
        
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def get_dashboard(
        self,
        db: "OrmSession",
    ) -> dict:
        enrolled_classes = (
            db.query(FitnessClass)
            .join(Enrollment, FitnessClass.id == Enrollment.class_id)
            .filter(
                Enrollment.member_id == self.id,
            )
            .order_by(FitnessClass.day_of_week, FitnessClass.start_time)
            .all()
        )
        
        return {
            "name": self.name,
            "email": self.email,
            "age": self.age,
            "gender": self.gender,
            "current_weight": self.current_weight,
            "weight_goal": self.weight_goal,
            "enrolled_classes": [
                {
                    "session_id": session.id,
                    "day_of_week": session.day_of_week,
                    "start_time": session.start_time,
                    "end_time": session.end_time,
                    "session_type": "group_class",
                    "name": session.name,
                }
                for session in enrolled_classes
            ],
        }

    def register_for_class(
        self,
        db: "OrmSession",
        class_id: int,
    ) -> Enrollment:
        session = (
            db.query(FitnessClass)
            .filter(
                FitnessClass.id == class_id,
            )
            .first()
        )
        
        if session is None:
            raise ValueError("Class not found")
        
        existing = (
            db.query(Enrollment)
            .filter(
                Enrollment.member_id == self.id,
                Enrollment.class_id == class_id,
            )
            .first()
        )
        
        if existing is not None:
            raise ValueError("Already registered for this class")
        
        if session.capacity is not None:
            current_enrollments = (
                db.query(func.count(Enrollment.member_id))
                .filter(Enrollment.class_id == class_id)
                .scalar()
            )
            
            if current_enrollments >= session.capacity:
                raise ValueError("Class is at full capacity")
        
        enrollment = Enrollment(
            member_id=self.id,
            class_id=class_id,
            registration_date=datetime.utcnow(),
        )
        
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)
        return enrollment
