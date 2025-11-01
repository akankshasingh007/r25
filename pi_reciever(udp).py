import socket
import pygame
import time

# === CONFIG ===
HOST = "10.118.243.44"   # ← replace with your BASE PC’s IP address
PORT = 5050

# === SOCKET CONNECT ===
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
print("[CLIENT] Connected to base server")

# === CONTROLLER SETUP ===
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("⚠️  No controller detected!")
    pygame.quit()
    sock.close()
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"[CLIENT] Controller: {joystick.get_name()}")

# Map Xbox button IDs → readable names
button_map = {
    0: "A",
    1: "B",
    2: "X",
    3: "Y",
    4: "LB",
    5: "RB",
    6: "View",
    7: "Menu",
    8: "Xbox",
    9: "Left Stick",
    10: "Right Stick"
}

# === MAIN LOOP ===
try:
    while True:
        pygame.event.pump()
        for i in range(joystick.get_numbuttons()):
            if joystick.get_button(i):
                name = button_map.get(i, f"Button {i}")
                msg = f"{name} pressed"
                sock.sendall(msg.encode())
                print(f"[SENT] {msg}")
                time.sleep(0.25)  # debounce
except KeyboardInterrupt:
    print("\n[CLIENT] Exiting...")
finally:
    sock.close()
    pygame.quit()
