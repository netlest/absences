"""
Absences API endpoints.
Best practice: Use APIRouter for modular endpoint organization.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ..deps import get_db
from ..models import Absence, Object, AbsenceType
from ..schemas import (
    AbsenceCreate,
    AbsenceResponse,
    BulkAbsenceCreate,
    BulkAbsenceResponse,
)
from ..core.security import verify_token

# Best practice: Create router with prefix and tags for API organization
router = APIRouter(prefix="/absences", tags=["absences"])


@router.post(
    "/bulk",
    response_model=BulkAbsenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Bulk insert absences",
    description="""
    Create multiple absences in a single request.
    
    Best practices demonstrated:
    - Bearer token authentication required
    - Request validation with Pydantic
    - Transaction management (all or nothing)
    - Proper error handling
    - Foreign key validation
    - Bulk insert optimization
    """,
    responses={
        201: {"description": "Absences created successfully"},
        400: {"description": "Invalid request data"},
        401: {"description": "Unauthorized - Invalid or missing token"},
        404: {"description": "Referenced object or absence type not found"},
        500: {"description": "Internal server error"},
    }
)
async def bulk_create_absences(
    bulk_data: BulkAbsenceCreate,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token),  # Best practice: Dependency injection for auth
) -> BulkAbsenceResponse:
    """
    Bulk insert absences endpoint.
    
    Best practice: Use dependency injection for database session and authentication.
    """
    errors: List[str] = []
    created_absences: List[Absence] = []
    
    try:
        # Best practice: Validate foreign keys before insertion
        # Collect unique object_ids and type_ids for validation
        object_ids = {absence.object_id for absence in bulk_data.absences}
        type_ids = {absence.type_id for absence in bulk_data.absences}
        
        # Validate objects exist
        existing_objects = db.query(Object.id).filter(Object.id.in_(object_ids)).all()
        existing_object_ids = {obj.id for obj in existing_objects}
        missing_objects = object_ids - existing_object_ids
        
        if missing_objects:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Objects not found: {missing_objects}"
            )
        
        # Validate absence types exist
        existing_types = db.query(AbsenceType.id).filter(AbsenceType.id.in_(type_ids)).all()
        existing_type_ids = {t.id for t in existing_types}
        missing_types = type_ids - existing_type_ids
        
        if missing_types:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Absence types not found: {missing_types}"
            )
        
        # Best practice: Use bulk insert for performance
        # Create absence objects from validated data
        absence_objects = [
            Absence(**absence.model_dump())
            for absence in bulk_data.absences
        ]
        
        # Best practice: Use add_all for bulk insertion
        db.add_all(absence_objects)
        
        # Best practice: Use transaction - commit all or rollback all
        db.commit()
        
        # Refresh objects to get IDs
        for absence in absence_objects:
            db.refresh(absence)
            created_absences.append(absence)
        
        return BulkAbsenceResponse(
            created_count=len(created_absences),
            absences=[AbsenceResponse.model_validate(a) for a in created_absences],
            errors=errors if errors else None
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        db.rollback()
        raise
        
    except IntegrityError as e:
        # Best practice: Handle database constraint violations
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database integrity error: {str(e.orig)}"
        )
        
    except SQLAlchemyError as e:
        # Best practice: Handle database errors gracefully
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
        
    except Exception as e:
        # Best practice: Catch-all for unexpected errors
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.post(
    "/",
    response_model=AbsenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a single absence",
    description="Create a single absence entry",
)
async def create_absence(
    absence: AbsenceCreate,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token),
) -> AbsenceResponse:
    """
    Create a single absence.
    Best practice: Also provide single-item endpoint alongside bulk endpoint.
    """
    try:
        # Validate object exists
        obj = db.query(Object).filter(Object.id == absence.object_id).first()
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Object with id {absence.object_id} not found"
            )
        
        # Validate absence type exists
        absence_type = db.query(AbsenceType).filter(AbsenceType.id == absence.type_id).first()
        if not absence_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Absence type with id {absence.type_id} not found"
            )
        
        # Create absence
        db_absence = Absence(**absence.model_dump())
        db.add(db_absence)
        db.commit()
        db.refresh(db_absence)
        
        return AbsenceResponse.model_validate(db_absence)
        
    except HTTPException:
        db.rollback()
        raise
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database integrity error: {str(e.orig)}"
        )


@router.get(
    "/",
    response_model=List[AbsenceResponse],
    summary="List absences",
    description="Retrieve list of absences with optional filtering",
)
async def list_absences(
    skip: int = 0,
    limit: int = 100,
    object_id: int = None,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token),
) -> List[AbsenceResponse]:
    """
    List absences with pagination.
    Best practice: Provide read endpoints with pagination.
    """
    query = db.query(Absence)
    
    if object_id:
        query = query.filter(Absence.object_id == object_id)
    
    absences = query.offset(skip).limit(limit).all()
    return [AbsenceResponse.model_validate(a) for a in absences]


@router.get(
    "/{absence_id}",
    response_model=AbsenceResponse,
    summary="Get absence by ID",
    description="Retrieve a specific absence by its ID",
)
async def get_absence(
    absence_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token),
) -> AbsenceResponse:
    """
    Get a specific absence.
    Best practice: Provide individual resource endpoints.
    """
    absence = db.query(Absence).filter(Absence.id == absence_id).first()
    
    if not absence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Absence with id {absence_id} not found"
        )
    
    return AbsenceResponse.model_validate(absence)
