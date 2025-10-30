import cv2
import socket
import pickle

UDP_IP = "0.0.0.0"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

data = b""
while True:
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

sock.close()
cv2.destroyAllWindows()
