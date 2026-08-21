from ultralytics import YOLO
import cv2
import os

MODEL_PATH = "yolo11n.pt"

model = YOLO(MODEL_PATH)


def detect_image(image_path):
    results = model.predict(
        source=image_path,
        conf=0.40,
        save=True
    )

    detections = []

    for result in results:
        boxes = result.boxes

        for box in boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            class_name = model.names[class_id]

            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0].tolist()
            )

            detections.append({
                "object": class_name,
                "confidence": round(confidence, 2),
                "bbox": {
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2
                }
            })

    return detections


if __name__ == "__main__":

    image_path = "ai/input/image/test.jpg"

    detections = detect_image(image_path)

    print("\nDetected Objects:")

    for detection in detections:
        print(detection)