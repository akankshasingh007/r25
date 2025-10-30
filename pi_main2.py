# base_main.py
import cv2
import socket
import pickle

# --- Video receive ---
UDP_IP = "0.0.0.0"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

# --- TCP send commands ---
TCP_IP = "192.168.1.50"  # Pi IP
TCP_PORT = 6000
sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_tcp.connect((TCP_IP, TCP_PORT))

data = b""
while True:
    # receive video
    packet, addr = sock.recvfrom(65536)
    data += packet
    try:
        frame = pickle.loads(data)
        cv2.imshow("Pi Camera Feed", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break
        data = b""
    except Exception:
        pass

    # send command example
    cmd = input("Enter command for Pi (forward/left/right/stop/exit): ")
    sock_tcp.send(cmd.encode())
    if cmd.lower() == "exit":
        break

sock.close()
sock_tcp.close()
