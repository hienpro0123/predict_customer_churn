from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.session import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(10), primary_key=True)
    age: Mapped[int | None] = mapped_column(Integer)
    gender: Mapped[str | None] = mapped_column(String(10))
    tenure: Mapped[int | None] = mapped_column(Integer)
    usage_frequency: Mapped[int | None] = mapped_column(Integer)
    support_calls: Mapped[int | None] = mapped_column(Integer)
    payment_delay: Mapped[int | None] = mapped_column(Integer)
    subscription_type: Mapped[str | None] = mapped_column(String(20))
    contract_length: Mapped[str | None] = mapped_column(String(20))
    total_spend: Mapped[float | None] = mapped_column(Float)
    last_interaction: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    predictions = relationship("Prediction", back_populates="customer", cascade="all, delete-orphan")
