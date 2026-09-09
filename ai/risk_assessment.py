import cv2
import math
import numpy as np

from ultralytics import YOLO
from pathlib import Path
from collections import defaultdict

from alert_manager import AlertManager


# =========================
# PATHS
# =========================

BASE_DIR = Path(__file__).parent

MODEL_PATH = BASE_DIR / "models" / "yolo11n.pt"
INPUT_VIDEO = BASE_DIR / "input" / "videos" / "railway_test.mp4"

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_VIDEO = OUTPUT_DIR / "risk_assessment.mp4"


# =========================
# DANGER ZONE
# =========================
# Example coordinates.
# These must be calibrated for the actual
# railway camera later.

DANGER_ZONE = np.array([
    (150, 400),
    (1130, 400),
    (1270, 720),
    (50, 720)
], dtype=np.int32)


# =========================
# SETTINGS
# =========================

HISTORY_LENGTH = 10

MOVEMENT_THRESHOLD = 5

# Classes considered important
# for railway intrusion detection.

RISK_CLASSES = {
    "person",
    "animal",
    "vehicle"
}


# =========================
# LOAD MODEL
# =========================

print("Loading YOLO model...")

model = YOLO(str(MODEL_PATH))

print("YOLO model loaded successfully!")
print("Starting risk assessment...\n")


# =========================
# ALERT MANAGER
# =========================

alert_manager = AlertManager()


# =========================
# OPEN VIDEO
# =========================

cap = cv2.VideoCapture(str(INPUT_VIDEO))

if not cap.isOpened():
    raise RuntimeError(
        f"Could not open video: {INPUT_VIDEO}"
    )


fps = cap.get(cv2.CAP_PROP_FPS)

if fps <= 0:
    fps = 25


width = int(
    cap.get(cv2.CAP_PROP_FRAME_WIDTH)
)

height = int(
    cap.get(cv2.CAP_PROP_FRAME_HEIGHT
))


# =========================
# OUTPUT VIDEO
# =========================

fourcc = cv2.VideoWriter_fourcc(
    *"mp4v"
)

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
# RISK COUNTERS
# =========================

risk_counts = {
    "SAFE": 0,
    "WARNING": 0,
    "HIGH": 0,
    "CRITICAL": 0
}


# =========================
# MAIN LOOP
# =========================

while True:

    success, frame = cap.read()

    if not success:
        break

    frame_number += 1


    # =========================
    # YOLO + BYTETRACK
    # =========================

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

    overlay = annotated_frame.copy()

    cv2.fillPoly(
        overlay,
        [DANGER_ZONE],
        (0, 0, 255)
    )

    annotated_frame = cv2.addWeighted(
        overlay,
        0.15,
        annotated_frame,
        0.85,
        0
    )

    cv2.polylines(
        annotated_frame,
        [DANGER_ZONE],
        True,
        (0, 0, 255),
        3
    )


    # =========================
    # PROCESS TRACKED OBJECTS
    # =========================

    if (
        result.boxes is not None
        and result.boxes.id is not None
    ):

        boxes = (
            result.boxes.xyxy
            .cpu()
            .tolist()
        )

        track_ids = (
            result.boxes.id
            .int()
            .cpu()
            .tolist()
        )

        class_ids = (
            result.boxes.cls
            .int()
            .cpu()
            .tolist()
        )

        confidences = (
            result.boxes.conf
            .cpu()
            .tolist()
        )


        for (
            box,
            track_id,
            class_id,
            confidence
        ) in zip(
            boxes,
            track_ids,
            class_ids,
            confidences
        ):

            x1, y1, x2, y2 = map(
                int,
                box
            )


            # =========================
            # OBJECT CENTER
            # =========================

            center_x = int(
                (x1 + x2) / 2
            )

            center_y = int(
                (y1 + y2) / 2
            )


            # =========================
            # CLASS NAME
            # =========================

            class_name = model.names[
                class_id
            ]


            # =========================
            # POSITION HISTORY
            # =========================

            history = position_history[
                track_id
            ]

            history.append(
                (center_x, center_y)
            )

            if len(history) > HISTORY_LENGTH:

                history.pop(0)


            # =========================
            # DIRECTION
            # =========================

            direction = "STATIONARY"

            dx = 0
            dy = 0


            if len(history) >= 2:

                old_x, old_y = history[0]

                new_x, new_y = history[-1]

                dx = new_x - old_x

                dy = new_y - old_y


                if (
                    abs(dx) < MOVEMENT_THRESHOLD
                    and
                    abs(dy) < MOVEMENT_THRESHOLD
                ):

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
            # PIXEL SPEED
            # =========================

            speed = 0.0


            if len(history) >= 2:

                old_x, old_y = history[0]

                new_x, new_y = history[-1]


                distance = math.sqrt(
                    (new_x - old_x) ** 2
                    +
                    (new_y - old_y) ** 2
                )


                time_seconds = (
                    len(history) - 1
                ) / fps


                if time_seconds > 0:

                    speed = (
                        distance /
                        time_seconds
                    )


            # Remove tiny detection noise

            if speed < 2:

                speed = 0.0


            # =========================
            # DANGER ZONE CHECK
            # =========================

            inside_zone = (
                cv2.pointPolygonTest(
                    DANGER_ZONE,
                    (center_x, center_y),
                    False
                ) >= 0
            )


            # =========================
            # DISTANCE TO DANGER ZONE
            # =========================

            zone_distance = (
                cv2.pointPolygonTest(
                    DANGER_ZONE,
                    (center_x, center_y),
                    True
                )
            )

            distance_to_zone = abs(
                zone_distance
            )


            # =========================
            # RISK ASSESSMENT
            # =========================

            risk_level = "SAFE"


            if class_name in RISK_CLASSES:

                # -------------------------
                # OBJECT INSIDE ZONE
                # -------------------------

                if inside_zone:

                    if (
                        direction != "STATIONARY"
                        and speed > 10
                    ):

                        risk_level = "CRITICAL"

                    else:

                        risk_level = "HIGH"


                # -------------------------
                # OBJECT APPROACHING ZONE
                # -------------------------

                else:

                    if (
                        distance_to_zone < 100
                        and
                        direction != "STATIONARY"
                    ):

                        risk_level = "WARNING"

                    else:

                        risk_level = "SAFE"


            # =========================
            # UPDATE RISK COUNTER
            # =========================

            risk_counts[
                risk_level
            ] += 1


            # =========================
            # ALERT GENERATION
            # =========================

            if risk_level in {
                "HIGH",
                "CRITICAL"
            }:

                # ---------------------------------
                # TRY TO CREATE NEW ALERT
                # ---------------------------------

                alert = (
                    alert_manager.create_alert(
                        track_id=track_id,
                        object_type=class_name,
                        direction=direction,
                        speed=speed,
                        risk_level=risk_level
                    )
                )


                # ---------------------------------
                # NEW ALERT
                # ---------------------------------

                if alert:

                    print(
                        f"ALERT: {risk_level} | "
                        f"ID {track_id} | "
                        f"{class_name} | "
                        f"{direction} | "
                        f"{speed:.2f} px/s"
                    )


                # ---------------------------------
                # EXISTING ALERT
                # CHECK FOR ESCALATION
                # ---------------------------------

                else:

                    escalation = (
                        alert_manager.update_alert(
                            track_id=track_id,
                            direction=direction,
                            speed=speed,
                            risk_level=risk_level
                        )
                    )


                    if escalation:

                        print(
                            f"ALERT ESCALATED: "
                            f"CRITICAL | "
                            f"ID {track_id} | "
                            f"{class_name} | "
                            f"{direction} | "
                            f"{speed:.2f} px/s"
                        )


            # =========================
            # DRAW OBJECT BOX
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
            # MOTION TRAIL
            # =========================

            for i in range(
                1,
                len(history)
            ):

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

            label = (
                f"ID {track_id} | "
                f"{class_name} | "
                f"{direction} | "
                f"{risk_level}"
            )


            cv2.putText(
                annotated_frame,
                label,
                (
                    x1,
                    max(
                        y1 - 10,
                        20
                    )
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.48,
                (255, 255, 255),
                2
            )


    # =========================
    # SYSTEM INFORMATION
    # =========================

    cv2.putText(
        annotated_frame,
        "PILOTWATCH - RISK ASSESSMENT",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (255, 255, 255),
        2
    )


    cv2.putText(
        annotated_frame,
        "RAILWAY DANGER ZONE",
        (30, height - 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (255, 255, 255),
        2
    )


    # =========================
    # WRITE OUTPUT
    # =========================

    writer.write(
        annotated_frame
    )


    cv2.imshow(
        "PilotWatch - Risk Assessment",
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
# FINAL RESULT
# =========================

print(
    "\nRisk assessment completed!"
)

print(
    f"Frames processed: "
    f"{frame_number}"
)


print("\nRisk event counts:")

for risk, count in risk_counts.items():

    print(
        f"{risk}: {count}"
    )


print(
    f"\nOutput video: "
    f"{OUTPUT_VIDEO}"
)