import cv2
import time
import logging

from config import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT
from hand_detector import HandDetector
from firebase_service import FirebaseService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Main")


def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        logger.error("Cannot access webcam. Exiting.")
        return

    detector = HandDetector()
    firebase = FirebaseService()

    last_gesture = None
    last_send_time = 0
    cooldown = 0.5

    cv2.namedWindow("Hand Gesture Analytics", cv2.WINDOW_NORMAL)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.warning("Failed to capture frame")
                break

            frame = cv2.flip(frame, 1)
            frame = detector.find_hands(frame, draw=True)
            finger_count = detector.count_fingers()

            current_time = time.time()

            if finger_count is not None:
                gesture = detector.get_gesture_name(finger_count)
                cv2.putText(
                    frame, f"Gesture: {gesture}",
                    (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 2
                )
                cv2.putText(
                    frame, f"Fingers: {finger_count}",
                    (10, 100), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 2
                )

                if (current_time - last_send_time) >= cooldown:
                    firebase.update_current(finger_count, gesture)
                    if gesture != last_gesture:
                        logger.info("Gesture changed: %s -> %s", last_gesture, gesture)
                        last_gesture = gesture
                    last_send_time = current_time
            else:
                if last_gesture is not None and (current_time - last_send_time) >= 2.0:
                    firebase.update_current(0, "No Hand")
                    last_gesture = None
                    last_send_time = current_time

                cv2.putText(
                    frame, "No Hand Detected",
                    (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 0, 255), 2
                )

            cv2.imshow("Hand Gesture Analytics", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                logger.info("Quit signal received")
                break

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        detector.release()
        logger.info("Cleanup complete")


if __name__ == "__main__":
    main()
