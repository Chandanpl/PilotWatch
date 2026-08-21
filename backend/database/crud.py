from datetime import datetime
from sqlalchemy.orm import Session
from database import models, schemas
from utils.security import hash_password

# ----------------- Loco Pilot CRUD -----------------

def get_loco_pilot_by_employee_id(db: Session, employee_id: str):
    """Retrieve a Loco Pilot by their unique Employee ID."""
    return db.query(models.LocoPilot).filter(models.LocoPilot.employee_id == employee_id).first()

def get_all_loco_pilots(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve all Loco Pilots with pagination."""
    return db.query(models.LocoPilot).offset(skip).limit(limit).all()

def create_loco_pilot(db: Session, pilot: schemas.LocoPilotCreate):
    """Create a new Loco Pilot with a hashed password."""
    hashed_pwd = hash_password(pilot.password)
    db_pilot = models.LocoPilot(
        employee_id=pilot.employee_id,
        full_name=pilot.full_name,
        email=pilot.email,
        phone_number=pilot.phone_number,
        password=hashed_pwd,
        train_number=pilot.train_number,
        locomotive_number=pilot.locomotive_number,
        assigned_route=pilot.assigned_route,
        status=pilot.status
    )
    db.add(db_pilot)
    db.commit()
    db.refresh(db_pilot)
    return db_pilot


# ----------------- Checkpost Watcher CRUD -----------------

def get_checkpost_watcher_by_employee_id(db: Session, employee_id: str):
    """Retrieve a Checkpost Watcher by their unique Employee ID."""
    return db.query(models.CheckpostWatcher).filter(models.CheckpostWatcher.employee_id == employee_id).first()

def get_all_checkpost_watchers(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve all Checkpost Watchers with pagination."""
    return db.query(models.CheckpostWatcher).offset(skip).limit(limit).all()

def create_checkpost_watcher(db: Session, watcher: schemas.CheckpostWatcherCreate):
    """Create a new Checkpost Watcher with a hashed password."""
    hashed_pwd = hash_password(watcher.password)
    db_watcher = models.CheckpostWatcher(
        employee_id=watcher.employee_id,
        full_name=watcher.full_name,
        email=watcher.email,
        phone_number=watcher.phone_number,
        password=hashed_pwd,
        checkpost_id=watcher.checkpost_id,
        checkpost_name=watcher.checkpost_name,
        location=watcher.location,
        shift=watcher.shift,
        status=watcher.status
    )
    db.add(db_watcher)
    db.commit()
    db.refresh(db_watcher)
    return db_watcher


# ----------------- Login History & Session Tracking CRUD -----------------

def create_loco_login_record(db: Session, employee_id: str, ip_address: str = None, device_name: str = None):
    """Start a login session for a Loco Pilot, closing any existing active sessions."""
    close_active_loco_sessions(db, employee_id)
    
    db_record = models.LocoLoginHistory(
        employee_id=employee_id,
        login_status="Active",
        ip_address=ip_address,
        device_name=device_name
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def close_active_loco_sessions(db: Session, employee_id: str):
    """Find and log out all active login history sessions for a Loco Pilot."""
    active_sessions = db.query(models.LocoLoginHistory).filter(
        models.LocoLoginHistory.employee_id == employee_id,
        models.LocoLoginHistory.login_status == "Active"
    ).all()
    
    now = datetime.utcnow()
    for session in active_sessions:
        session.logout_time = now
        duration = int((now - session.login_time).total_seconds())
        session.session_duration = max(0, duration)
        session.login_status = "Logged Out"
    
    if active_sessions:
        db.commit()

def get_loco_login_history(db: Session, employee_id: str):
    """Retrieve login history records for a Loco Pilot."""
    return db.query(models.LocoLoginHistory).filter(
        models.LocoLoginHistory.employee_id == employee_id
    ).order_by(models.LocoLoginHistory.login_time.desc()).all()


def create_checkpost_login_record(db: Session, employee_id: str, ip_address: str = None, device_name: str = None):
    """Start a login session for a Checkpost Watcher, closing any existing active sessions."""
    close_active_checkpost_sessions(db, employee_id)
    
    db_record = models.CheckpostLoginHistory(
        employee_id=employee_id,
        login_status="Active",
        ip_address=ip_address,
        device_name=device_name
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def close_active_checkpost_sessions(db: Session, employee_id: str):
    """Find and log out all active login history sessions for a Checkpost Watcher."""
    active_sessions = db.query(models.CheckpostLoginHistory).filter(
        models.CheckpostLoginHistory.employee_id == employee_id,
        models.CheckpostLoginHistory.login_status == "Active"
    ).all()
    
    now = datetime.utcnow()
    for session in active_sessions:
        session.logout_time = now
        duration = int((now - session.login_time).total_seconds())
        session.session_duration = max(0, duration)
        session.login_status = "Logged Out"
    
    if active_sessions:
        db.commit()

def get_checkpost_login_history(db: Session, employee_id: str):
    """Retrieve login history records for a Checkpost Watcher."""
    return db.query(models.CheckpostLoginHistory).filter(
        models.CheckpostLoginHistory.employee_id == employee_id
    ).order_by(models.CheckpostLoginHistory.login_time.desc()).all()


# ----------------- Database Initial Seeding -----------------

def seed_database(db: Session):
    """Seed the SQLite database with default demo data if not already present."""
    
    # 1. Default Loco Pilots
    loco_pilots_data = [
        {
            "employee_id": "LP001",
            "full_name": "Ravi Kumar",
            "password": "pilot123",
            "email": "ravi@pilotwatch.in",
            "train_number": "12301",
            "locomotive_number": "WAP7-37001",
            "assigned_route": "NDLS-BPL"
        },
        {
            "employee_id": "LP002",
            "full_name": "Arun Singh",
            "password": "pilot123",
            "email": "arun@pilotwatch.in",
            "train_number": "12626",
            "locomotive_number": "WAP7-37002",
            "assigned_route": "BPL-NDLS"
        }
    ]
    
    for pilot_info in loco_pilots_data:
        existing = get_loco_pilot_by_employee_id(db, pilot_info["employee_id"])
        if not existing:
            hashed_pwd = hash_password(pilot_info["password"])
            db_pilot = models.LocoPilot(
                employee_id=pilot_info["employee_id"],
                full_name=pilot_info["full_name"],
                email=pilot_info["email"],
                password=hashed_pwd,
                train_number=pilot_info["train_number"],
                locomotive_number=pilot_info["locomotive_number"],
                assigned_route=pilot_info["assigned_route"],
                status="Active"
            )
            db.add(db_pilot)
            
    # 2. Default Checkpost Watchers (mapped from CP credentials)
    checkpost_watchers_data = [
        {
            "employee_id": "CP001",
            "full_name": "Mahesh",
            "password": "check123",
            "email": "mahesh@pilotwatch.in",
            "checkpost_id": "CP42",
            "checkpost_name": "Gate 42 Crossing",
            "location": "Km 425/6",
            "shift": "Day"
        },
        {
            "employee_id": "CP002",
            "full_name": "Suresh",
            "password": "check123",
            "email": "suresh@pilotwatch.in",
            "checkpost_id": "CP43",
            "checkpost_name": "Gate 43 Crossing",
            "location": "Km 430/1",
            "shift": "Night"
        }
    ]
    
    for watcher_info in checkpost_watchers_data:
        existing = get_checkpost_watcher_by_employee_id(db, watcher_info["employee_id"])
        if not existing:
            hashed_pwd = hash_password(watcher_info["password"])
            db_watcher = models.CheckpostWatcher(
                employee_id=watcher_info["employee_id"],
                full_name=watcher_info["full_name"],
                email=watcher_info["email"],
                password=hashed_pwd,
                checkpost_id=watcher_info["checkpost_id"],
                checkpost_name=watcher_info["checkpost_name"],
                location=watcher_info["location"],
                shift=watcher_info["shift"],
                status="Active"
            )
            db.add(db_watcher)
            
    db.commit()
