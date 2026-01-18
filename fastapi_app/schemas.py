"""
Pydantic models for request/response validation.
These models define the API contract and handle data validation.
"""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator


# Absence Schemas
class AbsenceBase(BaseModel):
    """Base schema for Absence with common fields."""
    object_id: int = Field(..., description="ID of the object this absence belongs to", gt=0)
    type_id: int = Field(..., description="ID of the absence type", gt=0)
    abs_date_start: date = Field(..., description="Start date of the absence")
    abs_date_end: date = Field(..., description="End date of the absence")
    description: Optional[str] = Field(None, max_length=150, description="Optional description of the absence")

    @field_validator('abs_date_end')
    @classmethod
    def end_date_must_be_after_start(cls, v: date, info) -> date:
        """Validate that end date is not before start date."""
        if 'abs_date_start' in info.data and v < info.data['abs_date_start']:
            raise ValueError('abs_date_end must be on or after abs_date_start')
        return v


class AbsenceCreate(AbsenceBase):
    """Schema for creating a new absence."""
    pass


class AbsenceResponse(AbsenceBase):
    """Schema for absence response with additional fields."""
    id: int = Field(..., description="Unique identifier for the absence")
    
    model_config = ConfigDict(from_attributes=True)


class AbsenceBulkCreate(BaseModel):
    """Schema for bulk creating absences."""
    absences: List[AbsenceCreate] = Field(..., min_length=1, description="List of absences to create")
    
    @field_validator('absences')
    @classmethod
    def validate_absences_list(cls, v: List[AbsenceCreate]) -> List[AbsenceCreate]:
        """Validate that we have at least one absence."""
        if not v:
            raise ValueError('At least one absence must be provided')
        return v


class AbsenceBulkResponse(BaseModel):
    """Response schema for bulk operations."""
    created_count: int = Field(..., description="Number of absences successfully created")
    absences: List[AbsenceResponse] = Field(..., description="List of created absences")


# Object Schemas
class ObjectBase(BaseModel):
    """Base schema for Object."""
    name: str = Field(..., max_length=30, description="Name of the object")
    description: Optional[str] = Field(None, max_length=255, description="Optional description")
    user_id: int = Field(..., gt=0, description="User ID that owns this object")
    group_id: int = Field(..., gt=0, description="Group ID this object belongs to")


class ObjectResponse(ObjectBase):
    """Schema for object response."""
    id: int = Field(..., description="Unique identifier for the object")
    
    model_config = ConfigDict(from_attributes=True)


# AbsenceType Schemas
class AbsenceTypeBase(BaseModel):
    """Base schema for AbsenceType."""
    name: str = Field(..., max_length=50, description="Name of the absence type")
    color: Optional[str] = Field(None, max_length=30, description="Color code for the absence type")


class AbsenceTypeResponse(AbsenceTypeBase):
    """Schema for absence type response."""
    id: int = Field(..., description="Unique identifier for the absence type")
    
    model_config = ConfigDict(from_attributes=True)


# Enhanced response schemas with relationships
class AbsenceDetailResponse(AbsenceResponse):
    """Detailed absence response including related object and type information."""
    object: Optional[ObjectResponse] = Field(None, description="Object information")
    absence_type: Optional[AbsenceTypeResponse] = Field(None, description="Absence type information")


# Error Response Schema
class ErrorResponse(BaseModel):
    """Standard error response schema."""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code for programmatic handling")


# Success Response Schema
class MessageResponse(BaseModel):
    """Generic success message response."""
    message: str = Field(..., description="Success message")
    data: Optional[dict] = Field(None, description="Optional additional data")
