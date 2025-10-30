import cv2
import numpy as np
import time
import threading
import sys
import os

def check_terminal_exit():
    input("Press Enter in terminal to exit...\n")
    sys.exit(0)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

prev_red, prev_green = False, False
last_print_time = time.time()
threading.Thread(target=check_terminal_exit, daemon=True).start()

# RED strict (ignore skin tones)
lower_red1 = np.array([0, 120, 80])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([170, 120, 80])
upper_red2 = np.array([180, 255, 255])

# GREEN strict (ignore yellowish green shades)
lower_green = np.array([35, 50, 50])
upper_green = np.array([90, 255, 255])

pixel_threshold = 1000
contour_area_threshold = 1000
kernel = np.ones((5,5), np.uint8)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (640,480))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Masks
        mask_red = cv2.inRange(hsv, lower_red1, upper_red1) + cv2.inRange(hsv, lower_red2, upper_red2)
        mask_green = cv2.inRange(hsv, lower_green, upper_green)

        mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, kernel)
        mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_CLOSE, kernel)
        mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_OPEN, kernel)
        mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_CLOSE, kernel)

        red_pixels = cv2.countNonZero(mask_red)
        green_pixels = cv2.countNonZero(mask_green)

        red_present = red_pixels > pixel_threshold
        green_present = green_pixels > pixel_threshold

        # Print updates
        if time.time() - last_print_time > 1:
            os.system('cls' if os.name=='nt' else 'clear')
            if red_present != prev_red:
                print("Red object detected ✅" if red_present else "Red object not present ❌")
                prev_red = red_present
            if green_present != prev_green:
                print("Green object detected ✅" if green_present else "Green object not present ❌")
                prev_green = green_present
            last_print_time = time.time()

        color_masks = {
            'red': (mask_red, (0,0,255), "Red"),
            'green': (mask_green, (0,255,0), "Green")
        }

        for color_name, (mask, color_bgr, label) in color_masks.items():
            if locals().get(f"{color_name}_present", False):
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for contour in contours:
                    if cv2.contourArea(contour) > contour_area_threshold:
                        x,y,w,h = cv2.boundingRect(contour)
                        cv2.rectangle(frame, (x,y),(x+w,y+h), color_bgr, 2)
                        cv2.putText(frame, label, (x,y-10), cv2.FONT_HERSHEY_SIMPLEX,0.6,color_bgr,2)

                        M = cv2.moments(contour)
                        if M['m00'] != 0:
                            cx = int(M['m10']/M['m00'])
                            cy = int(M['m01']/M['m00'])
                            cv2.circle(frame, (cx,cy), 5, (0,255,255), -1)
                            position = "Left" if cx<frame.shape[1]//3 else "Right" if cx>2*frame.shape[1]//3 else "Center"
                            cv2.putText(frame, position, (x,y+h+20), cv2.FONT_HERSHEY_SIMPLEX,0.6,color_bgr,2)

        cv2.imshow("Red & Green Only Detection", frame)
        if cv2.waitKey(1) & 0xFF==ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()

