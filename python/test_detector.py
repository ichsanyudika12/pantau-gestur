import cv2
import time
from hand_detector import HandDetector

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Camera FAILED")
    exit(1)

print("Camera OK")
detector = HandDetector()
ret, frame = cap.read()

if ret:
    frame = detector.find_hands(frame, draw=False)
    time.sleep(0.5)
    count = detector.count_fingers()
    print("Finger count:", count)
    print("Gesture:", detector.get_gesture_name(count) if count is not None else "None")

detector.release()
cap.release()
print("Test OK")
