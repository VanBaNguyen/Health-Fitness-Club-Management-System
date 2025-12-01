from sqlalchemy import Column, Integer, String
from user import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    capacity = Column(Integer, nullable=True)

    def __repr__(self) -> str:
        return f"<Room id={self.id} name={self.name} capacity={self.capacity}>"
