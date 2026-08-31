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

    error_message: Mapped[str | None] = mapped_column(
    String(1000),
    nullable=True,
)



class Refund(Base):
    __tablename__ = "refunds"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[str] = mapped_column(String(100))
    customer_id: Mapped[int] = mapped_column()
    reason: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
    )
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow
    )


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column()
    status: Mapped[str] = mapped_column(
        String(50),
        default="active",
    )
    pending_intent: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    pending_account_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    pending_field: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow
    )

class Approval(Base):
    __tablename__ = "approvals"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column()
    intent: Mapped[str] = mapped_column(String(100))
    account_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    new_address: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    refund_reason: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
    )
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column()
    action: Mapped[str] = mapped_column(String(100))
    intent: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    account_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    result: Mapped[str] = mapped_column(String(50))
    details: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow
    )