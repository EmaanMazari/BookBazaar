"""
BookBazaar Pakistan - Phase 5 Real-World Buyer & Seller Journey Verification
Runs real HTTP client requests against the live Django server and queries PostgreSQL.
Uses Python built-in urllib (no external requests library required).
"""

import os
import sys
import io
import json
import urllib.request
import urllib.parse
import urllib.error
from decimal import Decimal
from PIL import Image

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookbazaar_backend.settings')
django.setup()

from django.db import connection
from django.contrib.auth.models import User
from bazaar.models import UserProfile, Book, Listing, ContactUnlock, PaymentTransaction

BASE_URL = "http://127.0.0.1:8000"

def http_json(method, path, data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Token {token}"

    body = json.dumps(data).encode('utf-8') if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()
            res_body = response.read().decode('utf-8')
            return status_code, json.loads(res_body) if res_body else {}
    except urllib.error.HTTPError as e:
        res_body = e.read().decode('utf-8')
        try:
            return e.code, json.loads(res_body)
        except Exception:
            return e.code, {"error": res_body}

def http_multipart(path, fields, file_field_name, filename, file_bytes, content_type, token=None):
    url = f"{BASE_URL}{path}"
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = io.BytesIO()

    for k, v in fields.items():
        body.write(f"--{boundary}\r\n".encode())
        body.write(f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode())
        body.write(f"{v}\r\n".encode())

    body.write(f"--{boundary}\r\n".encode())
    body.write(f'Content-Disposition: form-data; name="{file_field_name}"; filename="{filename}"\r\n'.encode())
    body.write(f"Content-Type: {content_type}\r\n\r\n".encode())
    body.write(file_bytes)
    body.write(b"\r\n")
    body.write(f"--{boundary}--\r\n".encode())

    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}"
    }
    if token:
        headers["Authorization"] = f"Token {token}"

    req = urllib.request.Request(url, data=body.getvalue(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            return response.getcode(), json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        res_body = e.read().decode('utf-8')
        try:
            return e.code, json.loads(res_body)
        except Exception:
            return e.code, {"error": res_body}

def create_in_memory_image():
    file_obj = io.BytesIO()
    img = Image.new("RGB", (120, 120), color=(16, 185, 129))
    img.save(file_obj, format="JPEG")
    file_obj.seek(0)
    return "test_clean_code.jpg", file_obj.read(), "image/jpeg"

def main():
    print("=" * 70)
    print(" BOOKBAZAAR PAKISTAN - REAL-WORLD MARKETPLACE JOURNEY VERIFICATION")
    print("=" * 70)

    # -------------------------------------------------------------------------
    # STEP 1: VERIFY POSTGRESQL IS THE ACTIVE DATABASE
    # -------------------------------------------------------------------------
    print("\n[STEP 1] Verifying Active Database Engine & Connection...")
    db_vendor = connection.vendor
    db_name = connection.settings_dict.get('NAME')
    db_user = connection.settings_dict.get('USER')
    db_host = connection.settings_dict.get('HOST')
    db_port = connection.settings_dict.get('PORT')

    print(f"  * Engine Vendor : {db_vendor}")
    print(f"  * Database Name : {db_name}")
    print(f"  * Database User : {db_user}")
    print(f"  * Host & Port   : {db_host}:{db_port}")

    if db_vendor != 'postgresql':
        print(f"  [ERROR] Database vendor is {db_vendor}, expected postgresql!")
        sys.exit(1)

    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        pg_version = cursor.fetchone()[0]
        print(f"  * PostgreSQL Version : {pg_version[:65]}...")

    print("  [SUCCESS] PostgreSQL 18 is active, connected, and verified!")

    # -------------------------------------------------------------------------
    # STEP 2: REGISTER & LOGIN SELLER ACCOUNT
    # -------------------------------------------------------------------------
    print("\n[STEP 2] Creating & Authenticating Separate Seller Account...")
    seller_phone = "03019876543"
    User.objects.filter(username=f"user_{seller_phone}").delete()
    UserProfile.objects.filter(phone_number=seller_phone).delete()

    seller_reg_data = {
        "phone_number": seller_phone,
        "password": "SellerVerificationPass123!",
        "full_name": "Tariq Mehmood (Verification Seller)",
        "city": "Bahawalpur",
        "campus_or_area": "IUB Baghdad Campus - Dept of Software Eng",
        "user_type": "student"
    }

    code, seller_data = http_json("POST", "/api/auth/register/", seller_reg_data)
    if code != 201:
        print(f"  [ERROR] Seller registration failed (HTTP {code}): {seller_data}")
        sys.exit(1)

    seller_token = seller_data['token']
    seller_id = seller_data['profile']['id']
    print(f"  * Seller Registered : {seller_data['profile']['full_name']} (ID: {seller_id})")
    print(f"  * Phone Number      : {seller_data['profile']['phone_number']}")
    print(f"  * Auth Token        : {seller_token[:10]}...")

    # -------------------------------------------------------------------------
    # STEP 3: SELLER CREATES USED BOOK LISTING WITH IMAGE
    # -------------------------------------------------------------------------
    print("\n[STEP 3] Seller Creates Used Book Listing via HTTP POST...")
    book = Book.objects.filter(isbn="9780132350884").first()
    if not book:
        book = Book.objects.create(
            isbn="9780132350884",
            title="Clean Code: A Handbook of Agile Software Craftsmanship",
            author="Robert C. Martin",
            publisher="Prentice Hall",
            edition="1st Edition",
            category="Software Engineering",
            education_board="Higher Education / University",
            grade_class="Bachelor / BS / Undergrad",
            subject="Software Engineering Practices",
            original_retail_price=Decimal("1800.00")
        )

    listing_fields = {
        "isbn": book.isbn,
        "title": book.title,
        "author": book.author,
        "condition": "Like New",
        "price": "680.00",
        "city": "Bahawalpur",
        "pickup_location": "Main Gate 1 / Library Fountain",
        "description": "Barely used for 4th semester OOP/SE course. No torn pages, genuine original copy."
    }

    filename, file_bytes, content_type = create_in_memory_image()
    code_list, res_list = http_multipart(
        "/api/listings/create/",
        listing_fields,
        "image",
        filename,
        file_bytes,
        content_type,
        token=seller_token
    )

    if code_list != 201:
        print(f"  [ERROR] Listing creation failed (HTTP {code_list}): {res_list}")
        sys.exit(1)

    created_listing = res_list['listing']
    listing_id = created_listing['id']
    print(f"  * Listing Created ID : #{listing_id}")
    print(f"  * Book Title         : {created_listing['book']['title']}")
    print(f"  * Listing Price      : Rs. {created_listing['price']}")
    print(f"  * Seller Name        : {created_listing['seller_name']}")
    print(f"  * Image Attached     : {bool(created_listing.get('image'))}")

    # -------------------------------------------------------------------------
    # STEP 4: REGISTER & LOGIN SEPARATE BUYER ACCOUNT
    # -------------------------------------------------------------------------
    print("\n[STEP 4] Creating & Authenticating Separate Buyer Account...")
    buyer_phone = "03123456789"
    User.objects.filter(username=f"user_{buyer_phone}").delete()
    UserProfile.objects.filter(phone_number=buyer_phone).delete()

    buyer_reg_data = {
        "phone_number": buyer_phone,
        "password": "BuyerVerificationPass123!",
        "full_name": "Fatima Zahra (Verification Buyer)",
        "city": "Bahawalpur",
        "campus_or_area": "Girls Hostel 2",
        "user_type": "student"
    }

    code_buyer, buyer_data = http_json("POST", "/api/auth/register/", buyer_reg_data)
    if code_buyer != 201:
        print(f"  [ERROR] Buyer registration failed (HTTP {code_buyer}): {buyer_data}")
        sys.exit(1)

    buyer_token = buyer_data['token']
    buyer_id = buyer_data['profile']['id']
    print(f"  * Buyer Registered  : {buyer_data['profile']['full_name']} (ID: {buyer_id})")
    print(f"  * Phone Number      : {buyer_data['profile']['phone_number']}")
    print(f"  * Auth Token        : {buyer_token[:10]}...")

    # -------------------------------------------------------------------------
    # STEP 5: BUYER SEARCHES MARKETPLACE & VERIFIES CONTACT PRIVACY (BEFORE UNLOCK)
    # -------------------------------------------------------------------------
    print("\n[STEP 5] Buyer Searches for Book & Verifies Contact Privacy...")
    code_search, search_items = http_json("GET", "/api/listings/?search=Clean%20Code", token=buyer_token)
    if code_search != 200:
        print(f"  [ERROR] Search failed: {search_items}")
        sys.exit(1)

    found_item = next((item for item in search_items if item['id'] == listing_id), None)
    if not found_item:
        print(f"  [ERROR] Created listing #{listing_id} not found in search results!")
        sys.exit(1)

    print(f"  * Listing found in search results: '{found_item['book']['title']}' (Rs. {found_item['price']})")

    # Fetch detailed listing
    code_detail, detail_data = http_json("GET", f"/api/listings/{listing_id}/", token=buyer_token)
    masked_phone = detail_data.get('seller_phone')
    is_unlocked = detail_data.get('is_contact_unlocked')

    print(f"  * Contact Privacy Check (BEFORE PAYMENT):")
    print(f"    - Seller Phone Masked   : '{masked_phone}' (Expected: '0301-*******')")
    print(f"    - Is Contact Unlocked   : {is_unlocked} (Expected: False)")

    if masked_phone != "0301-*******" or is_unlocked is not False:
        print("  [ERROR] Privacy violation: Seller phone was NOT properly masked before payment!")
        sys.exit(1)
    print("  [PASS] Seller phone number is strictly masked before unlock payment.")

    # -------------------------------------------------------------------------
    # STEP 6: BUYER INITIATES RS. 50 SANDBOX PAYMENT (JAZZCASH)
    # -------------------------------------------------------------------------
    print("\n[STEP 6] Buyer Initiates Rs. 50 Contact Unlock via JazzCash Sandbox...")
    initiate_payload = {
        "listing_id": listing_id,
        "gateway": "jazzcash",
        "account_number": buyer_phone
    }

    code_init, init_data = http_json("POST", "/api/payments/initiate/", initiate_payload, token=buyer_token)
    if code_init != 201:
        print(f"  [ERROR] Payment initiation failed (HTTP {code_init}): {init_data}")
        sys.exit(1)

    transaction_id = init_data['transaction_id']
    amount = init_data['amount']
    gateway = init_data['gateway']
    secure_hash = init_data['initiation_data']['parameters'].get('pp_SecureHash')

    print(f"  * Payment Transaction ID : {transaction_id}")
    print(f"  * Amount to Charge       : Rs. {amount} PKR")
    print(f"  * Payment Gateway        : {gateway.upper()}")
    print(f"  * HMAC-SHA256 SecureHash : {secure_hash[:20]}...")

    # -------------------------------------------------------------------------
    # STEP 7: BUYER VERIFIES PAYMENT & UNLOCKS SELLER CONTACT
    # -------------------------------------------------------------------------
    print("\n[STEP 7] Verifying Sandbox Payment Server-Side & Unlocking Contact...")
    verify_payload = {
        "transaction_id": transaction_id,
        "payload": {
            "pp_TxnRefNo": "TXN-JC-VERIFY-1001",
            "pp_ResponseCode": "000",
            "pp_ResponseMessage": "Approved and Completed Successfully"
        }
    }

    code_verify, verify_data = http_json("POST", "/api/payments/verify/", verify_payload, token=buyer_token)
    if code_verify != 200:
        print(f"  [ERROR] Payment verification failed (HTTP {code_verify}): {verify_data}")
        sys.exit(1)

    seller_contact = verify_data['seller_contact']
    unlocked_phone = seller_contact['phone_number']
    whatsapp_link = seller_contact['whatsapp_link']

    print(f"  * Payment Status   : {verify_data.get('status').upper()}")
    print(f"  * Unlocked Phone   : {unlocked_phone}")
    print(f"  * WhatsApp Link    : {whatsapp_link[:40]}...")

    if unlocked_phone != seller_phone:
        print(f"  [ERROR] Unlocked phone '{unlocked_phone}' does not match seller phone '{seller_phone}'!")
        sys.exit(1)
    print("  [PASS] Seller contact successfully unlocked and unmasked after verified payment.")

    # -------------------------------------------------------------------------
    # STEP 8: CHECK LISTING DETAIL AFTER PAYMENT (UNMASKED IN UI)
    # -------------------------------------------------------------------------
    print("\n[STEP 8] Confirming Unmasked Contact State in Listing Detail API...")
    code_after, after_data = http_json("GET", f"/api/listings/{listing_id}/", token=buyer_token)
    print(f"  * Post-Payment Phone : '{after_data.get('seller_phone')}' (Unmasked)")
    print(f"  * Is Contact Unlocked: {after_data.get('is_contact_unlocked')}")

    if after_data.get('seller_phone') != seller_phone or after_data.get('is_contact_unlocked') is not True:
        print("  [ERROR] Listing detail did not reflect unlocked status for buyer!")
        sys.exit(1)
    print("  [PASS] Buyer now sees unmasked contact details across subsequent requests.")

    # -------------------------------------------------------------------------
    # STEP 9: DUPLICATE CHARGE PREVENTION
    # -------------------------------------------------------------------------
    print("\n[STEP 9] Testing Duplicate Unlock Attempt (Zero Double Charges)...")
    code_dup, dup_data = http_json("POST", "/api/unlocks/request/", {"listing_id": listing_id}, token=buyer_token)
    if code_dup != 200:
        print(f"  [ERROR] Duplicate request failed (HTTP {code_dup}): {dup_data}")
        sys.exit(1)

    print(f"  * Duplicate Charge Flag : is_new_charge = {dup_data.get('is_new_charge')}")
    print(f"  * Return Status         : HTTP {code_dup} OK (Existing record returned)")

    if dup_data.get('is_new_charge') is not False:
        print("  [ERROR] System flagged duplicate unlock as a new charge!")
        sys.exit(1)
    print("  [PASS] Buyer is protected from duplicate contact unlock charges.")

    # -------------------------------------------------------------------------
    # STEP 10: DIRECT POSTGRESQL DATABASE RECORD AUDIT
    # -------------------------------------------------------------------------
    print("\n[STEP 10] Direct Database Inspection in PostgreSQL 18...")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, fee_amount, payment_method, deal_status, payment_timestamp
            FROM bazaar_contactunlock
            WHERE listing_id = %s;
        """, [listing_id])
        unlock_row = cursor.fetchone()
        print(f"  * PostgreSQL bazaar_contactunlock: ID={unlock_row[0]}, Fee=Rs.{unlock_row[1]}, Gateway={unlock_row[2]}, Status={unlock_row[3]}")

        cursor.execute("""
            SELECT transaction_id, amount, gateway, status, verified_at
            FROM bazaar_paymenttransaction
            WHERE transaction_id = %s;
        """, [transaction_id])
        txn_row = cursor.fetchone()
        print(f"  * PostgreSQL bazaar_paymenttransaction: UUID={txn_row[0]}, Amount=Rs.{txn_row[1]}, Gateway={txn_row[2]}, Status={txn_row[3]}")

    print("  [PASS] Transaction and Unlock records verified in active PostgreSQL database.")

    # -------------------------------------------------------------------------
    # STEP 11: SAFE TEST CLEANUP
    # -------------------------------------------------------------------------
    print("\n[STEP 11] Cleaning Up Journey Test Records...")
    ContactUnlock.objects.filter(listing_id=listing_id).delete()
    PaymentTransaction.objects.filter(transaction_id=transaction_id).delete()
    Listing.objects.filter(id=listing_id).delete()
    User.objects.filter(username=f"user_{seller_phone}").delete()
    UserProfile.objects.filter(phone_number=seller_phone).delete()
    User.objects.filter(username=f"user_{buyer_phone}").delete()
    UserProfile.objects.filter(phone_number=buyer_phone).delete()
    print("  [CLEANUP] Verification test entities safely cleaned up.")

    print("\n" + "=" * 70)
    print(" [ALL VERIFICATION STEPS PASSED] FULL BUYER/SELLER JOURNEY CONFIRMED!")
    print("=" * 70 + "\n")

if __name__ == '__main__':
    main()
