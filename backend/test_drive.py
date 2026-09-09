from google_drive import get_drive_service

service = get_drive_service()

about = service.about().get(
    fields="user"
).execute()

print("Google Drive connected!")
print("Account:", about["user"]["emailAddress"])