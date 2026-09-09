import cv2
from ultralytics import YOLO
from pathlib import Path
from collections import defaultdict

# =========================
# PATHS
# =========================

BASE_DIR = Path(__file__).parent

MODEL_PATH = BASE_DIR / "models" / "yolo11n.pt"
INPUT_VIDEO = BASE_DIR / "input" / "videos" / "railway_test.mp4"

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_VIDEO = OUTPUT_DIR / "motion_analysis.mp4"


# =========================
# SETTINGS
# =========================

# Number of previous positions to remember
HISTORY_LENGTH = 20

# Minimum movement in pixels before deciding direction
MOVEMENT_THRESHOLD = 5


# =========================
# LOAD MODEL
# =========================

print("Loading YOLO model...")

model = YOLO(str(MODEL_PATH))

print("YOLO model loaded successfully!")
print("Starting motion analysis...\n")


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
# TRACKING + MOTION LOOP
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
    # PROCESS TRACKED OBJECTS
    # =========================

    if result.boxes is not None and result.boxes.id is not None:

        boxes = result.boxes.xyxy.cpu().tolist()
        track_ids = result.boxes.id.int().cpu().tolist()
        classes = result.boxes.cls.int().cpu().tolist()
        confidences = result.boxes.conf.cpu().tolist()

        for box, track_id, class_id, confidence in zip(
            boxes,
            track_ids,
            classes,
            confidences
        ):

            x1, y1, x2, y2 = map(int, box)

            # Center of bounding box
            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)

            # Save position
            history = position_history[track_id]

            history.append((center_x, center_y))

            # Keep only recent positions
            if len(history) > HISTORY_LENGTH:
                history.pop(0)


            # =========================
            # DIRECTION
            # =========================

            direction = "STATIONARY"

            if len(history) >= 2:

                old_x, old_y = history[0]
                new_x, new_y = history[-1]

                dx = new_x - old_x
                dy = new_y - old_y

                if abs(dx) < MOVEMENT_THRESHOLD and abs(dy) < MOVEMENT_THRESHOLD:
                    direction = "STATIONARY"

                elif abs(dx) > abs(dy):

                    if dx > 0:
                        direction = "RIGHT"
                    else:
                        direction = "LEFT"

                else:

                    if dy > 0:
                        direction = "DOWN"
                    else:
                        direction = "UP"


            # =========================
            # DRAW TRACKING BOX
            # =========================

            cv2.rectangle(
                annotated_frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )


            # Draw center point

            cv2.circle(
                annotated_frame,
                (center_x, center_y),
                5,
                (0, 0, 255),
                -1
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
            # OBJECT LABEL
            # =========================

            label = f"ID {track_id} | {direction}"

            cv2.putText(
                annotated_frame,
                label,
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )


    # =========================
    # DISPLAY
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
        "PilotWatch - Motion Analysis",
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


print("\nMotion analysis completed!")

print(f"Frames processed: {frame_number}")

print(f"Output video: {OUTPUT_VIDEO}")