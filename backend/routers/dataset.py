from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import zipfile
import shutil
import uuid

router = APIRouter(
    prefix="/dataset",
    tags=["Dataset"]
)

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Dataset directory
DATASET_DIR = PROJECT_ROOT / "ai" / "dataset"

# Temporary uploads
UPLOAD_DIR = PROJECT_ROOT / "ai" / "dataset_uploads"

DATASET_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


ALLOWED_EXTENSIONS = {".zip"}


def count_files(directory: Path, extensions=None):
    if not directory.exists():
        return 0

    if extensions:
        return sum(
            1
            for file in directory.rglob("*")
            if file.is_file() and file.suffix.lower() in extensions
        )

    return sum(
        1
        for file in directory.rglob("*")
        if file.is_file()
    )


def find_yaml_file(directory: Path):
    for file in directory.rglob("*.yaml"):
        return file

    for file in directory.rglob("*.yml"):
        return file

    return None


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No dataset file selected"
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only ZIP dataset files are supported"
        )

    unique_name = f"{uuid.uuid4()}_{file.filename}"

    zip_path = UPLOAD_DIR / unique_name

    try:

        # Save uploaded ZIP
        with open(zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Clear previous dataset
        if DATASET_DIR.exists():
            for item in DATASET_DIR.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()

        # Extract ZIP
        with zipfile.ZipFile(zip_path, "r") as zip_ref:

            # Security check against path traversal
            for member in zip_ref.infolist():

                member_path = DATASET_DIR / member.filename

                if not member_path.resolve().is_relative_to(
                    DATASET_DIR.resolve()
                ):
                    raise HTTPException(
                        status_code=400,
                        detail="Unsafe ZIP file detected"
                    )

            zip_ref.extractall(DATASET_DIR)

        # Remove temporary ZIP
        zip_path.unlink(missing_ok=True)

        # Count files
        image_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".bmp",
            ".webp"
        }

        label_extensions = {
            ".txt"
        }

        image_count = count_files(
            DATASET_DIR,
            image_extensions
        )

        label_count = count_files(
            DATASET_DIR,
            label_extensions
        )

        yaml_file = find_yaml_file(DATASET_DIR)

        # Detect common YOLO folders
        train_exists = (
            (DATASET_DIR / "images" / "train").exists()
            or (DATASET_DIR / "train" / "images").exists()
        )

        val_exists = (
            (DATASET_DIR / "images" / "val").exists()
            or (DATASET_DIR / "valid" / "images").exists()
            or (DATASET_DIR / "val" / "images").exists()
        )

        test_exists = (
            (DATASET_DIR / "images" / "test").exists()
            or (DATASET_DIR / "test" / "images").exists()
        )

        dataset_ready = (
            image_count > 0
            and label_count > 0
            and yaml_file is not None
        )

        return {
            "success": True,
            "message": "Dataset uploaded successfully",
            "filename": file.filename,
            "dataset_path": str(DATASET_DIR),
            "images": image_count,
            "labels": label_count,
            "data_yaml": yaml_file.name if yaml_file else None,
            "train_available": train_exists,
            "validation_available": val_exists,
            "test_available": test_exists,
            "ready_for_training": dataset_ready
        }

    except zipfile.BadZipFile:

        zip_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=400,
            detail="Invalid or corrupted ZIP file"
        )

    except Exception as e:

        zip_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail=f"Dataset processing failed: {str(e)}"
        )