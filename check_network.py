# -*- coding: utf-8 -*-
# check_network.py
import socket
import os
import sys
from dotenv import load_dotenv

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

uri = os.getenv("NEO4J_URI", "")
# URI에서 주소만 깔끔하게 추출 (neo4j+s:// 제거)
host = uri.replace("neo4j+s://", "").replace("neo4j://", "").replace("bolt://", "")
port = 7687

print(f"[NET] Network Connection Test: {host}:{port}")

try:
    sock = socket.create_connection((host, port), timeout=5)
    print("[OK] Connection successful! Network path is open.")
    sock.close()
except Exception as e:
    print(f"[FAILED] Connection failed! Network is blocked.\nError: {e}")
    print("[TIP] Try connecting via mobile hotspot (LTE/5G).")

