import cv2
from ultralytics import YOLO
from pathlib import Path


# --------------------------------------------------
# Paths
# --------------------------------------------------

MODEL_PATH = Path(__file__).parent / "models" / "yolo11n.pt"

INPUT_VIDEO = Path(__file__).parent / "input" / "videos" / "test.mp4"

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_VIDEO = OUTPUT_DIR / "detected_video.mp4"


# --------------------------------------------------
# Load YOLO model
# --------------------------------------------------

print("Loading YOLO model...")

model = YOLO(str(MODEL_PATH))

print("YOLO model loaded successfully!")


# --------------------------------------------------
# Open video
# --------------------------------------------------

cap = cv2.VideoCapture(str(INPUT_VIDEO))

if not cap.isOpened():
    raise RuntimeError(
        f"Could not open video: {INPUT_VIDEO}"
    )


fps = cap.get(cv2.CAP_PROP_FPS)

if fps <= 0:
    fps = 25


width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))


# --------------------------------------------------
# Output video writer
# --------------------------------------------------

fourcc = cv2.VideoWriter_fourcc(*"mp4v")

writer = cv2.VideoWriter(
    str(OUTPUT_VIDEO),
    fourcc,
    fps,
    (width, height)
)


# --------------------------------------------------
# Process video
# --------------------------------------------------

frame_number = 0

print("\nStarting video detection...\n")


while True:

    success, frame = cap.read()

    if not success:
        break

    frame_number += 1

    # YOLO detection
    results = model(
        frame,
        verbose=False
    )

    # Draw detections
    annotated_frame = results[0].plot()

    writer.write(annotated_frame)

    # Display
    cv2.imshow(
        "PilotWatch - YOLO Video Detection",
        annotated_frame
    )

    # Press Q to stop
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# --------------------------------------------------
# Cleanup
# --------------------------------------------------

cap.release()
writer.release()
cv2.destroyAllWindows()


print("\nVideo detection completed!")
print(f"Frames processed: {frame_number}")
print(f"Output video: {OUTPUT_VIDEO}")