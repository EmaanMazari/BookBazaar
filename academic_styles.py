import os, base64, subprocess

WORKSPACE = r'C:\Users\Microsoft\Desktop\fypfinal'
CHROME = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
LOGO_PATH = os.path.join(WORKSPACE, 'doc_images', 'iub_logo.png')

with open(LOGO_PATH, 'rb') as f:
    LOGO_B64 = base64.b64encode(f.read()).decode('utf-8')

# The exact CSS matching the original DOCX styles
ACADEMIC_CSS = """
@page {
    size: A4;
    margin: 25mm 20mm 25mm 20mm;
    @bottom-center {
        content: counter(page);
        font-family: 'Times New Roman', Times, serif;
        font-size: 10pt;
    }
}

body {
    font-family: 'Times New Roman', Times, serif;
    font-size: 11pt;
    line-height: 1.25;
    color: #000000;
    margin: 0;
    padding: 0;
    text-align: justify;
}

/* Original Heading Colors from styles.xml: 1F4D78 (Dark Navy) & 2E74B5 (Medium Blue) */
h1 {
    font-size: 16pt;
    font-weight: bold;
    color: #1F4D78;
    text-transform: uppercase;
    margin-top: 18pt;
    margin-bottom: 6pt;
    page-break-after: avoid;
}

h2 {
    font-size: 13pt;
    font-weight: bold;
    color: #2E74B5;
    margin-top: 14pt;
    margin-bottom: 4pt;
    page-break-after: avoid;
}

h3 {
    font-size: 11.5pt;
    font-weight: bold;
    color: #1F4D78;
    margin-top: 10pt;
    margin-bottom: 3pt;
    page-break-after: avoid;
}

h4 {
    font-size: 11pt;
    font-weight: bold;
    color: #000000;
    margin-top: 8pt;
    margin-bottom: 2pt;
    page-break-after: avoid;
}

p {
    margin-top: 0pt;
    margin-bottom: 6pt;
}

ul, ol {
    margin-top: 0pt;
    margin-bottom: 6pt;
    padding-left: 24pt;
}

li {
    margin-bottom: 3pt;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 6pt;
    margin-bottom: 10pt;
    font-size: 10pt;
    page-break-inside: avoid;
}

table, th, td {
    border: 1px solid #000000;
}

th {
    background-color: #1F4D78;
    color: #ffffff;
    font-weight: bold;
    padding: 5pt 7pt;
    text-align: left;
}

td {
    padding: 4pt 7pt;
    vertical-align: top;
}

tr:nth-child(even) td {
    background-color: #f9fbfd;
}

.table-approval th {
    background-color: #f2f4f8;
    color: #1F4D78;
}

.title-page {
    text-align: center;
    page-break-after: always;
    padding-top: 20pt;
}

.title-doc {
    font-size: 20pt;
    font-weight: bold;
    color: #1F4D78;
    margin-bottom: 6pt;
}

.title-for {
    font-size: 12pt;
    font-style: italic;
    color: #333333;
    margin-bottom: 6pt;
}

.title-app {
    font-size: 22pt;
    font-weight: bold;
    color: #1F4D78;
    margin-bottom: 4pt;
}

.title-sub {
    font-size: 12pt;
    color: #2E74B5;
    margin-bottom: 8pt;
}

.title-ver {
    font-size: 11pt;
    font-weight: bold;
    color: #555555;
    margin-bottom: 20pt;
}

.title-logo {
    width: 160px;
    height: auto;
    margin-bottom: 20pt;
}

.meta-block {
    margin-top: 15pt;
    font-size: 11pt;
    line-height: 1.4;
}

.meta-bold {
    font-weight: bold;
    color: #1F4D78;
}

.meta-dept {
    font-weight: bold;
    font-size: 11.5pt;
    color: #1F4D78;
    margin-top: 15pt;
}

pre, code {
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 9pt;
}

pre {
    background-color: #f8fafc;
    border: 1px solid #cbd5e1;
    border-left: 3px solid #1F4D78;
    padding: 8pt 10pt;
    overflow-x: auto;
    line-height: 1.35;
    margin-top: 4pt;
    margin-bottom: 8pt;
    page-break-inside: avoid;
    color: #0f172a;
}

.caption {
    text-align: center;
    font-style: italic;
    font-size: 9.5pt;
    margin-top: 4pt;
    margin-bottom: 10pt;
    color: #334155;
}

.diagram-box {
    border: 1px solid #cbd5e1;
    background-color: #ffffff;
    padding: 8pt;
    margin: 8pt 0;
    text-align: center;
    border-radius: 4pt;
    page-break-inside: avoid;
}

.diagram-box pre {
    text-align: left;
    background: transparent;
    border: none;
    padding: 0;
    margin: 0;
}

hr {
    border: 0;
    border-top: 1px solid #cbd5e1;
    margin: 12pt 0;
}
"""

print("Academic CSS loaded successfully.")
