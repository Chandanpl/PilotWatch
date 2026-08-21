from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import crud, schemas
from database.database import get_db
from utils.security import verify_password, create_access_token, get_current_user_payload

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login/loco", response_model=schemas.Token)
def login_loco(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Authenticate a Loco Pilot, generate a JWT token, and log the session start time."""
    pilot = crud.get_loco_pilot_by_employee_id(db, request.employee_id)
    if not pilot or not verify_password(request.password, pilot.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Employee ID or Password"
        )
    if pilot.status != "Active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Loco Pilot account is Inactive"
        )
    
    # Record the login event in history
    crud.create_loco_login_record(
        db, 
        employee_id=pilot.employee_id, 
        ip_address=request.ip_address, 
        device_name=request.device_name
    )
    
    # Generate the access token containing subject and role
    token_data = {"sub": pilot.employee_id, "role": "Loco Pilot"}
    token = create_access_token(data=token_data)
    
    return {
        "success": True,
        "token": token,
        "role": "Loco Pilot"
    }


@router.post("/login/checkpost", response_model=schemas.Token)
def login_checkpost(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Authenticate a Checkpost Watcher, generate a JWT token, and log the session start time."""
    watcher = crud.get_checkpost_watcher_by_employee_id(db, request.employee_id)
    if not watcher or not verify_password(request.password, watcher.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Employee ID or Password"
        )
    if watcher.status != "Active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Checkpost Watcher account is Inactive"
        )
    
    # Record the login event in history
    crud.create_checkpost_login_record(
        db, 
        employee_id=watcher.employee_id, 
        ip_address=request.ip_address, 
        device_name=request.device_name
    )
    
    # Generate the access token containing subject and role
    token_data = {"sub": watcher.employee_id, "role": "Checkpost Watcher"}
    token = create_access_token(data=token_data)
    
    return {
        "success": True,
        "token": token,
        "role": "Checkpost Watcher"
    }


@router.post("/logout/loco")
def logout_loco(current_user: dict = Depends(get_current_user_payload), db: Session = Depends(get_db)):
    """Log out a Loco Pilot, update their session end time, and calculate active duration."""
    employee_id = current_user.get("sub")
    role = current_user.get("role")
    
    if role != "Loco Pilot":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid role token for Loco Pilot logout"
        )
        
    crud.close_active_loco_sessions(db, employee_id)
    return {"success": True, "message": "Loco Pilot logged out successfully"}


@router.post("/logout/checkpost")
def logout_checkpost(current_user: dict = Depends(get_current_user_payload), db: Session = Depends(get_db)):
    """Log out a Checkpost Watcher, update their session end time, and calculate active duration."""
    employee_id = current_user.get("sub")
    role = current_user.get("role")
    
    if role != "Checkpost Watcher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid role token for Checkpost Watcher logout"
        )
        
    crud.close_active_checkpost_sessions(db, employee_id)
    return {"success": True, "message": "Checkpost Watcher logged out successfully"}
