"""
API route handlers for absence management.
Implements REST endpoints with proper authentication and validation.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .database import get_db
from .models import Absence, User, Object, AbsenceType
from .schemas import (
    AbsenceCreate,
    AbsenceResponse,
    AbsenceBulkCreate,
    AbsenceBulkResponse,
    AbsenceDetailResponse,
    MessageResponse,
)
from .auth import get_current_active_user

router = APIRouter(prefix="/api/v1/absences", tags=["absences"])


@router.post(
    "/bulk",
    response_model=AbsenceBulkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Bulk create absences",
    description="Create multiple absences in a single request. Requires bearer token authentication."
)
async def bulk_create_absences(
    bulk_data: AbsenceBulkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AbsenceBulkResponse:
    """
    Bulk insert absences into the database.
    
    This endpoint demonstrates best practices:
    - Bearer token authentication required
    - Pydantic validation for all input data
    - Async database operations
    - Proper error handling
    - Transaction management (all or nothing)
    
    Args:
        bulk_data: List of absences to create
        db: Database session (injected)
        current_user: Authenticated user (injected)
        
    Returns:
        AbsenceBulkResponse: Created absences count and list
        
    Raises:
        HTTPException: If validation fails or database error occurs
    """
    created_absences: List[Absence] = []
    
    try:
        # Validate that all referenced objects and types exist
        for absence_data in bulk_data.absences:
            # Check if object exists
            obj_result = await db.execute(
                select(Object).where(Object.id == absence_data.object_id)
            )
            obj = obj_result.scalar_one_or_none()
            if not obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Object with id {absence_data.object_id} not found"
                )
            
            # Check if absence type exists
            type_result = await db.execute(
                select(AbsenceType).where(AbsenceType.id == absence_data.type_id)
            )
            absence_type = type_result.scalar_one_or_none()
            if not absence_type:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"AbsenceType with id {absence_data.type_id} not found"
                )
            
            # Create absence instance
            absence = Absence(
                object_id=absence_data.object_id,
                type_id=absence_data.type_id,
                abs_date_start=absence_data.abs_date_start,
                abs_date_end=absence_data.abs_date_end,
                description=absence_data.description,
            )
            created_absences.append(absence)
        
        # Bulk insert all absences
        db.add_all(created_absences)
        await db.commit()
        
        # Refresh to get IDs and any server-generated values
        for absence in created_absences:
            await db.refresh(absence)
        
        # Convert to response schema
        response_absences = [
            AbsenceResponse.model_validate(absence)
            for absence in created_absences
        ]
        
        return AbsenceBulkResponse(
            created_count=len(response_absences),
            absences=response_absences
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create absences: {str(e)}"
        )


@router.post(
    "/",
    response_model=AbsenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a single absence",
    description="Create a new absence. Requires bearer token authentication."
)
async def create_absence(
    absence_data: AbsenceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AbsenceResponse:
    """
    Create a single absence.
    
    Args:
        absence_data: Absence data to create
        db: Database session (injected)
        current_user: Authenticated user (injected)
        
    Returns:
        AbsenceResponse: Created absence
        
    Raises:
        HTTPException: If validation fails or database error occurs
    """
    try:
        # Validate object exists
        obj_result = await db.execute(
            select(Object).where(Object.id == absence_data.object_id)
        )
        obj = obj_result.scalar_one_or_none()
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Object with id {absence_data.object_id} not found"
            )
        
        # Validate absence type exists
        type_result = await db.execute(
            select(AbsenceType).where(AbsenceType.id == absence_data.type_id)
        )
        absence_type = type_result.scalar_one_or_none()
        if not absence_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"AbsenceType with id {absence_data.type_id} not found"
            )
        
        # Create absence
        absence = Absence(
            object_id=absence_data.object_id,
            type_id=absence_data.type_id,
            abs_date_start=absence_data.abs_date_start,
            abs_date_end=absence_data.abs_date_end,
            description=absence_data.description,
        )
        
        db.add(absence)
        await db.commit()
        await db.refresh(absence)
        
        return AbsenceResponse.model_validate(absence)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create absence: {str(e)}"
        )


@router.get(
    "/",
    response_model=List[AbsenceDetailResponse],
    summary="List absences",
    description="Get a list of all absences. Requires bearer token authentication."
)
async def list_absences(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[AbsenceDetailResponse]:
    """
    List absences with pagination.
    
    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        db: Database session (injected)
        current_user: Authenticated user (injected)
        
    Returns:
        List[AbsenceDetailResponse]: List of absences with related data
    """
    # Query with eager loading of relationships to avoid N+1 queries
    result = await db.execute(
        select(Absence)
        .options(selectinload(Absence.object), selectinload(Absence.absence_type))
        .offset(skip)
        .limit(limit)
    )
    absences = result.scalars().all()
    
    # Convert to response schema (relationships are already loaded)
    response_list = [AbsenceDetailResponse.model_validate(absence) for absence in absences]
    
    return response_list


@router.get(
    "/{absence_id}",
    response_model=AbsenceDetailResponse,
    summary="Get absence by ID",
    description="Retrieve a specific absence by its ID. Requires bearer token authentication."
)
async def get_absence(
    absence_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AbsenceDetailResponse:
    """
    Get a specific absence by ID.
    
    Args:
        absence_id: ID of the absence to retrieve
        db: Database session (injected)
        current_user: Authenticated user (injected)
        
    Returns:
        AbsenceDetailResponse: Absence with related data
        
    Raises:
        HTTPException: If absence not found
    """
    # Query with eager loading of relationships
    result = await db.execute(
        select(Absence)
        .options(selectinload(Absence.object), selectinload(Absence.absence_type))
        .where(Absence.id == absence_id)
    )
    absence = result.scalar_one_or_none()
    
    if not absence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Absence with id {absence_id} not found"
        )
    
    return AbsenceDetailResponse.model_validate(absence)


@router.delete(
    "/{absence_id}",
    response_model=MessageResponse,
    summary="Delete absence",
    description="Delete a specific absence by its ID. Requires bearer token authentication."
)
async def delete_absence(
    absence_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> MessageResponse:
    """
    Delete an absence by ID.
    
    Args:
        absence_id: ID of the absence to delete
        db: Database session (injected)
        current_user: Authenticated user (injected)
        
    Returns:
        MessageResponse: Success message
        
    Raises:
        HTTPException: If absence not found
    """
    result = await db.execute(
        select(Absence).where(Absence.id == absence_id)
    )
    absence = result.scalar_one_or_none()
    
    if not absence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Absence with id {absence_id} not found"
        )
    
    await db.delete(absence)
    await db.commit()
    
    return MessageResponse(
        message=f"Absence with id {absence_id} successfully deleted"
    )
