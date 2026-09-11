import cv2
from ultralytics import YOLO
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "yolo11n.pt"

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def track_video(input_video, output_video=None):

    input_video = Path(input_video)

    if output_video is None:
        output_video = OUTPUT_DIR / "tracked_video.mp4"
    else:
        output_video = Path(output_video)

    print("Loading YOLO model...")

    model = YOLO(str(MODEL_PATH))

    print("YOLO model loaded successfully!")
    print("Starting ByteTrack tracking...\n")

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

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    writer = cv2.VideoWriter(
        str(output_video),
        fourcc,
        fps,
        (width, height)
    )

    frame_number = 0
    unique_ids = set()

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

            for track_id in track_ids:
                unique_ids.add(track_id)

        writer.write(annotated_frame)

    cap.release()
    writer.release()

    return {
        "frames_processed": frame_number,
        "unique_objects": len(unique_ids),
        "output_video": str(output_video)
    }


if __name__ == "__main__":

    INPUT_VIDEO = (
        BASE_DIR
        / "input"
        / "videos"
        / "railway_test.mp4"
    )

    result = track_video(INPUT_VIDEO)

    print("\nByteTrack tracking completed!")

    print(
        f"Frames processed: "
        f"{result['frames_processed']}"
    )

    print(
        f"Unique objects tracked: "
        f"{result['unique_objects']}"
    )

    print(
        f"Output video: "
        f"{result['output_video']}"
    )