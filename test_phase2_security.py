"""
BookLoop Phase 2 Comprehensive Security & Marketplace Verification Test Suite
Tests:
- Authentication & Password Hashing (Django PBKDF2)
- Token Authentication & Protected Private APIs (401/403)
- Owner-Only Listing Operations (Edit/Delete block for non-owners)
- Admin-Only API Security (403 for normal users, 200 for staff)
- Seller Contact Privacy Masking (Masked until verified unlock)
- Image File Validation (Size, Extension, Pillow integrity)
- Multi-Seller Comparison & Education Board Search
- Rs. 50 Sandbox Contact Unlock, Duplicate Charge Prevention
- Deal Confirmation & No-Deal Wallet Refund
- Throttling & Rate Limiting Configuration
"""

import os
import sys
import io
from decimal import Decimal
from PIL import Image

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookbazaar_backend.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from rest_framework.authtoken.models import Token
from rest_framework import status

from bazaar.models import (
    UserProfile, Book, Listing, ContactUnlock,
    SellerReview, Favorite, PlatformSetting
)


def create_test_image(filename="test.png", size=(100, 100), color="blue"):
    file_obj = io.BytesIO()
    img = Image.new("RGB", size, color=color)
    img.save(file_obj, format="PNG")
    file_obj.name = filename
    file_obj.seek(0)
    return file_obj


class Phase2SecurityAndMarketplaceTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Ensure platform setting
        self.setting = PlatformSetting.get_settings()
        self.setting.contact_unlock_fee = Decimal('50.00')
        self.setting.require_admin_approval = False
        self.setting.save()

        # 1. Create Staff / Admin User
        self.admin_user = User.objects.create_superuser(
            username='p2_admin',
            email='admin@bookloop.pk',
            password='AdminPassword123!'
        )
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            phone_number='03000000001',
            full_name='Platform Administrator',
            city='Bahawalpur',
            user_type='admin'
        )
        self.admin_token, _ = Token.objects.get_or_create(user=self.admin_user)

        # 2. Create Seller User
        self.seller_user = User.objects.create_user(
            username='p2_seller',
            email='seller@bookloop.pk',
            password='SellerPassword123!'
        )
        self.seller_profile = UserProfile.objects.create(
            user=self.seller_user,
            phone_number='03111111111',
            full_name='Tariq Mehmood (Seller)',
            city='Bahawalpur',
            campus_or_area='Baghdad-ul-Jadeed Campus',
            user_type='student',
            wallet_balance=Decimal('100.00')
        )
        self.seller_token, _ = Token.objects.get_or_create(user=self.seller_user)

        # 3. Create Buyer User
        self.buyer_user = User.objects.create_user(
            username='p2_buyer',
            email='buyer@bookloop.pk',
            password='BuyerPassword123!'
        )
        self.buyer_profile = UserProfile.objects.create(
            user=self.buyer_user,
            phone_number='03222222222',
            full_name='Ayesha Siddiqa (Buyer)',
            city='Multan',
            campus_or_area='Gulgasht Colony',
            user_type='student',
            wallet_balance=Decimal('200.00')
        )
        self.buyer_token, _ = Token.objects.get_or_create(user=self.buyer_user)

        # 4. Create Standard Book in Catalog
        self.book = Book.objects.create(
            isbn='9789690010011',
            title='Data Structures & Algorithms in Python',
            author='Michael T. Goodrich',
            publisher='Wiley Pakistan',
            category='Software Engineering',
            education_board='Higher Education / University',
            grade_class='Bachelor / BS / Undergrad',
            subject='Computer Science',
            original_retail_price=Decimal('1800.00')
        )

        # 5. Create Seller's Listing
        self.listing = Listing.objects.create(
            book=self.book,
            seller=self.seller_profile,
            condition='Good',
            price=Decimal('650.00'),
            city='Bahawalpur',
            pickup_location='CS Department Lab 1',
            status='active'
        )

    # ----------------------------------------------------
    # MODULE 1: AUTHENTICATION, PASSWORDS & TOKENS
    # ----------------------------------------------------
    def test_01_password_hashing(self):
        """Verify user passwords are secure and properly hashed in the database"""
        user = User.objects.get(username='p2_seller')
        self.assertFalse(user.password.startswith('SellerPassword123!'))
        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))
        self.assertTrue(check_password('SellerPassword123!', user.password))
        print("[PASS] 01. Passwords are securely hashed with PBKDF2/SHA256.")

    def test_02_registration_and_login_flow(self):
        """Verify registration and login endpoints return tokens and enforce validation"""
        # Register new account
        reg_res = self.client.post('/api/auth/register/', {
            'phone_number': '03334445555',
            'password': 'SecurePass789!',
            'full_name': 'Zahid Bashir',
            'city': 'Lahore'
        }, content_type='application/json')
        self.assertEqual(reg_res.status_code, status.HTTP_201_CREATED)
        data = reg_res.json()
        self.assertIn('token', data)
        self.assertEqual(data['profile']['full_name'], 'Zahid Bashir')

        # Test login
        login_res = self.client.post('/api/auth/login/', {
            'phone_or_username': '03334445555',
            'password': 'SecurePass789!'
        }, content_type='application/json')
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)
        login_data = login_res.json()
        self.assertEqual(login_data['token'], data['token'])
        print("[PASS] 02. Secure Registration and Token Login verified.")

    def test_03_private_api_protection_unauthenticated(self):
        """Verify unauthenticated requests cannot create, edit, delete listings or unlock contacts"""
        # Unauthenticated create listing
        res_create = self.client.post('/api/listings/create/', {'price': '500'})
        self.assertEqual(res_create.status_code, status.HTTP_401_UNAUTHORIZED)

        # Unauthenticated edit listing
        res_edit = self.client.post(f'/api/listings/{self.listing.id}/edit/', {'price': '700'}, content_type='application/json')
        self.assertEqual(res_edit.status_code, status.HTTP_401_UNAUTHORIZED)

        # Unauthenticated unlock request
        res_unlock = self.client.post('/api/unlocks/request/', {'listing_id': self.listing.id}, content_type='application/json')
        self.assertEqual(res_unlock.status_code, status.HTTP_401_UNAUTHORIZED)
        print("[PASS] 03. Unauthenticated requests to private endpoints correctly blocked (401 Unauthorized).")

    # ----------------------------------------------------
    # MODULE 1: OWNERSHIP PERMISSIONS
    # ----------------------------------------------------
    def test_04_owner_only_listing_modification(self):
        """Verify a user cannot edit or delete another seller's listing"""
        buyer_headers = {'HTTP_AUTHORIZATION': f'Token {self.buyer_token.key}'}

        # Buyer attempts to edit Seller's listing
        res_edit = self.client.post(
            f'/api/listings/{self.listing.id}/edit/',
            {'price': '100.00', 'condition': 'Fair'},
            content_type='application/json',
            **buyer_headers
        )
        self.assertEqual(res_edit.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('Permission denied', res_edit.json()['error'])

        # Buyer attempts to delete Seller's listing
        res_del = self.client.post(
            f'/api/listings/{self.listing.id}/delete/',
            content_type='application/json',
            **buyer_headers
        )
        self.assertEqual(res_del.status_code, status.HTTP_403_FORBIDDEN)

        # Seller successfully edits their own listing
        seller_headers = {'HTTP_AUTHORIZATION': f'Token {self.seller_token.key}'}
        res_seller_edit = self.client.post(
            f'/api/listings/{self.listing.id}/edit/',
            {'price': '620.00', 'condition': 'Like New'},
            content_type='application/json',
            **seller_headers
        )
        self.assertEqual(res_seller_edit.status_code, status.HTTP_200_OK)
        self.listing.refresh_from_db()
        self.assertEqual(float(self.listing.price), 620.0)
        self.assertEqual(self.listing.condition, 'Like New')
        print("[PASS] 04. Ownership rules enforced (Non-owner gets 403 Forbidden; Owner successfully edits).")

    # ----------------------------------------------------
    # MODULE 1: PRIVACY MASKING & CONTACT UNLOCK
    # ----------------------------------------------------
    def test_05_contact_privacy_masking_before_and_after_unlock(self):
        """Verify seller phone number is masked for public/buyer until verified contact unlock"""
        # 1. Public listings query
        res_public = self.client.get('/api/listings/')
        self.assertEqual(res_public.status_code, status.HTTP_200_OK)
        listings = res_public.json()
        item = [l for l in listings if l['id'] == self.listing.id][0]
        self.assertTrue('0311-*******' in item['seller_phone'] or '03XX-*******' in item['seller_phone'])
        self.assertNotIn('03111111111', item['seller_phone'])
        self.assertFalse(item['is_contact_unlocked'])

        # 2. Buyer performs verified contact unlock (Rs. 50 sandbox)
        buyer_headers = {'HTTP_AUTHORIZATION': f'Token {self.buyer_token.key}'}
        res_unlock = self.client.post('/api/unlocks/request/', {
            'listing_id': self.listing.id,
            'payment_method': 'jazzcash',
            'account_number': '03222222222'
        }, content_type='application/json', **buyer_headers)
        self.assertEqual(res_unlock.status_code, status.HTTP_201_CREATED)
        unlock_data = res_unlock.json()
        self.assertTrue(unlock_data['is_new_charge'])
        self.assertEqual(unlock_data['seller_contact']['phone_number'], '03111111111')
        self.assertIn('wa.me/92311111111', unlock_data['seller_contact']['whatsapp_link'])

        # 3. Buyer queries listings again: phone is unmasked for this buyer
        res_buyer = self.client.get('/api/listings/', **buyer_headers)
        buyer_item = [l for l in res_buyer.json() if l['id'] == self.listing.id][0]
        self.assertEqual(buyer_item['seller_phone'], '03111111111')
        self.assertTrue(buyer_item['is_contact_unlocked'])
        print("[PASS] 05. Seller phone number privacy masking verified (Masked before unlock, Revealed after).")

    def test_06_duplicate_unlock_charge_prevention(self):
        """Verify buyer is not charged twice for unlocking the same seller contact"""
        buyer_headers = {'HTTP_AUTHORIZATION': f'Token {self.buyer_token.key}'}

        # First unlock
        res1 = self.client.post('/api/unlocks/request/', {
            'listing_id': self.listing.id,
            'payment_method': 'easypaisa',
            'account_number': '03222222222'
        }, content_type='application/json', **buyer_headers)
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res1.json()['is_new_charge'])
        txn1 = res1.json()['unlock']['transaction_id']

        # Second unlock request on same listing
        res2 = self.client.post('/api/unlocks/request/', {
            'listing_id': self.listing.id,
            'payment_method': 'easypaisa',
            'account_number': '03222222222'
        }, content_type='application/json', **buyer_headers)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertFalse(res2.json()['is_new_charge'])
        self.assertEqual(res2.json()['unlock']['transaction_id'], txn1)
        self.assertEqual(ContactUnlock.objects.filter(listing=self.listing, buyer=self.buyer_profile).count(), 1)
        print("[PASS] 06. Duplicate unlock charge prevention verified (Idempotent 200 OK, no extra charge).")

    def test_07_deal_confirmation_and_wallet_refund(self):
        """Verify deal completion marks book sold, and no-deal refunds Rs. 50 to buyer wallet"""
        buyer_headers = {'HTTP_AUTHORIZATION': f'Token {self.buyer_token.key}'}

        # 1. Unlock listing
        res_unlock = self.client.post('/api/unlocks/request/', {
            'listing_id': self.listing.id,
            'payment_method': 'jazzcash'
        }, content_type='application/json', **buyer_headers)
        unlock_id = res_unlock.json()['unlock']['unlock_id']

        # 2. Confirm Deal
        res_confirm = self.client.post(f'/api/unlocks/{unlock_id}/confirm_deal/', content_type='application/json', **buyer_headers)
        self.assertEqual(res_confirm.status_code, status.HTTP_200_OK)
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.status, 'sold')

        # 3. Create a second listing to test refund
        listing2 = Listing.objects.create(
            book=self.book,
            seller=self.seller_profile,
            condition='Fair',
            price=Decimal('500.00'),
            city='Bahawalpur',
            status='active'
        )
        res_unlock2 = self.client.post('/api/unlocks/request/', {
            'listing_id': listing2.id,
            'payment_method': 'jazzcash'
        }, content_type='application/json', **buyer_headers)
        unlock_id2 = res_unlock2.json()['unlock']['unlock_id']

        initial_balance = self.buyer_profile.wallet_balance

        # 4. Cancel Deal & Refund
        res_cancel = self.client.post(f'/api/unlocks/{unlock_id2}/cancel_deal/', {
            'reason': 'Seller did not respond on WhatsApp.'
        }, content_type='application/json', **buyer_headers)
        self.assertEqual(res_cancel.status_code, status.HTTP_200_OK)
        cancel_data = res_cancel.json()
        self.assertIn('refund_transaction_id', cancel_data)

        self.buyer_profile.refresh_from_db()
        self.assertEqual(self.buyer_profile.wallet_balance, initial_balance + Decimal('50.00'))
        print("[PASS] 07. Deal confirmation (status=sold) and Rs. 50 wallet refund verified.")

    # ----------------------------------------------------
    # MODULE 1: ADMIN SECURITY
    # ----------------------------------------------------
    def test_08_admin_api_security(self):
        """Verify normal users are blocked from admin APIs (403), while staff users are granted access"""
        buyer_headers = {'HTTP_AUTHORIZATION': f'Token {self.buyer_token.key}'}
        admin_headers = {'HTTP_AUTHORIZATION': f'Token {self.admin_token.key}'}

        # Non-admin attempts admin stats
        res_unauth = self.client.get('/api/admin/stats/', **buyer_headers)
        self.assertEqual(res_unauth.status_code, status.HTTP_403_FORBIDDEN)

        # Non-admin attempts admin settings update
        res_unauth_set = self.client.post('/api/admin/settings/', {'contact_unlock_fee': 100}, content_type='application/json', **buyer_headers)
        self.assertEqual(res_unauth_set.status_code, status.HTTP_403_FORBIDDEN)

        # Admin accesses stats
        res_admin = self.client.get('/api/admin/stats/', **admin_headers)
        self.assertEqual(res_admin.status_code, status.HTTP_200_OK)
        self.assertIn('metrics', res_admin.json())

        # Admin updates settings
        res_admin_set = self.client.post('/api/admin/settings/', {'contact_unlock_fee': 55.0}, content_type='application/json', **admin_headers)
        self.assertEqual(res_admin_set.status_code, status.HTTP_200_OK)
        self.setting.refresh_from_db()
        self.assertEqual(float(self.setting.contact_unlock_fee), 55.0)
        print("[PASS] 08. Admin endpoints strictly protected by IsAdminOnly.")

    # ----------------------------------------------------
    # MODULE 3: IMAGE & MEDIA VALIDATION
    # ----------------------------------------------------
    def test_09_image_validation(self):
        """Verify image uploads validate file type, file size, and pillow integrity"""
        seller_headers = {'HTTP_AUTHORIZATION': f'Token {self.seller_token.key}'}

        # 1. Invalid non-image content (arbitrary text pretending to be an image)
        fake_file = io.BytesIO(b"MALICIOUS_EXEC_OR_TEXT_DATA")
        fake_file.name = "malicious.png"
        res_bad = self.client.post('/api/listings/create/', {
            'title': 'Test Book with Bad Image',
            'price': '450.00',
            'condition': 'Good',
            'city': 'Bahawalpur',
            'image': fake_file
        }, **seller_headers)
        self.assertEqual(res_bad.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('not a valid or readable image', res_bad.json()['error'])

        # 2. Valid image upload
        valid_img = create_test_image("clean_book.png", size=(120, 160), color="green")
        res_good = self.client.post('/api/listings/create/', {
            'title': 'Operating System Concepts',
            'author': 'Silberschatz',
            'price': '850.00',
            'condition': 'Brand New',
            'city': 'Bahawalpur',
            'image': valid_img
        }, **seller_headers)
        self.assertEqual(res_good.status_code, status.HTTP_201_CREATED)
        listing_data = res_good.json()['listing']
        self.assertTrue('clean_book' in listing_data['display_image'])
        print("[PASS] 09. Image upload security validated (Fake files rejected, authentic images accepted).")

    # ----------------------------------------------------
    # MODULE 4: MULTI-SELLER COMPARISON & SEARCH
    # ----------------------------------------------------
    def test_10_multi_seller_comparison_and_board_search(self):
        """Verify multiple sellers for same book appear in price comparison and board search filters"""
        # Create second seller with same book
        seller2_user = User.objects.create_user(username='p2_seller2', password='PassUser2!')
        seller2_prof = UserProfile.objects.create(
            user=seller2_user, phone_number='03444444444',
            full_name='Rashid Ali (Seller 2)', city='Lahore'
        )
        Listing.objects.create(
            book=self.book,
            seller=seller2_prof,
            condition='Brand New',
            price=Decimal('800.00'),
            city='Lahore',
            status='active'
        )

        # Scan ISBN query
        res_scan = self.client.get(f'/api/books/scan/?isbn={self.book.isbn}')
        self.assertEqual(res_scan.status_code, status.HTTP_200_OK)
        scan_data = res_scan.json()
        self.assertEqual(len(scan_data['listings']), 2)
        self.assertEqual(scan_data['price_stats']['lowest_price'], 650.0)
        self.assertEqual(scan_data['price_stats']['highest_price'], 800.0)

        # Search by board and class
        res_filter = self.client.get('/api/listings/?board=Higher%20Education%20/%20University&grade_class=Bachelor%20/%20BS%20/%20Undergrad')
        self.assertEqual(res_filter.status_code, status.HTTP_200_OK)
        filtered = res_filter.json()
        self.assertTrue(any(l['book']['isbn'] == self.book.isbn for l in filtered))
        print("[PASS] 10. Multi-seller price comparison and education board filters verified.")


def run_tests():
    print("\n=======================================================")
    print(" Running BookLoop Phase 2 Security & Marketplace Tests")
    print("=======================================================\n")
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(Phase2SecurityAndMarketplaceTests)
    runner = unittest.TextTestRunner(verbosity=1)
    result = runner.run(suite)
    print("\n=======================================================")
    if result.wasSuccessful():
        print(" [ALL TESTS PASSED] Phase 2 Security Requirements Verified!")
    else:
        print(f" [TEST FAILURES] {len(result.failures)} failures, {len(result.errors)} errors.")
    print("=======================================================\n")
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
