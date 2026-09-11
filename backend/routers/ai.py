from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import tempfile
import os
import json

from ai.detection import detect_image

router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


BASE_DIR = Path(__file__).resolve().parents[2]

ALERT_FILE = (
    BASE_DIR
    / "ai"
    / "output"
    / "alerts.json"
)


# --------------------------------------------------
# AI STATUS
# --------------------------------------------------

@router.get("/status")
def ai_status():

    return {
        "success": True,
        "service": "PilotWatch AI",
        "status": "ready"
    }


# --------------------------------------------------
# IMAGE DETECTION
# --------------------------------------------------

@router.post("/detect")
async def detect(
    file: UploadFile = File(...)
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No image selected"
        )

    extension = (
        Path(file.filename)
        .suffix
        .lower()
    )

    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".webp"
    }

    if extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail="Only image files are supported"
        )

    temp_path = None

    try:

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

        detections = detect_image(
            temp_path
        )

        return {

            "success": True,

            "filename": file.filename,

            "detections": detections,

            "count": len(detections)
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"AI detection failed: {str(e)}"
        )

    finally:

        await file.close()

        if (
            temp_path
            and
            os.path.exists(temp_path)
        ):

            try:
                os.remove(temp_path)

            except Exception:
                pass


# --------------------------------------------------
# GET ACTIVE ALERTS
# --------------------------------------------------

@router.get("/alerts")
def get_alerts():

    if not ALERT_FILE.exists():

        return {
            "success": True,
            "active_alerts": [],
            "alert_history": []
        }

    try:

        with open(
            ALERT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return {
            "success": True,
            "active_alerts": data.get(
                "active_alerts",
                []
            ),
            "alert_history": data.get(
                "alert_history",
                []
            )
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Could not read alerts: {str(e)}"
        )


# --------------------------------------------------
# GET ONLY ACTIVE ALERTS
# --------------------------------------------------

@router.get("/alerts/active")
def get_active_alerts():

    if not ALERT_FILE.exists():

        return {
            "success": True,
            "active_alerts": []
        }

    try:

        with open(
            ALERT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return {
            "success": True,
            "active_alerts": data.get(
                "active_alerts",
                []
            )
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Could not read active alerts: {str(e)}"
        )


# --------------------------------------------------
# GET ALERT HISTORY
# --------------------------------------------------

@router.get("/alerts/history")
def get_alert_history():

    if not ALERT_FILE.exists():

        return {
            "success": True,
            "alert_history": []
        }

    try:

        with open(
            ALERT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return {
            "success": True,
            "alert_history": data.get(
                "alert_history",
                []
            )
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Could not read alert history: {str(e)}"
        )