"""
SQLAlchemy ORM models using SQLAlchemy 2.0 mapped_column syntax.
These models represent the database schema with type hints.
"""
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import ForeignKey, String, Boolean, Integer, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class User(Base):
    """User model representing application users."""
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    objects: Mapped[List["Object"]] = relationship("Object", back_populates="user")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>"


class Group(Base):
    """Group model for organizing objects."""
    __tablename__ = 'groups'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationships
    objects: Mapped[List["Object"]] = relationship("Object", back_populates="group", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Group(id={self.id}, name='{self.name}')>"


class Object(Base):
    """Object model representing entities that can have absences."""
    __tablename__ = 'objects'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey('groups.id', ondelete='CASCADE'), nullable=False)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="objects")
    group: Mapped["Group"] = relationship("Group", back_populates="objects")
    absences: Mapped[List["Absence"]] = relationship("Absence", back_populates="object", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Object(id={self.id}, name='{self.name}')>"


class AbsenceType(Base):
    """AbsenceType model defining different types of absences."""
    __tablename__ = 'absence_types'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    color: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    # Relationships
    absences: Mapped[List["Absence"]] = relationship("Absence", back_populates="absence_type")

    def __repr__(self) -> str:
        return f"<AbsenceType(id={self.id}, name='{self.name}')>"


class Absence(Base):
    """Absence model representing periods when objects are absent."""
    __tablename__ = 'absences'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    object_id: Mapped[int] = mapped_column(Integer, ForeignKey('objects.id', ondelete='CASCADE'), nullable=False)
    type_id: Mapped[int] = mapped_column(Integer, ForeignKey('absence_types.id', ondelete='CASCADE'), nullable=False)
    abs_date_start: Mapped[date] = mapped_column(Date, nullable=False)
    abs_date_end: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)

    # Relationships
    object: Mapped["Object"] = relationship("Object", back_populates="absences")
    absence_type: Mapped["AbsenceType"] = relationship("AbsenceType", back_populates="absences")

    def __repr__(self) -> str:
        return f"<Absence(id={self.id}, object_id={self.object_id}, start={self.abs_date_start}, end={self.abs_date_end})>"


class Holiday(Base):
    """Holiday model for tracking public holidays."""
    __tablename__ = 'holidays'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    country: Mapped[str] = mapped_column(String(4), nullable=False)
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    recurring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def __repr__(self) -> str:
        return f"<Holiday(id={self.id}, country='{self.country}', date={self.event_date})>"
