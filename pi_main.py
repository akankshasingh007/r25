import socket
import cv2
import pickle
import struct
import time

# Change this to your Base Station IP
SERVER_IP = '10.118.243.44'
PORT = 9999

# Connect to server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, PORT))
print("[CLIENT] Connected to base station.")

# Open camera
camera = cv2.VideoCapture(0)
time.sleep(2)  # Give the camera a moment to warm up

while True:
    ret, frame = camera.read()
    if not ret:
        print("[CLIENT] Frame capture failed, exiting...")
        break

    # Optional resize for smoother streaming
    frame = cv2.resize(frame, (320, 240))

    # Serialize frame
    data = pickle.dumps(frame)
    message = struct.pack("Q", len(data)) + data
    client_socket.sendall(message)

camera.release()
client_socket.close()
