import cv2
import time
from detect import ObjectDetector


detector = ObjectDetector()
cap = cv2.VideoCapture(0)
prev_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    results = detector.detect(frame)
    annotated_frame = results[0].plot()

    #FPS
    current_time = time.time()
    fps = 1 / (current_time - prev_time)
    prev_time = current_time

    cv2.putText(annotated_frame,
                f"FPS: {fps:.1f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0,255,0),
                2)
    
    cv2.imshow("Detection", annotated_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
# Change your model inference line in obj_det.py or detect.py to match this:
