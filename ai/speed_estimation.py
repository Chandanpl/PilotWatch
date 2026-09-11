import cv2
import math
from pathlib import Path
from ultralytics import YOLO

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "yolo11n.pt"

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def calculate_speed(previous_position, current_position, fps):
    """
    Calculate object speed in pixels per second.
    """

    if previous_position is None:
        return 0.0

    previous_x, previous_y = previous_position
    current_x, current_y = current_position

    dx = current_x - previous_x
    dy = current_y - previous_y

    distance = math.sqrt(dx ** 2 + dy ** 2)

    speed = distance * fps

    return speed


def speed_estimation(input_video, output_video=None):

    input_video = Path(input_video)

    if output_video is None:
        output_video = OUTPUT_DIR / "speed_estimation.mp4"
    else:
        output_video = Path(output_video)

    print("Loading YOLO model...")
    model = YOLO(str(MODEL_PATH))
    print("YOLO model loaded successfully!")
    print("Starting speed estimation...\n")

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

    speed_values = []

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

                speed = calculate_speed(
                    previous_position,
                    current_position,
                    fps
                )

                speed_values.append(speed)

                previous_positions[track_id] = current_position

                cv2.putText(
                    annotated_frame,
                    f"ID {track_id} | {speed:.1f} px/s",
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

    average_speed = (
        sum(speed_values) / len(speed_values)
        if speed_values
        else 0
    )

    maximum_speed = (
        max(speed_values)
        if speed_values
        else 0
    )

    print("\nSpeed estimation completed!")

    print(f"Frames processed: {frame_number}")
    print(f"Average speed: {average_speed:.2f} px/s")
    print(f"Maximum speed: {maximum_speed:.2f} px/s")

    print(f"\nOutput video: {output_video}")

    return {
        "frames_processed": frame_number,
        "average_speed_pixels_per_second": round(
            average_speed, 2
        ),
        "maximum_speed_pixels_per_second": round(
            maximum_speed, 2
        ),
        "output_video": str(output_video)
    }


if __name__ == "__main__":

    INPUT_VIDEO = (
        BASE_DIR /
        "input" /
        "videos" /
        "railway_test.mp4"
    )

    speed_estimation(INPUT_VIDEO)