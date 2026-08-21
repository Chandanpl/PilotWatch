from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    success: bool
    token: str
    role: str

class TokenData(BaseModel):
    employee_id: str
    role: str

class LoginRequest(BaseModel):
    employee_id: str
    password: str
    ip_address: Optional[str] = None
    device_name: Optional[str] = None


# Loco Pilot Schemas
class LocoPilotBase(BaseModel):
    employee_id: str
    full_name: str
    email: Optional[str] = None
    phone_number: Optional[str] = None
    train_number: Optional[str] = None
    locomotive_number: Optional[str] = None
    assigned_route: Optional[str] = None
    status: Optional[str] = "Active"

class LocoPilotCreate(LocoPilotBase):
    password: str

class LocoPilotResponse(LocoPilotBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 compatibility for SQLAlchemy objects (orm_mode in v1)


# Checkpost Watcher Schemas
class CheckpostWatcherBase(BaseModel):
    employee_id: str
    full_name: str
    email: Optional[str] = None
    phone_number: Optional[str] = None
    checkpost_id: Optional[str] = None
    checkpost_name: Optional[str] = None
    location: Optional[str] = None
    shift: Optional[str] = None
    status: Optional[str] = "Active"

class CheckpostWatcherCreate(CheckpostWatcherBase):
    password: str

class CheckpostWatcherResponse(CheckpostWatcherBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Login History Schemas
class LocoLoginHistoryResponse(BaseModel):
    session_id: str
    employee_id: str
    login_time: datetime
    logout_time: Optional[datetime] = None
    session_duration: Optional[int] = None
    login_status: str
    ip_address: Optional[str] = None
    device_name: Optional[str] = None

    class Config:
        from_attributes = True


class CheckpostLoginHistoryResponse(BaseModel):
    session_id: str
    employee_id: str
    login_time: datetime
    logout_time: Optional[datetime] = None
    session_duration: Optional[int] = None
    login_status: str
    ip_address: Optional[str] = None
    device_name: Optional[str] = None

    class Config:
        from_attributes = True
