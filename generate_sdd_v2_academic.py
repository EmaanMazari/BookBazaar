import os, base64, subprocess
from academic_styles import ACADEMIC_CSS, LOGO_B64, WORKSPACE, CHROME

sdd_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Software Design Document (SDD) - BookBazaar v2.0</title>
<style>
{ACADEMIC_CSS}
</style>
</head>
<body>

<!-- Title Page -->
<div class="title-page">
    <div class="title-doc">Software Design Document (SDD)</div>
    <div class="title-for">for</div>
    <div class="title-app">BookBazaar</div>
    <div class="title-sub">Book Scan, Buy & Sell Platform for Pakistan</div>
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
        The Islamia University, Bahawalpur
    </div>
</div>

<!-- Revision History -->
<h2>Revision History</h2>
<table>
    <tr>
        <th style="width: 15%;">Date</th>
        <th style="width: 20%;">Description</th>
        <th style="width: 25%;">Author</th>
        <th style="width: 40%;">Comments</th>
    </tr>
    <tr>
        <td>3 Nov 2026</td>
        <td>Version 1.0</td>
        <td>Emaan Mazari, Laila Akhtar</td>
        <td>First Revision (Initial Design)</td>
    </tr>
    <tr>
        <td>9 Nov 2026</td>
        <td>Version 2.0</td>
        <td>Emaan Mazari, Laila Akhtar</td>
        <td>Updated to 100% match implemented Django REST backend, PostgreSQL 18 schema, HTML5/Tailwind responsive client, DRF Token authentication, internal wallet refunds, and admin panel</td>
    </tr>
</table>

<!-- Document Approval -->
<h2>Document Approval</h2>
<p>The following Software Design Document (SDD) has been accepted and approved by the following:</p>
<table class="table-approval">
    <tr>
        <th style="width: 25%;">Signature</th>
        <th style="width: 25%;">Printed Name</th>
        <th style="width: 30%;">Title</th>
        <th style="width: 20%;">Date</th>
    </tr>
    <tr>
        <td style="height: 35pt;"></td>
        <td>Sir Gulraiz</td>
        <td>Supervisor, SENG-4301</td>
        <td>November 2026</td>
    </tr>
</table>

<!-- Table of Contents -->
<h2>Table of Contents</h2>
<table>
    <tr><td><strong>1. Introduction</strong></td><td style="text-align: right;"><strong>4</strong></td></tr>
    <tr><td>&nbsp;&nbsp;&nbsp;&nbsp;1.1. Purpose</td><td style="text-align: right;">4</td></tr>
    <tr><td>&nbsp;&nbsp;&nbsp;&nbsp;1.2. Scope</td><td style="text-align: right;">4</td></tr>
    <tr><td>&nbsp;&nbsp;&nbsp;&nbsp;1.3. Overview</td><td style="text-align: right;">4</td></tr>
    <tr><td>&nbsp;&nbsp;&nbsp;&nbsp;1.4. Reference Material</td><td style="text-align: right;">4</td></tr>
    <tr><td>&nbsp;&nbsp;&nbsp;&nbsp;1.5. Definitions and Acronyms</td><td style="text-align: right;">4</td></tr>
    <tr><td><strong>2. System Overview</strong></td><td style="text-align: right;"><strong>5</strong></td></tr>
    <tr><td><strong>3. System Architecture</strong></td><td style="text-align: right;"><strong>6</strong></td></tr>
    <tr><td>&nbsp;&nbsp;&nbsp;&nbsp;3.1. Architectural Design</td><td style="text-align: right;">6</td></tr>
    <tr><td>&nbsp;&nbsp;&nbsp;&nbsp;3.2. Decomposition Description</td><td style="text-align: right;">7</td></tr>
    <tr><td>&nbsp;&nbsp;&nbsp;&nbsp;3.3. Design Rationale</td><td style="text-align: right;">8</td></tr>
    <tr><td><strong>4. Data Design</strong></td><td style="text-align: right;"><strong>9</strong></td></tr>
    <tr><td>&nbsp;&nbsp;&nbsp;&nbsp;4.1. Data Description</td><td style="text-align: right;">9</td></tr>
    <tr><td>&nbsp;&nbsp;&nbsp;&nbsp;4.2. Data Dictionary</td><td style="text-align: right;">10</td></tr>
    <tr><td><strong>5. Component Design</strong></td><td style="text-align: right;"><strong>12</strong></td></tr>
    <tr><td><strong>6. Human Interface Design</strong></td><td style="text-align: right;"><strong>15</strong></td></tr>
    <tr><td>&nbsp;&nbsp;&nbsp;&nbsp;6.1. Overview of User Interface</td><td style="text-align: right;">15</td></tr>
    <tr><td>&nbsp;&nbsp;&nbsp;&nbsp;6.2. Screen Images</td><td style="text-align: right;">15</td></tr>
    <tr><td>&nbsp;&nbsp;&nbsp;&nbsp;6.3. Screen Objects and Actions</td><td style="text-align: right;">17</td></tr>
    <tr><td><strong>7. Requirements Matrix</strong></td><td style="text-align: right;"><strong>17</strong></td></tr>
    <tr><td><strong>8. Appendices</strong></td><td style="text-align: right;"><strong>18</strong></td></tr>
    <tr><td>&nbsp;&nbsp;&nbsp;&nbsp;Appendix A – Main REST API Endpoints</td><td style="text-align: right;">18</td></tr>
    <tr><td>&nbsp;&nbsp;&nbsp;&nbsp;Appendix B – System Settings</td><td style="text-align: right;">18</td></tr>
    <tr><td>&nbsp;&nbsp;&nbsp;&nbsp;Appendix C – Future Work</td><td style="text-align: right;">19</td></tr>
</table>

<div style="page-break-after: always;"></div>

<!-- Section 1 -->
<h1>1. INTRODUCTION</h1>

<h2>1.1. Purpose</h2>
<p>This Software Design Document (SDD) describes the architecture and system design of BookBazaar, an academic second-hand book marketplace that lets students and readers in Pakistan scan the barcode (ISBN) of a book, see verified catalog details and offers from different sellers, and unlock the seller contact by paying a small, 100% refundable contact unlock fee (Rs. 50 PKR). If the buyer and seller finalize the physical book exchange, the fee is kept by BookBazaar; if no deal is made or the book is unavailable, the fee is refunded immediately into the buyer's internal wallet balance. BookBazaar is a platform that connects buyers and sellers; sellers decide book prices and buyer and seller arrange physical inspection and handover themselves. This document serves as a guide for:</p>
<ul>
    <li><strong>Developers:</strong> to understand the modular structure of the system and maintain it correctly.</li>
    <li><strong>Testers:</strong> to prepare test plans, verify API integrity, and test state machine edge cases.</li>
    <li><strong>Stakeholders (supervisor and evaluation committee):</strong> to see how the requirements in the SRS are realized in the actual software implementation.</li>
</ul>

<h2>1.2. Scope</h2>
<p><strong>Software product:</strong> BookBazaar – an interactive Responsive Web Single-Page Application (HTML5, Tailwind CSS, Vanilla JavaScript) with an interactive smartphone mockup frame and desktop widescreen toggle, an HTML/CSS/JavaScript admin management panel, and a Django 6.1 REST backend with a PostgreSQL 18 database. (Native mobile applications using Flutter are architected as Phase 6 future work consuming the existing REST APIs).</p>
<p><strong>Goals and objectives:</strong> make academic textbooks cheaper and easier to trade in Pakistan; let a student list a book in under 60 seconds with one barcode scan; eliminate fake and uninterested contacts through a refundable contact fee; and earn platform revenue from contact fees and sponsored advertisements.</p>
<p><strong>Benefits:</strong> cheaper used textbooks for university students; fast peer-to-peer buying and selling; secure sandbox payment through trusted local mobile wallets (JazzCash, Easypaisa) in PKR; transparent in-app wallet refund rules; and complete English and Urdu language support.</p>

<h2>1.3. Overview</h2>
<p>This document follows the IEEE 1016-2009 structure and the department SDD template. Section 2 gives the system overview. Section 3 explains the architecture, decomposition and design rationale. Section 4 describes the data design and data dictionary for all 10 PostgreSQL models. Section 5 gives the component design in pseudo-code (PDL). Section 6 presents the human interface design. Section 7 gives the requirements matrix linking SRS requirements to design components, and Section 8 contains the appendices.</p>

<h2>1.4. Reference Material</h2>
<ul>
    <li>BookBazaar Software Requirement Specification (SRS), version 2.0.</li>
    <li>IEEE Std 1016-2009, Software Design Descriptions.</li>
    <li>ISO 2108, International Standard Book Number (ISBN).</li>
    <li>Google Books API and Open Library API technical documentation.</li>
    <li>JazzCash (MWALLET / HTTP Post Interface) and Easypaisa Merchant Integration Guides.</li>
    <li>Django 6.1, Django REST Framework, and PostgreSQL 18 official documentation.</li>
</ul>

<h2>1.5. Definitions and Acronyms</h2>
<table>
    <tr><th style="width: 25%;">Term</th><th style="width: 75%;">Meaning</th></tr>
    <tr><td><strong>SDD / SRS</strong></td><td>Software Design Document / Software Requirements Specification</td></tr>
    <tr><td><strong>ISBN</strong></td><td>International Standard Book Number, printed as a barcode on every book</td></tr>
    <tr><td><strong>API / REST</strong></td><td>Application Programming Interface / Representational State Transfer</td></tr>
    <tr><td><strong>Token Auth</strong></td><td>Django REST Framework database-backed token authentication (<code>Authorization: Token &lt;key&gt;</code>)</td></tr>
    <tr><td><strong>OTP</strong></td><td>One-Time Password used for evaluation and fast demo verification</td></tr>
    <tr><td><strong>PKR / Rs.</strong></td><td>Pakistani Rupee</td></tr>
    <tr><td><strong>Listing</strong></td><td>A used book offered for sale by a seller at the seller's self-chosen price</td></tr>
    <tr><td><strong>Contact Unlock Fee</strong></td><td>Fee of Rs. 50 paid by the buyer to unlock seller contact; kept if deal made, refunded if no deal</td></tr>
    <tr><td><strong>ContactUnlock</strong></td><td>Unified database record tracking contact unlock, deal confirmation, and refund state</td></tr>
    <tr><td><strong>DFD / ERD</strong></td><td>Data Flow Diagram / Entity Relationship Diagram</td></tr>
    <tr><td><strong>CRUD</strong></td><td>Create, Read, Update, Delete</td></tr>
    <tr><td><strong>SPA</strong></td><td>Single Page Application (responsive web client)</td></tr>
</table>

<!-- Section 2 -->
<h1>2. SYSTEM OVERVIEW</h1>
<p>BookBazaar is a specialized marketplace platform that makes buying and selling used academic books quick, affordable and trustworthy. A student points the phone/web camera at a book barcode, the system reads the ISBN, retrieves book metadata automatically, shows all competing seller offers sorted by price, and lets the buyer contact a seller after paying a nominal contact unlock fee (Rs. 50 PKR). The system is built for Pakistan and earns platform income from contact fees and sponsored advertisements.</p>
<ul>
    <li><strong>Platform environment:</strong> multiple sellers list books and multiple buyers search for them. Every book is identified by its ISBN-13 so that all offers for the same book are grouped together for instant price comparison.</li>
    <li><strong>Barcode scanning:</strong> the camera reads the ISBN-13, validates it, and fetches title, author, publisher, cover image, and retail price automatically using a cascading lookup sequence.</li>
    <li><strong>Selling books:</strong> the seller scans the book, chooses condition, sets the selling price, enters campus pickup location (e.g. <em>IUB Library Gate</em>), uploads a photo, and publishes.</li>
    <li><strong>Buying books:</strong> the buyer sees all offers sorted by lowest price and pays Rs. 50 to unlock the seller contact. Handover of the physical book and direct cash payment occur peer-to-peer at the agreed campus location.</li>
    <li><strong>Contact unlock, deal and refund:</strong> after contact, both users confirm in the app whether a deal was made. <em>Deal Made:</em> fee is kept by the platform. <em>No Deal:</em> fee of Rs. 50 is refunded 100% immediately into the buyer's internal BookBazaar wallet balance.</li>
    <li><strong>Login and language:</strong> login with Pakistani mobile number and password, with OTP fast switcher for evaluation; bilingual English and Urdu interface.</li>
    <li><strong>Advertisements:</strong> first-party banner, interstitial, native, and sponsored-listing ads managed by the admin from the admin dashboard.</li>
    <li><strong>Ratings and reviews:</strong> buyers rate sellers (1 to 5 stars) and write reviews after verified transactions.</li>
    <li><strong>Administration:</strong> the admin approves listings, blocks fraudulent users, resolves complaints, manages ads, and inspects real-time financial reports.</li>
    <li><strong>Security:</strong> HTTPS, DRF Token authentication, PBKDF2 password hashing, and HMAC-SHA256 signature verification for payment callbacks.</li>
</ul>

<!-- Section 3 -->
<h1>3. SYSTEM ARCHITECTURE</h1>

<h2>3.1. Architectural Design</h2>
<p>The system is divided into nine cohesive subsystems. Each has a clear responsibility, as listed below:</p>
<table>
    <tr>
        <th style="width: 5%;">No.</th>
        <th style="width: 28%;">Subsystem</th>
        <th style="width: 67%;">Responsibilities</th>
    </tr>
    <tr>
        <td>1</td>
        <td><strong>User / Authentication Module</strong></td>
        <td>Registration and login with mobile number and password; DRF Token management; profile editing; demo OTP switcher.</td>
    </tr>
    <tr>
        <td>2</td>
        <td><strong>Scanner and Catalog Module</strong></td>
        <td>Web camera barcode scanning, ISBN normalization, cascading lookup (DB &rarr; Curated Catalog &rarr; Google Books &rarr; Open Library &rarr; Manual).</td>
    </tr>
    <tr>
        <td>3</td>
        <td><strong>Buyer Module</strong></td>
        <td>Search and filter by Pakistani educational boards and classes, multi-seller price comparison, favorites wishlist, and violation reporting.</td>
    </tr>
    <tr>
        <td>4</td>
        <td><strong>Seller Module</strong></td>
        <td>Create listing from scan, set price (decided by seller), enter campus pickup location, Pillow-validated photo upload, and inventory management.</td>
    </tr>
    <tr>
        <td>5</td>
        <td><strong>Contact Unlock & Privacy Module</strong></td>
        <td>Mask seller phone numbers (<code>0301-*******</code>), initiate Rs. 50 fee payment, create atomic unlock records, and reveal contact details.</td>
    </tr>
    <tr>
        <td>6</td>
        <td><strong>Payment & Refund Module</strong></td>
        <td>Process payments via JazzCash, Easypaisa, and In-App Wallet; HMAC-SHA256 signature verification; atomic 100% refund crediting to buyer wallet.</td>
    </tr>
    <tr>
        <td>7</td>
        <td><strong>Advertisement Module</strong></td>
        <td>Deliver first-party banner, interstitial, and native ads; count impressions and clicks; ad campaign management.</td>
    </tr>
    <tr>
        <td>8</td>
        <td><strong>Notification & Activity Module</strong></td>
        <td>In-app transaction status alerts, activity counters (active listings, sold books, unlocks bought/received), and real-time deal updates.</td>
    </tr>
    <tr>
        <td>9</td>
        <td><strong>Admin Management Module</strong></td>
        <td>Moderate listings, block/unblock users, monitor transactions, resolve user violation reports, configure platform settings, and view revenue analytics.</td>
    </tr>
</table>

<h3>Architecture Diagram</h3>
<div class="diagram-box">
<pre>
+-----------------------------------------------------------------------------------------------+
|                                      CLIENT LAYER (Browser)                                   |
|   +---------------------------------------------+   +-------------------------------------+   |
|   |  Responsive Web Client (SPA: HTML/CSS/JS)   |   |        Admin Web Panel              |   |
|   |  (Mobile Simulator Frame + Desktop Toggle)  |   |    (Django Template Dashboard)      |   |
|   +---------------------------------------------+   +-------------------------------------+   |
+-----------------------------------------------------------------------------------------------+
                                               | HTTPS / JSON (Token Auth)
+-----------------------------------------------------------------------------------------------+
|                               SERVER LAYER (Django 6.1 REST API)                              |
|   [Authentication]  [Catalog & Scan]  [Listings & Search]  [Contact Unlock]  [Admin Views]    |
|                                [Payment & Refund Services]                                    |
+-----------------------------------------------------------------------------------------------+
             |                                 |                                 |
+-------------------------+       +-------------------------+       +---------------------------+
|    PERSISTENCE LAYER    |       |   EXTERNAL BOOK APIS    |       |  PAYMENT GATEWAY ADAPTERS |
|  PostgreSQL 18 Database |       |    - Google Books API   |       |   - JazzCash (HMAC-SHA256)|
|  Media Storage (Pillow) |       |    - Open Library API   |       |   - Easypaisa Wallet      |
+-------------------------+       +-------------------------+       +---------------------------+
</pre>
</div>
<div class="caption">Figure 3.1: Layered architecture diagram showing subsystems, data repositories and external services</div>

<h2>3.2. Decomposition Description</h2>
<p>An object-oriented, service-driven decomposition is used. The top-level data flow diagram is presented below, followed by component structure and interaction sequence.</p>

<div class="diagram-box">
<pre>
   [Buyer] <====== Credentials, Search, Barcode Scan, Unlock Fee, Confirmations ======> [BookBazaar Core System]
                                                                                                ^
   [Seller] <===== Listing Details, Selling Price, Campus Pickup, Photos ===============>       |
                                                                                                |
   [Admin] <====== Moderation Decisions, Platform Settings, Ad Campaigns, Disputes =====>      |
                                                                                                v
   [Google Books / Open Library] <=== ISBN Query & JSON Book Metadata Response ================>|
   [JazzCash / Easypaisa] <========== Secure HMAC-SHA256 Payload & Signed Callbacks ===========>|
   [PostgreSQL Database] <=========== ACID Transactions, Row-Level Locking, 10 Models =========>|
</pre>
</div>
<div class="caption">Figure 3.2: Top-level data flow diagram (Level-0 DFD)</div>

<h3>Structural Composition of Modules:</h3>
<table>
    <tr><th>Module</th><th>Main Classes / Services</th><th>Key Interfaces</th></tr>
    <tr><td>Authentication</td><td><code>UserProfile</code>, <code>User</code>, <code>Token</code></td><td>Register(), Login(), VerifyOTP(), GetProfile()</td></tr>
    <tr><td>Scanner & Catalog</td><td><code>Book</code>, <code>book_service.py</code></td><td>LookupBookByISBN(), NormalizeISBN(), FetchAPIData()</td></tr>
    <tr><td>Buyer</td><td><code>Listing</code>, <code>Favorite</code>, <code>MarketplaceReport</code></td><td>SearchListings(), FilterByBoard(), ToggleFavorite()</td></tr>
    <tr><td>Seller</td><td><code>Listing</code>, <code>ImageField</code></td><td>CreateListing(), UpdateListing(), ToggleStatus()</td></tr>
    <tr><td>Contact Unlock</td><td><code>ContactUnlock</code></td><td>RequestUnlock(), RevealContact(), GetUnlocks()</td></tr>
    <tr><td>Payment & Refund</td><td><code>PaymentTransaction</code>, <code>payment_service.py</code></td><td>InitiatePayment(), VerifySignature(), RefundToWallet()</td></tr>
    <tr><td>Advertisement</td><td><code>Advertisement</code></td><td>ServeAd(), TrackClick(), ToggleAd()</td></tr>
    <tr><td>Admin</td><td><code>PlatformSetting</code>, Admin Views</td><td>ModerateListing(), BlockUser(), UpdateSettings()</td></tr>
</table>

<h3>Sequence Diagram (Contact Unlock, Deal Confirmation and Refund):</h3>
<div class="diagram-box">
<pre>
Buyer                Web Client (SPA)           Django API          JazzCash/Easypaisa        Seller
  |                         |                       |                        |                  |
  |--- 1. Tap Contact ----->|                       |                        |                  |
  |                         |-- 2. POST /unlocks -->|                        |                  |
  |                         |                       |-- 3. Initiate Txn ---->|                  |
  |                         |                       |<-- 4. Signed Callback -|                  |
  |                         |                       |   [Verify HMAC-SHA256] |                  |
  |                         |                       |   [Save Completed Txn] |                  |
  |                         |                       |   [Create Unlock: pending]                |
  |                         |<-- 5. Reveal Contact -|                        |                  |
  |<-- 6. Show Phone/WA ----|                       |                        |                  |
  |                                                                                             |
  |=================== 7. Students meet at campus & inspect book ===============================|
  |                                                                                             |
  | [IF DEAL CONFIRMED]:                                                                        |
  |--- 8. Confirm Deal ---->|                       |                                           |
  |                         |-- 9. confirm_deal --->| [deal_status='deal_made'; platform keeps fee]
  |                                                                                             |
  | [IF NO DEAL MADE]:                                                                          |
  |--- 10. Cancel Deal ---->|                       |                                           |
  |                         |-- 11. cancel_deal --->| [deal_status='no_deal_refunded']          |
  |                         |                       | [buyer.wallet_balance += Rs. 50.00]       |
  |<-- 12. Rs. 50 in Wallet-|                       |                                           |
</pre>
</div>
<div class="caption">Figure 3.3: Sequence diagram for contact unlock, deal confirmation, and internal wallet refund</div>

<h3>State Diagram of a Contact Unlock Record:</h3>
<div class="diagram-box">
<pre>
   [Payment Pending] ---> (Payment Fails / Tampered) ---> [Payment Failed]
          |
   (HMAC-SHA256 Verified)
          v
   [Unlocked Pending] ---> (Both Confirm Handover) ------> [Deal Made] (Fee Kept)
          |
          +--------------> (Buyer Cancels / 5-Day Timeout) -> [No Deal Refunded] (Rs. 50 to Wallet)
          |
          +--------------> (Conflicting Claims) --------> [Disputed] (Admin Mediation)
</pre>
</div>
<div class="caption">Figure 3.4: State transition diagram of a contact unlock record</div>

<h2>3.3. Design Rationale</h2>
<p>The selected architecture is a modular, layered client-server architecture balancing performance, university evaluation practicality, and financial integrity:</p>
<ul>
    <li><strong>Responsive Web SPA with Mobile Emulator:</strong> For academic viva evaluation, a responsive web app allows evaluators to test the mobile user experience immediately in any browser without compiling APKs or configuring Android SDKs. The clean separation of REST APIs ensures 100% readiness for native Flutter apps in Phase 6.</li>
    <li><strong>Django 6.1 and PostgreSQL 18:</strong> Django provides built-in ORM protection against SQL injection, CSRF protection, and DRF Token authentication. PostgreSQL provides ACID guarantees, row-level locking (<code>select_for_update</code>), and transactional consistency essential for payments.</li>
    <li><strong>Internal Wallet Refund Model:</strong> Commercial bank gateway reverse disbursements incur delays and high fees in Pakistan. Refunding Rs. 50 directly into the buyer's internal BookBazaar wallet allows instant, zero-deduction refunds that students can reuse immediately.</li>
    <li><strong>Multi-Tier Catalog Lookup:</strong> Checking the local database and curated Pakistani academic catalog before calling Google Books eliminates external API rate limits and accelerates barcode lookups.</li>
</ul>

<!-- Section 4 -->
<h1>4. DATA DESIGN</h1>

<h2>4.1. Data Description</h2>
<p>Data is stored in PostgreSQL 18 across ten normalized relational tables. Integrity is enforced through foreign key constraints, unique indexes, and database transactions.</p>

<h2>4.2. Data Dictionary</h2>

<h3>4.2.1. UserProfile (<code>bazaar_userprofile</code>)</h3>
<p>Extends Django's <code>auth_user</code> table with marketplace attributes.</p>
<table>
    <tr><th>Attribute</th><th>Type</th><th>Constraints</th><th>Description</th></tr>
    <tr><td><code>id</code></td><td>BigAutoField</td><td>Primary Key</td><td>Unique profile identifier</td></tr>
    <tr><td><code>user_id</code></td><td>Integer</td><td>OneToOne to auth_user</td><td>Associated Django user account</td></tr>
    <tr><td><code>full_name</code></td><td>VARCHAR(150)</td><td>Not Null</td><td>Display full name</td></tr>
    <tr><td><code>phone_number</code></td><td>VARCHAR(20)</td><td>Unique, Not Null</td><td>Pakistani mobile number (03XXXXXXXXX)</td></tr>
    <tr><td><code>city</code></td><td>VARCHAR(80)</td><td>Indexed</td><td>City (Bahawalpur, Lahore, Karachi, etc.)</td></tr>
    <tr><td><code>campus_or_area</code></td><td>VARCHAR(150)</td><td>Blank</td><td>University campus / residential area</td></tr>
    <tr><td><code>wallet_balance</code></td><td>DECIMAL(10,2)</td><td>Default 0.00</td><td>In-app digital balance in PKR</td></tr>
    <tr><td><code>rating</code></td><td>DECIMAL(3,2)</td><td>Default 5.00</td><td>Average seller rating (1.00 to 5.00)</td></tr>
    <tr><td><code>total_reviews</code></td><td>Integer</td><td>Default 0</td><td>Count of received reviews</td></tr>
    <tr><td><code>is_blocked</code></td><td>Boolean</td><td>Default False</td><td>Administrative suspension flag</td></tr>
</table>

<h3>4.2.2. Book (<code>bazaar_book</code>)</h3>
<p>Central textbook catalog indexed by ISBN.</p>
<table>
    <tr><th>Attribute</th><th>Type</th><th>Constraints</th><th>Description</th></tr>
    <tr><td><code>id</code></td><td>BigAutoField</td><td>Primary Key</td><td>Catalog book ID</td></tr>
    <tr><td><code>isbn</code></td><td>VARCHAR(20)</td><td>Unique, Indexed</td><td>ISBN-10 or ISBN-13 identifier</td></tr>
    <tr><td><code>title</code></td><td>VARCHAR(255)</td><td>Not Null</td><td>Book title</td></tr>
    <tr><td><code>author</code></td><td>VARCHAR(255)</td><td>Not Null</td><td>Author(s)</td></tr>
    <tr><td><code>publisher</code></td><td>VARCHAR(255)</td><td>Blank</td><td>Publishing company</td></tr>
    <tr><td><code>edition</code></td><td>VARCHAR(50)</td><td>Blank</td><td>Edition (e.g. 7th Edition)</td></tr>
    <tr><td><code>category</code></td><td>VARCHAR(100)</td><td>Indexed</td><td>Discipline (Computer Science, Medical, etc.)</td></tr>
    <tr><td><code>education_board</code></td><td>VARCHAR(100)</td><td>Indexed</td><td>Board (Punjab, Federal, Cambridge, HEC)</td></tr>
    <tr><td><code>grade_class</code></td><td>VARCHAR(100)</td><td>Indexed</td><td>Class level (Matric, FSc, BS, Master)</td></tr>
    <tr><td><code>cover_image</code></td><td>Text</td><td>Blank</td><td>Cover image URL / base64 string</td></tr>
    <tr><td><code>original_retail_price</code></td><td>DECIMAL(10,2)</td><td>Default 1500.00</td><td>Estimated new retail price in PKR</td></tr>
</table>

<h3>4.2.3. Listing (<code>bazaar_listing</code>)</h3>
<p>Used book offers listed by sellers.</p>
<table>
    <tr><th>Attribute</th><th>Type</th><th>Constraints</th><th>Description</th></tr>
    <tr><td><code>id</code></td><td>BigAutoField</td><td>Primary Key</td><td>Listing ID</td></tr>
    <tr><td><code>book_id</code></td><td>BigInteger</td><td>ForeignKey to Book</td><td>Referenced book</td></tr>
    <tr><td><code>seller_id</code></td><td>BigInteger</td><td>ForeignKey to UserProfile</td><td>Listing seller</td></tr>
    <tr><td><code>condition</code></td><td>VARCHAR(20)</td><td>Choices</td><td>Brand New, Like New, Good, Fair</td></tr>
    <tr><td><code>price</code></td><td>DECIMAL(10,2)</td><td>Not Null</td><td>Selling price in PKR set by seller</td></tr>
    <tr><td><code>city</code></td><td>VARCHAR(80)</td><td>Indexed</td><td>City of listing</td></tr>
    <tr><td><code>pickup_location</code></td><td>VARCHAR(150)</td><td>Blank</td><td>Campus meeting point (e.g. Library Gate)</td></tr>
    <tr><td><code>image</code></td><td>VARCHAR(100)</td><td>Pillow Validated</td><td>Uploaded book photograph</td></tr>
    <tr><td><code>status</code></td><td>VARCHAR(20)</td><td>Indexed</td><td>active, pending, sold, inactive</td></tr>
    <tr><td><code>is_sponsored</code></td><td>Boolean</td><td>Indexed</td><td>Promoted listing flag</td></tr>
</table>

<h3>4.2.4. ContactUnlock (<code>bazaar_contactunlock</code>)</h3>
<p>Unified contact unlock, deal state machine, and refund record.</p>
<table>
    <tr><th>Attribute</th><th>Type</th><th>Constraints</th><th>Description</th></tr>
    <tr><td><code>id</code></td><td>BigAutoField</td><td>Primary Key</td><td>Internal ID</td></tr>
    <tr><td><code>unlock_id</code></td><td>UUID</td><td>Unique, Indexed</td><td>Public UUID token</td></tr>
    <tr><td><code>listing_id</code></td><td>BigInteger</td><td>ForeignKey to Listing</td><td>Unlocked listing</td></tr>
    <tr><td><code>buyer_id</code></td><td>BigInteger</td><td>ForeignKey to UserProfile</td><td>Unlocking buyer</td></tr>
    <tr><td><code>seller_id</code></td><td>BigInteger</td><td>ForeignKey to UserProfile</td><td>Listing seller</td></tr>
    <tr><td><code>fee_amount</code></td><td>DECIMAL(6,2)</td><td>Default 50.00</td><td>Unlock fee in PKR</td></tr>
    <tr><td><code>payment_method</code></td><td>VARCHAR(30)</td><td>Choices</td><td>jazzcash, easypaisa, card_safepay, wallet</td></tr>
    <tr><td><code>deal_status</code></td><td>VARCHAR(30)</td><td>Indexed</td><td>unlocked_pending, deal_made, no_deal_refunded</td></tr>
    <tr><td><code>refund_transaction_id</code></td><td>VARCHAR(100)</td><td>Blank</td><td>Refund ID (REF-XXXXXX)</td></tr>
</table>

<h3>4.2.5. PaymentTransaction (<code>bazaar_paymenttransaction</code>)</h3>
<p>Financial transaction audit log.</p>
<table>
    <tr><th>Attribute</th><th>Type</th><th>Constraints</th><th>Description</th></tr>
    <tr><td><code>id</code></td><td>BigAutoField</td><td>Primary Key</td><td>Transaction ID</td></tr>
    <tr><td><code>transaction_id</code></td><td>UUID</td><td>Unique, Indexed</td><td>Public UUID</td></tr>
    <tr><td><code>amount</code></td><td>DECIMAL(10,2)</td><td>Default 50.00</td><td>Amount paid in PKR</td></tr>
    <tr><td><code>gateway</code></td><td>VARCHAR(30)</td><td>Indexed</td><td>jazzcash, easypaisa, card, wallet</td></tr>
    <tr><td><code>status</code></td><td>VARCHAR(20)</td><td>Indexed</td><td>pending, completed, failed, refunded</td></tr>
    <tr><td><code>gateway_response_code</code></td><td>VARCHAR(50)</td><td>Blank</td><td>Gateway status code (000, 0000)</td></tr>
</table>

<h3>4.2.6. Other Models</h3>
<ul>
    <li><strong><code>SellerReview</code> (<code>bazaar_sellerreview</code>):</strong> Linked 1:1 to <code>ContactUnlock</code>, records 1 to 5-star rating and comment.</li>
    <li><strong><code>Advertisement</code> (<code>bazaar_advertisement</code>):</strong> Tracks title, ad type (banner, interstitial, native), impressions, and clicks.</li>
    <li><strong><code>PlatformSetting</code> (<code>bazaar_platformsetting</code>):</strong> Dynamic settings (unlock fee, auto-refund days, admin approval).</li>
    <li><strong><code>MarketplaceReport</code> (<code>bazaar_marketplacereport</code>):</strong> Moderation report filing against fraudulent listings or abusive sellers.</li>
    <li><strong><code>Favorite</code> (<code>bazaar_favorite</code>):</strong> User wishlist linking <code>UserProfile</code> and <code>Listing</code>.</li>
</ul>

<!-- Section 5 -->
<h1>5. COMPONENT DESIGN</h1>
<p>The algorithms of the core subsystems are detailed below in Program Design Language (PDL / Pseudo-code).</p>

<h2>5.1. Authentication – Register & Login with Token Auth</h2>
<pre>
FUNCTION RegisterUser(phone_number, full_name, city, password):
    phone_clean = StripNonDigits(phone_number)
    IF Length(phone_clean) != 11 OR NOT phone_clean.StartsWith("03") THEN:
        RETURN Error("Invalid Pakistani mobile number format (03XXXXXXXXX)")
    IF Length(password) < 6 THEN:
        RETURN Error("Password must be at least 6 characters")
    IF UserProfile.Exists(phone_number=phone_clean) THEN:
        RETURN Error("Account with this mobile number already exists")

    username = "user_" + phone_clean
    user = CreateAuthUser(username=username, password=password)  // Hashed with PBKDF2
    profile = CreateUserProfile(user=user, phone_number=phone_clean, full_name=full_name, city=city, wallet_balance=100.00)
    token = GenerateDRFToken(user)
    RETURN Success(token=token.key, profile=profile)
END FUNCTION
</pre>

<h2>5.2. Scanner and Catalog – Multi-Tier ISBN Lookup</h2>
<pre>
FUNCTION LookupBookByISBN(isbn_raw):
    clean_isbn = NormalizeISBN(isbn_raw)
    book = Book.Find(isbn=clean_isbn)
    IF book != NULL THEN RETURN book, "database"

    IF clean_isbn IN KNOWN_CATALOG THEN:
        book = Book.Insert(KNOWN_CATALOG[clean_isbn])
        RETURN book, "curated_catalog"

    api_result = QueryGoogleBooksAPI(clean_isbn)
    IF api_result.found THEN:
        book = Book.Insert(api_result.data)
        RETURN book, "google_books"

    ol_result = QueryOpenLibraryAPI(clean_isbn)
    IF ol_result.found THEN:
        book = Book.Insert(ol_result.data)
        RETURN book, "open_library"

    RETURN NULL, "manual_entry_required"
END FUNCTION
</pre>

<h2>5.3. Seller – Create Listing with Pillow Photo Upload</h2>
<pre>
FUNCTION CreateListing(seller, book_id, price, condition, city, pickup_location, photo_file):
    IF seller.is_blocked THEN RETURN Error("Account blocked by administration", 403)
    IF price <= 0 THEN RETURN Error("Price must be greater than zero", 400)
    IF photo_file != NULL THEN:
        ValidateImageFormat(photo_file, ["JPEG", "PNG", "WEBP"])
        ValidateImageSize(photo_file, max_mb=5.0)
        VerifyIntegrityWithPillow(photo_file)

    setting = PlatformSetting.Get()
    listing_status = (setting.require_admin_approval) ? "pending" : "active"
    listing = Listing.Insert(seller=seller, book_id=book_id, price=price, condition=condition,
                             city=city, pickup_location=pickup_location, image=photo_file, status=listing_status)
    RETURN Success(listing=listing)
END FUNCTION
</pre>

<h2>5.4. Contact Unlock – Payment & Signature Verification</h2>
<pre>
FUNCTION ExecuteContactUnlock(buyer, listing_id, method, account_number):
    listing = Listing.Find(id=listing_id)
    IF listing.seller == buyer THEN RETURN Error("Cannot unlock your own listing", 400)
    IF ContactUnlock.Exists(buyer=buyer, listing=listing) THEN RETURN Error("Already unlocked", 400)
    fee = PlatformSetting.Get().contact_unlock_fee

    START ATOMIC TRANSACTION:
        txn = PaymentTransaction.Insert(buyer=buyer, listing=listing, amount=fee, gateway=method, status="pending")
        IF method == "wallet" THEN:
            IF buyer.wallet_balance < fee THEN ROLLBACK ; RETURN Error("Insufficient wallet balance", 400)
            buyer.wallet_balance -= fee ; buyer.Save() ; is_verified = TRUE
        ELSE:
            payload = BuildGatewayPayload(txn, account_number)
            expected_hash = CalculateHMACSHA256(payload, INTEGRITY_SALT)
            is_verified = VerifyGatewayResponse(payload, expected_hash)

        IF NOT is_verified THEN:
            txn.status = "failed" ; txn.Save() ; ROLLBACK ; RETURN Error("Payment authorization failed", 400)

        txn.status = "completed" ; txn.verified_at = Now() ; txn.Save()
        unlock = ContactUnlock.Insert(listing=listing, buyer=buyer, seller=listing.seller, fee_amount=fee,
                                      payment_method=method, transaction_id=txn.transaction_id, deal_status="unlocked_pending")
        txn.unlock = unlock ; txn.Save()
    COMMIT TRANSACTION
    RETURN Success(seller_phone=listing.seller.phone_number, whatsapp_link="https://wa.me/92" + listing.seller.phone_number.SubString(1))
END FUNCTION
</pre>

<h2>5.5. Deal Confirmation and Wallet Refund</h2>
<pre>
FUNCTION CancelDealAndRefund(user, unlock_id, reason):
    unlock = ContactUnlock.Find(unlock_id=unlock_id)
    IF user != unlock.buyer.user AND user != unlock.seller.user AND NOT user.is_staff THEN:
        RETURN Error("Permission denied", 403)
    IF unlock.deal_status == "deal_made" THEN RETURN Error("Cannot refund confirmed deal", 400)
    IF unlock.deal_status == "no_deal_refunded" THEN RETURN Error("Fee has already been refunded", 400)

    START ATOMIC TRANSACTION:
        ref_id = "REF-" + GenerateRandomDigits(6)
        unlock.deal_status = "no_deal_refunded"
        unlock.cancellation_reason = reason
        unlock.refund_transaction_id = ref_id
        unlock.refund_timestamp = Now()
        unlock.Save()

        buyer = unlock.buyer
        buyer.wallet_balance += unlock.fee_amount
        buyer.Save()
    COMMIT TRANSACTION
    RETURN Success(message="Deal cancelled. Rs. 50 credited to your BookBazaar wallet.", refund_id=ref_id)
END FUNCTION
</pre>

<h2>5.6. Advertisement – Serve Ad</h2>
<pre>
FUNCTION ServeAd(ad_type, screen):
    IF screen IN ["checkout", "payment_modal", "otp_modal"] THEN RETURN NULL
    ad = Advertisement.Find(ad_type=ad_type, is_active=True).OrderByRandom().First()
    IF ad != NULL THEN:
        ad.impressions += 1
        ad.Save()
    RETURN ad
END FUNCTION
</pre>

<h2>5.7. Admin – Moderation and Dispute Resolution</h2>
<pre>
FUNCTION ModerateListing(admin, listing_id, decision):
    listing = Listing.Find(id=listing_id)
    listing.status = (decision == "Approve") ? "active" : "inactive"
    listing.Save()
    WriteAuditLog(admin, listing_id, decision)
END FUNCTION
</pre>

<h2>5.8. Reviews – Submit Review and Recalculate Rating</h2>
<pre>
FUNCTION SubmitReview(buyer, unlock_id, rating, comment):
    unlock = ContactUnlock.Find(unlock_id=unlock_id)
    IF unlock.buyer != buyer THEN RETURN Error("Not authorized", 403)
    IF SellerReview.Exists(unlock=unlock) THEN RETURN Error("Already reviewed", 400)
    SellerReview.Insert(unlock=unlock, seller=unlock.seller, buyer=buyer, rating=rating, comment=comment)
    unlock.seller.UpdateRating()  // Re-computes cumulative average rating
END FUNCTION
</pre>

<!-- Section 6 -->
<h1>6. HUMAN INTERFACE DESIGN</h1>

<h2>6.1. Overview of User Interface</h2>
<p>The BookBazaar interface is an interactive, responsive Single Page Application (SPA). On desktop displays it renders within an iPhone mockup frame with a live notch, time, wifi and battery simulator, and features a "Full Screen / Desktop" button to adapt into a standard wide layout. The interface supports English and Urdu (<code>اردو</code>) dynamically.</p>
<p><strong>Primary Tabs:</strong></p>
<ul>
    <li><strong>Home:</strong> Hero search bar, curriculum filter drawer (Board, Class, City, Condition), and book listing feed.</li>
    <li><strong>Scan:</strong> Live camera barcode scanner, torch switch, manual ISBN lookup, and multi-seller price comparison table.</li>
    <li><strong>Sell:</strong> Multi-field book listing creation with auto-fill, condition grading, campus meeting spot, and photo upload.</li>
    <li><strong>Deals:</strong> My Unlocks and Deals, unmasked phone numbers, direct Call and WhatsApp buttons, Deal Confirmation, and Refund triggers.</li>
    <li><strong>Profile:</strong> Wallet balance (PKR), user details, active listings inventory, and account controls.</li>
</ul>

<h2>6.2. Screen Images & Walkthrough</h2>
<p>The following screens illustrate the user experience:</p>
<ul>
    <li><strong>Login / Register Modal:</strong> Validates Pakistani phone numbers (<code>03XX-XXXXXXX</code>) and hashes passwords via PBKDF2.</li>
    <li><strong>Browse & Filter Drawer:</strong> Live filtering by Pakistani boards (Punjab, Federal, Cambridge, HEC) and class grades.</li>
    <li><strong>Barcode Scanner & Compare Table:</strong> Aggregates all competing seller offers sorted from lowest price with masked phone numbers.</li>
    <li><strong>Rs. 50 Sandbox Checkout Modal:</strong> Selects JazzCash, Easypaisa, or In-App Wallet, displays 100% refund guarantee banner, and verifies HMAC-SHA256 signatures.</li>
    <li><strong>Unmasked Contact Card:</strong> Displays full phone number (<code>03019876543</code>), direct "Call Seller" button, and "WhatsApp Chat" button.</li>
    <li><strong>Admin Panel (<code>/admin-panel/</code>):</strong> Full dashboard displaying gross fees, wallet refunds, net revenue, listing moderation, user blocking, and ad campaign scheduling.</li>
</ul>

<h2>6.3. Screen Objects and Actions</h2>
<table>
    <tr><th>Screen</th><th>Screen Objects</th><th>Actions</th></tr>
    <tr><td>Login Modal</td><td>Phone field, Password field, Switch Tab button</td><td>Register user, authenticate, switch language</td></tr>
    <tr><td>Home Tab</td><td>Search box, Board/Class filters, Favourites button</td><td>Search catalog, filter by curriculum, open listing</td></tr>
    <tr><td>Scan Tab</td><td>Camera viewfinder, Torch toggle, ISBN input</td><td>Scan barcode, view competing seller offers</td></tr>
    <tr><td>Unlock Modal</td><td>Fee display (Rs. 50), Gateway tabs, Pay button</td><td>Authorize payment, verify signature, unlock phone</td></tr>
    <tr><td>Sell Tab</td><td>Condition select, Price input, Campus pickup, Photo upload</td><td>Enter details, upload photo, publish listing</td></tr>
    <tr><td>Deals Tab</td><td>Call button, WhatsApp button, Confirm Deal, No Deal Refund</td><td>Contact seller, confirm deal, refund fee to wallet</td></tr>
    <tr><td>Admin Panel</td><td>Stat cards, Pending tables, Block toggle, Fee inputs</td><td>Approve listings, block users, change settings</td></tr>
</table>

<!-- Section 7 -->
<h1>7. REQUIREMENTS MATRIX</h1>
<p>Traces SRS v2.0 requirements to architectural modules, database tables, and UI screens:</p>
<table>
    <tr><th>SRS Req.</th><th>Requirement</th><th>Design Subsystem</th><th>Database Table</th><th>UI Screen</th></tr>
    <tr><td>FR-1</td><td>User registration & authentication</td><td>Authentication Module</td><td><code>auth_user</code>, <code>UserProfile</code></td><td>Login Modal</td></tr>
    <tr><td>FR-2</td><td>Barcode scanning & catalog lookup</td><td>Scanner & Catalog Module</td><td><code>Book</code></td><td>Scan Tab</td></tr>
    <tr><td>FR-3</td><td>Search & board filtering</td><td>Buyer Module</td><td><code>Book</code>, <code>Listing</code></td><td>Home Tab</td></tr>
    <tr><td>FR-4</td><td>Create and manage listings</td><td>Seller Module</td><td><code>Listing</code></td><td>Sell Tab</td></tr>
    <tr><td>FR-5</td><td>Contact unlock & privacy protection</td><td>Contact Unlock Module</td><td><code>ContactUnlock</code></td><td>Unlock Modal</td></tr>
    <tr><td>FR-6</td><td>Local payment gateway integration</td><td>Payment Service</td><td><code>PaymentTransaction</code></td><td>Checkout Modal</td></tr>
    <tr><td>FR-7</td><td>Deal confirmation & wallet refund</td><td>Deal & Refund Module</td><td><code>ContactUnlock</code>, <code>UserProfile</code></td><td>Deals Tab</td></tr>
    <tr><td>FR-8</td><td>Seller ratings and reviews</td><td>Reputation Module</td><td><code>SellerReview</code></td><td>Review Modal</td></tr>
    <tr><td>FR-9</td><td>In-app status & activity counters</td><td>Profile Module</td><td><code>UserProfile</code></td><td>Profile Tab</td></tr>
    <tr><td>FR-10</td><td>Proprietary ad engine</td><td>Advertisement Module</td><td><code>Advertisement</code></td><td>Banner / Interstitial</td></tr>
    <tr><td>FR-11</td><td>Admin management dashboard</td><td>Admin Module</td><td>All Tables, <code>PlatformSetting</code></td><td>Admin Panel</td></tr>
    <tr><td>FR-12</td><td>Wishlist & user favorites</td><td>Buyer Module</td><td><code>Favorite</code></td><td>Favourites Filter</td></tr>
    <tr><td>FR-13</td><td>Marketplace violation reports</td><td>Moderation Module</td><td><code>MarketplaceReport</code></td><td>Report Modal</td></tr>
</table>

<!-- Section 8 -->
<h1>8. APPENDICES</h1>

<h2>Appendix A – Main REST API Endpoints</h2>
<table>
    <tr><th>Endpoint</th><th>Method</th><th>Permission</th><th>Purpose</th></tr>
    <tr><td><code>/api/auth/register/</code></td><td>POST</td><td>AllowAny</td><td>Register new user with Pakistani phone</td></tr>
    <tr><td><code>/api/auth/login/</code></td><td>POST</td><td>AllowAny</td><td>Authenticate and issue DRF Token</td></tr>
    <tr><td><code>/api/auth/login_otp/</code></td><td>POST</td><td>AllowAny</td><td>Fast OTP login for evaluation</td></tr>
    <tr><td><code>/api/books/scan/?isbn={{isbn}}</code></td><td>GET</td><td>AllowAny</td><td>Barcode query and multi-seller offers</td></tr>
    <tr><td><code>/api/listings/</code></td><td>GET</td><td>AllowAny</td><td>Search and filter listings by board/class/city</td></tr>
    <tr><td><code>/api/listings/create/</code></td><td>POST</td><td>IsAuthenticated</td><td>Create listing with Pillow image upload</td></tr>
    <tr><td><code>/api/listings/{{id}}/edit/</code></td><td>POST</td><td>IsAuthenticated</td><td>Edit selling price and campus pickup point</td></tr>
    <tr><td><code>/api/unlocks/request/</code></td><td>POST</td><td>IsAuthenticated</td><td>Pay Rs. 50 fee and unlock contact</td></tr>
    <tr><td><code>/api/unlocks/{{id}}/confirm_deal/</code></td><td>POST</td><td>IsAuthenticated</td><td>Confirm deal made (fee kept by platform)</td></tr>
    <tr><td><code>/api/unlocks/{{id}}/cancel_deal/</code></td><td>POST</td><td>IsAuthenticated</td><td>Cancel deal (Rs. 50 refunded to wallet)</td></tr>
    <tr><td><code>/api/reviews/create/</code></td><td>POST</td><td>IsAuthenticated</td><td>Submit 1-5 star rating and comment</td></tr>
    <tr><td><code>/api/payments/initiate/</code></td><td>POST</td><td>IsAuthenticated</td><td>Construct signed gateway payload</td></tr>
    <tr><td><code>/api/payments/verify/</code></td><td>POST</td><td>IsAuthenticated</td><td>Verify HMAC-SHA256 signature</td></tr>
    <tr><td><code>/api/ads/</code></td><td>GET</td><td>AllowAny</td><td>Retrieve active ad banners</td></tr>
    <tr><td><code>/api/reports/submit/</code></td><td>POST</td><td>IsAuthenticated</td><td>Submit complaint against listing/seller</td></tr>
    <tr><td><code>/api/admin/stats/</code></td><td>GET</td><td>IsAdminUser</td><td>Real-time marketplace revenue metrics</td></tr>
    <tr><td><code>/api/admin/settings/</code></td><td>POST</td><td>IsAdminUser</td><td>Update fee, refund days, approval rules</td></tr>
    <tr><td><code>/api/admin/users/{{id}}/toggle_block/</code></td><td>POST</td><td>IsAdminUser</td><td>Suspend or reactivate user account</td></tr>
</table>

<h2>Appendix B – System Settings</h2>
<ul>
    <li><strong>Contact Unlock Fee:</strong> Rs. 50.00 PKR (configurable via <code>PlatformSetting</code>).</li>
    <li><strong>Deal Confirmation Period:</strong> Default 5 days before auto-refund.</li>
    <li><strong>Gateway Mode:</strong> Sandbox mode with HMAC-SHA256 signature validation.</li>
    <li><strong>Rate Limiting:</strong> 60 requests/min for anonymous users; 200 requests/min for authenticated users.</li>
</ul>

<h2>Appendix C – Future Work</h2>
<ul>
    <li>Cross-platform Flutter mobile applications (Android & iOS).</li>
    <li>Live corporate merchant accounts with Mobilink Microfinance Bank and Telenor Microfinance Bank.</li>
    <li>Commercial telecom SMS gateway integration for mobile OTP distribution.</li>
    <li>Asynchronous Celery/Redis workers for background auto-refund scheduling.</li>
</ul>

</body>
</html>
"""

html_path = os.path.join(WORKSPACE, 'BookBazaar_SDD_v2.0.html')
pdf_path = os.path.join(WORKSPACE, 'BookBazaar_SDD_v2.0.pdf')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(sdd_html)

print("Generated BookBazaar_SDD_v2.0.html. Rendering to PDF via Chrome...")
cmd = f'"{CHROME}" --headless=new --disable-gpu --run-all-compositor-stages-before-draw --print-to-pdf="{pdf_path}" "{html_path}"'
subprocess.run(cmd, shell=True, check=True)
print(f"BookBazaar_SDD_v2.0.pdf generated successfully! Size: {os.path.getsize(pdf_path)} bytes")
