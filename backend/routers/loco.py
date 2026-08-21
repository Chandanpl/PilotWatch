from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import crud, schemas
from database.database import get_db
from utils.security import get_current_user_payload

router = APIRouter(prefix="/loco", tags=["Loco Pilots"])

@router.get("/profile", response_model=schemas.LocoPilotResponse)
def get_profile(current_user: dict = Depends(get_current_user_payload), db: Session = Depends(get_db)):
    """Retrieve the profile data of the currently logged-in Loco Pilot."""
    employee_id = current_user.get("sub")
    role = current_user.get("role")
    
    if role != "Loco Pilot":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Loco Pilot access authorization required"
        )
        
    pilot = crud.get_loco_pilot_by_employee_id(db, employee_id)
    if not pilot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Loco Pilot profile record not found"
        )
    return pilot


@router.get("/history", response_model=List[schemas.LocoLoginHistoryResponse])
def get_history(current_user: dict = Depends(get_current_user_payload), db: Session = Depends(get_db)):
    """Retrieve the session login history for the active Loco Pilot."""
    employee_id = current_user.get("sub")
    role = current_user.get("role")
    
    if role != "Loco Pilot":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Loco Pilot access authorization required"
        )
        
    return crud.get_loco_login_history(db, employee_id)
