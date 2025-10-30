import socket
import json

UDP_IP = "0.0.0.0"
UDP_PORT = 6001
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#sock.connect('localhost',8888)
print('connected to base')
sock.bind((UDP_IP, UDP_PORT))

print("Listening for QR directions...")
while True:
    data, addr = sock.recvfrom(1024)
    msg = json.loads(data.decode())
    if not data =='exit':
        print('connection closed')
        break
    print(f"Received from {addr}: {msg}")
sock.close()