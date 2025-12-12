"""
Cases API Router
Endpoints for EB-1A case management and processing
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
import shutil
import uuid

from ..database import get_db
from ..models import Case, User
from ..auth import get_current_user
from ..services.case_orchestrator import CaseOrchestrator
from ..services.folder_validator import FolderValidator

router = APIRouter(prefix="/cases", tags=["cases"])


@router.post("/upload")
async def upload_case(
    beneficiary_name: str,
    uploaded_folder: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a case folder for processing

    Args:
        beneficiary_name: Name of the beneficiary
        uploaded_folder: Uploaded ZIP file containing case folder
        current_user: Authenticated user
        db: Database session

    Returns:
        Case creation response
    """
    try:
        # Create workspace for this case
        case_uuid = str(uuid.uuid4())
        workspace_path = Path(f"./workspaces/{case_uuid}")
        workspace_path.mkdir(parents=True, exist_ok=True)

        # Save uploaded file
        upload_path = workspace_path / "uploaded.zip"
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(uploaded_folder.file, buffer)

        # Extract ZIP
        import zipfile
        extract_path = workspace_path / "extracted"
        with zipfile.ZipFile(upload_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

        # Find the actual case folder (handle nested folders)
        case_folder = extract_path
        items = list(case_folder.iterdir())
        if len(items) == 1 and items[0].is_dir():
            case_folder = items[0]

        # Validate folder structure (now async with LLM-based detection)
        validator = FolderValidator()
        validation = await validator.validate_structure(str(case_folder))

        if not validation["valid"]:
            raise HTTPException(status_code=400, detail={
                "message": "Invalid folder structure",
                "errors": validation["errors"],
                "warnings": validation.get("warnings", [])
            })

        # Create case in database
        case = Case(
            user_id=current_user.id,
            case_name=beneficiary_name,
            upload_path=str(upload_path),
            workspace_path=str(workspace_path),
            case_overview_path=validation.get("case_overview_path"),
            status="uploaded",
            progress=0
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        return {
            "success": True,
            "case_id": case.id,
            "case_name": beneficiary_name,
            "validation": validation,
            "message": "Case uploaded successfully. Ready for processing."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{case_id}/process")
async def process_case(
    case_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start processing a case

    Args:
        case_id: Case ID to process
        background_tasks: FastAPI background tasks
        current_user: Authenticated user
        db: Database session

    Returns:
        Processing status
    """
    case = db.query(Case).filter(Case.id == case_id, Case.user_id == current_user.id).first()

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    if case.status == "processing":
        return {"message": "Case is already being processed", "case_id": case.id}

    if case.status == "completed":
        return {"message": "Case has already been processed", "case_id": case.id}

    # Find the case folder
    workspace_path = Path(case.workspace_path)
    extract_path = workspace_path / "extracted"

    case_folder = extract_path
    items = list(case_folder.iterdir())
    if len(items) == 1 and items[0].is_dir():
        case_folder = items[0]

    # Start processing in background
    orchestrator = CaseOrchestrator(db)

    async def process_task():
        result = await orchestrator.process_case(
            case_id=case.id,
            folder_path=str(case_folder),
            beneficiary_name=case.case_name
        )
        return result

    background_tasks.add_task(process_task)

    return {
        "success": True,
        "message": "Case processing started",
        "case_id": case.id
    }


@router.get("/{case_id}/status")
async def get_case_status(
    case_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current processing status of a case

    Args:
        case_id: Case ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Case status information
    """
    case = db.query(Case).filter(Case.id == case_id, Case.user_id == current_user.id).first()

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    return {
        "case_id": case.id,
        "case_name": case.case_name,
        "field": case.field,
        "status": case.status,
        "current_step": case.current_step,
        "progress": case.progress,
        "criteria_matched": case.num_criteria,
        "total_documents": case.total_documents,
        "total_exhibits": case.total_exhibits,
        "created_at": case.created_at,
        "completed_at": case.completed_at
    }


@router.get("/{case_id}/preview")
async def preview_letter(
    case_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get preview of generated letter

    Args:
        case_id: Case ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Letter content and metadata
    """
    case = db.query(Case).filter(Case.id == case_id, Case.user_id == current_user.id).first()

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    if case.status != "completed":
        raise HTTPException(status_code=400, detail="Case processing not completed")

    # Get latest generated letter
    from ..models import GeneratedLetter
    letter = db.query(GeneratedLetter).filter(
        GeneratedLetter.case_id == case.id
    ).order_by(GeneratedLetter.created_at.desc()).first()

    if not letter:
        raise HTTPException(status_code=404, detail="Generated letter not found")

    # Get exhibits
    from ..models import CaseExhibit
    exhibits = db.query(CaseExhibit).filter(CaseExhibit.case_id == case.id).all()

    exhibit_index = {}
    for exhibit in exhibits:
        group = exhibit.group_letter
        if group not in exhibit_index:
            exhibit_index[group] = []
        exhibit_index[group].append({
            "exhibit_id": exhibit.exhibit_id,
            "title": exhibit.title,
            "description": exhibit.description
        })

    return {
        "success": True,
        "case_id": case.id,
        "case_name": case.case_name,
        "field": case.field,
        "letter_content": letter.content,
        "exhibit_index": exhibit_index,
        "criteria_matched": case.num_criteria,
        "total_exhibits": case.total_exhibits,
        "is_polished": letter.is_polished
    }


@router.get("/{case_id}/download")
async def download_files(
    case_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get download links for generated files

    Args:
        case_id: Case ID
        current_user: Authenticated user
        db: Database session

    Returns:
        File paths for download
    """
    case = db.query(Case).filter(Case.id == case_id, Case.user_id == current_user.id).first()

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    if case.status != "completed":
        raise HTTPException(status_code=400, detail="Case processing not completed")

    return {
        "success": True,
        "files": {
            "attorney_letter": case.letter_path,
            "exhibit_index": case.exhibit_index_path,
            "metadata": case.metadata_path
        }
    }


@router.get("")
async def list_cases(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all cases for current user

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Authenticated user
        db: Database session

    Returns:
        List of cases
    """
    cases = db.query(Case).filter(
        Case.user_id == current_user.id
    ).offset(skip).limit(limit).all()

    return {
        "success": True,
        "cases": [
            {
                "case_id": case.id,
                "case_name": case.case_name,
                "field": case.field,
                "status": case.status,
                "progress": case.progress,
                "criteria_matched": case.num_criteria,
                "created_at": case.created_at,
                "completed_at": case.completed_at
            }
            for case in cases
        ],
        "total": len(cases)
    }


@router.delete("/{case_id}")
async def delete_case(
    case_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a case and all associated data

    Args:
        case_id: Case ID to delete
        current_user: Authenticated user
        db: Database session

    Returns:
        Deletion confirmation
    """
    case = db.query(Case).filter(Case.id == case_id, Case.user_id == current_user.id).first()

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Delete workspace folder
    if case.workspace_path:
        workspace = Path(case.workspace_path)
        if workspace.exists():
            shutil.rmtree(workspace)

    # Delete from database (cascades to documents, exhibits, letters)
    db.delete(case)
    db.commit()

    return {
        "success": True,
        "message": f"Case {case_id} deleted successfully"
    }
