import cv2
import time

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

frame_count = 0
start_time = time.time()
fps = 0

while True:
    ret, frame = cap.read()


    if not ret:
        print("Failed to grab frame")
        break
    frame_count += 1

    elapsed = time.time() - start_time
    
    if elapsed >= 1:
        fps = frame_count / elapsed
        frame_count = 0
        start_time = time.time()

    cv2.putText(
        frame,
        f"FPS: {fps:.1f}",
        (10,30),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255,255,0),
        2
    )    

    cv2.imshow("Jetson Camera", frame)

    if cv2.waitKey(1) == ord('q'):
        break    

cap.release()
cv2.destoryAllWindows()    