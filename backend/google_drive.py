from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# =========================================================
# Google Drive OAuth settings
# =========================================================

SCOPES = [
    "https://www.googleapis.com/auth/drive.file"
]

BASE_DIR = Path(__file__).resolve().parent

CLIENT_SECRET_FILE = (
    BASE_DIR
    / "credentials"
    / "client_secret.json"
)

TOKEN_FILE = (
    BASE_DIR
    / "credentials"
    / "token.json"
)


# =========================================================
# Get Google Drive service
# =========================================================

def get_drive_service():

    credentials = None

    # -----------------------------------------------------
    # Load existing OAuth token
    # -----------------------------------------------------

    if TOKEN_FILE.exists():

        from google.oauth2.credentials import Credentials

        credentials = Credentials.from_authorized_user_file(
            str(TOKEN_FILE),
            SCOPES
        )

    # -----------------------------------------------------
    # Authenticate if required
    # -----------------------------------------------------

    if not credentials or not credentials.valid:

        flow = InstalledAppFlow.from_client_secrets_file(
            str(CLIENT_SECRET_FILE),
            SCOPES
        )

        # IMPORTANT:
        # FastAPI uses port 8000.
        # Google OAuth uses port 8001.
        credentials = flow.run_local_server(
            port=8001
        )

        # Save token
        TOKEN_FILE.write_text(
            credentials.to_json(),
            encoding="utf-8"
        )

    # -----------------------------------------------------
    # Build Drive API service
    # -----------------------------------------------------

    service = build(
        "drive",
        "v3",
        credentials=credentials
    )

    return service


# =========================================================
# Create Google Drive folder
# =========================================================

def create_folder(
    service,
    folder_name,
    parent_id=None
):

    metadata = {
        "name": folder_name,
        "mimeType":
            "application/vnd.google-apps.folder"
    }

    if parent_id:

        metadata["parents"] = [
            parent_id
        ]

    folder = service.files().create(
        body=metadata,
        fields="id,name"
    ).execute()

    return folder["id"]


# =========================================================
# Find Google Drive folder
# =========================================================

def find_folder(
    service,
    folder_name,
    parent_id=None
):

    query = (
        f"name = '{folder_name}' "
        f"and mimeType = "
        f"'application/vnd.google-apps.folder' "
        f"and trashed = false"
    )

    if parent_id:

        query += (
            f" and '{parent_id}' in parents"
        )

    results = service.files().list(
        q=query,
        spaces="drive",
        fields="files(id,name)",
        pageSize=10
    ).execute()

    folders = results.get(
        "files",
        []
    )

    if folders:

        return folders[0]["id"]

    return None


# =========================================================
# Get existing folder or create it
# =========================================================

def get_or_create_folder(
    service,
    folder_name,
    parent_id=None
):

    folder_id = find_folder(
        service,
        folder_name,
        parent_id
    )

    if folder_id:

        return folder_id

    return create_folder(
        service,
        folder_name,
        parent_id
    )


# =========================================================
# Setup PilotWatch Drive folders
# =========================================================

def setup_pilotwatch_folders():

    service = get_drive_service()

    # -----------------------------------------------------
    # PilotWatch
    # -----------------------------------------------------

    pilotwatch_id = get_or_create_folder(
        service,
        "PilotWatch"
    )

    # -----------------------------------------------------
    # Dataset
    # -----------------------------------------------------

    dataset_id = get_or_create_folder(
        service,
        "Dataset",
        pilotwatch_id
    )

    # -----------------------------------------------------
    # Videos
    # -----------------------------------------------------

    videos_id = get_or_create_folder(
        service,
        "Videos",
        dataset_id
    )

    # -----------------------------------------------------
    # Images
    # -----------------------------------------------------

    images_id = get_or_create_folder(
        service,
        "Images",
        dataset_id
    )

    # -----------------------------------------------------
    # Datasets
    # -----------------------------------------------------

    datasets_id = get_or_create_folder(
        service,
        "Datasets",
        dataset_id
    )

    # -----------------------------------------------------
    # Other
    # -----------------------------------------------------

    other_id = get_or_create_folder(
        service,
        "Other",
        dataset_id
    )

    return {

        "pilotwatch":
            pilotwatch_id,

        "dataset":
            dataset_id,

        "videos":
            videos_id,

        "images":
            images_id,

        "datasets":
            datasets_id,

        "other":
            other_id
    }