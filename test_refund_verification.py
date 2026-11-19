import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookbazaar_backend.settings')
django.setup()

from decimal import Decimal
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory, force_authenticate
from bazaar.models import UserProfile, Book, Listing, ContactUnlock
from bazaar.views import cancel_deal_refund

print("=== TESTING RS. 50 REFUND-TO-WALLET & DUPLICATE PREVENTION ===")

test_buyer_phone = "03998877665"
test_seller_phone = "03998877666"

# Cleanup any previous runs
User.objects.filter(username__in=[f"user_{test_buyer_phone}", f"user_{test_seller_phone}"]).delete()
UserProfile.objects.filter(phone_number__in=[test_buyer_phone, test_seller_phone]).delete()

u_buyer = User.objects.create_user(username=f"user_{test_buyer_phone}", password="TestPass123!")
p_buyer = UserProfile.objects.create(user=u_buyer, full_name="Test Refund Buyer", phone_number=test_buyer_phone, wallet_balance=Decimal("100.00"))

u_seller = User.objects.create_user(username=f"user_{test_seller_phone}", password="TestPass123!")
p_seller = UserProfile.objects.create(user=u_seller, full_name="Test Refund Seller", phone_number=test_seller_phone)

book = Book.objects.first()
listing = Listing.objects.create(book=book, seller=p_seller, price=500, condition="Good", city="Bahawalpur", status="active")

unlock = ContactUnlock.objects.create(
    listing=listing,
    buyer=p_buyer,
    seller=p_seller,
    fee_amount=Decimal("50.00"),
    transaction_id="TXN-REFUND-VERIFY-001",
    deal_status="unlocked_pending"
)

print(f"1. Initial Buyer Wallet Balance : Rs. {p_buyer.wallet_balance}")
print(f"2. Initial Deal Status          : {unlock.deal_status}")

# First Refund Attempt
factory = APIRequestFactory()
req1 = factory.post(f"/api/unlocks/{unlock.unlock_id}/refund/", {"reason": "Seller unreachable"}, format="json")
force_authenticate(req1, user=u_buyer)
res1 = cancel_deal_refund(req1, unlock_id=unlock.unlock_id)

p_buyer.refresh_from_db()
unlock.refresh_from_db()

print(f"3. First Refund Response Code   : HTTP {res1.status_code}")
print(f"4. First Refund Response Msg    : {res1.data.get('message')}")
print(f"5. Balance After First Refund   : Rs. {p_buyer.wallet_balance} (Expected: 150.00)")
print(f"6. Deal Status After Refund     : {unlock.deal_status} (Expected: no_deal_refunded)")
print(f"7. Refund Reference ID          : {unlock.refund_transaction_id}")

assert res1.status_code == 200, "First refund failed"
assert p_buyer.wallet_balance == Decimal("150.00"), f"Expected 150.00 but got {p_buyer.wallet_balance}"
assert unlock.deal_status == "no_deal_refunded", f"Expected no_deal_refunded but got {unlock.deal_status}"

# Duplicate Refund Attempt
req2 = factory.post(f"/api/unlocks/{unlock.unlock_id}/refund/", {"reason": "Duplicate attempt"}, format="json")
force_authenticate(req2, user=u_buyer)
res2 = cancel_deal_refund(req2, unlock_id=unlock.unlock_id)

p_buyer.refresh_from_db()
unlock.refresh_from_db()

print(f"8. Duplicate Refund Response Code: HTTP {res2.status_code}")
print(f"9. Duplicate Refund Response Msg : {res2.data.get('message')}")
print(f"10. Balance After Duplicate Attempt: Rs. {p_buyer.wallet_balance} (Must strictly remain 150.00)")

assert res2.status_code == 200, "Duplicate request handler failed"
assert "already been refunded" in res2.data.get("message", "").lower(), "Expected already refunded message"
assert p_buyer.wallet_balance == Decimal("150.00"), f"CRITICAL: Duplicate refund credited extra money! Balance: {p_buyer.wallet_balance}"

# Cleanup
unlock.delete()
listing.delete()
p_buyer.delete()
p_seller.delete()
u_buyer.delete()
u_seller.delete()

print("\n>>> ALL REFUND & DUPLICATE PREVENTION CHECKS PASSED (100% CLEANED UP) <<<")
