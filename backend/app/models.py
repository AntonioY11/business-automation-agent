from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime

class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    subscription_status: Mapped[str] = mapped_column(String(50))
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[str] = mapped_column(String(100), unique=True)
    customer_id: Mapped[int] = mapped_column()
    subscription_status: Mapped[str] = mapped_column(String(50))



class Request(Base):
    __tablename__ = "requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column()
    raw_text: Mapped[str] = mapped_column(String(5000))
    status: Mapped[str] = mapped_column(String(50), default="pending")
    intent: Mapped[str | None] = mapped_column(String(100), nullable=True)
    priority: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    account_id: Mapped[str | None] = mapped_column(String(100), nullable=True)