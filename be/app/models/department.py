import uuid

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Department(Base):
    __tablename__ = "department"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    code: Mapped[str | None] = mapped_column(String(10), unique=True, nullable=True)

    cities: Mapped[list["City"]] = relationship(back_populates="department", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Department(id={self.id}, name={self.name})"


class City(Base):
    __tablename__ = "city"
    __table_args__ = (UniqueConstraint("department_id", "name", name="uq_city_department_name"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    department_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("department.id", ondelete="RESTRICT"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str | None] = mapped_column(String(10), nullable=True)

    department: Mapped["Department"] = relationship(back_populates="cities")

    def __repr__(self) -> str:
        return f"City(id={self.id}, name={self.name})"
