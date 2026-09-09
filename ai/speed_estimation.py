import cv2
from ultralytics import YOLO
from pathlib import Path
from collections import defaultdict
import math

# =========================
# PATHS
# =========================

BASE_DIR = Path(__file__).parent

MODEL_PATH = BASE_DIR / "models" / "yolo11n.pt"
INPUT_VIDEO = BASE_DIR / "input" / "videos" / "railway_test.mp4"

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_VIDEO = OUTPUT_DIR / "speed_estimation.mp4"


# =========================
# SETTINGS
# =========================

HISTORY_LENGTH = 10

# Ignore tiny movements caused by detection noise
MOVEMENT_THRESHOLD = 2.0


# =========================
# LOAD MODEL
# =========================

print("Loading YOLO model...")

model = YOLO(str(MODEL_PATH))

print("YOLO model loaded successfully!")
print("Starting speed estimation...\n")


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
# POSITION HISTORY
# =========================

position_history = defaultdict(list)

frame_number = 0


# =========================
# SPEED TRACKING
# =========================

while True:

    success, frame = cap.read()

    if not success:
        break

    frame_number += 1

    results = model.track(
        frame,
        persist=True,
        tracker="bytetrack.yaml",
        verbose=False
    )

    result = results[0]

    annotated_frame = frame.copy()


    # =========================
    # PROCESS OBJECTS
    # =========================

    if result.boxes is not None and result.boxes.id is not None:

        boxes = result.boxes.xyxy.cpu().tolist()

        track_ids = result.boxes.id.int().cpu().tolist()

        for box, track_id in zip(boxes, track_ids):

            x1, y1, x2, y2 = map(int, box)

            # Object center
            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)

            history = position_history[track_id]

            history.append((center_x, center_y))

            if len(history) > HISTORY_LENGTH:
                history.pop(0)


            # =========================
            # CALCULATE PIXEL SPEED
            # =========================

            speed_pixels_per_second = 0.0

            if len(history) >= 2:

                old_x, old_y = history[0]
                new_x, new_y = history[-1]

                pixel_distance = math.sqrt(
                    (new_x - old_x) ** 2 +
                    (new_y - old_y) ** 2
                )

                time_seconds = (
                    len(history) - 1
                ) / fps

                if time_seconds > 0:

                    speed_pixels_per_second = (
                        pixel_distance /
                        time_seconds
                    )


            # Remove tiny detection noise

            if speed_pixels_per_second < MOVEMENT_THRESHOLD:
                speed_pixels_per_second = 0.0


            # =========================
            # DRAW BOX
            # =========================

            cv2.rectangle(
                annotated_frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )


            # =========================
            # DRAW CENTER
            # =========================

            cv2.circle(
                annotated_frame,
                (center_x, center_y),
                5,
                (0, 0, 255),
                -1
            )


            # =========================
            # DRAW SPEED
            # =========================

            label = (
                f"ID {track_id} | "
                f"{speed_pixels_per_second:.1f} px/s"
            )

            cv2.putText(
                annotated_frame,
                label,
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2
            )


            # =========================
            # DRAW MOTION TRAIL
            # =========================

            for i in range(1, len(history)):

                cv2.line(
                    annotated_frame,
                    history[i - 1],
                    history[i],
                    (255, 0, 0),
                    2
                )


    # =========================
    # FRAME INFORMATION
    # =========================

    cv2.putText(
        annotated_frame,
        f"Frame: {frame_number}",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )


    writer.write(annotated_frame)

    cv2.imshow(
        "PilotWatch - Speed Estimation",
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


print("\nSpeed estimation completed!")

print(f"Frames processed: {frame_number}")

print(f"Output video: {OUTPUT_VIDEO}")