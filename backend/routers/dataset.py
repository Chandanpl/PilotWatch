from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import tempfile
import os

from google_drive import get_drive_service
from googleapiclient.http import MediaFileUpload


router = APIRouter(
    prefix="/dataset",
    tags=["Dataset"]
)


# Google Drive folder IDs created earlier
DRIVE_FOLDERS = {
    "videos": "1pdqmOZn0b7rnYPiYph2fdDgNNjVRcXFd",
    "images": "1SrG4mzrpAWbful2ngWTKRk-q9nB2m0NM",
    "datasets": "1iu-o14jEgaj9EQ49Lm6aqbqaQi8FkJS9",
    "other": "1WD8r-9f7IgSB6ZkGflYqEy7JvePdBor9",
}


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
    ".gif"
}

VIDEO_EXTENSIONS = {
    ".mp4",
    ".avi",
    ".mov",
    ".mkv",
    ".wmv",
    ".webm",
    ".mpeg",
    ".mpg"
}

DATASET_EXTENSIONS = {
    ".zip",
    ".tar",
    ".gz",
    ".7z",
    ".rar"
}


def get_drive_folder(extension: str) -> tuple[str, str]:

    extension = extension.lower()

    if extension in IMAGE_EXTENSIONS:
        return "images", DRIVE_FOLDERS["images"]

    if extension in VIDEO_EXTENSIONS:
        return "videos", DRIVE_FOLDERS["videos"]

    if extension in DATASET_EXTENSIONS:
        return "datasets", DRIVE_FOLDERS["datasets"]

    return "other", DRIVE_FOLDERS["other"]


def get_mime_type(filename: str) -> str:

    extension = Path(filename).suffix.lower()

    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".bmp": "image/bmp",
        ".webp": "image/webp",
        ".gif": "image/gif",

        ".mp4": "video/mp4",
        ".avi": "video/x-msvideo",
        ".mov": "video/quicktime",
        ".mkv": "video/x-matroska",
        ".webm": "video/webm",

        ".pdf": "application/pdf",
        ".json": "application/json",
        ".txt": "text/plain",
        ".csv": "text/csv",
        ".xml": "application/xml",

        ".zip": "application/zip",
        ".rar": "application/vnd.rar",
        ".7z": "application/x-7z-compressed",
    }

    return mime_types.get(
        extension,
        "application/octet-stream"
    )


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected"
        )

    filename = Path(file.filename).name

    extension = Path(filename).suffix.lower()

    folder_type, folder_id = get_drive_folder(extension)

    temp_path = None

    try:

        # -------------------------------------------------
        # 1. Save file temporarily
        # -------------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension
        ) as temp_file:

            temp_path = temp_file.name

            while True:

                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                temp_file.write(chunk)

        # -------------------------------------------------
        # 2. Connect to Google Drive
        # -------------------------------------------------

        service = get_drive_service()

        # -------------------------------------------------
        # 3. Upload to correct PilotWatch folder
        # -------------------------------------------------

        metadata = {
            "name": filename,
            "parents": [folder_id]
        }

        media = MediaFileUpload(
            temp_path,
            mimetype=get_mime_type(filename),
            resumable=True
        )

        uploaded_file = service.files().create(
            body=metadata,
            media_body=media,
            fields="id,name,size,webViewLink,mimeType"
        ).execute()
        media._fd.close()
        # -------------------------------------------------
        # 4. Remove temporary local file
        # -------------------------------------------------

        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except PermissionError:
                pass
        # -------------------------------------------------
        # 5. Return result
        # -------------------------------------------------

        return {
            "success": True,
            "message": "File uploaded successfully to Google Drive",

            "filename": uploaded_file.get(
                "name",
                filename
            ),

            "file_id": uploaded_file.get("id"),

            "file_type": folder_type,

            "mime_type": uploaded_file.get(
                "mimeType",
                get_mime_type(filename)
            ),

            "size": uploaded_file.get("size"),

            "drive_link": uploaded_file.get(
                "webViewLink"
            )
        }

    except Exception as e:

        # Always remove temporary file
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        raise HTTPException(
            status_code=500,
            detail=f"Google Drive upload failed: {str(e)}"
        )

    finally:

        await file.close()