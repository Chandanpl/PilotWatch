import cv2
import math
from pathlib import Path
from ultralytics import YOLO

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "yolo11n.pt"

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def calculate_direction(previous_position, current_position):
    """
    Calculate movement direction based on object center positions.
    """

    if previous_position is None:
        return "UNKNOWN"

    previous_x, previous_y = previous_position
    current_x, current_y = current_position

    dx = current_x - previous_x
    dy = current_y - previous_y

    distance = math.sqrt(dx ** 2 + dy ** 2)

    # Very small movement = stationary
    if distance < 2:
        return "STATIONARY"

    # Horizontal movement
    if abs(dx) > abs(dy):
        if dx > 0:
            return "RIGHT"
        else:
            return "LEFT"

    # Vertical movement
    if dy > 0:
        return "TOWARDS"
    else:
        return "AWAY"


def motion_analysis(input_video, output_video=None):

    input_video = Path(input_video)

    if output_video is None:
        output_video = OUTPUT_DIR / "motion_analysis.mp4"
    else:
        output_video = Path(output_video)

    print("Loading YOLO model...")
    model = YOLO(str(MODEL_PATH))
    print("YOLO model loaded successfully!")
    print("Starting motion analysis...\n")

    cap = cv2.VideoCapture(str(input_video))

    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {input_video}")

    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 25

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    writer = cv2.VideoWriter(
        str(output_video),
        fourcc,
        fps,
        (width, height)
    )

    previous_positions = {}

    frame_number = 0

    motion_counts = {
        "LEFT": 0,
        "RIGHT": 0,
        "TOWARDS": 0,
        "AWAY": 0,
        "STATIONARY": 0,
        "UNKNOWN": 0
    }

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

        annotated_frame = result.plot()

        if result.boxes is not None and result.boxes.id is not None:

            track_ids = result.boxes.id.int().cpu().tolist()
            boxes = result.boxes.xyxy.cpu().tolist()

            for track_id, box in zip(track_ids, boxes):

                x1, y1, x2, y2 = box

                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)

                current_position = (center_x, center_y)

                previous_position = previous_positions.get(track_id)

                direction = calculate_direction(
                    previous_position,
                    current_position
                )

                motion_counts[direction] += 1

                previous_positions[track_id] = current_position

                # Display direction
                cv2.putText(
                    annotated_frame,
                    f"ID {track_id}: {direction}",
                    (int(x1), int(y1) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2
                )

        writer.write(annotated_frame)

        if frame_number % 100 == 0:
            print(
                f"Processing frame "
                f"{frame_number}/{total_frames}..."
            )

    cap.release()
    writer.release()

    print("\nMotion analysis completed!")

    print(f"Frames processed: {frame_number}")

    print("\nMotion counts:")

    for direction, count in motion_counts.items():
        print(f"{direction}: {count}")

    print(f"\nOutput video: {output_video}")

    return {
        "frames_processed": frame_number,
        "motion_counts": motion_counts,
        "output_video": str(output_video)
    }


if __name__ == "__main__":

    INPUT_VIDEO = BASE_DIR / "input" / "videos" / "railway_test.mp4"

    result = motion_analysis(INPUT_VIDEO)