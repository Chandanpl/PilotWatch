import cv2
import json
import math
import numpy as np
from pathlib import Path
from ultralytics import YOLO

from alert_manager import AlertManager


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "yolo11n.pt"

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Objects relevant to PilotWatch
RELEVANT_OBJECTS = {
    "person",
    "train",
    "car",
    "truck",
    "bus",
    "motorcycle",
    "bicycle",
    "horse",
    "cow",
    "dog",
    "cat",
    "sheep",
    "elephant",
}


def calculate_direction(previous_position, current_position):

    if previous_position is None:
        return "UNKNOWN"

    dx = current_position[0] - previous_position[0]
    dy = current_position[1] - previous_position[1]

    distance = math.sqrt(dx ** 2 + dy ** 2)

    if distance < 2:
        return "STATIONARY"

    if abs(dx) > abs(dy):
        return "RIGHT" if dx > 0 else "LEFT"

    return "TOWARDS" if dy > 0 else "AWAY"


def calculate_speed(
    previous_position,
    current_position,
    fps
):

    if previous_position is None:
        return 0.0

    dx = current_position[0] - previous_position[0]
    dy = current_position[1] - previous_position[1]

    distance = math.sqrt(dx ** 2 + dy ** 2)

    return distance * fps


def calculate_risk(
    object_type,
    inside_danger_zone,
    direction,
    speed
):

    # Ignore irrelevant objects
    if object_type not in RELEVANT_OBJECTS:
        return "IGNORE"

    # Outside danger zone
    if not inside_danger_zone:
        return "SAFE"

    # Newly detected object
    if direction == "UNKNOWN":
        return "WARNING"

    # Stationary object inside danger zone
    if direction == "STATIONARY":
        return "HIGH"

    # Moving toward danger area
    if direction == "TOWARDS":
        return "CRITICAL"

    # Fast movement inside danger zone
    if speed > 100:
        return "CRITICAL"

    return "HIGH"


def risk_assessment(
    input_video,
    output_video=None
):

    input_video = Path(input_video)

    if output_video is None:
        output_video = (
            OUTPUT_DIR /
            "risk_assessment.mp4"
        )
    else:
        output_video = Path(output_video)

    print("Loading YOLO model...")

    model = YOLO(
        str(MODEL_PATH)
    )

    print(
        "YOLO model loaded successfully!"
    )

    print(
        "Starting improved risk assessment...\n"
    )

    cap = cv2.VideoCapture(
        str(input_video)
    )

    if not cap.isOpened():

        raise RuntimeError(
            f"Could not open video: {input_video}"
        )

    fps = cap.get(
        cv2.CAP_PROP_FPS
    )

    if fps <= 0:
        fps = 25

    width = int(
        cap.get(
            cv2.CAP_PROP_FRAME_WIDTH
        )
    )

    height = int(
        cap.get(
            cv2.CAP_PROP_FRAME_HEIGHT
        )
    )

    total_frames = int(
        cap.get(
            cv2.CAP_PROP_FRAME_COUNT
        )
    )

    fourcc = cv2.VideoWriter_fourcc(
        *"mp4v"
    )

    writer = cv2.VideoWriter(
        str(output_video),
        fourcc,
        fps,
        (width, height)
    )

    # --------------------------------------------------
    # Temporary danger zone
    # --------------------------------------------------

    danger_zone = [
        (
            int(width * 0.25),
            int(height * 0.55)
        ),
        (
            int(width * 0.75),
            int(height * 0.55)
        ),
        (
            int(width * 0.90),
            int(height * 0.95)
        ),
        (
            int(width * 0.10),
            int(height * 0.95)
        )
    ]

    polygon = np.array(
        danger_zone,
        dtype="int32"
    )

    # --------------------------------------------------
    # Tracking
    # --------------------------------------------------

    previous_positions = {}

    # Alert Manager
    alert_manager = AlertManager(
        persistence_frames=5,
        disappearance_frames=30
    )

    # --------------------------------------------------
    # Risk counters
    # --------------------------------------------------

    risk_counts = {
        "SAFE": 0,
        "WARNING": 0,
        "HIGH": 0,
        "CRITICAL": 0,
        "IGNORE": 0
    }

    frame_number = 0

    # --------------------------------------------------
    # Main video loop
    # --------------------------------------------------

    while True:

        success, frame = cap.read()

        if not success:
            break

        frame_number += 1

        # --------------------------------------------------
        # YOLO + ByteTrack
        # --------------------------------------------------

        results = model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            verbose=False
        )

        result = results[0]

        annotated_frame = result.plot()

        # --------------------------------------------------
        # Draw danger zone
        # --------------------------------------------------

        cv2.polylines(
            annotated_frame,
            [polygon],
            True,
            (0, 0, 255),
            3
        )

        cv2.putText(
            annotated_frame,
            "DANGER ZONE",
            (
                int(width * 0.40),
                int(height * 0.60)
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )

        # --------------------------------------------------
        # Track visible objects
        # --------------------------------------------------

        visible_track_ids = set()

        if (
            result.boxes is not None
            and result.boxes.id is not None
        ):

            track_ids = (
                result.boxes.id
                .int()
                .cpu()
                .tolist()
            )

            visible_track_ids.update(
                track_ids
            )

            boxes = (
                result.boxes.xyxy
                .cpu()
                .tolist()
            )

            class_ids = (
                result.boxes.cls
                .int()
                .cpu()
                .tolist()
            )

            # --------------------------------------------------
            # Process every tracked object
            # --------------------------------------------------

            for (
                track_id,
                box,
                class_id
            ) in zip(
                track_ids,
                boxes,
                class_ids
            ):

                x1, y1, x2, y2 = box

                # Bottom-center point
                center_x = int(
                    (x1 + x2) / 2
                )

                bottom_y = int(y2)

                current_position = (
                    center_x,
                    bottom_y
                )

                previous_position = (
                    previous_positions.get(
                        track_id
                    )
                )

                # --------------------------------------------------
                # Direction
                # --------------------------------------------------

                direction = calculate_direction(
                    previous_position,
                    current_position
                )

                # --------------------------------------------------
                # Speed
                # --------------------------------------------------

                speed = calculate_speed(
                    previous_position,
                    current_position,
                    fps
                )

                previous_positions[
                    track_id
                ] = current_position

                # --------------------------------------------------
                # Danger zone
                # --------------------------------------------------

                inside = (
                    cv2.pointPolygonTest(
                        polygon,
                        current_position,
                        False
                    ) >= 0
                )

                # --------------------------------------------------
                # Object type
                # --------------------------------------------------

                object_type = model.names[
                    class_id
                ]

                # --------------------------------------------------
                # Risk
                # --------------------------------------------------

                risk = calculate_risk(
                    object_type,
                    inside,
                    direction,
                    speed
                )

                risk_counts[risk] += 1

                # --------------------------------------------------
                # Ignore irrelevant objects
                # --------------------------------------------------

                if risk == "IGNORE":

                    cv2.putText(
                        annotated_frame,
                        (
                            f"ID {track_id} | "
                            f"{object_type} | IGNORE"
                        ),
                        (
                            int(x1),
                            int(y1) - 10
                        ),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 255, 255),
                        2
                    )

                    continue

                # --------------------------------------------------
                # Persistent Alert Manager
                # --------------------------------------------------

                alert = alert_manager.observe(
                    track_id=track_id,
                    object_type=object_type,
                    direction=direction,
                    speed=speed,
                    risk_level=risk,
                    inside_danger_zone=inside
                )

                # --------------------------------------------------
                # Print alert event
                # --------------------------------------------------

                if alert:

                    print(
                        f"ALERT EVENT: "
                        f"{alert['status']} | "
                        f"{alert['risk_level']} | "
                        f"ID {alert['track_id']} | "
                        f"{alert['object_type']} | "
                        f"{alert['direction']} | "
                        f"{alert['speed_pixels_per_second']:.2f} px/s"
                    )

                # --------------------------------------------------
                # Display information
                # --------------------------------------------------

                label = (
                    f"ID {track_id} | "
                    f"{object_type} | "
                    f"{direction} | "
                    f"{risk}"
                )

                text_color = (
                    (0, 0, 255)
                    if risk in [
                        "HIGH",
                        "CRITICAL"
                    ]
                    else (0, 255, 0)
                )

                cv2.putText(
                    annotated_frame,
                    label,
                    (
                        int(x1),
                        int(y1) - 10
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    text_color,
                    2
                )

        # --------------------------------------------------
        # Resolve disappeared objects
        # --------------------------------------------------

        resolved_alerts = (
            alert_manager.handle_missing_tracks(
                visible_track_ids
            )
        )

        for alert in resolved_alerts:

            print(
                f"ALERT RESOLVED | "
                f"ID {alert['track_id']} | "
                f"{alert['object_type']}"
            )

        # --------------------------------------------------
        # Write output
        # --------------------------------------------------

        writer.write(
            annotated_frame
        )

        if frame_number % 100 == 0:

            print(
                f"Processing frame "
                f"{frame_number}/{total_frames}..."
            )

    # --------------------------------------------------
    # Cleanup
    # --------------------------------------------------

    cap.release()
    writer.release()

    # --------------------------------------------------
    # Final summary
    # --------------------------------------------------

    summary = {

        "frames_processed":
            frame_number,

        "risk_counts":
            risk_counts,

        "active_alerts":
            alert_manager.get_active_alerts(),

        "alert_history":
            alert_manager.get_alert_history()
    }

    summary_file = (
        OUTPUT_DIR /
        "risk_summary.json"
    )

    with open(
        summary_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            summary,
            file,
            indent=4
        )

    print(
        "\nImproved risk assessment completed!"
    )

    print(
        f"Frames processed: "
        f"{frame_number}"
    )

    print(
        "\nRisk event counts:"
    )

    for risk, count in risk_counts.items():

        print(
            f"{risk}: {count}"
        )

    print(
        f"\nOutput video: "
        f"{output_video}"
    )

    print(
        f"Risk summary: "
        f"{summary_file}"
    )

    print(
        f"Active alerts: "
        f"{len(alert_manager.get_active_alerts())}"
    )

    print(
        f"Alert history: "
        f"{len(alert_manager.get_alert_history())}"
    )

    return summary


if __name__ == "__main__":

    INPUT_VIDEO = (
        BASE_DIR
        / "input"
        / "videos"
        / "railway_test.mp4"
    )

    risk_assessment(
        INPUT_VIDEO
    )