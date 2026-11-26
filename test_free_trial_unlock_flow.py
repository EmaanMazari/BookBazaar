import os
import sys
import json
import random
from decimal import Decimal
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookbazaar_backend.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from bazaar.models import UserProfile, Book, Listing, ContactUnlock, PlatformSetting

def run_tests():
    client = Client()
    print("==========================================================")
    print("   BOOKZY AI: FREE TRIAL & PAID UNLOCK VERIFICATION       ")
    print("==========================================================")

    # 1. Setup Seller & Buyer
    seller_phone = f"0331{random.randint(1000000, 9999999)}"
    seller_user = User.objects.create_user(username=f"seller_{seller_phone}", password="Password123!")
    seller = UserProfile.objects.create(
        user=seller_user,
        full_name="Tariq Baloch",
        phone_number=seller_phone,
        city="Quetta",
        campus_or_area="Jinnah Road",
        user_type="student"
    )

    buyer_phone = f"0345{random.randint(1000000, 9999999)}"
    buyer_user = User.objects.create_user(username=f"buyer_{buyer_phone}", password="Password123!")
    buyer = UserProfile.objects.create(
        user=buyer_user,
        full_name="Farhan Khan",
        phone_number=buyer_phone,
        city="Quetta",
        campus_or_area="Model Town",
        user_type="student",
        wallet_balance=Decimal('200.00')
    )

    # 2. Test Demo Login / Token Sync
    demo_login_res = client.post('/api/auth/demo_login/', data=json.dumps({'user_id': buyer.id}), content_type='application/json')
    assert demo_login_res.status_code == 200, f"Demo login failed: {demo_login_res.content}"
    token_key = demo_login_res.json()['token']
    assert token_key, "Token must be returned"
    print("[PASS] 01. Demo login / token sync succeeded.")

    auth_headers = {'HTTP_AUTHORIZATION': f'Token {token_key}'}

    # Create 3 active listings
    b1 = Book.objects.create(isbn=f"978{random.randint(1000000000, 9999999999)}", title="Balochistan Physics 11", author="Prof. Ahmed")
    l1 = Listing.objects.create(book=b1, seller=seller, price=Decimal('180.00'), condition='Like New', status='active')

    b2 = Book.objects.create(isbn=f"978{random.randint(1000000000, 9999999999)}", title="Punjab Chemistry 12", author="Dr. Qasim")
    l2 = Listing.objects.create(book=b2, seller=seller, price=Decimal('220.00'), condition='Good', status='active')

    b3 = Book.objects.create(isbn=f"978{random.randint(1000000000, 9999999999)}", title="Sindh Biology 10", author="Dr. Noman")
    l3 = Listing.objects.create(book=b3, seller=seller, price=Decimal('250.00'), condition='Fair', status='active')

    # 3. Test Trial Status endpoint initially
    status_res = client.get(f'/api/unlocks/trial-status/?user_id={buyer.id}', **auth_headers)
    assert status_res.status_code == 200
    st_data = status_res.json()
    assert st_data['unlocks_used'] == 0
    assert st_data['free_remaining'] == 2
    assert st_data['is_free_trial'] is True
    print("[PASS] 02. Initial trial status: 0 used, 2 remaining, is_free_trial=True.")

    # 4. Test Free Trial Unlock #1 (Live frontend payload with Token)
    p1 = {
        'listing_id': l1.id,
        'buyer_id': buyer.id,
        'user_id': buyer.id,
        'payment_method': 'free_trial',
        'gateway': 'free_trial',
        'amount': 0,
        'account_number': ''
    }
    u1_res = client.post('/api/unlocks/request/', data=json.dumps(p1), content_type='application/json', **auth_headers)
    assert u1_res.status_code == 201, f"Free Trial #1 failed: {u1_res.content}"
    u1_data = u1_res.json()
    assert u1_data['trial_info']['unlocks_used'] == 1
    assert u1_data['trial_info']['free_remaining'] == 1
    assert u1_data['trial_info']['is_free_trial'] is True
    assert Decimal(str(u1_data['unlock']['fee_amount'])) == Decimal('0.00')
    assert u1_data['seller_contact']['phone_number'] == seller_phone
    assert u1_data['seller_contact']['full_name'] == "Tariq Baloch"
    assert "https://wa.me/" in u1_data['seller_contact']['whatsapp_link']
    print("[PASS] 03. Free Trial Unlock #1 succeeded (Rs. 0, contact revealed, 1 of 2 remaining).")

    # 5. Test Idempotent Duplicate Unlock (Same Listing) -> 200 OK without re-charging
    dup_res = client.post('/api/unlocks/request/', data=json.dumps(p1), content_type='application/json', **auth_headers)
    assert dup_res.status_code == 200
    dup_data = dup_res.json()
    assert dup_data['is_new_charge'] is False
    assert dup_data['seller_contact']['phone_number'] == seller_phone
    print("[PASS] 04. Duplicate unlock returned 200 OK with seller contact and no new charge.")

    # 6. Test Free Trial Unlock #2 (Calling /api/unlocks/ root route without auth header, using buyer_id in payload)
    p2 = {
        'listing_id': l2.id,
        'buyer_id': buyer.id,
        'user_id': buyer.id,
        'payment_method': 'free_trial',
        'gateway': 'free_trial',
        'amount': 0,
        'account_number': ''
    }
    u2_res = client.post('/api/unlocks/', data=json.dumps(p2), content_type='application/json')
    assert u2_res.status_code == 201, f"Free Trial #2 failed: {u2_res.content}"
    u2_data = u2_res.json()
    assert u2_data['trial_info']['unlocks_used'] == 2
    assert u2_data['trial_info']['free_remaining'] == 0
    assert u2_data['trial_info']['is_free_trial'] is False
    assert Decimal(str(u2_data['unlock']['fee_amount'])) == Decimal('0.00')
    assert u2_data['seller_contact']['phone_number'] == seller_phone
    print("[PASS] 05. Free Trial Unlock #2 succeeded via /api/unlocks/ with fallback buyer_id resolution (0 of 2 remaining).")

    # 7. Test Attempting Free Trial #3 when 2 unlocks already used -> 400 Bad Request
    p3_free = {
        'listing_id': l3.id,
        'buyer_id': buyer.id,
        'user_id': buyer.id,
        'payment_method': 'free_trial',
        'gateway': 'free_trial',
        'amount': 0
    }
    u3_fail = client.post('/api/unlocks/request/', data=json.dumps(p3_free), content_type='application/json', **auth_headers)
    assert u3_fail.status_code == 400, f"Expected 400 when free trial exhausted, got: {u3_fail.status_code}"
    assert "used your 2 free contact unlocks" in u3_fail.json()['error']
    print("[PASS] 06. Free Trial #3 rejected when trial exhausted (clean server error message returned).")

    # 8. Test Paid Unlock #3 with Standard Fee (Rs. 50 via jazzcash or wallet) -> 201 Created
    p3_paid = {
        'listing_id': l3.id,
        'buyer_id': buyer.id,
        'user_id': buyer.id,
        'payment_method': 'jazzcash',
        'gateway': 'jazzcash',
        'amount': 50,
        'account_number': '03001234567'
    }
    u3_res = client.post('/api/unlocks/request/', data=json.dumps(p3_paid), content_type='application/json', **auth_headers)
    assert u3_res.status_code == 201, f"Paid unlock failed: {u3_res.content}"
    u3_data = u3_res.json()
    assert Decimal(str(u3_data['unlock']['fee_amount'])) == Decimal('50.00')
    assert u3_data['seller_contact']['phone_number'] == seller_phone
    print("[PASS] 07. Paid Unlock #3 succeeded (Rs. 50 charged, contact revealed).")

    # 9. Test Self-Unlock Prevention -> 400 Bad Request
    self_unlock = client.post('/api/unlocks/request/', data=json.dumps({
        'listing_id': l1.id,
        'buyer_id': seller.id,
        'user_id': seller.id
    }), content_type='application/json')
    assert self_unlock.status_code == 400
    assert "cannot unlock contact details for your own" in self_unlock.json()['error']
    print("[PASS] 08. Self-unlock prevention blocked seller with 400 Bad Request.")

    # 10. Test Anonymous Request with No Buyer ID -> 401 Unauthorized
    anon_client = Client()
    anon_unlock = anon_client.post('/api/unlocks/request/', data=json.dumps({
        'listing_id': l1.id
    }), content_type='application/json')
    assert anon_unlock.status_code == 401
    print("[PASS] 09. Anonymous unauthenticated request correctly rejected with 401 Unauthorized.")

    # 11. Test /api/unlocks/initiate/ with Free Trial on fresh buyer -> 201 Created with contact details
    fresh_phone = f"0319{random.randint(1000000, 9999999)}"
    fresh_user = User.objects.create_user(username=f"fresh_{fresh_phone}", password="Password123!")
    fresh_buyer = UserProfile.objects.create(user=fresh_user, full_name="Fresh Buyer", phone_number=fresh_phone, city="Lahore")
    
    b4 = Book.objects.create(isbn=f"978{random.randint(1000000000, 9999999999)}", title="Test Book 4", author="Author 4")
    l4 = Listing.objects.create(book=b4, seller=seller, price=Decimal('300.00'), condition='New', status='active')
    
    initiate_res = client.post('/api/unlocks/initiate/', data=json.dumps({
        'listing_id': l4.id,
        'buyer_id': fresh_buyer.id,
        'gateway': 'free_trial'
    }), content_type='application/json')
    assert initiate_res.status_code in [200, 201], f"Initiate free trial failed: {initiate_res.content}"
    init_data = initiate_res.json()
    assert init_data['seller_contact']['phone_number'] == seller_phone
    print("[PASS] 10. /api/unlocks/initiate/ returned 201 with contact details immediately for free trial.")

    print("\n==========================================================")
    print("   ALL 10 FREE TRIAL & UNLOCK VERIFICATION TESTS PASSED!   ")
    print("==========================================================")

if __name__ == '__main__':
    run_tests()
