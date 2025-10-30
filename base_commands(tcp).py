import socket
TCP_IP = "0.0.0.0"  # Pi IP
TCP_PORT = 6000
sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_tcp.connect((TCP_IP, TCP_PORT))
##sock_tcp.bind('localhost',8888)
connection , addr=sock_tcp.accept()

while True:
    cmd = input("Enter command for Pi (forward/left/right/stop/exit): ")
    sock_tcp.send(cmd.encode())
    if cmd.lower() == "exit":
        break
connection.close()
sock_tcp.close()