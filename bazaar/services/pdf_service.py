# ========================================================
# Bookzy AI - Digital Library & Soft Copy PDF Service
# Generates and serves valid, clean PDF soft copies for free books
# Zero 3rd-party binary dependencies (100% portable on any OS)
# ========================================================

import io
import re
from datetime import datetime


def _sanitize_pdf_text(text: str) -> str:
    """Sanitizes text for PDF literal string encoding."""
    if not text:
        return ""
    # Replace parentheses and backslashes
    clean = str(text).replace('\\', '/').replace('(', '[').replace(')', ']')
    # Filter to ASCII-printable or latin1
    clean = re.sub(r'[^\x20-\x7E]', ' ', clean)
    return clean.strip()


def generate_book_pdf(listing_or_book) -> bytes:
    """
    Generates a valid, beautifully formatted PDF document (PDF-1.4)
    containing book details, study notes, and digital library badge.
    """
    # Extract book and listing metadata
    if hasattr(listing_or_book, 'book'):
        book = listing_or_book.book
        listing = listing_or_book
        seller_name = getattr(listing.seller, 'full_name', 'Student Donor')
        condition = getattr(listing, 'condition', 'Good')
        city = getattr(listing, 'city', 'Pakistan')
        notes = getattr(listing, 'description', '') or getattr(book, 'description', '')
    else:
        book = listing_or_book
        listing = None
        seller_name = 'Verified Community Donor'
        condition = 'Digital Library Soft Copy'
        city = 'Pakistan'
        notes = getattr(book, 'description', '')

    title = _sanitize_pdf_text(getattr(book, 'title', 'Untitled Book'))[:75]
    author = _sanitize_pdf_text(getattr(book, 'author', 'Unknown Author'))[:60]
    category = _sanitize_pdf_text(getattr(book, 'category', 'General'))[:45]
    board = _sanitize_pdf_text(getattr(book, 'education_board', 'Higher Education / Pakistan'))[:50]
    subject = _sanitize_pdf_text(getattr(book, 'subject', ''))[:45] or category
    condition = _sanitize_pdf_text(condition)[:30]
    seller = _sanitize_pdf_text(seller_name)[:40]
    isbn = _sanitize_pdf_text(getattr(book, 'isbn', ''))[:30]
    
    if not notes:
        notes = f"This certified digital soft-copy edition of {title} is provided free of charge for students and educators across Pakistan via Bookzy AI community book donation initiative."
    notes = _sanitize_pdf_text(notes)[:320]

    # Split notes into 3 lines for clean PDF rendering
    line1 = notes[:85]
    line2 = notes[85:170]
    line3 = notes[170:255]
    line4 = notes[255:320]

    now_str = datetime.now().strftime("%Y-%m-%d")

    # PDF Stream content
    stream_content = f"""q
0.11 0.31 0.85 rg
50 720 512 42 re
f
Q
BT
/F1 13 Tf
1 1 1 rg
65 736 Td
(BOOKZY AI - CERTIFIED DIGITAL SOFT COPY) Tj
ET
BT
/F2 10 Tf
0.8 0.9 1 rg
380 736 Td
(100% FREE DONATION) Tj
ET

q
0.96 0.97 0.99 rg
50 535 512 170 re
f
0.82 0.86 0.92 RG
1.5 w
50 535 512 170 re
S
Q

BT
/F1 17 Tf
0.08 0.16 0.38 rg
70 668 Td
({title}) Tj
ET

BT
/F2 11 Tf
0.2 0.28 0.42 rg
70 642 Td
(Author: {author}) Tj
0 -20 Td
(Category: {category}   |   Subject: {subject}) Tj
0 -20 Td
(Board / Curriculum: {board}) Tj
0 -20 Td
(Condition: {condition}   |   Donor: {seller} ({city})) Tj
0 -20 Td
(ISBN: {isbn}   |   Digital Issue Date: {now_str}) Tj
ET

q
0.91 0.96 0.93 rg
50 415 512 105 re
f
0.22 0.62 0.35 RG
1.2 w
50 415 512 105 re
S
Q

BT
/F1 11 Tf
0.12 0.46 0.22 rg
70 495 Td
(COMMUNITY DONATION NOTICE & STUDY NOTES) Tj
ET
BT
/F2 10 Tf
0.16 0.22 0.28 rg
70 472 Td
({line1}) Tj
"""
    if line2:
        stream_content += f"""0 -16 Td
({line2}) Tj
"""
    if line3:
        stream_content += f"""0 -16 Td
({line3}) Tj
"""
    if line4:
        stream_content += f"""0 -16 Td
({line4}) Tj
"""

    stream_content += f"""ET

q
0.85 0.87 0.92 RG
0.8 w
50 85 512 0.8 re
S
Q

BT
/F2 9 Tf
0.4 0.45 0.52 rg
65 68 Td
(Bookzy AI Digital Library - Facilitating accessible education for students across Pakistan.) Tj
ET
BT
/F1 9 Tf
0.11 0.31 0.85 rg
440 68 Td
(bookzy.pk / Verified) Tj
ET
"""

    stream_bytes = stream_content.encode('latin1', errors='replace')
    stream_len = len(stream_bytes)

    objects = [
        b'<< /Type /Catalog /Pages 2 0 R >>',
        b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
        b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> >>',
        f'<< /Length {stream_len} >>\nstream\n'.encode('latin1') + stream_bytes + b'\nendstream',
        b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>',
        b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>'
    ]

    out = io.BytesIO()
    out.write(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
    
    offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(out.tell())
        out.write(f'{i} 0 obj\n'.encode('latin1'))
        out.write(obj)
        out.write(b'\nendobj\n')

    xref_offset = out.tell()
    out.write(f'xref\n0 {len(objects) + 1}\n'.encode('latin1'))
    out.write(b'0000000000 65535 f \n')
    for off in offsets[1:]:
        out.write(f'{off:010d} 00000 n \n'.encode('latin1'))

    out.write(f'trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n'.encode('latin1'))
    out.write(f'startxref\n{xref_offset}\n%%EOF\n'.encode('latin1'))

    return out.getvalue()
