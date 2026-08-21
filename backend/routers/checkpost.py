from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import crud, schemas
from database.database import get_db
from utils.security import get_current_user_payload

router = APIRouter(prefix="/checkpost", tags=["Checkpost Watchers"])

@router.get("/profile", response_model=schemas.CheckpostWatcherResponse)
def get_profile(current_user: dict = Depends(get_current_user_payload), db: Session = Depends(get_db)):
    """Retrieve the profile data of the currently logged-in Checkpost Watcher."""
    employee_id = current_user.get("sub")
    role = current_user.get("role")
    
    if role != "Checkpost Watcher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Checkpost Watcher access authorization required"
        )
        
    watcher = crud.get_checkpost_watcher_by_employee_id(db, employee_id)
    if not watcher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Checkpost Watcher profile record not found"
        )
    return watcher


@router.get("/history", response_model=List[schemas.CheckpostLoginHistoryResponse])
def get_history(current_user: dict = Depends(get_current_user_payload), db: Session = Depends(get_db)):
    """Retrieve the session login history for the active Checkpost Watcher."""
    employee_id = current_user.get("sub")
    role = current_user.get("role")
    
    if role != "Checkpost Watcher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Checkpost Watcher access authorization required"
        )
        
    return crud.get_checkpost_login_history(db, employee_id)
