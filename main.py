import cv2
import time
from ultralytics import YOLO
from rover_auto_control import Rover

CAMERA_ID = 0
MODEL_PATH = "yolov8n.pt"
TARGET_CLASS = "cup"
CONF_THRESHOLD = 0.5
MAX_SPEED = 0.45



def main():
    model = YOLO(MODEL_PATH)
    cap = cv2.VideoCapture(CAMERA_ID)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print("Cannot open camera")
        return

    rover = Rover(port='/dev/ttyUSB0')
    smooth_left = 0.0
    smooth_right = 0.0
    alpha = 0.4
    search_drection = 1
    search_counter = 0
   

    print("Starting... Press 'q' to quit")

    try:

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            results = model(frame, conf=CONF_THRESHOLD, verbose=False)
            annotated = results[0].plot()

            target_found = False
            frame_center = frame.shape[1] / 2

            left = 0.0
            right = 0.0

            for box in results[0].boxes:
                cls_id = int(box.cls[0])
                class_name = model.names[cls_id]

                if class_name == TARGET_CLASS:
                    target_found = True
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    box_center = (x1 + x2) / 2
                    box_area = (x2 - x1) * (y2 - y1)

                    error = (box_center - frame_center) / frame_center
                    if abs(error) < 0.07:
                        error = 0.0

                    turn = error * 0.75
                    forward = 0.44

                    if box_area > 35000:
                        forward = 0.3
                    if box_area > 55000:
                        forward = 0.18
                    if box_area > 80000:
                        forward = 0.0


                    left = max(min(left, 0.48), -0.48)
                    right = max(min(right, 0.48), -0.48)
                    break
            if not target_found:
                search_counter += 1
                if search_counter > 45:
                    search_direction *= -1
                    search_counter = 0
                left = -0.27 * search_direction
                right = 0.27 * search_direction

            smooth_left = alpha * left + (1 - alpha)  * smooth_left
            smooth_right = alpha * right + (1 - alpha) * smooth_right

            print(f"L:{smooth_left:.2f} R:{smooth_right:.2f}")

            rover.drive(smooth_left, smooth_right)

            cv2.imshow("Rover Visio", annotated)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        rover.close()
        cap.release()
        cv2.destroyAllWindows()
        print("Stopped")

if __name__ == "__main__":
    main()


                    
                                        
