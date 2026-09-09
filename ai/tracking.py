import cv2
from ultralytics import YOLO
from pathlib import Path

# =========================
# PATHS
# =========================

BASE_DIR = Path(__file__).parent

MODEL_PATH = BASE_DIR / "models" / "yolo11n.pt"
INPUT_VIDEO = BASE_DIR / "input" / "videos" / "railway_test.mp4"

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_VIDEO = OUTPUT_DIR / "tracked_video.mp4"


# =========================
# LOAD MODEL
# =========================

print("Loading YOLO model...")

model = YOLO(str(MODEL_PATH))

print("YOLO model loaded successfully!")
print("Starting ByteTrack tracking...\n")


# =========================
# OPEN VIDEO
# =========================

cap = cv2.VideoCapture(str(INPUT_VIDEO))

if not cap.isOpened():
    raise RuntimeError(f"Could not open video: {INPUT_VIDEO}")


fps = cap.get(cv2.CAP_PROP_FPS)

if fps <= 0:
    fps = 25

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))


# =========================
# OUTPUT VIDEO
# =========================

fourcc = cv2.VideoWriter_fourcc(*"mp4v")

writer = cv2.VideoWriter(
    str(OUTPUT_VIDEO),
    fourcc,
    fps,
    (width, height)
)


# =========================
# TRACKING LOOP
# =========================

frame_number = 0
unique_ids = set()

while True:

    success, frame = cap.read()

    if not success:
        break

    frame_number += 1

    # YOLO + ByteTrack
    results = model.track(
        frame,
        persist=True,
        tracker="bytetrack.yaml",
        verbose=False
    )

    result = results[0]

    # Draw tracking results
    annotated_frame = result.plot()

    # Get tracking IDs
    if result.boxes is not None and result.boxes.id is not None:

        track_ids = result.boxes.id.int().cpu().tolist()

        for track_id in track_ids:
            unique_ids.add(track_id)

    writer.write(annotated_frame)

    cv2.imshow(
        "PilotWatch - ByteTrack",
        annotated_frame
    )

    # Press Q to stop
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# =========================
# CLEANUP
# =========================

cap.release()
writer.release()
cv2.destroyAllWindows()


# =========================
# RESULTS
# =========================

print("\nByteTrack tracking completed!")

print(f"Frames processed: {frame_number}")

print(f"Unique objects tracked: {len(unique_ids)}")

print(f"Output video: {OUTPUT_VIDEO}")