import socket
import cv2
import pickle
import struct

# Base station server settings
HOST = ''       # Listen on all available network interfaces
PORT = 9999     # Choose any open port

# Create socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"[SERVER] Listening on port {PORT}...")
conn, addr = server_socket.accept()
print(f"[SERVER] Connected by {addr}")

data = b""
payload_size = struct.calcsize("Q")

while True:
    # Receive message size first
    while len(data) < payload_size:
        packet = conn.recv(4096)
        if not packet:
            break
        data += packet

    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("Q", packed_msg_size)[0]

    # Receive the full frame data
    while len(data) < msg_size:
        data += conn.recv(4096)

    frame_data = data[:msg_size]
    data = data[msg_size:]

    # Deserialize and show the frame
    frame = pickle.loads(frame_data)
    cv2.imshow("Camera Feed", frame)

    if cv2.waitKey(1) == ord('q'):
        break

conn.close()
cv2.destroyAllWindows()
