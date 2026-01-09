import socket
import time
import math

# ===== Unity 側 FingerUdpReceiver に合わせる =====
UNITY_IP = "127.0.0.1"   # Unity と同じ PC
UNITY_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

finger_id = 0
t = 0.0
dt = 0.05
omega = 2.0

print("Sending UDP to FingerUdpReceiver")

while True:
    value = (math.sin(omega * t) + 1.0) * 0.5
    msg = f"{finger_id},{value}"

    sock.sendto(msg.encode("ascii"), (UNITY_IP, UNITY_PORT))
    print("Send:", msg)

    t += dt
    time.sleep(dt)
