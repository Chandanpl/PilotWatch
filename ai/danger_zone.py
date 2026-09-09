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

OUTPUT_VIDEO = OUTPUT_DIR / "danger_zone.mp4"


# =========================
# DANGER ZONE
# =========================
# These points define the railway danger zone.
#
# IMPORTANT:
# Change these coordinates later according to
# the actual camera view.

DANGER_ZONE = [
    (150, 400),
    (1130, 400),
    (1270, 720),
    (50, 720)
]


# =========================
# SETTINGS
# =========================

HISTORY_LENGTH = 10
MOVEMENT_THRESHOLD = 5


# =========================
# LOAD MODEL
# =========================

print("Loading YOLO model...")

model = YOLO(str(MODEL_PATH))

print("YOLO model loaded successfully!")
print("Starting danger-zone analysis...\n")


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
# OUTPUT
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
# PROCESS VIDEO
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
    # DRAW DANGER ZONE
    # =========================

    zone_points = DANGER_ZONE

    cv2.polylines(
        annotated_frame,
        [__import__("numpy").array(zone_points)],
        True,
        (0, 0, 255),
        3
    )

    # Transparent zone overlay

    overlay = annotated_frame.copy()

    cv2.fillPoly(
        overlay,
        [__import__("numpy").array(zone_points)],
        (0, 0, 255)
    )

    annotated_frame = cv2.addWeighted(
        overlay,
        0.15,
        annotated_frame,
        0.85,
        0
    )


    # =========================
    # PROCESS OBJECTS
    # =========================

    if result.boxes is not None and result.boxes.id is not None:

        boxes = result.boxes.xyxy.cpu().tolist()

        track_ids = result.boxes.id.int().cpu().tolist()

        classes = result.boxes.cls.int().cpu().tolist()

        for box, track_id, class_id in zip(
            boxes,
            track_ids,
            classes
        ):

            x1, y1, x2, y2 = map(int, box)

            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)

            # =========================
            # POSITION HISTORY
            # =========================

            history = position_history[track_id]

            history.append((center_x, center_y))

            if len(history) > HISTORY_LENGTH:
                history.pop(0)


            # =========================
            # CHECK DANGER ZONE
            # =========================

            inside_zone = cv2.pointPolygonTest(
                __import__("numpy").array(zone_points),
                (center_x, center_y),
                False
            ) >= 0


            # =========================
            # DIRECTION
            # =========================

            direction = "STATIONARY"

            if len(history) >= 2:

                old_x, old_y = history[0]
                new_x, new_y = history[-1]

                dx = new_x - old_x
                dy = new_y - old_y

                if (
                    abs(dx) < MOVEMENT_THRESHOLD
                    and abs(dy) < MOVEMENT_THRESHOLD
                ):
                    direction = "STATIONARY"

                elif abs(dx) > abs(dy):

                    direction = "RIGHT" if dx > 0 else "LEFT"

                else:

                    direction = "DOWN" if dy > 0 else "UP"


            # =========================
            # RISK LEVEL
            # =========================

            if inside_zone:

                risk = "HIGH RISK"

            else:

                risk = "SAFE"


            # =========================
            # DRAW OBJECT
            # =========================

            cv2.rectangle(
                annotated_frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            cv2.circle(
                annotated_frame,
                (center_x, center_y),
                5,
                (0, 0, 255),
                -1
            )


            # =========================
            # MOTION TRAIL
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
            # LABEL
            # =========================

            label = (
                f"ID {track_id} | "
                f"{direction} | "
                f"{risk}"
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
    # ZONE LABEL
    # =========================

    cv2.putText(
        annotated_frame,
        "RAILWAY DANGER ZONE",
        (30, height - 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )


    # =========================
    # FRAME NUMBER
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
        "PilotWatch - Railway Danger Zone",
        annotated_frame
    )


    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# =========================
# CLEANUP
# =========================

cap.release()
writer.release()
cv2.destroyAllWindows()


print("\nDanger-zone analysis completed!")

print(f"Frames processed: {frame_number}")

print(f"Output video: {OUTPUT_VIDEO}")