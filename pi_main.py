import cv2
import socket
import json
import threading
import time

# === CONFIG ===
BASE_IP = "192.168.1.100"       # base station IP
BASE_TCP_PORT = 8888            # TCP command port
BASE_UDP_PORT = 6000            # UDP video feed port
CONTROLLER_IP = "192.168.1.101" # controller board IP
CONTROLLER_UDP_PORT = 6001      # UDP motion control port

# === GLOBALS ===
latest_command = None
stop_threads = False

# === SOCKETS ===
udp_video_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_video_sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)

udp_control_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.connect((BASE_IP, BASE_TCP_PORT))
print("✅ Connected to Base Station (TCP Command Channel)")

# === THREAD: TCP COMMAND RECEIVER ===
def receive_tcp_commands():
    global latest_command, stop_threads
    while not stop_threads:
        try:
            data = tcp_sock.recv(1024).decode().strip()
            if not data or data.lower() == "exit":
                print("🚪 Connection closed by Base Station.")
                stop_threads = True
                break
            latest_command = data
            print(f"📥 Received command from Base Station: {data}")
        except:
            break

threading.Thread(target=receive_tcp_commands, daemon=True).start()

# === CAMERA INIT ===
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Could not open Pi camera.")
    exit()

print("🔥 Pi Hybrid Camera + Control System Running...")

last_sent_command = None
last_sent_time = 0
send_interval = 0.5

# === MAIN LOOP ===
while not stop_threads:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Frame capture failed.")
        continue

    current_time = time.time()

    # ---- STREAM CAMERA FEED TO BASE (UDP) ----
    _, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
    udp_video_sock.sendto(buf.tobytes(), (BASE_IP, BASE_UDP_PORT))

    # ---- SEND COMMAND TO CONTROLLER IF EXISTS ----
    if latest_command and (latest_command != last_sent_command or current_time - last_sent_time > send_interval):
        msg = json.dumps({"command": latest_command}).encode()
        udp_control_sock.sendto(msg, (CONTROLLER_IP, CONTROLLER_UDP_PORT))
        print(f"📡 Sent to Controller: {latest_command.upper()}")
        last_sent_command = latest_command
        last_sent_time = current_time

    cv2.imshow("PiCam Feed", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
        stop_threads = True
        break
    if cv2.getWindowProperty("PiCam Feed", cv2.WND_PROP_VISIBLE) < 1:
        stop_threads = True
        break

# === CLEANUP ===
cap.release()
cv2.destroyAllWindows()
udp_video_sock.close()
udp_control_sock.close()
tcp_sock.close()
print("🧼 Pi system shutdown complete.")
