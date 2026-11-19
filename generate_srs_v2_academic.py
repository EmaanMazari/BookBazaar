import os, base64, subprocess
from academic_styles import ACADEMIC_CSS, LOGO_B64, WORKSPACE, CHROME

# Helper to load image as base64
def load_img_b64(fname):
    p = os.path.join(WORKSPACE, 'doc_images', fname)
    if os.path.exists(p):
        with open(p, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    return ""

fig2_1_b64 = load_img_b64('d0c41a29b10bf84df180d7ba7b86e033e84c891f.png')
fig3_1_b64 = load_img_b64('fe661bbbabab21661053fe6842ce7b733dedde2f.png')
fig3_2_b64 = load_img_b64('66d68e5f8a7ecb199a355952b4fd9fda989c77da.png')
fig4_1_b64 = load_img_b64('d797215213fa8e25d2f5bf4164131f499bb31092.png')
fig4_2_b64 = load_img_b64('d0c41a29b10bf84df180d7ba7b86e033e84c891f.png')
fig4_3_b64 = load_img_b64('85575053715ae7ecf8c545d2d4211722363c2a03.png')

srs_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Software Requirements Specification (SRS) - BookBazaar v2.0</title>
<style>
{ACADEMIC_CSS}
</style>
</head>
<body>

<!-- Title Page -->
<div class="title-page">
    <div class="title-doc">Software Requirements Specification (SRS)</div>
    <div class="title-for">for</div>
    <div class="title-app">BookBazaar</div>
    <div class="title-sub">Used Book Marketplace & Academic Textbook Barcode Platform for Pakistan</div>
    <div class="title-ver">Version 2.0 (Production Implementation Edition)</div>

    <img src="data:image/png;base64,{LOGO_B64}" class="title-logo" alt="The Islamia University of Bahawalpur">

    <div class="meta-block">
        <div class="meta-bold">Students</div>
        <div>Emaan Mazari &nbsp;&nbsp;&nbsp;&nbsp; F23BSEEN1E02157</div>
        <div>Laila Akhtar &nbsp;&nbsp;&nbsp;&nbsp; F23BSEEN1E02119</div>
    </div>

    <div class="meta-block">
        <div class="meta-bold">Advised By</div>
        <div>(Sir Gulraiz)</div>
    </div>

    <div class="meta-dept">
        Department of Software Engineering<br>
        Faculty of Computing<br>
        The Islamia University of Bahawalpur
    </div>
</div>

<!-- Revision History -->
<h2>Revision History</h2>
<table>
    <tr>
        <th style="width: 15%;">Date</th>
        <th style="width: 15%;">Version</th>
        <th style="width: 30%;">Authors</th>
        <th style="width: 40%;">Reason for Changes</th>
    </tr>
    <tr>
        <td>03-Nov-2026</td>
        <td>1.0</td>
        <td>Emaan Mazari, Laila Akhtar</td>
        <td>Initial Draft Specification.</td>
    </tr>
    <tr>
        <td>09-Nov-2026</td>
        <td>2.0</td>
        <td>Emaan Mazari, Laila Akhtar</td>
        <td>Comprehensive update reflecting actual implementation: DRF REST API backend, PostgreSQL 18 schema, HTML5/Tailwind responsive client, DRF Token authentication, Rs. 50 contact unlock, 5-day deal confirmation / 100% wallet refund workflow, and proprietary ad banner engine.</td>
    </tr>
</table>

<!-- Document Approval -->
<h2>Document Approval</h2>
<table class="table-approval">
    <tr>
        <th style="width: 25%;">Role</th>
        <th style="width: 35%;">Name</th>
        <th style="width: 20%;">Signature</th>
        <th style="width: 20%;">Date</th>
    </tr>
    <tr>
        <td><strong>Project Advisor</strong></td>
        <td>Sir Gulraiz</td>
        <td>____________________</td>
        <td>____/____/2026</td>
    </tr>
    <tr>
        <td><strong>Project Coordinator</strong></td>
        <td>Department of Software Engineering</td>
        <td>____________________</td>
        <td>____/____/2026</td>
    </tr>
</table>

<!-- Table of Contents -->
<div style="page-break-before: always;"></div>
<h2>Table of Contents</h2>
<table style="border: none;">
    <tr style="border: none;"><td style="border: none;"><strong>1. Introduction</strong></td><td style="border: none; text-align: right;"><strong>4</strong></td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 20px;">1.1 Purpose</td><td style="border: none; text-align: right;">4</td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 20px;">1.2 Scope</td><td style="border: none; text-align: right;">4</td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 20px;">1.3 Definitions, Acronyms, and Abbreviations</td><td style="border: none; text-align: right;">5</td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 20px;">1.4 References</td><td style="border: none; text-align: right;">5</td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 20px;">1.5 Overview</td><td style="border: none; text-align: right;">5</td></tr>
    <tr style="border: none;"><td style="border: none;"><strong>2. The Overall Description</strong></td><td style="border: none; text-align: right;"><strong>6</strong></td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 20px;">2.1 Product Perspective</td><td style="border: none; text-align: right;">6</td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 40px;">2.1.1 Operations</td><td style="border: none; text-align: right;">6</td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 40px;">2.1.2 Site Adaptation Requirements</td><td style="border: none; text-align: right;">7</td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 20px;">2.2 Product Functions</td><td style="border: none; text-align: right;">7</td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 20px;">2.3 User Characteristics</td><td style="border: none; text-align: right;">8</td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 20px;">2.4 General Constraints</td><td style="border: none; text-align: right;">8</td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 20px;">2.5 Assumptions and Dependencies</td><td style="border: none; text-align: right;">8</td></tr>
    <tr style="border: none;"><td style="border: none;"><strong>3. Specific Requirements</strong></td><td style="border: none; text-align: right;"><strong>9</strong></td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 20px;">3.1 External Interface Requirements</td><td style="border: none; text-align: right;">9</td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 40px;">3.1.1 System Interfaces</td><td style="border: none; text-align: right;">9</td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 40px;">3.1.2 User Interfaces</td><td style="border: none; text-align: right;">9</td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 40px;">3.1.3 Hardware Interfaces</td><td style="border: none; text-align: right;">10</td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 40px;">3.1.4 Software Interfaces</td><td style="border: none; text-align: right;">10</td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 40px;">3.1.5 Communications Interfaces</td><td style="border: none; text-align: right;">10</td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 20px;">3.2 Functional Requirements (FR-1 to FR-13)</td><td style="border: none; text-align: right;">10</td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 20px;">3.3 Use Cases</td><td style="border: none; text-align: right;">14</td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 20px;">3.4 Classes and Objects (Data Model Mapping)</td><td style="border: none; text-align: right;">17</td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 20px;">3.5 Non-Functional Requirements</td><td style="border: none; text-align: right;">18</td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 20px;">3.6 Inverse Requirements</td><td style="border: none; text-align: right;">20</td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 20px;">3.7 Logical Database Requirements</td><td style="border: none; text-align: right;">20</td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 20px;">3.8 Design Constraints and Standards Compliance</td><td style="border: none; text-align: right;">21</td></tr>
    <tr style="border: none;"><td style="border: none;"><strong>4. Analysis Models</strong></td><td style="border: none; text-align: right;"><strong>22</strong></td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 20px;">4.1 Sequence Diagrams</td><td style="border: none; text-align: right;">22</td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 20px;">4.2 Data Flow Diagrams (DFD)</td><td style="border: none; text-align: right;">23</td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 20px;">4.3 State-Transition Diagrams (STD)</td><td style="border: none; text-align: right;">24</td></tr>
    <tr style="border: none;"><td style="border: none;"><strong>5. Supporting Information</strong></td><td style="border: none; text-align: right;"><strong>25</strong></td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 20px;">Appendix A – Background Research on Pakistani Used Book Trade</td><td style="border: none; text-align: right;">25</td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 20px;">Appendix B – Complete Data Dictionary</td><td style="border: none; text-align: right;">26</td></tr>
    <tr style="border: none;"><td style="border: none; padding-left: 20px;">Appendix C – Phase 6 Mobile App & Production Expansion Roadmap</td><td style="border: none; text-align: right;">29</td></tr>
</table>

<!-- Section 1 -->
<div style="page-break-before: always;"></div>
<h1>1. INTRODUCTION</h1>

<h2>1.1 Purpose</h2>
<p>
This Software Requirements Specification (SRS) document provides a formal, comprehensive description of the requirements for <strong>BookBazaar</strong>. BookBazaar is a localized, web-based second-hand academic book marketplace and barcode query platform designed specifically for students, educators, and book collectors across Pakistan. It establishes a reliable peer-to-peer (C2C) ecosystem for buying, selling, and exchanging used educational textbooks and academic reference materials.
</p>
<p>
This document serves as the formal baseline agreement between the project development team, project advisor <strong>Sir Gulraiz</strong>, and the final year evaluation committee at the Department of Software Engineering, Faculty of Computing, The Islamia University of Bahawalpur (IUB).
</p>

<h2>1.2 Scope</h2>
<p>
BookBazaar addresses acute pain points within Pakistan's academic textbook market, where hyperinflation has pushed textbook prices beyond the means of ordinary students, and local second-hand book stalls operate without price transparency or searchability. The system provides:
</p>
<ul>
    <li><strong>Academic Catalog & Barcode Scanner:</strong> Automatic metadata extraction via ISBN-10/ISBN-13 lookup (interfacing Open Library / Google Books APIs) and structured academic categorization by Pakistani provincial boards (Punjab, Federal, Sindh, KPK, Balochistan), Cambridge (O/A Level), and university degree curricula.</li>
    <li><strong>Multi-Seller Comparison Feed:</strong> Direct aggregation of multiple student offers for the exact same textbook, sorted transparently from lowest to highest price.</li>
    <li><strong>Privacy-Preserving Contact Unlock:</strong> Seller phone numbers and campus physical meeting locations remain strictly masked. A buyer pays a nominal facilitation fee (Rs. 50 PKR) to unlock direct seller contact details.</li>
    <li><strong>5-Day Deal Confirmation & In-App Wallet Refund:</strong> A high-trust financial lifecycle where buyers confirm whether a transaction materialized. If the deal completes, the platform retains the fee; if the seller is unresponsive or the book is sold, 100% of the fee (Rs. 50 PKR) is instantly refunded into the buyer's internal platform wallet.</li>
    <li><strong>Proprietary First-Party Ad Engine:</strong> A privacy-respecting ad delivery engine enabling academic bookstores, coaching centers, and student services to display banners without third-party tracking cookies.</li>
    <li><strong>Administrative Management Console:</strong> Comprehensive Django administrative suite for reviewing listings, moderating complaints, setting platform parameters, and auditing financial ledgers.</li>
</ul>

<h2>1.3 Definitions, Acronyms, and Abbreviations</h2>
<table>
    <tr><th>Term / Acronym</th><th>Full Form / Definition</th></tr>
    <tr><td><strong>API</strong></td><td>Application Programming Interface (RESTful JSON endpoints).</td></tr>
    <tr><td><strong>C2C</strong></td><td>Customer-to-Customer (peer-to-peer marketplace model).</td></tr>
    <tr><td><strong>DRF</strong></td><td>Django REST Framework (Python backend API layer).</td></tr>
    <tr><td><strong>ERD</strong></td><td>Entity Relationship Diagram.</td></tr>
    <tr><td><strong>HMAC-SHA256</strong></td><td>Hash-based Message Authentication Code with SHA-256 (used for secure payment callbacks).</td></tr>
    <tr><td><strong>ISBN</strong></td><td>International Standard Book Number (ISO 2108, 10 or 13 digits).</td></tr>
    <tr><td><strong>OTP</strong></td><td>One-Time Password (verification mechanism for user mobile numbers).</td></tr>
    <tr><td><strong>PBKDF2</strong></td><td>Password-Based Key Derivation Function 2 (NIST-approved password hashing).</td></tr>
    <tr><td><strong>PKR</strong></td><td>Pakistani Rupee (official currency symbol Rs.).</td></tr>
    <tr><td><strong>Pillow</strong></td><td>Python Imaging Library used for server-side image validation and sanitization.</td></tr>
    <tr><td><strong>PostgreSQL</strong></td><td>Enterprise-grade relational database management system (Version 18.x).</td></tr>
    <tr><td><strong>SPA</strong></td><td>Single-Page Application (HTML5 / Tailwind CSS / Vanilla ES6 client).</td></tr>
</table>

<h2>1.4 References</h2>
<ul>
    <li>IEEE Std 830-1998, <em>IEEE Recommended Practice for Software Requirements Specifications</em>.</li>
    <li>ISO/IEC/IEEE 29148:2018, <em>Systems and software engineering — Life cycle processes — Requirements engineering</em>.</li>
    <li>ISO 2108:2017, <em>Information and documentation — International Standard Book Number (ISBN)</em>.</li>
    <li>Django 5.1 & Django REST Framework Official Documentation (2025/2026).</li>
    <li>PostgreSQL 18 Documentation, The PostgreSQL Global Development Group.</li>
    <li>State Bank of Pakistan (SBP) Guidelines on Digital Onboarding and Mobile Financial Services.</li>
</ul>

<h2>1.5 Overview</h2>
<p>
The remainder of this specification outlines the overall architecture, actors, operating constraints, and external interfaces (Section 2), elaborates the complete functional requirements (FR-1 through FR-13), use case specifications, data models, non-functional attributes, and database constraints (Section 3), provides formal analysis models including sequence, DFD, and state-transition diagrams (Section 4), and concludes with supporting background research, a comprehensive data dictionary, and future expansion roadmap (Section 5).
</p>

<!-- Section 2 -->
<div style="page-break-before: always;"></div>
<h1>2. THE OVERALL DESCRIPTION</h1>

<h2>2.1 Product Perspective</h2>
<p>
BookBazaar is designed as an autonomous, self-contained client-server web architecture engineered to operate across desktop and mobile form factors. The backend is implemented in Python 3.12 utilizing the Django 5.1 framework and Django REST Framework (DRF), deployed atop an enterprise PostgreSQL 18 relational database. The frontend is built as a highly responsive Single-Page Application (SPA) leveraging modern semantic HTML5, Tailwind CSS, and vanilla ES6 JavaScript, presented within an interactive dual-view interface (a 390px mobile smartphone simulator alongside a full desktop expander).
</p>

<div class="diagram-box">
    <img src="data:image/png;base64,{fig2_1_b64}" style="max-width: 90%; height: auto;" alt="Figure 2.1: BookBazaar Black Box Architecture">
    <div class="caption">Figure 2.1: BookBazaar as a black box with its external actors and integrated services</div>
</div>

<h3>2.1.1 Operations</h3>
<ul>
    <li><strong>Client-Server Asynchrony:</strong> All frontend interactions communicate asynchronously with the backend via JSON REST endpoints protected by token-based authentication.</li>
    <li><strong>Server-Side Image Ingestion:</strong> Book photos uploaded by sellers are validated, converted, and stripped of potentially malicious metadata using the Python Pillow imaging library.</li>
    <li><strong>Transactional Integrity:</strong> Financial unlocks, in-app wallet balances, and refund events are executed within atomic database transactions (<code>transaction.atomic()</code>) to guarantee zero balance corruption.</li>
    <li><strong>Lifecycle Mediation:</strong> An internal automated state engine monitors contact unlock requests, providing a 5-day resolution window for buyers before executing automated wallet refunds.</li>
</ul>

<h3>2.1.2 Site Adaptation Requirements</h3>
<ul>
    <li><strong>Server Environment:</strong> Linux/Windows server running Python 3.12+, PostgreSQL 18.x, and a WSGI application server (Gunicorn / Waitress).</li>
    <li><strong>Configuration Management:</strong> Environment-based configuration via <code>.env</code> keeping secret keys, database credentials, and payment gateway simulation flags strictly out of version control.</li>
    <li><strong>Media & Storage:</strong> Dedicated local or object storage (AWS S3 / Cloudinary) configured with secure MIME-type checks and max 5 MB upload quotas per image.</li>
</ul>

<h2>2.2 Product Functions</h2>
<p>
BookBazaar encapsulates thirteen major functional capabilities:
</p>
<ol>
    <li><strong>FR-1: User Registration, Authentication & Profiles:</strong> Pakistani phone number format validation (<code>+923XXXXXXXXX</code>), token-based authentication, and student campus profile management.</li>
    <li><strong>FR-2: Barcode Scanning & ISBN Book Cataloging:</strong> Optical EAN-13 barcode parsing and automated bibliographic retrieval via Open Library / Google Books.</li>
    <li><strong>FR-3: Academic Search, Multi-Filter & Price Comparison:</strong> Granular filtering across boards (Punjab, Sindh, Federal, etc.), grades (9th to University), subjects, and price sorting.</li>
    <li><strong>FR-4: Used Book Listing Management:</strong> Multi-photo uploads, condition grading (New, Like New, Good, Fair), custom pricing, and active/sold toggles.</li>
    <li><strong>FR-5: Masked Seller Contact & Request Workflow:</strong> Strict data masking of seller telephone numbers and physical meeting addresses until paid unlock.</li>
    <li><strong>FR-6: Payment Gateway Integration & Simulation:</strong> Seamless sandbox support for JazzCash and Easypaisa with HMAC-SHA256 callback validation.</li>
    <li><strong>FR-7: 5-Day Deal Confirmation & In-App Wallet Refund:</strong> Deal completion confirmation workflow with automatic 100% wallet refund on failed/cancelled deals.</li>
    <li><strong>FR-8: Seller Ratings & Reviews:</strong> Post-transaction 1-to-5 star rating and comment system restricted to verified buyers.</li>
    <li><strong>FR-9: Real-Time Alerts & Notification Feed:</strong> In-app activity notifications for unlocks, deal updates, and wallet adjustments.</li>
    <li><strong>FR-10: First-Party Proprietary Advertisement Engine:</strong> Contextual banner and interstitial ad delivery with impressions and CTR tracking.</li>
    <li><strong>FR-11: Centralized Admin Dashboard & Governance:</strong> Real-time platform revenue metrics, user management, and dynamic fee configurations.</li>
    <li><strong>FR-12: Wishlist & User Favorites:</strong> One-tap bookmarking of desired books with direct price tracking.</li>
    <li><strong>FR-13: Marketplace Dispute & Violation Reporting:</strong> User reporting mechanism for damaged books, abusive behavior, or fraudulent listings.</li>
</ol>

<h2>2.3 User Characteristics</h2>
<ul>
    <li><strong>Student Buyers:</strong> High school, college, and university students seeking low-cost textbooks. High mobile usage, price-sensitive, predominantly reliant on mobile wallets (JazzCash, Easypaisa).</li>
    <li><strong>Student Sellers:</strong> Graduating or continuing students liquidating previous semester course materials. Need rapid listing creation and assurance against telephone harassment.</li>
    <li><strong>Campus Bookshops:</strong> Local book stall operators near university campuses seeking digital visibility without hefty e-commerce transaction fees.</li>
    <li><strong>Platform Administrators:</strong> Academic coordinators or system administrators overseeing platform safety, verifying reported listings, and managing fee parameters.</li>
</ul>

<h2>2.4 General Constraints</h2>
<ul>
    <li><strong>Privacy by Design:</strong> Direct seller telephone numbers and meeting addresses shall never be exposed in public search results or API payloads prior to a verified payment transaction.</li>
    <li><strong>Financial Regulation:</strong> Live transaction processing requires State Bank of Pakistan (SBP) merchant onboarding; the current system operates under a compliant sandbox simulation architecture with production-grade HMAC verification.</li>
    <li><strong>Zero In-App Delivery:</strong> BookBazaar deliberately acts as an introductory facilitator; it does not operate courier networks or hold physical book inventory. Physical book exchange occurs on campus between students.</li>
    <li><strong>Single-Listing Integrity:</strong> A buyer cannot pay for multiple active unlock requests against the exact same listing, preventing double-charging.</li>
</ul>

<h2>2.5 Assumptions and Dependencies</h2>
<ul>
    <li>Users possess a smartphone or modern web browser with JavaScript enabled.</li>
    <li>Mobile camera or web camera hardware is available for barcode scanning; manual ISBN entry serves as universal fallback.</li>
    <li>External book cataloging APIs (Open Library, Google Books) maintain reasonable uptime for automated metadata population.</li>
    <li>Pakistani curriculum structures adhere to recognized provincial education boards and Higher Education Commission (HEC) standards.</li>
</ul>

<!-- Section 3 -->
<div style="page-break-before: always;"></div>
<h1>3. SPECIFIC REQUIREMENTS</h1>

<h2>3.1 External Interface Requirements</h2>

<h3>3.1.1 System Interfaces</h3>
<ul>
    <li><strong>PostgreSQL 18 Database:</strong> Structured relational database for transactional integrity, foreign key constraints, and concurrent row-level locking.</li>
    <li><strong>Bibliographic APIs:</strong> Open Library REST API and Google Books API for automated book title, author, and edition resolution via ISBN.</li>
    <li><strong>Payment Gateways (Simulated):</strong> JazzCash Sandbox API (HTTP POST callback with HMAC-SHA256 signature) and Easypaisa Direct Merchant API.</li>
</ul>

<h3>3.1.2 User Interfaces</h3>
<p>
The user interface is structured around a responsive Mobile Web SPA design paradigm:
</p>
<ul>
    <li><strong>Dual-Screen Evaluation Frame:</strong> A responsive smartphone simulator frame (390px width) equipped with an instant toggle switch to expand into a widescreen desktop layout.</li>
    <li><strong>Bottom Navigation Dock:</strong> Five core touch points: Home (Discovery Feed), Search (Academic Filters), Sell (Listing Creation), Wishlist (Favorites), and Profile (Wallet & Unlocks).</li>
    <li><strong>Interactive Modals:</strong> Dedicated modal dialogs for camera barcode scanning, payment selection (JazzCash/Easypaisa/Wallet), deal status confirmation, and dispute filing.</li>
    <li><strong>Admin Web Dashboard:</strong> Professional data tables, metric cards (Total Revenue, Active Users, Unlocks), and control switches.</li>
</ul>

<h3>3.1.3 Hardware Interfaces</h3>
<ul>
    <li>Standard rear-facing mobile camera or computer webcam for reading EAN-13 barcodes.</li>
    <li>Client hardware minimum: 1 GHz CPU, 2 GB RAM, color display supporting 360x640 resolution or higher.</li>
</ul>

<h3>3.1.4 Software Interfaces</h3>
<ul>
    <li><strong>Client Browsers:</strong> Google Chrome (v110+), Mozilla Firefox (v115+), Apple Safari (v16+), Microsoft Edge (v110+).</li>
    <li><strong>Backend Runtime:</strong> Python 3.12+, Django 5.1, Django REST Framework 3.15, Pillow 10.x, psycopg3 database driver.</li>
</ul>

<h3>3.1.5 Communications Interfaces</h3>
<ul>
    <li>All client-server data transfer occurs over HTTPS utilizing TLS 1.2 / TLS 1.3 encryption.</li>
    <li>Payload formats strictly adhere to <code>application/json</code> with UTF-8 character encoding.</li>
    <li>Authentication tokens are passed via the standard HTTP header: <code>Authorization: Token &lt;token_key&gt;</code>.</li>
</ul>

<h2>3.2 Functional Requirements</h2>

<h3>FR-1: User Registration, Authentication & Profiles</h3>
<p><strong>Description:</strong> The system shall allow users to register, log in, and manage their academic profile.</p>
<ul>
    <li><strong>Inputs:</strong> Mobile number (validated for Pakistan: <code>+923XXXXXXXXX</code> or <code>03XXXXXXXXX</code>), password, full name, city, university/college name.</li>
    <li><strong>Processing:</strong> Verify unique phone number; hash password with PBKDF2; issue DRF auth token upon successful login. Support evaluation OTP login mode for rapid grading without live SMS dependencies.</li>
    <li><strong>Outputs:</strong> Authentication token, user profile data, initial internal wallet balance (Rs. 0.00 PKR).</li>
</ul>

<h3>FR-2: Barcode Scanning & Multi-Tier Catalog Lookup</h3>
<p><strong>Description:</strong> The system shall parse book barcodes and automatically populate book metadata.</p>
<ul>
    <li><strong>Inputs:</strong> Barcode image stream or 10/13-digit ISBN string.</li>
    <li><strong>Processing:</strong> Query internal PostgreSQL database first; if absent, query Open Library and Google Books APIs; parse title, author, edition, and standard cover image; cache in database.</li>
    <li><strong>Outputs:</strong> Canonical Book record displaying title, author, publisher, and existing marketplace seller offers.</li>
</ul>

<h3>FR-3: Search, Curriculum Board Filtering & Multi-Seller Comparison</h3>
<p><strong>Description:</strong> The system shall provide structured academic search and multi-seller price comparisons.</p>
<ul>
    <li><strong>Inputs:</strong> Search keyword, Board filter (Punjab, Federal, Sindh, KPK, Cambridge, HEC), Class filter (Class 9-12, Bachelors, Masters), Subject filter, City filter.</li>
    <li><strong>Processing:</strong> Filter listings matching active criteria; aggregate multiple sellers offering the same book title; sort listings by price ascending (cheapest offer first).</li>
    <li><strong>Outputs:</strong> Paginated listing feed with thumbnail, condition badge, price in PKR, and seller campus location.</li>
</ul>

<h3>FR-4: Book Listing Creation & Seller Inventory Management</h3>
<p><strong>Description:</strong> The system shall permit authenticated users to post used books for sale.</p>
<ul>
    <li><strong>Inputs:</strong> Book selection/creation, condition (New, Like New, Good, Fair), asking price (PKR), physical photo upload, campus pickup point.</li>
    <li><strong>Processing:</strong> Server-side image sanitization via Pillow (MIME check, resize, EXIF stripping); record creation in <code>Listing</code> table; status set to <code>active</code>.</li>
    <li><strong>Outputs:</strong> Published listing visible in marketplace search and in the user's "My Listings" tab.</li>
</ul>

<h3>FR-5: Contact Unlock & Privacy Protection (Rs. 50 Fee)</h3>
<p><strong>Description:</strong> The system shall conceal seller contact information until a buyer pays the unlock fee.</p>
<ul>
    <li><strong>Inputs:</strong> Buyer user ID, target listing ID.</li>
    <li><strong>Processing:</strong> Verify buyer is not the seller; check if active unlock already exists (prevent duplicate charging); create <code>ContactUnlock</code> record with <code>deal_status = unlocked_pending</code>.</li>
    <li><strong>Outputs:</strong> Unmasked seller phone number and campus pickup address; WhatsApp direct-chat launch button.</li>
</ul>

<h3>FR-6: Secure Local Payment Gateway Integration</h3>
<p><strong>Description:</strong> The system shall support payment for contact unlocks via simulated local gateways or wallet.</p>
<ul>
    <li><strong>Inputs:</strong> Payment method (JazzCash, Easypaisa, Internal Wallet), unlock amount (Rs. 50 PKR).</li>
    <li><strong>Processing:</strong> If wallet balance &ge; Rs. 50, deduct immediately in atomic transaction. If external gateway, generate signed payload; receive server callback; verify HMAC-SHA256 signature; mark <code>PaymentTransaction</code> as <code>completed</code>.</li>
    <li><strong>Outputs:</strong> Payment confirmation receipt; trigger contact unlock state.</li>
</ul>

<h3>FR-7: Deal Confirmation, In-App Wallet Refund & Dispute Mediation</h3>
<p><strong>Description:</strong> The system shall track the outcome of unlocked listings and refund fees if deals fail.</p>
<ul>
    <li><strong>Inputs:</strong> Buyer confirmation response: "Deal Made" or "No Deal / Cancelled".</li>
    <li><strong>Processing:</strong> If "Deal Made", set <code>deal_status = deal_made</code> (platform keeps Rs. 50). If "No Deal", set <code>deal_status = no_deal_refunded</code> and atomically credit Rs. 50 PKR to buyer's <code>UserProfile.wallet_balance</code>. Prevent duplicate refunds via strict status guards. If 5 days elapse without response, system auto-refunds.</li>
    <li><strong>Outputs:</strong> Updated unlock record, updated wallet balance, transaction ledger entry.</li>
</ul>

<h3>FR-8: Seller Ratings and Reviews</h3>
<p><strong>Description:</strong> The system shall allow buyers to rate and review sellers following a contact unlock.</p>
<ul>
    <li><strong>Inputs:</strong> Seller ID, rating integer (1 to 5 stars), written review text.</li>
    <li><strong>Processing:</strong> Verify reviewer has an unlocked contact record with the seller; persist review; recompute seller's average rating.</li>
    <li><strong>Outputs:</strong> Published review displayed on seller profile and listing detail view.</li>
</ul>

<h3>FR-9: In-App Activity & Transaction Status Updates</h3>
<p><strong>Description:</strong> The system shall alert users to key transaction events.</p>
<ul>
    <li><strong>Inputs:</strong> System trigger (Contact Unlocked, Deal Confirmed, Refund Credited, Listing Sold).</li>
    <li><strong>Processing:</strong> Generate contextual notification message; associate with recipient user profile.</li>
    <li><strong>Outputs:</strong> In-app notification badge and activity feed list.</li>
</ul>

<h3>FR-10: First-Party Proprietary Advertisement Engine</h3>
<p><strong>Description:</strong> The system shall serve relevant academic advertisements without third-party tracking.</p>
<ul>
    <li><strong>Inputs:</strong> Ad placement request (Home Banner, Search Interstitial, Listing Sidebar).</li>
    <li><strong>Processing:</strong> Query active <code>Advertisement</code> records where <code>is_active = True</code> and current date is within date range; increment impression counter; track clicks.</li>
    <li><strong>Outputs:</strong> Formatted banner with target advertiser URL and high-resolution creative.</li>
</ul>

<h3>FR-11: Centralized Admin Dashboard & Governance</h3>
<p><strong>Description:</strong> The system shall provide administrators with platform control and oversight.</p>
<ul>
    <li><strong>Inputs:</strong> Admin credentials, moderation decisions, configuration values (Unlock Fee, Auto-Refund Days).</li>
    <li><strong>Processing:</strong> Display aggregated metrics (Gross Unlock Revenue, Active Listings, Completed Deals); allow user suspension; update <code>PlatformSetting</code>.</li>
    <li><strong>Outputs:</strong> Real-time analytical dashboard and persistent platform configuration.</li>
</ul>

<h3>FR-12: Wishlist & User Favorites</h3>
<p><strong>Description:</strong> The system shall permit users to save listings for later reference.</p>
<ul>
    <li><strong>Inputs:</strong> User ID, Listing ID.</li>
    <li><strong>Processing:</strong> Create or toggle record in <code>Favorite</code> table; verify uniqueness.</li>
    <li><strong>Outputs:</strong> Persistent "Wishlist" view filtered by active availability.</li>
</ul>

<h3>FR-13: Marketplace Safety & Listing/User Violation Reports</h3>
<p><strong>Description:</strong> The system shall provide a reporting mechanism for fraudulent or abusive listings.</p>
<ul>
    <li><strong>Inputs:</strong> Reporter User ID, Target Listing/User ID, Reason (Counterfeit, Wrong Edition, Unresponsive Seller, Abusive Content), description text.</li>
    <li><strong>Processing:</strong> Store in <code>MarketplaceReport</code>; queue for admin review; flag listings with &gt; 3 reports for automatic review.</li>
    <li><strong>Outputs:</strong> Confirmation ticket to user; actionable queue in Admin Panel.</li>
</ul>

<!-- Section 3.3 Use Cases -->
<div style="page-break-before: always;"></div>
<h2>3.3 Use Cases</h2>

<div class="diagram-box">
    <img src="data:image/png;base64,{fig3_1_b64}" style="max-width: 85%; height: auto;" alt="Figure 3.1: Use Case Diagram">
    <div class="caption">Figure 3.1: BookBazaar system use case diagram illustrating primary student and administrator interactions</div>
</div>

<h3>Use Case Specifications</h3>

<h4>UC-1: User Registration and DRF Token Authentication</h4>
<table>
    <tr><th style="width: 25%;">Use Case ID</th><td>UC-1</td></tr>
    <tr><th>Use Case Name</th><td>Register / Authenticate User</td></tr>
    <tr><th>Primary Actor</th><td>Student (Buyer / Seller)</td></tr>
    <tr><th>Preconditions</th><td>User has network access and a valid Pakistani mobile number.</td></tr>
    <tr><th>Main Flow</th><td>
        1. User opens BookBazaar and selects Login / Register.<br>
        2. User enters phone number, password, full name, city, and university.<br>
        3. System validates format (<code>+923XXXXXXXXX</code>) and ensures unique mobile number.<br>
        4. System hashes password using PBKDF2 and creates <code>UserProfile</code>.<br>
        5. System generates and returns a DRF Token for session authorization.
    </td></tr>
    <tr><th>Postconditions</th><td>User is authenticated; token is stored locally; user navigation reflects authenticated state.</td></tr>
    <tr><th>Exceptions</th><td>Phone number already registered &rarr; System displays "Account already exists, please login".</td></tr>
</table>

<h4>UC-2: Scan / Search Book and View Multi-Seller Offers</h4>
<table>
    <tr><th style="width: 25%;">Use Case ID</th><td>UC-2</td></tr>
    <tr><th>Use Case Name</th><td>Search Book & Compare Sellers</td></tr>
    <tr><th>Primary Actor</th><td>Buyer</td></tr>
    <tr><th>Preconditions</th><td>System is online; book listings exist in the database.</td></tr>
    <tr><th>Main Flow</th><td>
        1. Buyer opens Search tab and either scans barcode or enters keywords/ISBN.<br>
        2. System queries catalog and returns canonical book details.<br>
        3. System aggregates all active seller listings for that book.<br>
        4. Listings are displayed sorted by asking price (lowest to highest).<br>
        5. Buyer reviews conditions (New/Like New/Good) and campus locations.
    </td></tr>
    <tr><th>Postconditions</th><td>Buyer selects preferred listing to view details (seller contact remains masked).</td></tr>
    <tr><th>Exceptions</th><td>No matching book found &rarr; System displays empty state and invites user to create a listing.</td></tr>
</table>

<h4>UC-3: Create Used Book Listing with Image Upload</h4>
<table>
    <tr><th style="width: 25%;">Use Case ID</th><td>UC-3</td></tr>
    <tr><th>Use Case Name</th><td>Create Book Listing</td></tr>
    <tr><th>Primary Actor</th><td>Seller</td></tr>
    <tr><th>Preconditions</th><td>User is authenticated and has a registered profile.</td></tr>
    <tr><th>Main Flow</th><td>
        1. Seller navigates to "Sell" tab.<br>
        2. Seller selects book (via search or enters title/author/board/class).<br>
        3. Seller inputs book condition, price in PKR, and campus meeting location.<br>
        4. Seller uploads a real photo of the book cover.<br>
        5. Backend validates image via Pillow, resizes, strips EXIF, and saves record.<br>
        6. Listing becomes immediately active and searchable.
    </td></tr>
    <tr><th>Postconditions</th><td>Listing appears in marketplace search results and in seller's inventory.</td></tr>
    <tr><th>Exceptions</th><td>Image exceeds 5 MB or invalid file type &rarr; System prompts user to upload a valid image (JPEG/PNG).</td></tr>
</table>

<h4>UC-4: Unlock Seller Contact via Rs. 50 Sandbox Payment</h4>
<table>
    <tr><th style="width: 25%;">Use Case ID</th><td>UC-4</td></tr>
    <tr><th>Use Case Name</th><td>Unlock Seller Contact</td></tr>
    <tr><th>Primary Actor</th><td>Buyer</td></tr>
    <tr><th>Preconditions</th><td>Buyer is authenticated and viewing a listing owned by another user.</td></tr>
    <tr><th>Main Flow</th><td>
        1. Buyer clicks "Unlock Contact (Rs. 50)".<br>
        2. System checks if buyer already has an active unlock for this listing.<br>
        3. Payment modal opens offering: Internal Wallet, JazzCash Sandbox, Easypaisa Sandbox.<br>
        4. Buyer selects payment method and confirms.<br>
        5. Gateway callback verifies HMAC-SHA256 signature; creates <code>PaymentTransaction</code>.<br>
        6. <code>ContactUnlock</code> record created with <code>deal_status = unlocked_pending</code>.<br>
        7. Seller telephone number and campus pickup point are unmasked on screen.
    </td></tr>
    <tr><th>Postconditions</th><td>Buyer obtains unmasked contact details and a direct WhatsApp chat button.</td></tr>
    <tr><th>Exceptions</th><td>Duplicate unlock attempted &rarr; System prevents charging and displays existing contact.</td></tr>
</table>

<h4>UC-5: Deal Confirmation & 100% Wallet Refund</h4>
<table>
    <tr><th style="width: 25%;">Use Case ID</th><td>UC-5</td></tr>
    <tr><th>Use Case Name</th><td>Confirm Deal Outcome or Request Refund</td></tr>
    <tr><th>Primary Actor</th><td>Buyer / System Timer</td></tr>
    <tr><th>Preconditions</th><td>Buyer holds an active <code>ContactUnlock</code> with <code>deal_status = unlocked_pending</code>.</td></tr>
    <tr><th>Main Flow</th><td>
        1. Buyer navigates to "My Unlocks" tab within the 5-day resolution window.<br>
        2. Case A (Deal Made): Buyer clicks "Deal Completed". System updates <code>deal_status = deal_made</code>. Platform retains the Rs. 50 facilitation fee.<br>
        3. Case B (No Deal): Buyer clicks "No Deal / Cancelled". System updates <code>deal_status = no_deal_refunded</code> and atomically credits Rs. 50.00 PKR back to buyer's <code>wallet_balance</code>.<br>
        4. Case C (Timeout): If 5 days elapse without input, background system automatically triggers Case B (full refund).
    </td></tr>
    <tr><th>Postconditions</th><td>Unlock record is permanently closed; wallet balance is updated; duplicate refunds strictly blocked.</td></tr>
    <tr><th>Exceptions</th><td>Buyer attempts refund on already-refunded record &rarr; Request rejected by database status check.</td></tr>
</table>

<!-- Section 3.4 Classes & Objects -->
<div style="page-break-before: always;"></div>
<h2>3.4 Classes and Objects (Data Model Mapping)</h2>
<p>
The object architecture of BookBazaar directly maps to ten production Django ORM models residing in the PostgreSQL 18 database:
</p>

<table>
    <tr><th>Class / Model</th><th>Key Attributes</th><th>Primary Methods / Operations</th></tr>
    <tr>
        <td><strong>UserProfile</strong></td>
        <td><code>user</code> (OneToOne User), <code>mobile_number</code>, <code>city</code>, <code>university</code>, <code>wallet_balance</code>, <code>is_verified</code>, <code>rating_avg</code></td>
        <td><code>deposit_wallet()</code>, <code>deduct_wallet()</code>, <code>recalculate_rating()</code></td>
    </tr>
    <tr>
        <td><strong>Book</strong></td>
        <td><code>isbn</code>, <code>title</code>, <code>author</code>, <code>board</code>, <code>class_level</code>, <code>subject</code>, <code>edition</code>, <code>cover_image_url</code></td>
        <td><code>get_active_listings()</code>, <code>lowest_price()</code>, <code>fetch_external_metadata()</code></td>
    </tr>
    <tr>
        <td><strong>Listing</strong></td>
        <td><code>book</code> (FK), <code>seller</code> (FK), <code>condition</code>, <code>price</code>, <code>pickup_location</code>, <code>image</code>, <code>status</code>, <code>created_at</code></td>
        <td><code>mark_as_sold()</code>, <code>toggle_active()</code>, <code>is_available()</code></td>
    </tr>
    <tr>
        <td><strong>ContactUnlock</strong></td>
        <td><code>buyer</code> (FK), <code>listing</code> (FK), <code>fee_amount</code>, <code>deal_status</code>, <code>unlocked_at</code>, <code>expires_at</code></td>
        <td><code>confirm_deal()</code>, <code>process_refund()</code>, <code>is_expired()</code></td>
    </tr>
    <tr>
        <td><strong>PaymentTransaction</strong></td>
        <td><code>unlock</code> (FK), <code>gateway</code>, <code>transaction_id</code>, <code>amount</code>, <code>status</code>, <code>signature</code>, <code>created_at</code></td>
        <td><code>verify_signature()</code>, <code>mark_completed()</code>, <code>record_failure()</code></td>
    </tr>
    <tr>
        <td><strong>SellerReview</strong></td>
        <td><code>seller</code> (FK), <code>buyer</code> (FK), <code>rating</code> (1-5), <code>comment</code>, <code>created_at</code></td>
        <td><code>validate_buyer_eligible()</code>, <code>update_seller_avg()</code></td>
    </tr>
    <tr>
        <td><strong>Advertisement</strong></td>
        <td><code>title</code>, <code>image</code>, <code>target_url</code>, <code>placement</code>, <code>is_active</code>, <code>impressions_count</code>, <code>clicks_count</code></td>
        <td><code>record_impression()</code>, <code>record_click()</code>, <code>calculate_ctr()</code></td>
    </tr>
    <tr>
        <td><strong>PlatformSetting</strong></td>
        <td><code>unlock_fee</code>, <code>auto_refund_days</code>, <code>jazzcash_sandbox</code>, <code>easypaisa_sandbox</code>, <code>maintenance_mode</code></td>
        <td><code>get_active_fee()</code>, <code>get_refund_window()</code></td>
    </tr>
    <tr>
        <td><strong>MarketplaceReport</strong></td>
        <td><code>reporter</code> (FK), <code>listing</code> (FK), <code>reported_user</code> (FK), <code>reason</code>, <code>description</code>, <code>is_resolved</code></td>
        <td><code>mark_resolved()</code>, <code>escalate_to_admin()</code></td>
    </tr>
    <tr>
        <td><strong>Favorite</strong></td>
        <td><code>user</code> (FK), <code>listing</code> (FK), <code>created_at</code></td>
        <td><code>toggle_favorite()</code></td>
    </tr>
</table>

<h2>3.5 Non-Functional Requirements</h2>

<h3>3.5.1 Performance</h3>
<ul>
    <li><strong>NFR-P1 (Scan Latency):</strong> Barcode lookup shall return matching book metadata and seller offers within 1.5 seconds under normal 4G / broadband network conditions.</li>
    <li><strong>NFR-P2 (Search Query Time):</strong> Complex multi-criteria database queries (filtering across Board, Grade, Subject, and City) shall execute in under 300 ms on PostgreSQL 18.</li>
    <li><strong>NFR-P3 (Concurrent Capacity):</strong> The backend architecture shall support at least 250 concurrent authenticated student sessions without degradation of response times.</li>
    <li><strong>NFR-P4 (Client Footprint):</strong> The responsive SPA client shall have a total uncompressed asset payload under 1.8 MB to guarantee instant loading on mid-range smartphones.</li>
</ul>

<h3>3.5.2 Reliability & Financial Integrity</h3>
<ul>
    <li><strong>NFR-R1 (Zero Lost Funds):</strong> Every contact unlock and wallet adjustment shall occur within atomic database transactions with an immutable audit log.</li>
    <li><strong>NFR-R2 (Duplicate Prevention):</strong> The system shall enforce database-level unique constraints and state guards preventing duplicate charges or multiple refunds on the same unlock.</li>
    <li><strong>NFR-R3 (Fault Tolerance):</strong> If an external metadata API (Google Books / Open Library) times out or fails, the system shall seamlessly degrade to manual text entry.</li>
</ul>

<h3>3.5.3 Security</h3>
<ul>
    <li><strong>NFR-S1 (Data Privacy):</strong> Seller contact telephone numbers and specific pickup addresses shall be redacted from public API outputs and visible only after a verified unlock transaction.</li>
    <li><strong>NFR-S2 (Authentication):</strong> API authentication shall utilize DRF Tokens passed via secure HTTP headers. Passwords shall be hashed using PBKDF2 with SHA-256.</li>
    <li><strong>NFR-S3 (Signature Verification):</strong> All payment gateway callbacks shall be validated server-side using HMAC-SHA256 signature verification prior to updating transaction status.</li>
    <li><strong>NFR-S4 (Image Sanitization):</strong> User-submitted photos shall undergo strict MIME validation, re-encoding, and EXIF geolocation stripping via Pillow to prevent file inclusion or privacy leakage.</li>
    <li><strong>NFR-S5 (OWASP Compliance):</strong> The platform shall incorporate native protection against CSRF, SQL Injection (via Django ORM parameterized queries), and XSS.</li>
</ul>

<h3>3.5.4 Maintainability & Extensibility</h3>
<ul>
    <li><strong>NFR-M1 (Modular Decoupling):</strong> The Django backend shall strictly decouple business logic into distinct apps/modules (catalog, marketplace, payments, advertising, administration).</li>
    <li><strong>NFR-M2 (Dynamic Configuration):</strong> Fee amounts and refund duration policies shall be modifiable in real-time via <code>PlatformSetting</code> without modifying code.</li>
    <li><strong>NFR-M3 (API Versioning):</strong> All endpoints shall be prefixed with <code>/api/</code> to accommodate seamless future client migrations (such as the Phase 6 Flutter app).</li>
</ul>

<h3>3.5.5 Portability & Responsiveness</h3>
<ul>
    <li><strong>NFR-PO1 (Responsive Layout):</strong> The web application shall provide an optimized user experience across mobile displays (360px - 430px viewport width) and standard desktop displays.</li>
    <li><strong>NFR-PO2 (Cross-Browser Compatibility):</strong> The application shall render consistently across Google Chrome, Apple Safari, Mozilla Firefox, and Microsoft Edge.</li>
</ul>

<h2>3.6 Inverse Requirements</h2>
<p>
To prevent scope creep and maintain strict legal and architectural boundaries, BookBazaar explicitly <strong>shall not</strong>:
</p>
<ul>
    <li>The system <strong>shall not</strong> sell books directly or hold physical inventory; it is exclusively a peer-to-peer facilitator.</li>
    <li>The system <strong>shall not</strong> handle physical delivery, courier shipping, or in-person cash collection.</li>
    <li>The system <strong>shall not</strong> expose seller contact phone numbers in public search or unauthenticated API responses.</li>
    <li>The system <strong>shall not</strong> store raw credit card numbers, bank PINs, or mobile wallet MPINs.</li>
    <li>The system <strong>shall not</strong> charge duplicate fees for an already unlocked listing.</li>
    <li>The system <strong>shall not</strong> allow sellers to buy or unlock contact info for their own listings.</li>
</ul>

<h2>3.7 Logical Database Requirements</h2>
<p>
The database layer is implemented on PostgreSQL 18. All primary keys utilize 64-bit auto-incrementing integers or UUIDs, with foreign keys enforcing relational integrity and indexed search columns.
</p>

<div class="diagram-box">
    <img src="data:image/png;base64,{fig3_2_b64}" style="max-width: 90%; height: auto;" alt="Figure 3.2: Entity Relationship Diagram">
    <div class="caption">Figure 3.2: Entity Relationship Diagram illustrating the 10 production tables and relational cardinalities</div>
</div>

<h2>3.8 Design Constraints and Standards Compliance</h2>
<ul>
    <li><strong>Language & Code Style:</strong> Python code adheres to PEP 8 style standards; JavaScript adheres to ECMAScript 2022 standards.</li>
    <li><strong>ISBN Standard:</strong> Book cataloging conforms strictly to ISO 2108 (EAN-13 / ISBN-10 checksum algorithms).</li>
    <li><strong>REST Conventions:</strong> API endpoints utilize standard HTTP methods (GET, POST, PUT, DELETE) and conventional HTTP status codes (200, 201, 400, 401, 403, 404, 500).</li>
    <li><strong>Financial Audit Trail:</strong> Every rupee credited or debited to user wallets is tracked with timestamps, transaction IDs, and associated unlock IDs.</li>
</ul>

<!-- Section 4 -->
<div style="page-break-before: always;"></div>
<h1>4. ANALYSIS MODELS</h1>

<h2>4.1 Sequence Diagrams</h2>
<p>
The following sequence diagram models the core transaction lifecycle: from contact unlock initiation, through payment verification, contact unmasking, deal resolution, and the in-app wallet refund workflow.
</p>

<div class="diagram-box">
    <img src="data:image/png;base64,{fig4_1_b64}" style="max-width: 90%; height: auto;" alt="Figure 4.1: Sequence Diagram for Contact Unlock and Refund">
    <div class="caption">Figure 4.1: Sequence diagram for contact unlock, gateway payment, deal confirmation, and wallet refund</div>
</div>

<h2>4.2 Data Flow Diagrams (DFD)</h2>
<p>
The Level-0 Context DFD visualizes the data boundaries between primary student actors, external payment/catalog services, and the centralized BookBazaar processing core.
</p>

<div class="diagram-box">
    <img src="data:image/png;base64,{fig4_2_b64}" style="max-width: 90%; height: auto;" alt="Figure 4.2: Level-0 Data Flow Diagram">
    <div class="caption">Figure 4.2: Level-0 Data Flow Diagram illustrating external entity interactions and core processing pipelines</div>
</div>

<h2>4.3 State-Transition Diagrams (STD)</h2>
<p>
The state machine below defines the exact states through which a <code>ContactUnlock</code> record transitions during its lifecycle.
</p>

<div class="diagram-box">
    <img src="data:image/png;base64,{fig4_3_b64}" style="max-width: 85%; height: auto;" alt="Figure 4.3: State-Transition Diagram of a Contact Request">
    <div class="caption">Figure 4.3: State-Transition Diagram illustrating the Contact Unlock record lifecycle from initiation to deal resolution or refund</div>
</div>

<!-- Section 5 -->
<div style="page-break-before: always;"></div>
<h1>5. SUPPORTING INFORMATION</h1>

<h2>Appendix A – Background Research on Pakistani Used Book Trade</h2>
<p>
Textbook inflation in Pakistan has escalated by over 140% across recent academic years due to rising paper pulp import costs, local currency devaluation, and publisher price revisions. At universities such as The Islamia University of Bahawalpur (IUB) and colleges nationwide, students frequently struggle to afford mandatory reference materials.
</p>
<p>
Informal second-hand book markets (such as Urdu Bazaar in Lahore, Rawalpindi, and Karachi, as well as local bookstalls in Bahawalpur) suffer from severe limitations:
</p>
<ul>
    <li><strong>Information Asymmetry:</strong> No transparent price indexing; bookstall vendors purchase books from graduating students at 15–20% of retail price and resell them at 65–80%, extracting heavy margins.</li>
    <li><strong>Geographic & Time Inefficiency:</strong> Students must physically travel to dense bazaars, searching stall by stall to locate specific textbook editions or course codes.</li>
    <li><strong>Harassment & Privacy Barriers:</strong> Female students frequently avoid posting phone numbers on public classifieds (such as OLX or social media groups) due to unsolicited calls and privacy violations.</li>
</ul>
<p>
BookBazaar solves each of these challenges through localized curriculum filtering, transparent multi-seller price comparisons, privacy-preserving contact masking, and a low-friction Rs. 50 facilitation fee with an ironclad 100% wallet refund guarantee.
</p>

<h2>Appendix B – Complete Data Dictionary</h2>
<p>
Below is the comprehensive data dictionary detailing all fields, data types, constraints, and descriptions across the ten PostgreSQL database tables:
</p>

<h3>Table 1: UserProfile</h3>
<table>
    <tr><th>Field Name</th><th>Data Type</th><th>Constraints</th><th>Description</th></tr>
    <tr><td><code>id</code></td><td>BigAutoField</td><td>Primary Key</td><td>Unique user profile record identifier.</td></tr>
    <tr><td><code>user_id</code></td><td>OneToOneField</td><td>ForeignKey &rarr; auth_user</td><td>Reference to standard Django auth user.</td></tr>
    <tr><td><code>mobile_number</code></td><td>CharField(15)</td><td>Unique, Not Null</td><td>Pakistani format phone (e.g., +923001234567).</td></tr>
    <tr><td><code>city</code></td><td>CharField(50)</td><td>Not Null</td><td>User's residential city (e.g., Bahawalpur).</td></tr>
    <tr><td><code>university</code></td><td>CharField(100)</td><td>Nullable</td><td>Enrolled university/college (e.g., IUB).</td></tr>
    <tr><td><code>wallet_balance</code></td><td>DecimalField(10,2)</td><td>Default 0.00, &ge; 0</td><td>Internal wallet balance for platform refunds.</td></tr>
    <tr><td><code>is_verified</code></td><td>BooleanField</td><td>Default False</td><td>Phone/student identity verification flag.</td></tr>
    <tr><td><code>rating_avg</code></td><td>DecimalField(3,2)</td><td>Default 0.00</td><td>Running average rating as seller (1.00 - 5.00).</td></tr>
    <tr><td><code>created_at</code></td><td>DateTimeField</td><td>Auto Now Add</td><td>Timestamp of account creation.</td></tr>
</table>

<h3>Table 2: Book</h3>
<table>
    <tr><th>Field Name</th><th>Data Type</th><th>Constraints</th><th>Description</th></tr>
    <tr><td><code>id</code></td><td>BigAutoField</td><td>Primary Key</td><td>Unique canonical book catalog identifier.</td></tr>
    <tr><td><code>isbn</code></td><td>CharField(20)</td><td>Index, Nullable</td><td>Cleaned ISBN-10 or ISBN-13 identifier.</td></tr>
    <tr><td><code>title</code></td><td>CharField(255)</td><td>Not Null, Index</td><td>Full book title.</td></tr>
    <tr><td><code>author</code></td><td>CharField(255)</td><td>Not Null</td><td>Primary author(s) or editor(s).</td></tr>
    <tr><td><code>board</code></td><td>CharField(50)</td><td>Nullable, Index</td><td>Academic curriculum board (e.g., Punjab Board).</td></tr>
    <tr><td><code>class_level</code></td><td>CharField(50)</td><td>Nullable, Index</td><td>Target grade/level (e.g., Class 10, BS SE).</td></tr>
    <tr><td><code>subject</code></td><td>CharField(100)</td><td>Nullable</td><td>Subject matter (e.g., Computer Science).</td></tr>
    <tr><td><code>edition</code></td><td>CharField(50)</td><td>Nullable</td><td>Book edition (e.g., 5th Edition).</td></tr>
    <tr><td><code>cover_image_url</code></td><td>URLField</td><td>Nullable</td><td>External or standard book cover thumbnail.</td></tr>
</table>

<h3>Table 3: Listing</h3>
<table>
    <tr><th>Field Name</th><th>Data Type</th><th>Constraints</th><th>Description</th></tr>
    <tr><td><code>id</code></td><td>BigAutoField</td><td>Primary Key</td><td>Unique used book listing identifier.</td></tr>
    <tr><td><code>book_id</code></td><td>ForeignKey</td><td>&rarr; Book, CASCADE</td><td>Reference to catalog book entity.</td></tr>
    <tr><td><code>seller_id</code></td><td>ForeignKey</td><td>&rarr; User, CASCADE</td><td>Reference to seller user account.</td></tr>
    <tr><td><code>condition</code></td><td>CharField(20)</td><td>Choices</td><td>Condition: New, Like New, Good, Fair.</td></tr>
    <tr><td><code>price</code></td><td>DecimalField(10,2)</td><td>Not Null, &gt; 0</td><td>Seller's asking price in PKR.</td></tr>
    <tr><td><code>pickup_location</code></td><td>CharField(255)</td><td>Not Null</td><td>Campus pickup meeting spot (masked to public).</td></tr>
    <tr><td><code>image</code></td><td>ImageField</td><td>Nullable</td><td>Uploaded book photograph (Pillow processed).</td></tr>
    <tr><td><code>status</code></td><td>CharField(20)</td><td>Default 'active'</td><td>Choices: active, reserved, sold, deleted.</td></tr>
    <tr><td><code>created_at</code></td><td>DateTimeField</td><td>Auto Now Add</td><td>Timestamp listing was published.</td></tr>
</table>

<h3>Table 4: ContactUnlock</h3>
<table>
    <tr><th>Field Name</th><th>Data Type</th><th>Constraints</th><th>Description</th></tr>
    <tr><td><code>id</code></td><td>BigAutoField</td><td>Primary Key</td><td>Unique contact unlock record identifier.</td></tr>
    <tr><td><code>buyer_id</code></td><td>ForeignKey</td><td>&rarr; User, CASCADE</td><td>Student who paid the unlock fee.</td></tr>
    <tr><td><code>listing_id</code></td><td>ForeignKey</td><td>&rarr; Listing, CASCADE</td><td>Listing whose contact was unlocked.</td></tr>
    <tr><td><code>fee_amount</code></td><td>DecimalField(10,2)</td><td>Default 50.00</td><td>Facilitation fee charged (Rs. 50 PKR).</td></tr>
    <tr><td><code>deal_status</code></td><td>CharField(25)</td><td>Default 'unlocked_pending'</td><td>Choices: unlocked_pending, deal_made, no_deal_refunded.</td></tr>
    <tr><td><code>unlocked_at</code></td><td>DateTimeField</td><td>Auto Now Add</td><td>Timestamp of contact unmasking.</td></tr>
    <tr><td><code>expires_at</code></td><td>DateTimeField</td><td>Not Null</td><td>Deal confirmation expiry (default +5 days).</td></tr>
</table>

<h3>Table 5: PaymentTransaction</h3>
<table>
    <tr><th>Field Name</th><th>Data Type</th><th>Constraints</th><th>Description</th></tr>
    <tr><td><code>id</code></td><td>BigAutoField</td><td>Primary Key</td><td>Unique payment ledger record identifier.</td></tr>
    <tr><td><code>unlock_id</code></td><td>ForeignKey</td><td>&rarr; ContactUnlock</td><td>Associated contact unlock operation.</td></tr>
    <tr><td><code>gateway</code></td><td>CharField(20)</td><td>Choices</td><td>JazzCash, Easypaisa, Wallet.</td></tr>
    <tr><td><code>transaction_id</code></td><td>CharField(100)</td><td>Unique, Index</td><td>Gateway reference or internal UUID.</td></tr>
    <tr><td><code>amount</code></td><td>DecimalField(10,2)</td><td>Not Null</td><td>Transaction amount (Rs. 50.00 PKR).</td></tr>
    <tr><td><code>status</code></td><td>CharField(20)</td><td>Default 'completed'</td><td>completed, failed, refunded.</td></tr>
    <tr><td><code>signature</code></td><td>CharField(255)</td><td>Nullable</td><td>HMAC-SHA256 callback verification hash.</td></tr>
    <tr><td><code>created_at</code></td><td>DateTimeField</td><td>Auto Now Add</td><td>Timestamp transaction occurred.</td></tr>
</table>

<h3>Table 6: SellerReview</h3>
<table>
    <tr><th>Field Name</th><th>Data Type</th><th>Constraints</th><th>Description</th></tr>
    <tr><td><code>id</code></td><td>BigAutoField</td><td>Primary Key</td><td>Unique review record identifier.</td></tr>
    <tr><td><code>seller_id</code></td><td>ForeignKey</td><td>&rarr; User, CASCADE</td><td>Seller receiving the review.</td></tr>
    <tr><td><code>buyer_id</code></td><td>ForeignKey</td><td>&rarr; User, CASCADE</td><td>Verified buyer submitting the review.</td></tr>
    <tr><td><code>rating</code></td><td>PositiveSmallIntegerField</td><td>1 to 5</td><td>Numerical score between 1 and 5 stars.</td></tr>
    <tr><td><code>comment</code></td><td>TextField</td><td>Nullable</td><td>Written feedback regarding transaction.</td></tr>
    <tr><td><code>created_at</code></td><td>DateTimeField</td><td>Auto Now Add</td><td>Timestamp review was submitted.</td></tr>
</table>

<h3>Table 7: Advertisement</h3>
<table>
    <tr><th>Field Name</th><th>Data Type</th><th>Constraints</th><th>Description</th></tr>
    <tr><td><code>id</code></td><td>BigAutoField</td><td>Primary Key</td><td>Unique ad campaign record identifier.</td></tr>
    <tr><td><code>title</code></td><td>CharField(150)</td><td>Not Null</td><td>Campaign title / advertiser name.</td></tr>
    <tr><td><code>image</code></td><td>ImageField</td><td>Not Null</td><td>Promotional creative banner graphic.</td></tr>
    <tr><td><code>target_url</code></td><td>URLField</td><td>Not Null</td><td>Destination URL upon click.</td></tr>
    <tr><td><code>placement</code></td><td>CharField(30)</td><td>Choices</td><td>home_banner, search_interstitial, sidebar.</td></tr>
    <tr><td><code>is_active</code></td><td>BooleanField</td><td>Default True</td><td>Active campaign delivery toggle.</td></tr>
    <tr><td><code>impressions_count</code></td><td>PositiveIntegerField</td><td>Default 0</td><td>Cumulative impressions served.</td></tr>
    <tr><td><code>clicks_count</code></td><td>PositiveIntegerField</td><td>Default 0</td><td>Cumulative user click-throughs recorded.</td></tr>
</table>

<h3>Table 8: PlatformSetting</h3>
<table>
    <tr><th>Field Name</th><th>Data Type</th><th>Constraints</th><th>Description</th></tr>
    <tr><td><code>id</code></td><td>BigAutoField</td><td>Primary Key</td><td>Configuration record identifier (singleton).</td></tr>
    <tr><td><code>unlock_fee</code></td><td>DecimalField(10,2)</td><td>Default 50.00</td><td>Standard contact unlock fee (Rs. PKR).</td></tr>
    <tr><td><code>auto_refund_days</code></td><td>PositiveIntegerField</td><td>Default 5</td><td>Number of days before auto-refund fires.</td></tr>
    <tr><td><code>jazzcash_sandbox</code></td><td>BooleanField</td><td>Default True</td><td>Toggle for JazzCash simulation mode.</td></tr>
    <tr><td><code>easypaisa_sandbox</code></td><td>BooleanField</td><td>Default True</td><td>Toggle for Easypaisa simulation mode.</td></tr>
    <tr><td><code>maintenance_mode</code></td><td>BooleanField</td><td>Default False</td><td>Global marketplace maintenance switch.</td></tr>
</table>

<h3>Table 9: MarketplaceReport</h3>
<table>
    <tr><th>Field Name</th><th>Data Type</th><th>Constraints</th><th>Description</th></tr>
    <tr><td><code>id</code></td><td>BigAutoField</td><td>Primary Key</td><td>Unique moderation report identifier.</td></tr>
    <tr><td><code>reporter_id</code></td><td>ForeignKey</td><td>&rarr; User, CASCADE</td><td>User who filed the report.</td></tr>
    <tr><td><code>listing_id</code></td><td>ForeignKey</td><td>Nullable, &rarr; Listing</td><td>Reported listing (if applicable).</td></tr>
    <tr><td><code>reported_user_id</code></td><td>ForeignKey</td><td>Nullable, &rarr; User</td><td>Reported user (if applicable).</td></tr>
    <tr><td><code>reason</code></td><td>CharField(50)</td><td>Choices</td><td>counterfeit, wrong_edition, harassment, other.</td></tr>
    <tr><td><code>description</code></td><td>TextField</td><td>Not Null</td><td>Detailed statement of complaint.</td></tr>
    <tr><td><code>is_resolved</code></td><td>BooleanField</td><td>Default False</td><td>Administrative resolution status flag.</td></tr>
    <tr><td><code>created_at</code></td><td>DateTimeField</td><td>Auto Now Add</td><td>Timestamp report was filed.</td></tr>
</table>

<h3>Table 10: Favorite</h3>
<table>
    <tr><th>Field Name</th><th>Data Type</th><th>Constraints</th><th>Description</th></tr>
    <tr><td><code>id</code></td><td>BigAutoField</td><td>Primary Key</td><td>Unique bookmark record identifier.</td></tr>
    <tr><td><code>user_id</code></td><td>ForeignKey</td><td>&rarr; User, CASCADE</td><td>User who saved the listing.</td></tr>
    <tr><td><code>listing_id</code></td><td>ForeignKey</td><td>&rarr; Listing, CASCADE</td><td>Listing marked as favorite.</td></tr>
    <tr><td><code>created_at</code></td><td>DateTimeField</td><td>Auto Now Add</td><td>Timestamp item was favorited.</td></tr>
</table>

<h2>Appendix C – Phase 6 Mobile App & Production Expansion Roadmap</h2>
<p>
Following successful deployment and evaluation of the current Phase 5 web platform baseline, the project roadmap establishes clear milestones for subsequent production phases:
</p>
<ul>
    <li><strong>Phase 6.1: Cross-Platform Mobile Applications:</strong> Compile native Android APK/AAB and iOS IPA applications using Google Flutter, consuming the existing hardened DRF REST API endpoints.</li>
    <li><strong>Phase 6.2: Commercial Payment Gateway Onboarding:</strong> Transition sandbox simulation endpoints to live commercial merchant contracts with Mobilink Microfinance Bank (JazzCash Corporate) and Telenor Microfinance Bank (Easypaisa Direct API), subject to SBP commercial compliance.</li>
    <li><strong>Phase 6.3: Automated Background Workers:</strong> Introduce Redis and Celery task queues for distributed background scheduling of the 5-day auto-refund timer, removing synchronous overhead from web request threads.</li>
    <li><strong>Phase 6.4: Campus Ambassador & Book Exchange Network:</strong> Establish authorized campus book exchange hubs across university faculties to facilitate zero-cost in-person book drop-offs and verifications.</li>
</ul>

</body>
</html>
"""

html_path = os.path.join(WORKSPACE, 'BookBazaar_SRS_v2.0.html')
pdf_path = os.path.join(WORKSPACE, 'BookBazaar_SRS_v2.0.pdf')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(srs_html)

print("Generated BookBazaar_SRS_v2.0.html. Rendering to PDF via Chrome...")
cmd = f'"{CHROME}" --headless=new --disable-gpu --run-all-compositor-stages-before-draw --print-to-pdf="{pdf_path}" "{html_path}"'
subprocess.run(cmd, shell=True, check=True)
print(f"BookBazaar_SRS_v2.0.pdf generated successfully! Size: {os.path.getsize(pdf_path)} bytes")
