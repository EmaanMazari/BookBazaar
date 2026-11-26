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
from bazaar.models import UserProfile, Book, Listing, ContactUnlock, SellerReview, AdminNotification

def run_deal_closing_tests():
    client = Client()
    print("==========================================================")
    print("   BOOKZY AI: DEAL CLOSING FLOW VERIFICATION TESTS        ")
    print("==========================================================")

    # 1. Setup Seller & Buyer
    seller_phone = f"0333{random.randint(1000000, 9999999)}"
    seller_user = User.objects.create_user(username=f"seller_{seller_phone}", password="Password123!")
    seller = UserProfile.objects.create(
        user=seller_user,
        full_name="Muhammad Seller",
        phone_number=seller_phone,
        city="Lahore",
        user_type="student",
        rating=Decimal('0.00'),
        total_reviews=0
    )
    seller_token, _ = Token.objects.get_or_create(user=seller_user)
    seller_auth = {'HTTP_AUTHORIZATION': f'Token {seller_token.key}'}

    buyer_phone = f"0344{random.randint(1000000, 9999999)}"
    buyer_user = User.objects.create_user(username=f"buyer_{buyer_phone}", password="Password123!")
    buyer = UserProfile.objects.create(
        user=buyer_user,
        full_name="Ayesha Buyer",
        phone_number=buyer_phone,
        city="Lahore",
        user_type="student",
        wallet_balance=Decimal('500.00')
    )
    buyer_token, _ = Token.objects.get_or_create(user=buyer_user)
    buyer_auth = {'HTTP_AUTHORIZATION': f'Token {buyer_token.key}'}

    other_user = User.objects.create_user(username=f"other_{random.randint(1000, 9999)}", password="Password123!")
    other_token, _ = Token.objects.get_or_create(user=other_user)
    other_auth = {'HTTP_AUTHORIZATION': f'Token {other_token.key}'}

    # Book & Listing
    test_isbn = f"9789{random.randint(100000000, 999999999)}"
    book = Book.objects.create(
        isbn=test_isbn,
        title="Data Structures & Algorithms in Python",
        author="Michael T. Goodrich",
        category="Computer Science & IT",
        original_retail_price=Decimal('2800.00')
    )
    listing = Listing.objects.create(
        book=book,
        seller=seller,
        condition="Like New",
        price=Decimal('1200.00'),
        city="Lahore",
        status="active"
    )

    print(f"Created Book: {book.title} (Listing ID: {listing.id})")

    # 2. Buyer unlocks contact
    unlock_res = client.post('/api/unlocks/request/', data=json.dumps({
        'listing_id': listing.id,
        'buyer_id': buyer.id,
        'payment_method': 'jazzcash',
        'account_number': buyer.phone_number
    }), content_type='application/json', **buyer_auth)
    assert unlock_res.status_code == 201, f"Unlock failed: {unlock_res.content}"
    unlock_data = unlock_res.json()
    unlock_id = unlock_data['unlock']['unlock_id']
    unlock_obj = ContactUnlock.objects.get(unlock_id=unlock_id)
    assert unlock_obj.deal_status == 'unlocked_pending'
    print(f"PASS: Contact unlocked (ID: {unlock_id}) - Status: unlocked_pending")

    # 3. Test Security: Other user cannot mark listing as sold
    unauth_sold = client.post(f'/api/listings/{listing.id}/mark-sold/', **other_auth)
    assert unauth_sold.status_code == 403, f"Expected 403, got {unauth_sold.status_code}"
    print("PASS: Non-owner blocked from marking listing as sold (HTTP 403)")

    # 4. Test Seller Action: Mark Listing as Sold
    sold_res = client.post(f'/api/listings/{listing.id}/mark-sold/', **seller_auth)
    assert sold_res.status_code == 200, f"Mark sold failed: {sold_res.content}"
    listing.refresh_from_db()
    assert listing.status == 'sold'
    print("PASS: Listing status updated to 'sold'")

    # Check that pending unlock was auto-completed
    unlock_obj.refresh_from_db()
    assert unlock_obj.deal_status == 'deal_made', f"Expected deal_made, got {unlock_obj.deal_status}"
    assert unlock_obj.buyer_confirmation == 'confirmed'
    assert unlock_obj.seller_confirmation == 'confirmed'
    assert unlock_obj.resolved_at is not None
    print("PASS: Pending unlock auto-completed to 'deal_made' upon seller marking listing sold")

    # 5. Test Buyer 5-Star Rating & Deal Closure Flow
    # Create another listing and unlock for testing rating-triggered deal completion
    listing2 = Listing.objects.create(
        book=book,
        seller=seller,
        condition="Good",
        price=Decimal('900.00'),
        city="Lahore",
        status="active"
    )
    unlock_res2 = client.post('/api/unlocks/request/', data=json.dumps({
        'listing_id': listing2.id,
        'buyer_id': buyer.id,
        'payment_method': 'wallet'
    }), content_type='application/json', **buyer_auth)
    assert unlock_res2.status_code == 201
    unlock_id2 = unlock_res2.json()['unlock']['unlock_id']

    # Rating validation (must be 1-5)
    bad_rating_res = client.post('/api/reviews/create/', data=json.dumps({
        'unlock_id': unlock_id2,
        'rating': 6,
        'comment': 'Too high rating'
    }), content_type='application/json', **buyer_auth)
    assert bad_rating_res.status_code == 400
    print("PASS: Rating > 5 rejected with HTTP 400")

    # Other user cannot review
    other_review = client.post('/api/reviews/create/', data=json.dumps({
        'unlock_id': unlock_id2,
        'rating': 5,
        'comment': 'Fake review'
    }), content_type='application/json', **other_auth)
    assert other_review.status_code == 403
    print("PASS: Non-buyer blocked from reviewing seller (HTTP 403)")

    # Buyer submits valid 5-star review
    review_res = client.post('/api/reviews/create/', data=json.dumps({
        'unlock_id': unlock_id2,
        'rating': 5,
        'comment': 'Excellent book condition, very polite seller!'
    }), content_type='application/json', **buyer_auth)
    assert review_res.status_code == 200, f"Review submission failed: {review_res.content}"
    review_data = review_res.json()
    assert review_data['success'] is True
    assert "Thank you for rating the seller" in review_data['message']

    # Verify listing2 is marked sold
    listing2.refresh_from_db()
    assert listing2.status == 'sold', "Listing should be marked sold upon rating submission"

    # Verify unlock2 is marked deal_made
    unlock_obj2 = ContactUnlock.objects.get(unlock_id=unlock_id2)
    assert unlock_obj2.deal_status == 'deal_made'

    # Verify seller rating is updated
    seller.refresh_from_db()
    assert seller.rating == Decimal('5.00')
    assert seller.total_reviews == 1
    assert review_data['new_seller_rating'] == 5.0
    print(f"PASS: Deal closed & seller rating updated to {seller.rating} (Total reviews: {seller.total_reviews})")

    # Clean up test records
    seller_user.delete()
    buyer_user.delete()
    other_user.delete()
    book.delete()

    print("\n==========================================================")
    print("   ALL DEAL CLOSING FLOW TESTS PASSED (100%)              ")
    print("==========================================================")

if __name__ == '__main__':
    run_deal_closing_tests()
