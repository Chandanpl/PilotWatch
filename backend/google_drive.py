from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


SCOPES = [
    "https://www.googleapis.com/auth/drive.file"
]

BASE_DIR = Path(__file__).resolve().parent

CLIENT_SECRET_FILE = BASE_DIR / "credentials" / "client_secret.json"
TOKEN_FILE = BASE_DIR / "credentials" / "token.json"


def get_drive_service():
    credentials = None

    if TOKEN_FILE.exists():
        from google.oauth2.credentials import Credentials

        credentials = Credentials.from_authorized_user_file(
            str(TOKEN_FILE),
            SCOPES
        )

    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(CLIENT_SECRET_FILE),
            SCOPES
        )

        credentials = flow.run_local_server(
            port=8000
        )

        TOKEN_FILE.write_text(
            credentials.to_json(),
            encoding="utf-8"
        )

    service = build(
        "drive",
        "v3",
        credentials=credentials
    )

    return service


def create_folder(service, folder_name, parent_id=None):
    """Create a folder in Google Drive."""

    metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder"
    }

    if parent_id:
        metadata["parents"] = [parent_id]

    folder = service.files().create(
        body=metadata,
        fields="id, name"
    ).execute()

    return folder["id"]


def find_folder(service, folder_name, parent_id=None):
    """Find an existing folder."""

    query = (
        f"name = '{folder_name}' "
        f"and mimeType = 'application/vnd.google-apps.folder' "
        f"and trashed = false"
    )

    if parent_id:
        query += f" and '{parent_id}' in parents"

    results = service.files().list(
        q=query,
        spaces="drive",
        fields="files(id, name)",
        pageSize=10
    ).execute()

    folders = results.get("files", [])

    if folders:
        return folders[0]["id"]

    return None


def get_or_create_folder(service, folder_name, parent_id=None):
    """Return existing folder or create it."""

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


def setup_pilotwatch_folders():
    """Create PilotWatch Dataset folder structure."""

    service = get_drive_service()

    # Main PilotWatch folder
    pilotwatch_id = get_or_create_folder(
        service,
        "PilotWatch"
    )

    # Dataset folder
    dataset_id = get_or_create_folder(
        service,
        "Dataset",
        pilotwatch_id
    )

    # Dataset subfolders
    videos_id = get_or_create_folder(
        service,
        "Videos",
        dataset_id
    )

    images_id = get_or_create_folder(
        service,
        "Images",
        dataset_id
    )

    datasets_id = get_or_create_folder(
        service,
        "Datasets",
        dataset_id
    )

    other_id = get_or_create_folder(
        service,
        "Other",
        dataset_id
    )

    return {
        "pilotwatch": pilotwatch_id,
        "dataset": dataset_id,
        "videos": videos_id,
        "images": images_id,
        "datasets": datasets_id,
        "other": other_id
    }