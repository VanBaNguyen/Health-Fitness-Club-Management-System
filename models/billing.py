from datetime import datetime
from random import randint
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, Session as OrmSession
from sqlalchemy.ext.hybrid import hybrid_property
from user import Base, User


class Bill(Base):
    #2nf/3nf: amounts computed via hybrid properties
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    member = relationship("User")
    line_items = relationship("BillLineItem", back_populates="bill", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="bill", cascade="all, delete-orphan")

    @hybrid_property
    def total_amount(self) -> float:
        return sum(item.amount for item in self.line_items) if self.line_items else 0.0

    @hybrid_property
    def amount_paid(self) -> float:
        return sum(
            p.amount for p in self.payments if p.status == "completed"
        ) if self.payments else 0.0

    @hybrid_property
    def amount_due(self) -> float:
        return max(self.total_amount - self.amount_paid, 0.0)

    def update_status(self, db: "OrmSession") -> "Bill":
        if self.amount_due <= 0 and self.total_amount > 0:
            self.status = "paid"
        elif self.amount_paid > 0:
            self.status = "partial"
        else:
            self.status = "pending"
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    @classmethod
    def create(cls, db: "OrmSession", member_id: int) -> "Bill":
        bill = cls(
            member_id=member_id,
            status="pending",
        )
        db.add(bill)
        db.commit()
        db.refresh(bill)
        return bill


class BillLineItem(Base):
    __tablename__ = "bill_line_items"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False, index=True)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)

    bill = relationship("Bill", back_populates="line_items")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String, nullable=False, default="pending")

    bill = relationship("Bill", back_populates="payments")

    @classmethod
    def record(cls, db: "OrmSession", bill: Bill, amount: float) -> "Payment":
        if bill.amount_due <= 0:
            raise ValueError("Bill is already fully paid.")
        
        if amount <= 0:
            raise ValueError("Payment amount must be positive.")

        if amount > bill.amount_due:
             raise ValueError(f"Payment amount ({amount}) exceeds amount due ({bill.amount_due}).")

        payment = cls(
            bill_id=bill.id,
            amount=amount,
            status="completed",
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)
        bill.update_status(db)
        return payment
