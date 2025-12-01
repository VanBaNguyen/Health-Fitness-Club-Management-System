from sqlalchemy.orm import Session as OrmSession
from room import Room
from fitness_class import FitnessClass
from billing import Bill, BillLineItem, Payment
from trainer_availability import TrainerAvailability
from trainer import Trainer


class Admin:

    @classmethod
    def create_room(cls, db: "OrmSession", name: str, capacity: int | None = None) -> Room:
        room = Room(name=name, capacity=capacity)
        db.add(room)
        db.commit()
        db.refresh(room)
        return room

    @classmethod
    def define_class(
        cls,
        db: "OrmSession",
        name: str,
        trainer_id: int,
        day_of_week: int,
        start_time,
        end_time,
        room_id: int | None = None,
        capacity: int | None = None,
    ) -> FitnessClass:
        return FitnessClass.schedule(
            db=db,
            name=name,
            trainer_id=trainer_id,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            room_id=room_id,
            capacity=capacity,
        )

    @classmethod
    def update_class_schedule(
        cls,
        db: "OrmSession",
        class_id: int,
        *,
        name: str | None = None,
        trainer_id: int | None = None,
        room_id: int | None = None,
        day_of_week: int | None = None,
        start_time = None,
        end_time = None,
        capacity: int | None = None,
    ) -> FitnessClass:
        return FitnessClass.update_schedule(
            db=db,
            class_id=class_id,
            name=name,
            trainer_id=trainer_id,
            room_id=room_id,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            capacity=capacity,
        )

    @classmethod
    def generate_bill(cls, db: "OrmSession", member_id: int) -> Bill:
        return Bill.create(db=db, member_id=member_id)

    @classmethod
    def add_bill_line_item(
        cls,
        db: "OrmSession",
        bill_id: int,
        description: str,
        amount: float,
    ) -> BillLineItem:
        bill = db.query(Bill).filter(Bill.id == bill_id).first()
        if bill is None:
            raise ValueError("Bill not found")

        item = BillLineItem(
            bill_id=bill_id,
            description=description,
            amount=amount,
        )

        db.add(item)
        db.commit()
        db.refresh(item)
        bill.update_status(db)

        return item

    @classmethod
    def record_payment_for_bill(cls, db: "OrmSession", bill_id: int) -> Payment:
        bill = db.query(Bill).filter(Bill.id == bill_id).first()
        if bill is None:
            raise ValueError("Bill not found")

        return Payment.record(db=db, bill=bill)

    @classmethod
    def get_all_trainer_availabilities(cls, db: "OrmSession") -> list[TrainerAvailability]:
        return (
            db.query(TrainerAvailability)
            .join(Trainer)
            .order_by(Trainer.name, TrainerAvailability.day_of_week, TrainerAvailability.start_time)
            .all()
        )