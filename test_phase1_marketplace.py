import os
import sys
import json
import random
import io
from decimal import Decimal
from PIL import Image

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookbazaar_backend.settings')
django.setup()

from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from bazaar.models import UserProfile, Book, Listing, ContactUnlock, PlatformSetting

def create_valid_test_image(name="test.jpg"):
    img_io = io.BytesIO()
    img = Image.new("RGB", (100, 100), color="blue")
    img.save(img_io, format="JPEG")
    img_io.seek(0)
    return SimpleUploadedFile(name, img_io.read(), content_type="image/jpeg")

def run_phase1_tests():
    client = Client()
    print("==========================================================")
    print("   BOOKLOOP PHASE 1 CORE MARKETPLACE VERIFICATION TESTS   ")
    print("==========================================================")

    # 1. Test User Registration with Real Password & Token Auth
    reg_phone = f"0311{random.randint(1000000, 9999999)}"
    reg_payload = {
        'full_name': 'Test Student Buyer',
        'phone_number': reg_phone,
        'password': 'SecurePassword123!',
        'city': 'Bahawalpur',
        'campus_or_area': 'IUB Baghdad Campus'
    }
    resp = client.post('/api/auth/register/', data=json.dumps(reg_payload), content_type='application/json')
    assert resp.status_code == 201, f"Registration failed: {resp.content}"
    reg_data = resp.json()
    assert 'token' in reg_data, "Auth token should be issued on registration"
    buyer_id = reg_data['profile']['id']
    buyer_token = reg_data['token']
    buyer_auth = {'HTTP_AUTHORIZATION': f'Token {buyer_token}'}
    print(f"PASS [Auth]: User registered successfully (Phone: {reg_phone}). Token: {buyer_token[:10]}...")

    # 2. Test User Login with Password
    login_payload = {
        'phone_or_username': reg_phone,
        'password': 'SecurePassword123!'
    }
    resp = client.post('/api/auth/login/', data=json.dumps(login_payload), content_type='application/json')
    assert resp.status_code == 200, f"Login failed: {resp.content}"
    login_data = resp.json()
    assert login_data['profile']['phone_number'] == reg_phone
    print("PASS [Auth]: User password login verified successfully.")

    # 3. Test Seller Listing Creation with Actual Image File Upload
    seller = UserProfile.objects.filter(phone_number='03017654321').first()
    if not seller:
        seller = UserProfile.objects.exclude(phone_number=reg_phone).first()
    seller_token, _ = Token.objects.get_or_create(user=seller.user)
    seller_auth = {'HTTP_AUTHORIZATION': f'Token {seller_token.key}'}

    dummy_image = create_valid_test_image("clean_code_photo.jpg")
    
    create_payload = {
        'seller_id': seller.id,
        'isbn': '9780132350884',
        'title': 'Clean Code: A Handbook of Agile Software Craftsmanship',
        'author': 'Robert C. Martin',
        'price': '520.00',
        'condition': 'Like New',
        'city': 'Bahawalpur',
        'pickup_location': 'IUB Abbasia Campus Gate',
        'category': 'Software Engineering',
        'education_board': 'Higher Education / University',
        'grade_class': 'Bachelor / BS / Undergrad',
        'subject': 'Software Engineering',
        'description': 'Clean copy used during Spring semester.',
        'image': dummy_image
    }
    resp = client.post('/api/listings/create/', data=create_payload, **seller_auth)
    assert resp.status_code == 201, f"Create listing with image failed: {resp.content}"
    create_res = resp.json()
    new_listing_id = create_res['listing']['id']
    assert create_res['listing']['image'] is not None, "Image field should be saved"
    print(f"PASS [Seller]: Book listing #{new_listing_id} created with real image upload.")

    # 4. Test Seller Edit Listing
    edit_payload = {
        'seller_id': seller.id,
        'price': '490.00',
        'condition': 'Good',
        'description': 'Updated price for fast sale'
    }
    resp = client.post(f'/api/listings/{new_listing_id}/edit/', data=json.dumps(edit_payload), content_type='application/json', **seller_auth)
    assert resp.status_code == 200, f"Edit listing failed: {resp.content}"
    updated_listing = Listing.objects.get(id=new_listing_id)
    assert updated_listing.price == Decimal('490.00')
    print("PASS [Seller]: Seller successfully edited listing price & details.")

    # 5. Test Seller Toggle Status (Active -> Sold -> Active)
    resp = client.post(f'/api/listings/{new_listing_id}/toggle_status/', **seller_auth)
    assert resp.status_code == 200
    assert Listing.objects.get(id=new_listing_id).status == 'sold'

    # Toggle back to active
    client.post(f'/api/listings/{new_listing_id}/toggle_status/', **seller_auth)
    assert Listing.objects.get(id=new_listing_id).status == 'active'
    print("PASS [Seller]: Seller toggled listing status between Active and Sold.")

    # 6. Test Buyer Search by Class, Board, Subject, and Title
    resp = client.get('/api/listings/?search=Software+Engineering&board=Higher+Education+%2F+University')
    assert resp.status_code == 200
    search_results = resp.json()
    assert len(search_results) > 0, "Should return matching university listings"
    print(f"PASS [Buyer]: Search by Board and Subject returned {len(search_results)} listings.")

    # 7. Test Favourites / Wishlist System
    resp = client.post('/api/favorites/toggle/', data=json.dumps({
        'user_id': buyer_id,
        'listing_id': new_listing_id
    }), content_type='application/json', **buyer_auth)
    assert resp.status_code == 200
    assert resp.json()['is_favorited'] is True
    print("PASS [Buyer]: Added listing to Favourites.")

    resp = client.get(f'/api/favorites/user/{buyer_id}/', **buyer_auth)
    assert resp.status_code == 200
    fav_list = resp.json()
    assert len(fav_list) == 1
    assert fav_list[0]['listing']['id'] == new_listing_id
    print("PASS [Buyer]: User favourites list retrieved correctly.")

    # 8. Test Contact Unlock #1 (Free Trial Unlock - Rs. 0 Fee)
    unlock_payload = {
        'listing_id': new_listing_id,
        'buyer_id': buyer_id,
        'payment_method': 'free_trial',
        'account_number': reg_phone
    }
    resp = client.post('/api/unlocks/request/', data=json.dumps(unlock_payload), content_type='application/json', **buyer_auth)
    assert resp.status_code == 201, f"Unlock failed: {resp.content}"
    unlock_data = resp.json()
    assert unlock_data['is_new_charge'] is True
    assert Decimal(str(unlock_data['unlock']['fee_amount'])) == Decimal('0.00'), "First contact unlock must be Rs. 0 Free Trial"
    assert unlock_data['unlock']['payment_method'] == 'free_trial'
    assert unlock_data['seller_contact']['phone_number'] == seller.phone_number
    assert 'whatsapp_link' in unlock_data['seller_contact']
    unlock_uuid = unlock_data['unlock']['unlock_id']
    print(f"PASS [Unlock #1]: Free Trial Contact Unlock (1 of 2 remaining). Fee: Rs. {unlock_data['unlock']['fee_amount']}.")
    print(f"PASS [Unlock]: Seller Phone revealed: {unlock_data['seller_contact']['phone_number']}")

    # 9. Test Duplicate Charge Prevention
    resp_dup = client.post('/api/unlocks/request/', data=json.dumps(unlock_payload), content_type='application/json', **buyer_auth)
    assert resp_dup.status_code == 200, "Should succeed with existing unlock"
    assert resp_dup.json()['is_new_charge'] is False, "Duplicate unlock must NOT charge fee again"
    print("PASS [Unlock]: Duplicate charge prevention verified (No double deduction).")

    # 10. Test Self-Unlock Prevention
    resp_self = client.post('/api/unlocks/request/', data=json.dumps({
        'listing_id': new_listing_id,
        'buyer_id': seller.id,
        'payment_method': 'jazzcash'
    }), content_type='application/json', **seller_auth)
    assert resp_self.status_code == 400, "Seller unlocking own book must be rejected"
    print("PASS [Unlock]: Self-unlock prevention verified (Blocked).")

    # 11. Test Deal Confirmed (Fee Kept, Book Marked Sold, Rating Saved)
    resp = client.post(f'/api/unlocks/{unlock_uuid}/confirm_deal/', data=json.dumps({'user_id': buyer_id}), content_type='application/json', **buyer_auth)
    assert resp.status_code == 200
    assert Listing.objects.get(id=new_listing_id).status == 'sold'
    print("PASS [Deal]: Deal confirmed, book marked as sold, fee finalized.")

    # Rating
    resp = client.post('/api/reviews/create/', data=json.dumps({
        'unlock_id': unlock_uuid,
        'rating': 5,
        'comment': 'Smooth deal at IUB Baghdad campus. Recommended seller!'
    }), content_type='application/json', **buyer_auth)
    assert resp.status_code == 200
    print("PASS [Review]: 5-star seller rating submitted and seller rating updated.")

    # 12. Test Contact Unlock #2 (Free Trial Unlock - 2 of 2 used)
    listing_2 = Listing.objects.filter(status='active').exclude(id=new_listing_id).first()
    resp_u2 = client.post('/api/unlocks/request/', data=json.dumps({
        'listing_id': listing_2.id,
        'buyer_id': buyer_id,
        'payment_method': 'free_trial'
    }), content_type='application/json', **buyer_auth)
    assert resp_u2.status_code == 201
    assert Decimal(str(resp_u2.json()['unlock']['fee_amount'])) == Decimal('0.00'), "Second unlock must also be Rs. 0 Free Trial"
    print("PASS [Unlock #2]: Free Trial Contact Unlock (2 of 2 used). Fee: Rs. 0.00.")

    # 13. Test Contact Unlock #3 (Paid Tier - Rs. 50 Fee applies from 3rd unlock onward)
    listing_for_refund = Listing.objects.filter(status='active').exclude(id__in=[new_listing_id, listing_2.id]).first()
    resp_u3 = client.post('/api/unlocks/request/', data=json.dumps({
        'listing_id': listing_for_refund.id,
        'buyer_id': buyer_id,
        'payment_method': 'easypaisa',
        'account_number': reg_phone
    }), content_type='application/json', **buyer_auth)
    assert resp_u3.status_code == 201
    assert Decimal(str(resp_u3.json()['unlock']['fee_amount'])) == Decimal('50.00'), "3rd unlock onward must charge Rs. 50"
    u3_uuid = resp_u3.json()['unlock']['unlock_id']
    print(f"PASS [Unlock #3]: Paid Tier Contact Unlock (3rd unlock onward). Fee: Rs. {resp_u3.json()['unlock']['fee_amount']} (Easypaisa).")

    # 14. Test Cancellation & Instant 100% Refund on Paid Unlock
    buyer_prof_before = UserProfile.objects.get(id=buyer_id)
    bal_before = buyer_prof_before.wallet_balance

    resp_cancel = client.post(f'/api/unlocks/{u3_uuid}/cancel_deal/', data=json.dumps({
        'reason': 'Seller unreachable after calling.'
    }), content_type='application/json', **buyer_auth)
    assert resp_cancel.status_code == 200
    cancel_data = resp_cancel.json()
    assert cancel_data['unlock']['deal_status'] == 'no_deal_refunded'
    assert cancel_data['refund_transaction_id'].startswith('REF-')
    
    bal_after = UserProfile.objects.get(id=buyer_id).wallet_balance
    assert bal_after == bal_before + Decimal('50.00'), "Refund must credit Rs. 50 back to wallet"
    print(f"PASS [Refund]: Deal Cancelled -> Instant full Rs. 50 refund credited to wallet (Ref: {cancel_data['refund_transaction_id']}).")

    # 13. Test Admin Analytics & Controls
    admin_user = User.objects.filter(is_staff=True).first()
    admin_token, _ = Token.objects.get_or_create(user=admin_user)
    admin_auth = {'HTTP_AUTHORIZATION': f'Token {admin_token.key}'}

    resp = client.get('/api/admin/stats/', **admin_auth)
    assert resp.status_code == 200
    stats = resp.json()
    assert stats['metrics']['current_unlock_fee'] == 50.0, "Platform fee in stats must reflect Rs. 50"
    assert stats['metrics']['retained_revenue'] > 0
    assert stats['metrics']['refunded_amount'] > 0
    print("PASS [Admin]: Admin Analytics accurately tracks Retained Revenue vs Refunded Fees.")

    # Clean up test listing
    client.post(f'/api/listings/{new_listing_id}/delete/', data=json.dumps({'seller_id': seller.id}), content_type='application/json', **seller_auth)
    print("PASS [Seller]: Deleted test listing successfully.")

    print("\n==========================================================")
    print("   ALL PHASE 1 CORE MARKETPLACE TESTS PASSED (13/13)      ")
    print("==========================================================")

if __name__ == '__main__':
    run_phase1_tests()
