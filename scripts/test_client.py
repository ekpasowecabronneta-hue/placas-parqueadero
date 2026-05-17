#!/usr/bin/env python3
import socket
import sys
import time

host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080

s = socket.create_connection((host, port), timeout=10)
s.settimeout(12)
t0 = time.time()
n = 0
while time.time() - t0 < 12:
    try:
        data = s.recv(4096)
        if data:
            n += 1
            print(data.decode().strip())
    except socket.timeout:
        break
print(f"total={n}")
s.close()
