from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func

from app.database import Base


# Base mixin for common model fields.
# I used a similar pattern in a previous team to avoid repeating
# id and timestamp fields across all ORM models.
class BaseModelMixin:
    @declared_attr
    def id(cls):
        return Column(Integer, primary_key=True, index=True)

    @declared_attr
    def created_at(cls):
        return Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    @declared_attr
    def updated_at(cls):
        return Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)


class User(Base, BaseModelMixin):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<User(email={self.email}, name={self.first_name})>"


class Item(Base, BaseModelMixin):
    __tablename__ = "items"

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, index=True)
    status = Column(String(50), default="active", nullable=False)
    is_deleted = Column(Boolean, default=False, index=True, nullable=False)

    def __repr__(self):
        return f"<Item(name={self.name}, category={self.category}, status={self.status})>"
