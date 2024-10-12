from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    Enum,
    ForeignKey,
    Table,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
from datetime import datetime
from typing import Any

import uuid
import enum

Base = declarative_base()


# Mapping to raw data
def to_dict(obj: Base) -> dict[str, Any]:
    return {
        c.name: (
            str(getattr(obj, c.name))
            if isinstance(getattr(obj, c.name), (uuid.UUID, datetime))
            else getattr(obj, c.name)
        )
        for c in obj.__table__.columns
    }


class DBCustomer(Base):
    __tablename__ = "customer"
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(250), nullable=True)
    last_name = Column(String(250), nullable=True)
    email = Column(String(250), nullable=True)


class OrderStatus(enum.Enum):
    pending = "pending"
    canceled = "canceled"
    completed = "completed"


class PaymentStatus(enum.Enum):
    unpaid = "unpaid"
    paid = "paid"
    failed = "failed"


class DBProduct(Base):
    __tablename__ = "product"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = Column(String(250), nullable=False)
    description = Column(String(500), nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=func.now(),
        nullable=False,
    )


order_product = Table(
    "order_product",
    Base.metadata,
    Column("order_id", UUID(as_uuid=True), ForeignKey("orders.id"), primary_key=True),
    Column(
        "product_id", UUID(as_uuid=True), ForeignKey("product.id"), primary_key=True
    ),
    Column("quantity", Integer, nullable=False),
)


class DBOrder(Base):
    __tablename__ = "orders"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    customer_id = Column(Integer, ForeignKey("customer.id"), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.pending)
    payment_status = Column(
        Enum(PaymentStatus), nullable=False, default=PaymentStatus.unpaid
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False)

    customer = relationship(
        "DBCustomer", backref=backref("orders", cascade="all, delete-orphan")
    )
    products = relationship(
        "DBProduct", secondary=order_product, back_populates="orders"
    )


DBProduct.orders = relationship(
    "DBOrder", secondary=order_product, back_populates="products"
)
