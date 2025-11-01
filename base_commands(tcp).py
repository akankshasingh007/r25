import socket

HOST = ''
PORT = 5050

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"[SERVER] Waiting for connection on port {PORT}...")
conn, addr = server_socket.accept()
print(f"[SERVER] Connected by {addr}")

try:
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        print(f"[CONTROLLER] {data}")
except KeyboardInterrupt:
    print("\n[SERVER] Shutting down...")
finally:
    conn.close()
    server_socket.close()
