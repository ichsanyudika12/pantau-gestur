import cv2
import os
import signal
import socket
import subprocess
import threading
import time
import logging

from flask import Flask, Response, jsonify
from flask_cors import CORS

from hand_detector import HandDetector
from firebase_service import FirebaseService
from config import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Server")

shutdown = threading.Event()

raw_frame = None
raw_lock = threading.Lock()

display_frame = None
display_lock = threading.Lock()

current_detection = {
    "gesture": "No Hand",
    "fingers": 0,
    "timestamp": 0,
}
detection_lock = threading.Lock()

current_stats = {
    "totalDetection": 0,
    "fistCount": 0,
    "pointCount": 0,
    "peaceCount": 0,
    "threeCount": 0,
    "fourCount": 0,
    "openHandCount": 0,
}
stats_lock = threading.Lock()

STAT_KEY_MAP = {
    "Fist": "fistCount",
    "Point": "pointCount",
    "Peace": "peaceCount",
    "Three": "threeCount",
    "Four": "fourCount",
    "Open Hand": "openHandCount",
}

app = Flask(__name__)
CORS(app)


def grab_loop():
    global raw_frame
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        logger.error("Cannot access webcam")
        return
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    logger.info("Grab loop started")

    while not shutdown.is_set():
        try:
            ret, frame = cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                with raw_lock:
                    raw_frame = frame
            else:
                logger.warning("Failed to grab frame")
                time.sleep(0.1)
        except Exception as e:
            logger.error("Grab loop error: %s", e)
            time.sleep(0.1)

    cap.release()
    logger.info("Grab loop stopped")


def detect_loop():
    global display_frame, current_detection, current_stats

    detector = HandDetector()
    firebase = FirebaseService()

    last_gesture = None
    last_send_time = 0
    cooldown = 0.5
    error_count = 0

    logger.info("Detect loop started")

    while not shutdown.is_set():
        try:
            with raw_lock:
                if raw_frame is None:
                    time.sleep(0.01)
                    continue
                frame = raw_frame.copy()

            frame = detector.find_hands(frame, draw=True)
            finger_count = detector.count_fingers()

            with display_lock:
                display_frame = frame

            now = time.time()
            error_count = 0

            if finger_count is not None:
                gesture = detector.get_gesture_name(finger_count)

                with detection_lock:
                    current_detection = {
                        "gesture": gesture,
                        "fingers": finger_count,
                        "timestamp": int(now),
                    }

                if (now - last_send_time) >= cooldown:
                    firebase.update_current(finger_count, gesture)
                    if gesture != last_gesture:
                        logger.info("Gesture: %s (%d fingers)", gesture, finger_count)
                        with stats_lock:
                            current_stats["totalDetection"] += 1
                            key = STAT_KEY_MAP.get(gesture)
                            if key:
                                current_stats[key] += 1
                        last_gesture = gesture
                    last_send_time = now
            else:
                now_ms = int(now * 1000)
                with detection_lock:
                    current_detection = {
                        "gesture": "No Hand",
                        "fingers": 0,
                        "timestamp": now_ms,
                    }

                if last_gesture is not None and (now - last_send_time) >= 2.0:
                    firebase.update_current(0, "No Hand")
                    last_gesture = None
                    last_send_time = now
        except Exception as e:
            error_count += 1
            if error_count > 10:
                logger.error("Too many detect errors, stopping loop")
                break
            logger.error("Detect loop error: %s", e)

        time.sleep(0.01)

    detector.release()
    logger.info("Detect loop stopped")


@app.route("/frame.jpg")
def frame():
    with display_lock:
        if display_frame is None:
            return "", 204
        ret, buffer = cv2.imencode(
            ".jpg", display_frame,
            [cv2.IMWRITE_JPEG_QUALITY, 65]
        )
        if not ret:
            return "", 500
        frame_bytes = buffer.tobytes()
    return Response(frame_bytes, mimetype="image/jpeg")


@app.route("/detection_data")
def detection_data():
    with detection_lock:
        data = dict(current_detection)
    with stats_lock:
        data["stats"] = dict(current_stats)
    return jsonify(data)


@app.route("/reset_stats")
def reset_stats():
    with stats_lock:
        current_stats["totalDetection"] = 0
        current_stats["fistCount"] = 0
        current_stats["pointCount"] = 0
        current_stats["peaceCount"] = 0
        current_stats["threeCount"] = 0
        current_stats["fourCount"] = 0
        current_stats["openHandCount"] = 0
    logger.info("Stats reset to zero")
    return jsonify({"status": "ok"})


def _handle_signal(signum, frame):
    logger.info("Shutdown signal received")
    shutdown.set()


def free_port(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("0.0.0.0", port))
            return True
    except OSError:
        logger.warning("Port %d in use, attempting to free it...", port)
        try:
            subprocess.run(
                ["fuser", "-k", f"{port}/tcp"],
                capture_output=True, timeout=5,
            )
            time.sleep(0.5)
            return True
        except Exception:
            logger.error("Could not free port %d", port)
            return False


if __name__ == "__main__":
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)
    free_port(5002)

    threads = [
        threading.Thread(target=grab_loop),
        threading.Thread(target=detect_loop),
    ]
    for t in threads:
        t.start()

    port = 5002
    logger.info("Stream server starting on port %d", port)
    try:
        app.run(host="0.0.0.0", port=port, threaded=True, debug=False)
    except (KeyboardInterrupt, SystemExit, OSError):
        shutdown.set()

    logger.info("Shutting down...")
    shutdown.set()
    for t in threads:
        t.join(timeout=3)
    logger.info("Server stopped")
