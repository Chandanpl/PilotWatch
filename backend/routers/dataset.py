from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import tempfile
import os
import zipfile

from google_drive import get_drive_service
from googleapiclient.http import MediaFileUpload


router = APIRouter(
    prefix="/dataset",
    tags=["Dataset"]
)


# =========================================================
# Google Drive folder IDs
# =========================================================

DRIVE_FOLDERS = {
    "videos": "1pdqmOZn0b7rnYPiYph2fdDgNNjVRcXFd",
    "images": "1SrG4mzrpAWbful2ngWTKRk-q9nB2m0NM",
    "datasets": "1iu-o14jEgaj9EQ49Lm6aqbqaQi8FkJS9",
    "other": "1WD8r-9f7IgSB6ZkGflYqEy7JvePdBor9",
}


# =========================================================
# Supported file types
# =========================================================

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


# =========================================================
# Determine Google Drive folder
# =========================================================

def get_drive_folder(extension: str) -> tuple[str, str]:

    extension = extension.lower()

    if extension in IMAGE_EXTENSIONS:
        return "images", DRIVE_FOLDERS["images"]

    if extension in VIDEO_EXTENSIONS:
        return "videos", DRIVE_FOLDERS["videos"]

    if extension in DATASET_EXTENSIONS:
        return "datasets", DRIVE_FOLDERS["datasets"]

    return "other", DRIVE_FOLDERS["other"]


# =========================================================
# MIME type
# =========================================================

def get_mime_type(filename: str) -> str:

    extension = Path(filename).suffix.lower()

    mime_types = {

        # Images
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".bmp": "image/bmp",
        ".webp": "image/webp",
        ".gif": "image/gif",

        # Videos
        ".mp4": "video/mp4",
        ".avi": "video/x-msvideo",
        ".mov": "video/quicktime",
        ".mkv": "video/x-matroska",
        ".wmv": "video/x-ms-wmv",
        ".webm": "video/webm",
        ".mpeg": "video/mpeg",
        ".mpg": "video/mpeg",

        # Documents
        ".pdf": "application/pdf",
        ".json": "application/json",
        ".txt": "text/plain",
        ".csv": "text/csv",
        ".xml": "application/xml",

        # Dataset archives
        ".zip": "application/zip",
        ".rar": "application/vnd.rar",
        ".7z": "application/x-7z-compressed",
        ".gz": "application/gzip",
        ".tar": "application/x-tar",
    }

    return mime_types.get(
        extension,
        "application/octet-stream"
    )


# =========================================================
# Dataset validation
# =========================================================

def validate_yolo_dataset(zip_path: str) -> dict:

    try:

        with zipfile.ZipFile(zip_path, "r") as zip_ref:

            # =================================================
            # Read ZIP contents
            # =================================================

            file_names = [
                name.replace("\\", "/").strip("/")
                for name in zip_ref.namelist()
                if name and not name.endswith("/")
            ]

            # =================================================
            # Supported YOLO image extensions
            # =================================================

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

            # =================================================
            # Find images
            # =================================================

            image_files = [
                name
                for name in file_names
                if Path(name).suffix.lower()
                in image_extensions
            ]

            image_count = len(image_files)

            # =================================================
            # Find labels
            # =================================================

            label_files = [
                name
                for name in file_names
                if Path(name).suffix.lower()
                in label_extensions
            ]

            label_count = len(label_files)

            # =================================================
            # Find data.yaml
            # =================================================

            yaml_files = [
                name
                for name in file_names
                if Path(name).name.lower() == "data.yaml"
            ]

            data_yaml = (
                yaml_files[0]
                if yaml_files
                else None
            )

            # =================================================
            # Normalize paths
            # =================================================

            normalized_paths = [
                name.lower()
                for name in file_names
            ]

            # =================================================
            # Folder detection helper
            # =================================================

            def has_path(path_fragment: str) -> bool:

                path_fragment = (
                    path_fragment
                    .lower()
                    .strip("/")
                )

                return any(
                    path == path_fragment
                    or path.startswith(
                        path_fragment + "/"
                    )
                    for path in normalized_paths
                )

            # =================================================
            # Roboflow YOLO structure
            # =================================================

            roboflow_train = (
                has_path("train/images")
                and has_path("train/labels")
            )

            roboflow_valid = (
                has_path("valid/images")
                and has_path("valid/labels")
            )

            roboflow_test = (
                has_path("test/images")
                and has_path("test/labels")
            )

            # =================================================
            # Standard YOLO structure
            # =================================================

            standard_train = (
                has_path("images/train")
                and has_path("labels/train")
            )

            standard_val = (
                has_path("images/val")
                and has_path("labels/val")
            )

            standard_test = (
                has_path("images/test")
                and has_path("labels/test")
            )

            # =================================================
            # Split availability
            # =================================================

            train_available = (
                roboflow_train
                or standard_train
            )

            validation_available = (
                roboflow_valid
                or standard_val
            )

            test_available = (
                roboflow_test
                or standard_test
            )

            # =================================================
            # Dataset structure
            # =================================================

            if (
                roboflow_train
                or roboflow_valid
                or roboflow_test
            ):

                dataset_structure = "Roboflow YOLO"

            elif (
                standard_train
                or standard_val
                or standard_test
            ):

                dataset_structure = "Standard YOLO"

            else:

                dataset_structure = "Unknown"

            # =================================================
            # Image ↔ Label matching
            #
            # IMPORTANT:
            #
            # We compare only the filename stem.
            #
            # Example:
            #
            # test/images/abc.jpg
            # test/labels/abc.txt
            #
            # Both become:
            #
            # abc
            #
            # Therefore they are correctly matched.
            # =================================================

            all_missing_labels = []
            all_unmatched_labels = []

            split_names = [
                "train",
                "valid",
                "val",
                "test"
            ]

            for split in split_names:

                # -------------------------------------------------
                # Images for this split
                # -------------------------------------------------

                split_images = [
                    file
                    for file in image_files
                    if (
                        f"/{split}/images/"
                        in file.lower()
                        or file.lower().startswith(
                            f"{split}/images/"
                        )
                    )
                ]

                # -------------------------------------------------
                # Labels for this split
                # -------------------------------------------------

                split_labels = [
                    file
                    for file in label_files
                    if (
                        f"/{split}/labels/"
                        in file.lower()
                        or file.lower().startswith(
                            f"{split}/labels/"
                        )
                    )
                ]

                # -------------------------------------------------
                # Image filename stems
                # -------------------------------------------------

                image_stems = {
                    Path(file).stem.lower()
                    for file in split_images
                }

                # -------------------------------------------------
                # Label filename stems
                # -------------------------------------------------

                label_stems = {
                    Path(file).stem.lower()
                    for file in split_labels
                }

                # -------------------------------------------------
                # Images without labels
                # -------------------------------------------------

                missing = sorted(
                    image_stems - label_stems
                )

                # -------------------------------------------------
                # Labels without images
                # -------------------------------------------------

                unmatched = sorted(
                    label_stems - image_stems
                )

                # -------------------------------------------------
                # Store missing labels
                # -------------------------------------------------

                all_missing_labels.extend(
                    [
                        f"{split}/images/{item}"
                        for item in missing
                    ]
                )

                # -------------------------------------------------
                # Store unmatched labels
                # -------------------------------------------------

                all_unmatched_labels.extend(
                    [
                        f"{split}/labels/{item}"
                        for item in unmatched
                    ]
                )

            # =================================================
            # Remove duplicates
            # =================================================

            all_missing_labels = sorted(
                set(all_missing_labels)
            )

            all_unmatched_labels = sorted(
                set(all_unmatched_labels)
            )

            missing_label_count = len(
                all_missing_labels
            )

            unmatched_label_count = len(
                all_unmatched_labels
            )

            # =================================================
            # Image-label consistency
            # =================================================

            image_label_match = (
                missing_label_count == 0
                and unmatched_label_count == 0
            )

            # =================================================
            # Training readiness
            # =================================================

            ready_for_training = (
                data_yaml is not None
                and train_available
                and validation_available
                and image_count > 0
                and label_count > 0
                and image_label_match
            )

            # =================================================
            # Return validation result
            # =================================================

            return {

                "images":
                    image_count,

                "labels":
                    label_count,

                "train_available":
                    train_available,

                "validation_available":
                    validation_available,

                "test_available":
                    test_available,

                "ready_for_training":
                    ready_for_training,

                "data_yaml":
                    data_yaml,

                "dataset_structure":
                    dataset_structure,

                "missing_label_count":
                    missing_label_count,

                "unmatched_label_count":
                    unmatched_label_count,

                "missing_labels":
                    all_missing_labels[:20],

                "unmatched_labels":
                    all_unmatched_labels[:20],

                "validation": {

                    "data_yaml_found":
                        data_yaml is not None,

                    "images_found":
                        image_count > 0,

                    "labels_found":
                        label_count > 0,

                    "train_found":
                        train_available,

                    "validation_found":
                        validation_available,

                    "test_found":
                        test_available,

                    "image_label_match":
                        image_label_match
                }
            }

    except zipfile.BadZipFile:

        raise HTTPException(
            status_code=400,
            detail=(
                "The uploaded file is not a valid "
                "ZIP dataset."
            )
        )

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Dataset validation failed: {str(e)}"
            )
        )


# =========================================================
# Upload Dataset
# =========================================================

@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...)
):

    # =====================================================
    # Check file
    # =====================================================

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file selected"
        )

    filename = Path(
        file.filename
    ).name

    extension = Path(
        filename
    ).suffix.lower()

    # =====================================================
    # Dataset Testing currently accepts ZIP only
    # =====================================================

    if extension != ".zip":

        raise HTTPException(
            status_code=400,
            detail=(
                "Dataset Testing currently accepts "
                "ZIP files only."
            )
        )

    temp_path = None

    try:

        # =================================================
        # 1. Save ZIP temporarily
        # =================================================

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension
        ) as temp_file:

            temp_path = temp_file.name

            while True:

                chunk = await file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                temp_file.write(chunk)

        # =================================================
        # 2. Validate dataset
        # =================================================

        validation = validate_yolo_dataset(
            temp_path
        )

        # =================================================
        # 3. Connect to Google Drive
        # =================================================

        service = get_drive_service()

        # =================================================
        # 4. Upload original ZIP
        # =================================================

        metadata = {
            "name": filename,
            "parents": [
                DRIVE_FOLDERS["datasets"]
            ]
        }

        media = MediaFileUpload(
            temp_path,
            mimetype="application/zip",
            resumable=True
        )

        uploaded_file = service.files().create(
            body=metadata,
            media_body=media,
            fields=(
                "id,"
                "name,"
                "size,"
                "webViewLink,"
                "mimeType"
            )
        ).execute()

        # =================================================
        # Close Google Drive file handle
        # =================================================

        if hasattr(media, "_fd") and media._fd:

            media._fd.close()

        # =================================================
        # 5. Delete temporary ZIP
        # =================================================

        if temp_path and os.path.exists(
            temp_path
        ):

            try:

                os.remove(temp_path)

            except PermissionError:

                pass

        # =================================================
        # 6. Return complete result
        # =================================================

        return {

            "success": True,

            "message": (
                "Dataset validated and uploaded "
                "successfully to Google Drive"
            ),

            # -------------------------------------------------
            # File information
            # -------------------------------------------------

            "filename": uploaded_file.get(
                "name",
                filename
            ),

            "file_id": uploaded_file.get(
                "id"
            ),

            "file_type": "datasets",

            "mime_type": uploaded_file.get(
                "mimeType",
                "application/zip"
            ),

            "size": uploaded_file.get(
                "size"
            ),

            "drive_link": uploaded_file.get(
                "webViewLink"
            ),

            # -------------------------------------------------
            # Dataset information
            # -------------------------------------------------

            "images":
                validation["images"],

            "labels":
                validation["labels"],

            "train_available":
                validation["train_available"],

            "validation_available":
                validation["validation_available"],

            "test_available":
                validation["test_available"],

            "ready_for_training":
                validation["ready_for_training"],

            "data_yaml":
                validation["data_yaml"],

            "dataset_structure":
                validation["dataset_structure"],

            # -------------------------------------------------
            # Label consistency
            # -------------------------------------------------

            "missing_label_count":
                validation[
                    "missing_label_count"
                ],

            "unmatched_label_count":
                validation[
                    "unmatched_label_count"
                ],

            "missing_labels":
                validation[
                    "missing_labels"
                ],

            "unmatched_labels":
                validation[
                    "unmatched_labels"
                ],

            # -------------------------------------------------
            # Validation details
            # -------------------------------------------------

            "validation":
                validation["validation"]
        }

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Dataset upload failed: "
                f"{str(e)}"
            )
        )

    finally:

        await file.close()

        if temp_path and os.path.exists(
            temp_path
        ):

            try:

                os.remove(temp_path)

            except PermissionError:

                pass