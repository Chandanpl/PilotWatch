from google_drive import setup_pilotwatch_folders


folders = setup_pilotwatch_folders()

print("\nPilotWatch Google Drive folders created successfully!\n")

for name, folder_id in folders.items():
    print(f"{name}: {folder_id}")