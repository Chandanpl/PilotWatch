import cv2
from pathlib import Path
from ultralytics import YOLO

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "yolo11n.pt"

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# Check whether a point is inside the danger zone
# --------------------------------------------------

def is_inside_danger_zone(point, polygon):

    result = cv2.pointPolygonTest(
        polygon,
        point,
        False
    )

    return result >= 0


# --------------------------------------------------
# Process video
# --------------------------------------------------

def detect_danger_zone(input_video, output_video=None):

    input_video = Path(input_video)

    if output_video is None:
        output_video = OUTPUT_DIR / "danger_zone.mp4"
    else:
        output_video = Path(output_video)

    print("Loading YOLO model...")
    model = YOLO(str(MODEL_PATH))
    print("YOLO model loaded successfully!")
    print("Starting danger zone detection...\n")

    cap = cv2.VideoCapture(str(input_video))

    if not cap.isOpened():
        raise RuntimeError(
            f"Could not open video: {input_video}"
        )

    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 25

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    total_frames = int(
        cap.get(cv2.CAP_PROP_FRAME_COUNT)
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
    #
    # This is deliberately a simple zone.
    # We will calibrate it later for the real camera.
    # --------------------------------------------------

    danger_zone = [
        (int(width * 0.25), int(height * 0.55)),
        (int(width * 0.75), int(height * 0.55)),
        (int(width * 0.90), int(height * 0.95)),
        (int(width * 0.10), int(height * 0.95))
    ]

    polygon = __import__("numpy").array(
        danger_zone,
        dtype="int32"
    )

    frame_number = 0

    danger_events = 0
    safe_events = 0

    while True:

        success, frame = cap.read()

        if not success:
            break

        frame_number += 1

        # ----------------------------------------------
        # YOLO + ByteTrack
        # ----------------------------------------------

        results = model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            verbose=False
        )

        result = results[0]

        annotated_frame = result.plot()

        # ----------------------------------------------
        # Draw danger zone
        # ----------------------------------------------

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

        # ----------------------------------------------
        # Check detected objects
        # ----------------------------------------------

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

            boxes = (
                result.boxes.xyxy
                .cpu()
                .tolist()
            )

            for track_id, box in zip(
                track_ids,
                boxes
            ):

                x1, y1, x2, y2 = box

                # Use bottom-center of bounding box
                # as the object's ground/contact point.

                center_x = int(
                    (x1 + x2) / 2
                )

                bottom_y = int(y2)

                point = (
                    center_x,
                    bottom_y
                )

                inside = is_inside_danger_zone(
                    point,
                    polygon
                )

                if inside:

                    danger_events += 1

                    label = (
                        f"ID {track_id} - DANGER"
                    )

                    cv2.putText(
                        annotated_frame,
                        label,
                        (
                            int(x1),
                            int(y1) - 10
                        ),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 0, 255),
                        2
                    )

                else:

                    safe_events += 1

        # ----------------------------------------------
        # Write frame
        # ----------------------------------------------

        writer.write(
            annotated_frame
        )

        if frame_number % 100 == 0:

            print(
                f"Processing frame "
                f"{frame_number}/{total_frames}..."
            )

    cap.release()
    writer.release()

    print(
        "\nDanger zone detection completed!"
    )

    print(
        f"Frames processed: {frame_number}"
    )

    print(
        f"Danger events: {danger_events}"
    )

    print(
        f"Safe events: {safe_events}"
    )

    print(
        f"\nOutput video: {output_video}"
    )

    return {
        "frames_processed": frame_number,
        "danger_events": danger_events,
        "safe_events": safe_events,
        "output_video": str(output_video)
    }


# --------------------------------------------------
# Direct execution
# --------------------------------------------------

if __name__ == "__main__":

    INPUT_VIDEO = (
        BASE_DIR
        / "input"
        / "videos"
        / "railway_test.mp4"
    )

    detect_danger_zone(
        INPUT_VIDEO
    )