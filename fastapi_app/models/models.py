"""
SQLAlchemy models using mapped_column (SQLAlchemy 2.0 style).
Best practice: Use type hints and mapped_column for better IDE support.
"""
from datetime import date
from typing import Optional, List
from sqlalchemy import ForeignKey, String, Date, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..deps.database import Base


class User(Base):
    """
    User model with mapped_column annotations.
    Best practice: Use Mapped[] type hints for all columns.
    """
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Best practice: Use relationship() for ORM relationships
    objects: Mapped[List["Object"]] = relationship(
        "Object",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<User {self.username}>"


class Group(Base):
    """Group model for organizing objects"""
    __tablename__ = "groups"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Relationships
    objects: Mapped[List["Object"]] = relationship(
        "Object",
        back_populates="group",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Group {self.name}>"


class Object(Base):
    """
    Object model representing entities that can have absences.
    Best practice: Clear naming and relationships.
    """
    __tablename__ = "objects"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="objects")
    group: Mapped["Group"] = relationship("Group", back_populates="objects")
    absences: Mapped[List["Absence"]] = relationship(
        "Absence",
        back_populates="object",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Object {self.name}>"


class AbsenceType(Base):
    """
    Absence type model for categorizing absences.
    Best practice: Lookup tables for categorization.
    """
    __tablename__ = "absence_types"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    color: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    
    # Relationships
    absences: Mapped[List["Absence"]] = relationship(
        "Absence",
        back_populates="absence_type"
    )
    
    def __repr__(self) -> str:
        return f"<AbsenceType {self.name}>"


class Absence(Base):
    """
    Absence model representing absence periods.
    Best practice: Use Date type for date columns, proper foreign keys.
    """
    __tablename__ = "absences"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    object_id: Mapped[int] = mapped_column(
        ForeignKey("objects.id", ondelete="CASCADE"),
        nullable=False
    )
    type_id: Mapped[int] = mapped_column(
        ForeignKey("absence_types.id", ondelete="CASCADE"),
        nullable=False
    )
    abs_date_start: Mapped[date] = mapped_column(Date, nullable=False)
    abs_date_end: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    
    # Relationships
    object: Mapped["Object"] = relationship("Object", back_populates="absences")
    absence_type: Mapped["AbsenceType"] = relationship("AbsenceType", back_populates="absences")
    
    def __repr__(self) -> str:
        return f"<Absence {self.id} for Object {self.object_id}>"
