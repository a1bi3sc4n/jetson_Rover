import cv2
import time
from ultralytics import YOLO
from rover_auto_control import Rover

# ========== CONFIG ==========
CAMERA_ID = 0                  # usually 0 for USB camera
MODEL_PATH = "yolov8n.pt"  # your TensorRT engine file
TARGET_CLASS = "cup"        # change to whatever you want to follow
CONF_THRESHOLD = 0.5
MAX_SPEED = 0.50
last_seen_counter = 0
MAX_LOST_FRAMES =12
# ============================

def main():
    # Load your TensorRT model
    model = YOLO(MODEL_PATH, task='detect')

    # Open camera
    cap = cv2.VideoCapture(CAMERA_ID)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print("Cannot open camera")
        return

    rover = Rover(port='/dev/ttyUSB0')  # change port if needed

    print("Starting autonomous mode... Press 'q' to quit")

    try:

        search_direction = 1
        search_counter = 0
        SMOOTH_LEFT = 0.0
        SMOOTH_RIGHT = 0.0
        ALPHA = 0.41
        SMOOTH_CENTER = None
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Run detection
            results = model(frame, conf=CONF_THRESHOLD, verbose=False)
            annotated = results[0].plot()

            # Decision logic
            target_found = False
            frame_center = frame.shape[1] / 2

            for box in results[0].boxes:
                cls_id = int(box.cls[0])
                class_name = model.names[cls_id]

                if class_name == TARGET_CLASS:
                    target_found = True
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    box_center = (x1 + x2) / 2
                    box_area = (x2 - x1) * (y2 - y1)

                    #SMOOTH THE CUP'S Position
                    if SMOOTH_CENTER is None:
                        SMOOTH_CENTER = box_center
                    else:
                        SMOOTH_CENTER = 0.8 * SMOOTH_CENTER + 0.2 * box_center    

                    # Horizontal error (-1 to 1)
                    error = (SMOOTH_CENTER - frame_center) / frame_center

                    #Deadzone - prevent the jolting and twitching  when almost centered in frame
                    if abs(error) < 0.10:
                        error = 0.0

                    # Simple control
                    turn = error * 0.35
                    forward = 0.47


                    # Slow down if target is large (close)
                    if box_area > 25000:
                        forward = 0.0
                    if box_area > 12000:
                        forward = 0.10   # stop if very close
                    if box_area > 6000:
                        forward = 0.25 # stops when very close
                    else:
                        forward = 0.35


                    turn = max(-forward, min(forward, turn))

                    left = forward + turn
                    right = forward - turn    
                    # Limiting speeds
                    left = max(-MAX_SPEED, min(MAX_SPEED, left))
                    right = max(-MAX_SPEED, min(MAX_SPEED, right))

                    rover.drive(left, right)
                    break

            if not target_found:
                # Search behaviour: |The rover will wait 1.5 to 2 seconds before changing directuon and will slowly look left and right
                search_counter += 1
                if search_counter > 40:
                    search_direction *= -1
                    search_counter = 0

                left = -0.26 * search_direction
                right = 0.26 * search_direction
            else:

                pass

            #smoothing - may or may not help
            #SMOOTH_LEFT = ALPHA * left + (1- ALPHA) * SMOOTH_LEFT
            #SMOOTH_LEFT = ALPHA * right + (1 - ALPHA) * SMOOTH_RIGHT

            rover.drive(left, right)    
                

            # Show image
            cv2.imshow("Rover Vision", annotated)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        rover.close()
        cap.release()
        cv2.destroyAllWindows()
        print("Stopped")

if __name__ == "__main__":
    main()

    #Reflection:
        # What works:
        # - The rover gains speed and power when  the object class is in frame
        # -It loosely follows the direction relative to cv frame of the object (cup)

    # What to improve
    # The rover just spins on the spot when the object class(cup) is not in the cv frame, which must be updated with smoother less erratic behaviour
    # The direction and speed must eb changed to make movements towards the object calss cleaner.
    # part 2 iadded smoothing which semed to calkm down the turning on the spot but it onyl made it jolt on the spot and not move towards the obj at all, so now i will
    # try to fix it art the frame elvel rather than motor power