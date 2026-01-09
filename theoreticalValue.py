# =====================================================
# Unity Force Model Probe (Pico-less, Unity-safe)
# u -> Unity -> f logging
# =====================================================

import socket
import csv
import time
from datetime import datetime

# ---------- IP / Port ----------
UNITY_IP        = "127.0.0.1"
UNITY_PORT_RECV = 5005     # Unity listen
PYTHON_PORT_RECV = 60000   # Python listen

# ---------- Sweep Settings ----------
FINGER_ID = 0
U_START   = 0
U_END     = 0.26
U_STEP    = 0.001
SEND_INTERVAL = 0.5   # [s] Unity 安定待ち

BUFFER_SIZE = 128

# ---------- CSV ----------
log_filename = datetime.now().strftime("unity_force_probe_%Y%m%d_%H%M%S.csv")
csv_file = open(log_filename, "w", newline="", encoding="utf-8")
csv_writer = csv.writer(csv_file)

csv_writer.writerow([
    "timestamp",
    "finger_id",
    "u_normalized",
    "f_normalized"
])
csv_file.flush()

# ---------- Socket ----------
sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_recv.bind(("0.0.0.0", PYTHON_PORT_RECV))
sock_recv.settimeout(1)

print("Unity force probe started")
print("CSV :", log_filename)

# ---------- Main Sweep ----------
u = U_START
while u <= U_END + 1e-9:
    # ---- Unity が理解できる payload を厳密に送信 ----
    payload = f"{FINGER_ID},{u:.6f}"
    sock_send.sendto(payload.encode("ascii"),
                     (UNITY_IP, UNITY_PORT_RECV))

    print("Send -> Unity :", payload)

    # ---- Unity からの反力を待つ ----
    try:
        data, addr = sock_recv.recvfrom(BUFFER_SIZE)
        text = data.decode("ascii", errors="replace").strip()
        parts = text.split(",")

        if len(parts) >= 2:
            recv_finger = int(parts[0])
            f = float(parts[1])

            csv_writer.writerow([
                time.time(),
                recv_finger,
                u,
                f
            ])
            csv_file.flush()

            print("Recv <- Unity :", text)
        else:
            print("Invalid Unity payload :", text)

    except socket.timeout:
        print("Unity response timeout at u =", u)

    u += U_STEP
    time.sleep(SEND_INTERVAL)

csv_file.close()
print("Finished.")
