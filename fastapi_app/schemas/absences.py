"""
Pydantic schemas for request validation and response serialization.
Best practice: Separate schemas for input validation and output serialization.
"""
from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator


# Best practice: Base schema with common configuration
class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    model_config = ConfigDict(
        from_attributes=True,  # Enable ORM mode for SQLAlchemy models
        str_strip_whitespace=True,  # Strip whitespace from strings
    )


# Absence Schemas
class AbsenceBase(BaseSchema):
    """
    Base absence schema with common fields.
    Best practice: DRY - reuse common fields across schemas.
    """
    object_id: int = Field(..., gt=0, description="ID of the object")
    type_id: int = Field(..., gt=0, description="ID of the absence type")
    abs_date_start: date = Field(..., description="Start date of absence")
    abs_date_end: date = Field(..., description="End date of absence")
    description: Optional[str] = Field(None, max_length=150, description="Absence description")
    
    @field_validator('abs_date_end')
    @classmethod
    def validate_date_range(cls, v: date, info) -> date:
        """
        Validate that end date is not before start date.
        Best practice: Add business logic validation in Pydantic models.
        """
        if 'abs_date_start' in info.data and v < info.data['abs_date_start']:
            raise ValueError('abs_date_end must be greater than or equal to abs_date_start')
        return v


class AbsenceCreate(AbsenceBase):
    """
    Schema for creating an absence.
    Best practice: Separate create/update schemas from read schemas.
    """
    pass


class AbsenceResponse(AbsenceBase):
    """
    Schema for absence response.
    Best practice: Include ID and computed fields in response.
    """
    id: int = Field(..., description="Absence ID")
    
    model_config = ConfigDict(from_attributes=True)


# Bulk Insert Schemas
class BulkAbsenceCreate(BaseSchema):
    """
    Schema for bulk absence creation.
    Best practice: Use List type for bulk operations with validation.
    """
    absences: List[AbsenceCreate] = Field(
        ...,
        min_length=1,
        max_length=1000,  # Limit to prevent abuse
        description="List of absences to create"
    )


class BulkAbsenceResponse(BaseSchema):
    """
    Schema for bulk absence creation response.
    Best practice: Return detailed results for bulk operations.
    """
    created_count: int = Field(..., description="Number of absences created")
    absences: List[AbsenceResponse] = Field(..., description="Created absences")
    errors: Optional[List[str]] = Field(default=None, description="Any errors encountered")


# Object Schema (for reference)
class ObjectResponse(BaseSchema):
    """Schema for object response"""
    id: int
    user_id: int
    group_id: int
    name: str
    description: Optional[str] = None


# AbsenceType Schema (for reference)
class AbsenceTypeResponse(BaseSchema):
    """Schema for absence type response"""
    id: int
    name: str
    color: Optional[str] = None


# Error Response Schema
class ErrorResponse(BaseSchema):
    """
    Standardized error response schema.
    Best practice: Consistent error format across API.
    """
    detail: str = Field(..., description="Error detail message")
    status_code: int = Field(..., description="HTTP status code")


# Health Check Schema
class HealthCheckResponse(BaseSchema):
    """Health check response schema"""
    status: str = Field(..., description="Service status")
    database: str = Field(..., description="Database connection status")
