from datetime import datetime
import uuid
from sqlalchemy import Column, Integer, String, DateTime
from database.database import Base

class LocoPilot(Base):
    __tablename__ = "loco_pilots"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    password = Column(String, nullable=False)  # Hashed
    train_number = Column(String, nullable=True)
    locomotive_number = Column(String, nullable=True)
    assigned_route = Column(String, nullable=True)
    status = Column(String, default="Active")  # "Active" or "Inactive"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CheckpostWatcher(Base):
    __tablename__ = "checkpost_watchers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    password = Column(String, nullable=False)  # Hashed
    checkpost_id = Column(String, nullable=True)
    checkpost_name = Column(String, nullable=True)
    location = Column(String, nullable=True)
    shift = Column(String, nullable=True)
    status = Column(String, default="Active")  # "Active" or "Inactive"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LocoLoginHistory(Base):
    __tablename__ = "loco_login_history"

    session_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String, nullable=False)
    login_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    logout_time = Column(DateTime, nullable=True)
    session_duration = Column(Integer, nullable=True)  # Duration stored in seconds
    login_status = Column(String, default="Active")  # "Active" or "Logged Out"
    ip_address = Column(String, nullable=True)
    device_name = Column(String, nullable=True)


class CheckpostLoginHistory(Base):
    __tablename__ = "checkpost_login_history"

    session_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String, nullable=False)
    login_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    logout_time = Column(DateTime, nullable=True)
    session_duration = Column(Integer, nullable=True)  # Duration stored in seconds
    login_status = Column(String, default="Active")  # "Active" or "Logged Out"
    ip_address = Column(String, nullable=True)
    device_name = Column(String, nullable=True)
