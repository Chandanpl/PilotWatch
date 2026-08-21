from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.database import engine, SessionLocal
from database import models, crud
from routers import auth, loco, checkpost

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle context manager to create tables and seed default users on application startup."""
    # 1. Automatically create database tables if they do not exist
    models.Base.metadata.create_all(bind=engine)
    
    # 2. Open temporary database session to seed default demo accounts
    db = SessionLocal()
    try:
        crud.seed_database(db)
    finally:
        db.close()
        
    yield  # Hand over control to FastAPI execution loop


# Initialize FastAPI app with modern lifespan lifecycle hook
app = FastAPI(
    title="PilotWatch Railway Safety Monitoring System API",
    description="Backend API database and session tracking system for PilotWatch",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS middleware to enable React frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production to allow specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(loco.router)
app.include_router(checkpost.router)


@app.get("/")
def read_root():
    return {
        "status": "Online",
        "service": "PilotWatch Backend Service",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    # Start the server locally on port 8000
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
