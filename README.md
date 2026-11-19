# BookBazaar Pakistan 📚🇵🇰
**Used Books Marketplace with ISBN Price Comparison, Paid Contact Unlock & Concurrency-Safe Refund Architecture**  
*Final Year Project (FYP) & Commercial Marketplace Initiative*  

---

## 🌟 Implemented Features & Architecture Roadmap

| Module / Domain | Status | Implemented Capabilities |
| :--- | :---: | :--- |
| **Pre-Phase 6: Admin Notifications & 1-Click Refund System** | ✅ Active & Verified | • **Real-time Admin Notifications**: Event-driven notification engine for `PAYMENT_RECEIVED`, `DEAL_SUCCESSFUL`, `DEAL_FAILED_REFUND_REQ`, and `SYSTEM_ALERT`.<br>• **Header Notification Bell**: Live unread badge count with 25s auto-polling and dropdown notification drawer.<br>• **1-Click Admin Refund Action**: Atomically transitions contact unlock to `no_deal_refunded`, credits Rs. 50 to buyer wallet, and marks payment as refunded.<br>• **Row-Level Concurrency Locking**: Employs `select_for_update()` inside `transaction.atomic()` with strict idempotency to prevent duplicate refunds.<br>• **Automated Test Coverage**: 9 comprehensive tests verifying all notification triggers and duplicate refund guards. |
| **Phase 5: Production Readiness & Auditing** | ✅ Active & Verified | • **Zero-Warning Production Deployment**: `python manage.py check --deploy` passes with 0 issues.<br>• **High-Performance Database Indexes**: PostgreSQL composite & B-tree indexes on `Listing`, `Book`, `ContactUnlock`, and `PaymentTransaction`.<br>• **Static & Media Serving**: Integrated **Whitenoise** static storage with compressed manifest assets and Nginx/Gunicorn production templates.<br>• **Automated Disaster Recovery**: Scripted PostgreSQL daily backup & 7-day rotation (`deploy/postgres_backup.sh`).<br>• **75+ Tests Verified**: Full test pass rate across Phase 1, 2, 3, 4, 5, Pre-Phase 6, and FYP Proposal specifications. |
| **Phase 4: Admin Management** | ✅ Active & Verified | • **Comprehensive Admin Portal** at `/admin-panel/` with 8 modular management sections.<br>• **User Governance**: Search, role & status filtering, instant block/unblock, and detailed activity audit trail.<br>• **Listing Moderation**: Approve, reject, feature/sponsor, mark sold, direct field edits, and safe deletion.<br>• **Seller Activity Monitoring**: Track seller performance, ratings, active books, and contact unlock volume.<br>• **Payment & Unlock Ledger**: Rs. 50 contact unlock ledger, gateway breakdown, and admin force-refund override.<br>• **Reports & Complaints System**: Integrated user reporting with automated moderation actions.<br>• **Campaign & Ads Manager**: CRUD for banner/interstitial advertisements with Click-Through Rate (CTR) analytics.<br>• **Dynamic Platform Settings**: Instant control over unlock fee, auto-refund timeouts, and moderation requirements. |
| **Phase 3: Secure Payment Gateways** | ✅ Active & Verified | • **Modular Gateway Architecture**: Dedicated adapters for **JazzCash** and **Easypaisa** with clean separation from business logic.<br>• **Cryptographic Verification**: HMAC-SHA256 signature calculations (`pp_SecureHash` for JazzCash MWALLET; `merchantHashedReq` for Easypaisa Open API).<br>• **Replay Attack & Duplicate Protection**: Database-level atomic transactions with `select_for_update()` and `PaymentTransaction` state machine.<br>• **Strict Contact Privacy**: Seller phone number masked (`03XX-*******`) until payment status is server-verified as `completed`.<br>• **Dynamic Platform Fee**: Configurable unlock fee (default Rs. 50 PKR) via `PlatformSetting`.<br>• **Sandbox vs. Live Modes**: Safe sandbox default (`PAYMENT_GATEWAY_MODE=sandbox`) with authentic simulation; live mode strictly requires official merchant credentials. |
| **Phase 2: Security & PostgreSQL** | ✅ Active & Verified | • **PostgreSQL 18 is active** (`bookbazaar_db`, user: `bookbazaar_user`).<br>• Password hashing via Django PBKDF2/SHA256.<br>• Token-based authentication (`rest_framework.authtoken`).<br>• Ownership rules enforced (`IsOwnerOrReadOnly`): sellers can only edit/delete their own listings.<br>• Admin endpoints strictly protected (`IsAdminOnly`).<br>• Image validation (`bazaar/validators.py`) with Pillow memory verification. |
| **Phase 1: Core Marketplace** | ✅ Complete | • Multi-seller comparison by ISBN, education board, and grade/class.<br>• Buyer and seller accounts in the same user profile.<br>• Rs. 50 contact unlock fee (no book price collection, no escrow, no seller payouts).<br>• Deal confirmation and no-deal refund to internal wallet.<br>• Rating and review system. |

---

## 💳 Phase 3: Payment Gateway Architecture (JazzCash & Easypaisa)

### Business Model:
BookBazaar has a focused, lightweight payment model:
- **Contact Unlock Fee (Rs. 50 PKR)**: Buyer pays platform fee to unlock one selected seller's direct phone and WhatsApp contact.
- **Direct Handover**: The actual book price and delivery are arranged directly between buyer and seller. BookBazaar does **not** collect the book price, hold escrow, or handle seller payouts.
- **No Duplicate Charges**: The same buyer is never charged again for an already-unlocked listing. Database-level `unique_together = ('listing', 'buyer')` guarantees zero duplicate records.
- **Zero Self-Unlocks**: Users cannot unlock contact details for their own listings.

### Gateway Adapters (`bazaar/services/payment_service.py`):
1. **`JazzCashGatewayAdapter`**:
   - Supports official JazzCash MWALLET / HTTP Post Interface.
   - Calculates HMAC-SHA256 signature over alphanumeric sorted `pp_` parameters keyed with `JAZZCASH_INTEGRITY_SALT`.
   - Amount formatted in paisas (e.g. 5000 paisas for Rs. 50.00).
   - Verifies response code (`000` = success).
2. **`EasypaisaGatewayAdapter`**:
   - Supports official Easypaisa Open API / Direct Merchant Account.
   - Calculates HMAC-SHA256 signature using `EASYPAISA_HASH_KEY`.
   - Formats transaction amount in decimal PKR string (`50.00`).
   - Verifies response code (`0000` = success).
3. **`SafepayGatewayAdapter`**:
   - Debit / Credit Card test adapter.
4. **`WalletPaymentAdapter`**:
   - Instant in-app balance deduction with zero gateway fee.

### API Endpoints:
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/payments/initiate/` | Initiates transaction, returns transaction ID, amount, and gateway parameters with secure hash. |
| `POST` | `/api/payments/verify/` | Server-side cryptographic signature validation and contact unlock. |
| `POST` | `/api/payments/cancel/` | Cancels pending checkout transaction. |
| `POST` | `/api/payments/jazzcash/callback/` | Official JazzCash IPN / Return URL callback handler. |
| `POST` | `/api/payments/easypaisa/callback/` | Official Easypaisa IPN / Return URL callback handler. |
| `GET` | `/api/payments/transaction/<uuid>/` | Fetches transaction audit trail and status. |
| `POST` | `/api/unlocks/request/` | Unified backward-compatible contact unlock endpoint. |

### Sandbox vs. Live Configuration:
Set in `.env`:
```ini
# Sandbox Mode (Default - test cards/accounts simulate gateway authorization)
PAYMENT_GATEWAY_MODE=sandbox

# Live Mode (Requires official merchant credentials from Mobilink / Telenor Bank)
# PAYMENT_GATEWAY_MODE=live
# JAZZCASH_MERCHANT_ID=your_merchant_id
# JAZZCASH_PASSWORD=your_password
# JAZZCASH_INTEGRITY_SALT=your_integrity_salt
# EASYPAISA_STORE_ID=your_store_id
# EASYPAISA_HASH_KEY=your_hash_key
```

---

## 🛡️ Phase 4: Admin Dashboard & Marketplace Management

The BookBazaar Admin Dashboard is available at `/admin-panel/` (and standard Django admin at `/admin/`). Access is restricted to authorized platform administrators (`is_staff=True` via `IsAdminOnly` DRF permissions).

### Admin Portal Modules:
1. **📊 Overview & Analytics**: Live stats including registered users by role, active vs. sold listings, gateway distribution (JazzCash, Easypaisa, Wallet), retained unlock fees, and pending complaints badge.
2. **👥 User Management**: Search by username/phone, filter by role (Student, General Reader, Bookstore) and status (Active, Blocked). Real-time block and unblock actions with audit trail.
3. **📚 Listings Moderation**: Search, filter by status, approve pending listings, pause active listings, toggle sponsored status, edit book metadata, or delete fraudulent listings.
4. **🧑‍💼 Seller Activity Directory**: Overview of all sellers with active book count, books sold, contact unlocks received, and customer rating averages.
5. **💳 Payments & Unlocks Ledger**: Transaction ledger for all Rs. 50 contact unlocks with gateway breakdown, status badges, and an **Admin Force Refund** override that returns funds to the buyer's wallet in case of seller disputes.
6. **⚠️ Reports & Complaints Management**: Dedicated moderation pipeline where users report scams, piracy, or abuse. Admins can investigate, resolve, dismiss, and trigger one-click automated actions (e.g. deactivate listing, block seller).
7. **📢 Advertisement Manager**: Full campaign manager with banner previews, placement targeting, CTR tracking, and quick active toggling.
8. **⚙️ Platform Settings**: Dynamic control of unlock fee (Rs. 50 PKR default), auto-refund expiration timer, and listing approval policy.

### Admin API Endpoints:
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/admin/stats/` | Overview analytics, revenue summary, listing breakdown |
| `GET` | `/api/admin/users/` | User directory with search and role/status filtering |
| `GET` | `/api/admin/users/<id>/` | Deep-dive user audit trail (activity, listings, unlocks) |
| `POST`| `/api/admin/users/<id>/toggle_block/` | Block or unblock a user profile |
| `GET` | `/api/admin/listings/` | Listing moderation directory |
| `POST`| `/api/admin/listings/<id>/moderate/` | Action endpoint (`approve`, `reject`, `mark_sold`, `toggle_sponsored`, `delete`) |
| `PUT` | `/api/admin/listings/<id>/edit/` | Direct listing metadata edit |
| `GET` | `/api/admin/sellers/` | Seller activity and rating monitor |
| `GET` | `/api/admin/transactions/` | Payment gateway transaction ledger |
| `GET` | `/api/admin/unlocks/` | Contact unlock transaction ledger |
| `POST`| `/api/admin/unlocks/<id>/force_refund/` | Admin force refund override to buyer wallet |
| `GET` | `/api/admin/reports/` | Filterable user complaints directory |
| `POST`| `/api/admin/reports/<id>/resolve/` | Resolve or dismiss complaint with automated enforcement |
| `POST`| `/api/reports/submit/` | User complaint submission endpoint |
| `GET` | `/api/admin/ads/` | Advertisements list with CTR calculations |
| `POST`| `/api/admin/ads/create/` | Create advertisement |
| `PUT` | `/api/admin/ads/<id>/edit/` | Update advertisement |
| `POST`| `/api/admin/ads/<id>/toggle/` | Toggle active status |
| `DELETE`| `/api/admin/ads/<id>/delete/` | Delete advertisement |
| `GET`/`PUT`| `/api/admin/settings/` | Platform monetization & safety configuration |

---

## 🚀 Phase 5: Real-World Testing & Production Readiness

Phase 5 finalizes BookBazaar for production readiness, high-performance querying on PostgreSQL 18, bulletproof access control, and complete buyer/seller journey verification.

### Key Production Enhancements:
1. **Zero-Warning Production Settings**:
   - `python manage.py check --deploy` passes with **0 issues**.
   - HSTS (`SECURE_HSTS_SECONDS=31536000`), secure cookies (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`), and `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')` for reverse proxies.
   - Host protection (`ALLOWED_HOSTS`) and CORS/CSRF origin protections (`CSRF_TRUSTED_ORIGINS`).
2. **PostgreSQL High-Performance Indexing**:
   - B-tree and composite indexes on `Listing` (`status`, `city`, `created_at`, `is_sponsored`), `Book` (`category`, `education_board`, `grade_class`), `ContactUnlock` (`deal_status`, `payment_timestamp`), and `PaymentTransaction` (`gateway`, `status`).
   - Reusable connection pooling via `CONN_MAX_AGE = 600`.
3. **Static & Media Asset Delivery**:
   - **Whitenoise** (`CompressedManifestStaticFilesStorage`) automatically bundles, gzips, and hashes static assets.
   - Dedicated `requirements.txt` pinning framework dependencies.
4. **Production Deployment Suite (`deploy/`)**:
   - `deploy/production.env.example`: Secure environment configuration template.
   - `deploy/nginx.conf`: Nginx reverse proxy with SSL termination, HTTP/2, security headers, and static/media cache rules.
   - `deploy/gunicorn_conf.py`: High-concurrency WSGI runner with `(2 * CPU) + 1` worker threads.
   - `deploy/bookbazaar.service`: Systemd service unit file with auto-restart on failure.
   - `deploy/postgres_backup.sh`: Daily automated PostgreSQL `pg_dump` with gzip compression and 7-day backup rotation.

---

## 🧪 Automated Verification Test Suites

### 1. Phase 5 Real-World Testing & Production Readiness (12/12 Tests Passed)
```bash
python test_phase5_production_readiness.py
```
Verifies:
1. User registration, Token Auth, and Profile Update with real profile image
2. Book listing creation, search filtering, and multi-seller price comparison
3. Seller listing lifecycle: price edit, toggle active/sold, safe deletion
4. Buyer favorites lifecycle: add, list, and remove favorites
5. Contact unlock checkout via JazzCash and Easypaisa sandbox
6. Strict contact privacy lifecycle: phone masked before payment, revealed after
7. Duplicate charge & replay attack prevention (zero duplicate fees)
8. Security audit & ownership protection (403 on tampering, 400 on self-unlock)
9. Admin-only operations protection & user blocking enforcement
10. Image upload validation with Pillow memory verification (rejects fake files)
11. PostgreSQL active database & database performance indexes audit
12. Production settings, Whitenoise static storage, and CSRF trusted origins

### 2. Phase 4 Admin Management Suite (11/11 Tests Passed)
```bash
python test_phase4_admin.py
```
Verifies:
1. Admin Analytics API strictly protected and metrics verified
2. User management search, filtering, and blocking
3. Detailed user activity audit trail
4. Listing moderation actions (approve, sponsor, mark sold, delete)
5. Admin direct listing edit override
6. Seller performance & verification monitoring
7. Payment transactions & unlocks ledger filtering
8. Admin force refund override & wallet credit
9. Reports submission, moderation, and automated action
10. Advertisement full CRUD and CTR metrics
11. Platform monetization & safety policy settings

### 2. Phase 3 Payment Gateway Verification (15/15 Tests Passed)
```bash
python test_phase3_payments.py
```
Verifies:
1. Sandbox successful payment (JazzCash & Easypaisa)
2. Sandbox failed payment (Rejection handling)
3. Invalid signature rejection (Tampered HMAC-SHA256 signature)
4. Incorrect payment amount rejection (Amount mismatch validation)
5. Invalid transaction reference (404 on bad UUID)
6. Forged frontend success request rejection
7. Duplicate callback handling (Idempotent replay protection)
8. Duplicate unlock prevention (Zero duplicate fees / DB constraint)
9. Self-unlock rejection (Forbidden 400)
10. Contact privacy before payment (Phone masked `03XX-*******`)
11. Contact revealed after verified payment (Full phone & WhatsApp link)
12. Pending transaction behavior (No premature unlock access)
13. Cancelled transaction behavior (Status cancelled, blocked from verify)
14. Admin-configured dynamic platform fee behavior
15. Separate JazzCash and Easypaisa adapter architectures

### 2. Phase 2 Security & Marketplace Verification (10/10 Tests Passed)
```bash
python test_phase2_security.py
```

### 3. Phase 1 Core Marketplace Tests (13/13 Tests Passed)
```bash
python test_phase1_marketplace.py
```

### 4. Full Proposal End-to-End Test Suite (14/14 Tests Passed)
```bash
python test_all_features.py
```

---

## 🗄️ Database Management & Rollback Capability

### Active Database:
PostgreSQL 18 is active by default in `.env`:
```ini
USE_POSTGRES=True
DB_NAME=bookbazaar_db
DB_USER=bookbazaar_user
DB_HOST=127.0.0.1
DB_PORT=5432
```

### Switching Back to SQLite (Rollback):
To switch back to SQLite at any time:
1. Open `.env` and set:
   ```ini
   USE_POSTGRES=False
   ```
2. Restart the Django server. All original SQLite records in `db.sqlite3` remain completely untouched.

### Database Backup & Restore:
```bash
# Create fresh binary backup and UTF-8 JSON fixture
python scripts/db_backup_restore.py backup

# Check database record counts
python scripts/db_backup_restore.py counts

# Restore database from JSON
python scripts/db_backup_restore.py restore datadump_utf8.json
```

---

## 🛠️ Troubleshooting & Frequently Asked Questions

### 1. "Signature verification failed" error:
- Ensure `JAZZCASH_INTEGRITY_SALT` (for JazzCash) or `EASYPAISA_HASH_KEY` (for Easypaisa) matches between merchant portal and `.env`.
- In JazzCash, all `pp_` parameters must be sorted alphabetically before computing HMAC-SHA256.

### 2. Live payment credentials not found:
- When `PAYMENT_GATEWAY_MODE=live`, missing credentials raise `LiveCredentialsRequiredError`.
- For development and student testing, keep `PAYMENT_GATEWAY_MODE=sandbox` in `.env`.

### 3. Contact number still masked after payment:
- The seller contact is only unmasked when the transaction status reaches `completed`.
- If a payment is in `pending` or `failed` state, the seller phone remains masked (`03XX-*******`) for privacy protection.

### 4. Running both PostgreSQL and Django:
```bash
# Verify PostgreSQL is active:
python -c "import django; django.setup(); from django.db import connection; print(connection.vendor)"
# Outputs: postgresql
```

### 5. "ERR_CONNECTION_REFUSED" or "can't open file manage.py":
- **Important**: `manage.py` is located in the **project root folder** (`C:\Users\Microsoft\Desktop\fypfinal`), NOT in `bookbazaar_backend`!
- If your terminal is inside `fypfinal\bookbazaar_backend`, type `cd ..` to return to the root folder.
- **Starting the server properly**:
  ```powershell
  cd C:\Users\Microsoft\Desktop\fypfinal
  python manage.py runserver 127.0.0.1:8000
  ```
- Or simply double-click:
  ```
  run_bookbazaar.bat
  ```
- Open `http://127.0.0.1:8000/` in Chrome.
- Admin Panel is accessible at `http://127.0.0.1:8000/admin-panel/`.

---

## 📋 Commercial Production & Gateway Status Classification

| Category | Features & Capabilities | Operational Status |
| :--- | :--- | :--- |
| **Fully Completed & Operational** | • Core marketplace buy/sell, book catalog & ISBN barcode scanner.<br>• Multi-seller price comparison & savings calculator.<br>• User accounts with dual buyer/seller capabilities.<br>• Secure Token-based authentication & PBKDF2/SHA256 password hashing.<br>• Strict ownership authorization (`IsOwnerOrReadOnly`) & image validation (Pillow).<br>• Seller contact masking & conditional unmasking after unlock.<br>• Complete 8-module Admin Dashboard at `/admin-panel/`.<br>• User moderation, listing moderation, dispute reports, and admin force refunds.<br>• PostgreSQL 18 active database with performance composite & B-tree indexes.<br>• Whitenoise static file serving & zero-warning deploy check (`python manage.py check --deploy`).<br>• Nginx, Gunicorn, Systemd, and Automated Daily DB Backup configurations. | ✅ **100% Complete & Active** |
| **Sandbox-Verified Features** | • JazzCash MWALLET Sandbox Checkout & HMAC-SHA256 signature verification.<br>• Easypaisa Open API Sandbox Checkout & Hash verification.<br>• Replay attack protection & duplicate charge prevention.<br>• Contact unlock fee retention vs. cancellation wallet refund lifecycle.<br>• Simulated payment failure and tampered signature rejection handling. | 🧪 **100% Verified in Sandbox Mode** |
| **Pending External Business Verification** | • Official Mobilink JazzCash Corporate Merchant Production Credentials.<br>• Official Telenor Easypaisa Corporate Merchant Production Credentials.<br>• Domain registration (`bookbazaar.pk`) and public DNS records.<br>• Production VPS / Cloud server provisioning (e.g. DigitalOcean, AWS, Linode). | ⚠️ **Awaiting Commercial Merchant Approval & Hosting Provisioning** (Safely isolated via `PAYMENT_GATEWAY_MODE=sandbox`) |
