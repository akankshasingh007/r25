import cv2
import numpy as np
import time
from collections import defaultdict
import webbrowser

cv2.setLogLevel(0)

qr_detector = cv2.QRCodeDetector()
qr_ignore_interval = 5.0  # for direction QR
location_qr_ignore_interval = 5.0  # for location QR

direction_keywords = {
    "left": ["left", "go left", "turn left", "move left"],
    "right": ["right", "go right", "turn right", "move right"],
    "forward": ["forward", "go forward", "move forward", "ahead", "straight"]
}

def classify_direction(text):
    text = text.lower().strip()
    for direction, phrases in direction_keywords.items():
        if any(phrase in text for phrase in phrases):
            return direction
    return None

def multi_qr_direction(frame, qr_counts, qr_last_seen):
    current_time = time.time()
    seen_this_frame = set()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detected = []

    # Multi-scale detection
    scales = [1.0, 0.75, 0.5]
    for scale in scales:
        resized = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR) if scale != 1.0 else gray.copy()
        retval, decoded_infos, points, _ = qr_detector.detectAndDecodeMulti(resized)
        if retval:
            for qr_data, qr_point in zip(decoded_infos, points):
                if not qr_data:
                    continue
                if scale != 1.0:
                    qr_point = qr_point / scale
                detected.append((qr_data, qr_point))

    # Process detected QRs (up to 5)
    for qr_data, qr_point in detected[:5]:
        qr_data = qr_data.strip()
        if qr_data in seen_this_frame:
            continue
        seen_this_frame.add(qr_data)

        if qr_data in qr_last_seen and (current_time - qr_last_seen[qr_data]) < qr_ignore_interval:
            continue
        qr_last_seen[qr_data] = current_time

        direction = classify_direction(qr_data)
        if direction:
            qr_counts[direction] += 1

        pts = qr_point.astype(int).reshape(-1, 2)
        for i in range(len(pts)):
            cv2.line(frame, tuple(pts[i]), tuple(pts[(i + 1) % len(pts)]), (255, 0, 0), 2)
        x, y = pts[0]
        cv2.putText(frame, qr_data, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    y0, line_height = 30, 25
    if qr_counts:
        most_common_direction = max(qr_counts, key=qr_counts.get)
        cv2.putText(frame, f"➡ Max: {most_common_direction.upper()} ({qr_counts[most_common_direction]})",
                    (10, y0), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        y = y0 + line_height
        for direction, count in qr_counts.items():
            cv2.putText(frame, f"{direction.capitalize()}: {count}", (10, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            y += line_height

    return frame

def single_qr_location(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    retval, points = qr_detector.detect(gray)
    
    if retval is not None and points is not None:
        decoded_result = qr_detector.decode(gray, points)
        if isinstance(decoded_result, (tuple, list)):
            qr_data = decoded_result[0]
        else:
            qr_data = decoded_result

        if qr_data:
            qr_data = qr_data.strip()
            pts = points.astype(int).reshape(-1, 2)
            for i in range(len(pts)):
                cv2.line(frame, tuple(pts[i]), tuple(pts[(i + 1) % len(pts)]), (0, 255, 0), 2)
            x, y = pts[0]
            cv2.putText(frame, qr_data, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            return qr_data, pts
    return None, None

mode = input("Select mode (1 = Max Direction / 2 = Location QR): ").strip()

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Error: Could not open camera.")
    exit()

qr_counts = defaultdict(int)
qr_last_seen = {}
location_qr_last_seen = {}
reset_interval = 10
last_reset_time = time.time()

print("🔥 QR Detection Running... Press ESC to exit.")

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    current_time = time.time()

    if mode == "1":
        frame = multi_qr_direction(frame, qr_counts, qr_last_seen)

        if current_time - last_reset_time > reset_interval:
            qr_counts.clear()
            last_reset_time = current_time

    elif mode == "2":
        qr_location, location_pts = single_qr_location(frame)
        if qr_location:
            # Check ignore interval
            if qr_location not in location_qr_last_seen or (current_time - location_qr_last_seen[qr_location]) > location_qr_ignore_interval:
                location_qr_last_seen[qr_location] = current_time
                print(f"📍 Location QR Detected: {qr_location}")

                # Auto-open URL if detected
                if qr_location.lower().startswith(("http://", "https://")):
                    print(f"🌐 Opening URL: {qr_location}")
                    webbrowser.open(qr_location)

    cv2.imshow("QR Detection Feed", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
print("🧼 QR Detection Shutdown Complete.")
