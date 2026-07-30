import os
import subprocess
import threading
import time
import socket

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(ROOT, "output")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def serve_file(port=8080, directory=None):
    if directory is None:
        directory = OUTPUT_DIR
    if not os.path.exists(directory):
        print(f"[x] Directory not found: {directory}")
        return

    ip = get_local_ip()
    print(f"[*] HTTP server starting on {ip}:{port}")
    print(f"[*] Serving files from: {directory}")
    print(f"[*] URL: http://{ip}:{port}/")
    print("[*] Press Ctrl+C to stop")

    os.chdir(directory)
    try:
        subprocess.run(
            f"python3 -m http.server {port}",
            shell=True
        )
    except KeyboardInterrupt:
        print("\n[+] Server stopped")
