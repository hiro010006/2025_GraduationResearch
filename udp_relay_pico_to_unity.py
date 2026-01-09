# ============================================
# UDP Relay with CSV Logging
# Pico <-> Unity bidirectional bridge
# ============================================

import socket
import select
import csv
import time
from datetime import datetime

# ---------- IP Settings ----------
UNITY_IP = "127.0.0.1"   # Unity 実行 PC
PICO_IP = None           # 初回 Pico 受信時に自動取得

# ---------- Port Settings ----------
# Pico -> Python -> Unity
PICO_SEND_PORT = 5000
UNITY_RECV_PORT = 5005

# Unity -> Python -> Pico
UNITY_SEND_PORT = 60000
PICO_RECV_PORT = 5001

BUFFER_SIZE = 64

# ---------- CSV Log Setup ----------
log_filename = datetime.now().strftime("udp_log_%Y%m%d_%H%M%S.csv")
log_file = open(log_filename, "w", newline="", encoding="utf-8")
csv_writer = csv.writer(log_file)

# CSV Header
csv_writer.writerow([
    "timestamp",
    "direction",
    "src_ip",
    "src_port",
    "dst_ip",
    "dst_port",
    "payload"
])
log_file.flush()

# ---------- Socket Setup ----------
sock_from_pico = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_from_pico.bind(("0.0.0.0", PICO_SEND_PORT))

sock_from_unity = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_from_unity.bind(("0.0.0.0", UNITY_SEND_PORT))

sock_to_unity = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_to_pico = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("UDP Relay started (CSV logging enabled)")
print("Log file :", log_filename)
print("Pico  -> Python -> Unity :", PICO_SEND_PORT, "->", UNITY_RECV_PORT)
print("Unity -> Python -> Pico  :", UNITY_SEND_PORT, "->", PICO_RECV_PORT)

# ---------- Main Loop ----------
while True:
    readable, _, _ = select.select(
        [sock_from_pico, sock_from_unity],
        [],
        []
    )

    for s in readable:
        data, addr = s.recvfrom(BUFFER_SIZE)
        timestamp = time.time()

        # Pico -> Unity
        if s is sock_from_pico:
            PICO_IP = addr[0]

            sock_to_unity.sendto(data, (UNITY_IP, UNITY_RECV_PORT))

            csv_writer.writerow([
                timestamp,
                "Pico->Unity",
                addr[0],
                addr[1],
                UNITY_IP,
                UNITY_RECV_PORT,
                data.decode("ascii", errors="replace")
            ])
            log_file.flush()

            print("Pico -> Unity :", data)

        # Unity -> Pico
        elif s is sock_from_unity:
            if PICO_IP is None:
                print("Waiting for Pico IP...")
                continue

            sock_to_pico.sendto(data, (PICO_IP, PICO_RECV_PORT))

            csv_writer.writerow([
                timestamp,
                "Unity->Pico",
                addr[0],
                addr[1],
                PICO_IP,
                PICO_RECV_PORT,
                data.decode("ascii", errors="replace")
            ])
            log_file.flush()

            print("Unity -> Pico :", data)
