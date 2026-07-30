# PDF RAT v1.0

Create malicious PDF files that deliver Metasploit payloads to **Windows 10+** targets. For authorized penetration testing only.

## Features

- **3 exploit methods** — Adobe Reader exploit, custom PDF with embedded EXE, PDF with download link
- **6 payload types** — x64/x86 Meterpreter, stageless, shell
- **4 lure templates** — Invoice, Confidential Report, Security Update, Resume
- **Auto mode** — Generate PDF + start listener in one go
- **Built-in HTTP server** — Deliver the PDF over LAN

## Installation (Kali Linux)

```bash
git clone https://github.com/rizqihasanfadilla01-cmd/PDF_RAT.git
cd PDF_RAT/kali
pip install -r requirements.txt
python3 pdf-rat.py
```

## Usage

```
╔══════════════════════════════════════════════╗
║           PDF RAT v1.0 - Kali Linux          ║
╚══════════════════════════════════════════════╝

 LHOST: 192.168.1.100    LPORT: 4444
 Payload: x64 Meterpreter
 Method: Custom PDF + Embedded EXE
 Lure: Invoice

  [1]  Generate PDF Payload
  [2]  Select Exploit Method
  [3]  Select Payload Type
  [4]  Configure LHOST / LPORT
  [5]  Select Lure Template
  [6]  Set Output Filename
  [7]  Start Metasploit Listener
  [8]  Stop Listener
  [9]  Serve PDF via HTTP
  [A]  Auto Mode (All-in-One)
  [Q]  Quit
```

## Exploit Methods

| Method | Technique | Target |
|---|---|---|
| **1** | Metasploit `adobe_pdf_embedded_exe` | Adobe Reader DC |
| **2** | Custom lure PDF + embedded EXE | Adobe Reader / manual open |
| **3** | PDF with clickable download link | Any PDF reader + social engineering |

## Payloads

| ID | Payload | Arch |
|---|---|---|
| 1 | `windows/x64/meterpreter/reverse_tcp` | x64 |
| 2 | `windows/meterpreter/reverse_tcp` | x86 |
| 3 | `windows/x64/meterpreter_reverse_tcp` | x64 (stageless) |
| 4 | `windows/meterpreter_reverse_tcp` | x86 (stageless) |
| 5 | `windows/x64/shell_reverse_tcp` | x64 |
| 6 | `windows/shell_reverse_tcp` | x86 |

## Lure Templates

1. **Invoice** — Fake invoice with payment details
2. **Confidential Report** — Internal audit document
3. **Security Update** — Fake IT security patch notice
4. **Resume** — Job application with attached profile

## Delivery Options

- HTTP server: `[9] Serve PDF via HTTP` → target downloads from browser
- USB drop: Copy PDF to USB and deliver physically
- Email: Send as attachment with social engineering pretext

## Output

Generated files are saved to `kali/output/`:

```
kali/output/
├── invoice.pdf         # Malicious PDF
├── payload.exe         # Standalone payload (for method 3)
```

## Requirements

- Kali Linux (or any Debian-based distro with Metasploit)
- Metasploit Framework (`msfvenom`, `msfconsole`)
- Python 3 + pip
- reportlab (`pip install reportlab`)

## Disclaimer

This tool is for **authorized security testing only**. Unauthorized use against systems you do not own or have explicit permission to test is illegal. The author is not responsible for misuse.
