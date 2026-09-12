from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import tempfile
import os

from google_drive import get_drive_service
from googleapiclient.http import MediaIoBaseDownload

from training import (
    start_training,
    get_training_status
)


router = APIRouter(
    prefix="/training",
    tags=["Training"]
)


# =========================================================
# Training request
# =========================================================

class TrainingRequest(BaseModel):

    file_id: str

    epochs: int = 50

    imgsz: int = 640

    batch: int = 8


# =========================================================
# Start training
# =========================================================

@router.post("/start")
async def start_model_training(
    request: TrainingRequest
):

    try:

        # -------------------------------------------------
        # Connect to Google Drive
        # -------------------------------------------------

        service = get_drive_service()

        # -------------------------------------------------
        # Get file information
        # -------------------------------------------------

        file_info = service.files().get(
            fileId=request.file_id,
            fields="id,name,size,mimeType"
        ).execute()

        filename = file_info.get(
            "name",
            "dataset.zip"
        )

        # -------------------------------------------------
        # Make temporary ZIP file
        # -------------------------------------------------

        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".zip"
        )

        temp_path = temp_file.name

        temp_file.close()

        # -------------------------------------------------
        # Download from Google Drive
        # -------------------------------------------------

        request_media = service.files().get_media(
            fileId=request.file_id
        )

        with open(
            temp_path,
            "wb"
        ) as output_file:

            downloader = MediaIoBaseDownload(
                output_file,
                request_media
            )

            done = False

            while not done:

                status, done = downloader.next_chunk()

        # -------------------------------------------------
        # Start background training
        # -------------------------------------------------

        result = start_training(

            temp_path,

            epochs=request.epochs,

            imgsz=request.imgsz,

            batch=request.batch
        )

        return {

            "success": True,

            "message":
                "Training started successfully.",

            "filename":
                filename,

            "file_id":
                request.file_id,

            "job_id":
                result.get("job_id"),

            "status":
                result.get("status")
        }

    except Exception as e:

        if "temp_path" in locals():

            if os.path.exists(
                temp_path
            ):

                try:
                    os.remove(
                        temp_path
                    )
                except:
                    pass

        raise HTTPException(

            status_code=500,

            detail=(
                f"Could not start training: {str(e)}"
            )
        )


# =========================================================
# Training status
# =========================================================

@router.get("/status")
def training_status():

    return {

        "success": True,

        **get_training_status()

    }