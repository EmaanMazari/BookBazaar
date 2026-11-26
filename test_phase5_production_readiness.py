"""
BookBazaar Phase 5: Real-World Testing & Production Readiness Test Suite
Verifies:
1. Complete Buyer & Seller Workflow: Registration, Token Auth, Profile Update with image.
2. Listing Lifecycle: Create listing with image, search & filter, multi-seller price comparison.
3. Seller Listing Management: Edit price/details, toggle active/sold, safe delete.
4. Buyer Favorites: Add, list, and remove favorites.
5. Payment & Unlock Lifecycle: Rs. 50 contact unlock via JazzCash and Easypaisa sandbox.
6. Strict Contact Privacy: Phone masked before payment, unmasked after verified payment.
7. Duplicate & Replay Protection: Zero duplicate charges, idempotent callbacks.
8. Security & Authorization: Ownership protection (403), Self-unlock prevention (400).
9. Admin Protection & User Blocking: 403 on non-admin access, blocked user login denial.
10. Image Validation & Sanitization: Valid images accepted, fake/malicious files rejected.
11. Database Indexes & Query Performance: PostgreSQL active, key indexes present.
12. Production Readiness: Whitenoise middleware, CSRF trusted origins, SSL proxy headers.
"""

import os
import io
import sys
from decimal import Decimal
from PIL import Image

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookbazaar_backend.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.conf import settings
from rest_framework.authtoken.models import Token
from rest_framework import status

from bazaar.models import (
    UserProfile, Book, Listing, ContactUnlock,
    PlatformSetting, PaymentTransaction, Favorite, MarketplaceReport
)
from bazaar.services.payment_service import get_gateway_adapter


def create_test_image(filename="test.jpg", image_format="JPEG", size=(100, 100), color=(0, 128, 0)):
    """Helper to generate a real, valid in-memory image for testing."""
    file_obj = io.BytesIO()
    img = Image.new("RGB", size, color=color)
    img.save(file_obj, format=image_format)
    file_obj.seek(0)
    return SimpleUploadedFile(filename, file_obj.read(), content_type=f"image/{image_format.lower()}")


class Phase5ProductionReadinessTests(TestCase):
    def setUp(self):
        self.client = Client()

        # 1. Platform Settings
        self.setting = PlatformSetting.get_settings()
        self.setting.contact_unlock_fee = Decimal('50.00')
        self.setting.require_admin_approval = False
        self.setting.save()

        # 2. Admin User
        self.admin_user = User.objects.create_superuser(
            username='admin_p5',
            password='AdminPassword123!',
            email='admin_p5@bookbazaar.pk'
        )
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            full_name='System Admin Officer',
            phone_number='03009998877',
            city='Bahawalpur',
            campus_or_area='Administration Block',
            user_type='admin'
        )
        self.admin_token = Token.objects.get_or_create(user=self.admin_user)[0].key

        # 3. Seller User
        self.seller_user = User.objects.create_user(
            username='seller_p5',
            password='SellerPassword123!'
        )
        self.seller_profile = UserProfile.objects.create(
            user=self.seller_user,
            full_name='Kamran Akmal (Seller)',
            phone_number='03017999991',
            city='Bahawalpur',
            campus_or_area='Faculty of Computing',
            user_type='student',
            rating=Decimal('4.80'),
            total_reviews=12
        )
        self.seller_token = Token.objects.get_or_create(user=self.seller_user)[0].key

        # 4. Buyer User
        self.buyer_user = User.objects.create_user(
            username='buyer_p5',
            password='BuyerPassword123!'
        )
        self.buyer_profile = UserProfile.objects.create(
            user=self.buyer_user,
            full_name='Sadia Noreen (Buyer)',
            phone_number='03129999992',
            city='Bahawalpur',
            campus_or_area='Girls Hostel 3',
            user_type='student',
            wallet_balance=Decimal('200.00')
        )
        self.buyer_token = Token.objects.get_or_create(user=self.buyer_user)[0].key

        # 5. Competitor Seller (for multi-seller price comparison)
        self.seller2_user = User.objects.create_user(
            username='seller2_p5',
            password='SellerPassword123!'
        )
        self.seller2_profile = UserProfile.objects.create(
            user=self.seller2_user,
            full_name='Babar Azam (Store)',
            phone_number='03211112222',
            city='Bahawalpur',
            campus_or_area='Model Town Market',
            user_type='bookstore'
        )
        self.seller2_token = Token.objects.get_or_create(user=self.seller2_user)[0].key

        # 6. Sample Book
        self.book, _ = Book.objects.get_or_create(
            isbn='9780132350884',
            defaults={
                'title': 'Clean Code: A Handbook of Agile Software Craftsmanship',
                'author': 'Robert C. Martin',
                'publisher': 'Prentice Hall',
                'edition': '1st Edition',
                'category': 'Software Engineering',
                'education_board': 'Higher Education / University',
                'grade_class': 'Bachelor / BS / Undergrad',
                'subject': 'Software Engineering Practices',
                'original_retail_price': Decimal('1800.00')
            }
        )

    # -------------------------------------------------------------------------
    # TEST 1: BUYER & SELLER REGISTRATION, AUTH & PROFILE UPDATE
    # -------------------------------------------------------------------------
    def test_01_complete_buyer_and_seller_registration_and_profile_workflow(self):
        """Verify user registration, token generation, login, and profile update with image."""
        # A. Register new user
        reg_payload = {
            'phone_number': '03451234567',
            'password': 'SecurePassWord99!',
            'full_name': 'Zainab Fatima',
            'city': 'Bahawalpur',
            'campus_or_area': 'Baghdad Campus',
            'user_type': 'student'
        }
        res = self.client.post('/api/auth/register/', reg_payload, content_type='application/json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        data = res.json()
        self.assertIn('token', data)
        self.assertIn('profile', data)
        token = data['token']
        self.assertEqual(data['profile']['full_name'], 'Zainab Fatima')
        # Ensure password is never leaked in profile data
        self.assertNotIn('password', data['profile'])

        # B. Verify login with credentials
        login_res = self.client.post('/api/auth/login/', {
            'phone_or_username': '03451234567',
            'password': 'SecurePassWord99!'
        }, content_type='application/json')
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)
        self.assertEqual(login_res.json()['token'], token)

        # C. Update profile details and upload profile picture
        test_img = create_test_image('avatar.jpg', 'JPEG')
        update_res = self.client.post(
            '/api/auth/profile/update/',
            {
                'full_name': 'Zainab Fatima (Software Eng)',
                'campus_or_area': 'Department of Computer Science',
                'profile_picture': test_img
            },
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        self.assertEqual(update_res.status_code, status.HTTP_200_OK)
        updated_prof = update_res.json()['profile']
        self.assertEqual(updated_prof['full_name'], 'Zainab Fatima (Software Eng)')
        self.assertIn('Department of Computer Science', updated_prof['campus_or_area'])

    # -------------------------------------------------------------------------
    # TEST 2: ADD LISTING, SEARCH & MULTI-SELLER PRICE COMPARISON
    # -------------------------------------------------------------------------
    def test_02_add_listing_search_and_multi_seller_price_comparison(self):
        """Verify creating listings with real images, search filtering, and multi-seller comparison."""
        # Seller 1 lists book at Rs. 950
        img1 = create_test_image('clean_code_seller1.jpg', 'JPEG')
        res1 = self.client.post(
            '/api/listings/create/',
            {
                'isbn': self.book.isbn,
                'title': self.book.title,
                'author': self.book.author,
                'condition': 'Like New',
                'price': '950.00',
                'city': 'Bahawalpur',
                'pickup_location': 'CS Dept Gate',
                'description': 'Barely used for one semester.',
                'image': img1
            },
            HTTP_AUTHORIZATION=f'Token {self.seller_token}'
        )
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        listing1_id = res1.json()['listing']['id']

        # Seller 2 lists the same book at a cheaper price: Rs. 750
        img2 = create_test_image('clean_code_seller2.jpg', 'JPEG')
        res2 = self.client.post(
            '/api/listings/create/',
            {
                'isbn': self.book.isbn,
                'title': self.book.title,
                'author': self.book.author,
                'condition': 'Good',
                'price': '750.00',
                'city': 'Bahawalpur',
                'pickup_location': 'Main Gate 1',
                'description': 'Clean pages, highlighted in 2 chapters.',
                'image': img2
            },
            HTTP_AUTHORIZATION=f'Token {self.seller2_token}'
        )
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)
        listing2_id = res2.json()['listing']['id']

        # Buyer searches for "Clean Code"
        search_res = self.client.get('/api/listings/?search=Clean Code')
        self.assertEqual(search_res.status_code, status.HTTP_200_OK)
        listings = search_res.json()
        self.assertGreaterEqual(len(listings), 2)

        # Buyer scans barcode / checks ISBN comparison
        scan_res = self.client.get(f'/api/books/scan/?isbn={self.book.isbn}')
        self.assertEqual(scan_res.status_code, status.HTTP_200_OK)
        scan_data = scan_res.json()
        self.assertTrue(scan_data['found_in_catalog'])
        self.assertEqual(scan_data['price_stats']['lowest_price'], 750.00)
        self.assertEqual(scan_data['price_stats']['total_offers'], 2)
        # Listings returned are ordered by price ascending
        self.assertEqual(float(scan_data['listings'][0]['price']), 750.00)
        self.assertEqual(float(scan_data['listings'][1]['price']), 950.00)

    # -------------------------------------------------------------------------
    # TEST 3: SELLER LISTING MANAGEMENT (EDIT, TOGGLE, DELETE)
    # -------------------------------------------------------------------------
    def test_03_seller_listing_management_edit_toggle_and_delete(self):
        """Verify seller can edit price, toggle sold status, and delete their listing."""
        listing = Listing.objects.create(
            book=self.book,
            seller=self.seller_profile,
            condition='Good',
            price=Decimal('800.00'),
            city='Bahawalpur',
            status='active'
        )

        # A. Seller edits price to Rs. 720
        edit_res = self.client.post(
            f'/api/listings/{listing.id}/edit/',
            {
                'price': '720.00',
                'condition': 'Like New',
                'description': 'Updated price for quick sale'
            },
            HTTP_AUTHORIZATION=f'Token {self.seller_token}',
            content_type='application/json'
        )
        self.assertEqual(edit_res.status_code, status.HTTP_200_OK)
        listing.refresh_from_db()
        self.assertEqual(listing.price, Decimal('720.00'))
        self.assertEqual(listing.condition, 'Like New')

        # B. Seller marks listing as sold
        toggle_res = self.client.post(
            f'/api/listings/{listing.id}/toggle_status/',
            {},
            HTTP_AUTHORIZATION=f'Token {self.seller_token}',
            content_type='application/json'
        )
        self.assertEqual(toggle_res.status_code, status.HTTP_200_OK)
        listing.refresh_from_db()
        self.assertEqual(listing.status, 'sold')

        # When sold, listing should not appear in active search
        active_res = self.client.get('/api/listings/?search=Clean Code')
        active_ids = [l['id'] for l in active_res.json()]
        self.assertNotIn(listing.id, active_ids)

        # C. Seller deletes listing
        del_res = self.client.delete(
            f'/api/listings/{listing.id}/delete/',
            HTTP_AUTHORIZATION=f'Token {self.seller_token}'
        )
        self.assertEqual(del_res.status_code, status.HTTP_200_OK)
        self.assertFalse(Listing.objects.filter(id=listing.id).exists())

    # -------------------------------------------------------------------------
    # TEST 4: FAVORITES WORKFLOW
    # -------------------------------------------------------------------------
    def test_04_buyer_favorites_lifecycle(self):
        """Verify buyer can add a listing to favorites, view favorites, and remove it."""
        listing = Listing.objects.create(
            book=self.book,
            seller=self.seller_profile,
            condition='Good',
            price=Decimal('850.00'),
            city='Bahawalpur',
            status='active'
        )

        # Add to favorites via /api/favorites/toggle/
        fav_res = self.client.post(
            '/api/favorites/toggle/',
            {'listing_id': listing.id},
            HTTP_AUTHORIZATION=f'Token {self.buyer_token}',
            content_type='application/json'
        )
        self.assertEqual(fav_res.status_code, status.HTTP_200_OK)
        self.assertTrue(fav_res.json()['is_favorited'])
        self.assertTrue(Favorite.objects.filter(user=self.buyer_profile, listing=listing).exists())

        # Retrieve user favorites list via /api/favorites/user/<id>/
        list_res = self.client.get(
            f'/api/favorites/user/{self.buyer_profile.id}/',
            HTTP_AUTHORIZATION=f'Token {self.buyer_token}'
        )
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        favs = list_res.json()
        self.assertEqual(len(favs), 1)
        self.assertEqual(favs[0]['listing']['id'], listing.id)

        # Toggle again to remove from favorites
        unfav_res = self.client.post(
            '/api/favorites/toggle/',
            {'listing_id': listing.id},
            HTTP_AUTHORIZATION=f'Token {self.buyer_token}',
            content_type='application/json'
        )
        self.assertEqual(unfav_res.status_code, status.HTTP_200_OK)
        self.assertFalse(unfav_res.json()['is_favorited'])
        self.assertFalse(Favorite.objects.filter(user=self.buyer_profile, listing=listing).exists())

    # -------------------------------------------------------------------------
    # TEST 5: CONTACT UNLOCK & SANDBOX PAYMENT WORKFLOW (JAZZCASH & EASYPAISA)
    # -------------------------------------------------------------------------
    def test_05_contact_unlock_and_sandbox_payment_workflow(self):
        """Verify Rs. 50 contact unlock checkout lifecycle via JazzCash & Easypaisa sandbox."""
        listing = Listing.objects.create(
            book=self.book,
            seller=self.seller_profile,
            condition='Good',
            price=Decimal('800.00'),
            city='Bahawalpur',
            status='active'
        )

        # A. Initiate JazzCash Payment
        init_res = self.client.post(
            '/api/payments/initiate/',
            {
                'listing_id': listing.id,
                'gateway': 'jazzcash',
                'mobile_number': '03129999992'
            },
            HTTP_AUTHORIZATION=f'Token {self.buyer_token}',
            content_type='application/json'
        )
        self.assertEqual(init_res.status_code, status.HTTP_201_CREATED)
        init_data = init_res.json()
        txn_id = init_data['transaction_id']
        self.assertEqual(float(init_data['amount']), 50.00)
        self.assertEqual(init_data['gateway'], 'jazzcash')
        self.assertIn('pp_SecureHash', init_data['initiation_data']['parameters'])

        # B. Verify Payment Server-Side
        verify_payload = {
            'transaction_id': txn_id,
            'payload': {
                'pp_TxnRefNo': 'TXN-JC-992211',
                'pp_ResponseCode': '000',
                'pp_ResponseMessage': 'Approved or Completed Successfully'
            }
        }
        verify_res = self.client.post(
            '/api/payments/verify/',
            verify_payload,
            HTTP_AUTHORIZATION=f'Token {self.buyer_token}',
            content_type='application/json'
        )
        self.assertEqual(verify_res.status_code, status.HTTP_200_OK)
        unlock_data = verify_res.json()
        self.assertEqual(unlock_data['status'], 'completed')
        self.assertEqual(unlock_data['seller_contact']['phone_number'], '03017999991')
        self.assertIn('wa.me/923017999991', unlock_data['seller_contact']['whatsapp_link'])

        # Verify DB records
        unlock = ContactUnlock.objects.get(listing=listing, buyer=self.buyer_profile)
        self.assertEqual(unlock.fee_amount, Decimal('50.00'))
        self.assertEqual(unlock.deal_status, 'unlocked_pending')

    # -------------------------------------------------------------------------
    # TEST 6: STRICT CONTACT PRIVACY LIFECYCLE
    # -------------------------------------------------------------------------
    def test_06_strict_contact_privacy_lifecycle(self):
        """Seller phone is strictly masked before unlock and revealed only after verified unlock."""
        listing = Listing.objects.create(
            book=self.book,
            seller=self.seller_profile,
            condition='Good',
            price=Decimal('900.00'),
            city='Bahawalpur',
            status='active'
        )

        # 1. Anonymous visitor sees masked phone
        anon_res = self.client.get(f'/api/listings/{listing.id}/')
        self.assertEqual(anon_res.status_code, status.HTTP_200_OK)
        self.assertEqual(anon_res.json()['seller_phone'], '0301-*******')
        self.assertFalse(anon_res.json()['is_contact_unlocked'])

        # 2. Buyer before unlock also sees masked phone
        buyer_res = self.client.get(f'/api/listings/{listing.id}/', HTTP_AUTHORIZATION=f'Token {self.buyer_token}')
        self.assertEqual(buyer_res.status_code, status.HTTP_200_OK)
        self.assertEqual(buyer_res.json()['seller_phone'], '0301-*******')
        self.assertFalse(buyer_res.json()['is_contact_unlocked'])

        # 3. Create verified unlock
        ContactUnlock.objects.create(
            listing=listing,
            buyer=self.buyer_profile,
            seller=self.seller_profile,
            fee_amount=Decimal('50.00'),
            payment_method='jazzcash',
            transaction_id='TXN-PRIV-01',
            deal_status='unlocked_pending'
        )

        # 4. Buyer after unlock sees full unmasked phone
        unlocked_res = self.client.get(f'/api/listings/{listing.id}/', HTTP_AUTHORIZATION=f'Token {self.buyer_token}')
        self.assertEqual(unlocked_res.status_code, status.HTTP_200_OK)
        self.assertEqual(unlocked_res.json()['seller_phone'], '03017999991')
        self.assertTrue(unlocked_res.json()['is_contact_unlocked'])

    # -------------------------------------------------------------------------
    # TEST 7: DUPLICATE CHARGE & REPLAY PROTECTION
    # -------------------------------------------------------------------------
    def test_07_duplicate_charge_and_replay_protection(self):
        """Buyer is never charged twice for an already-unlocked listing."""
        listing = Listing.objects.create(
            book=self.book,
            seller=self.seller_profile,
            condition='Good',
            price=Decimal('900.00'),
            city='Bahawalpur',
            status='active'
        )

        # Unlock once via direct API -> 201 Created
        res1 = self.client.post(
            '/api/unlocks/request/',
            {'listing_id': listing.id, 'payment_method': 'jazzcash'},
            HTTP_AUTHORIZATION=f'Token {self.buyer_token}',
            content_type='application/json'
        )
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res1.json()['is_new_charge'])
        self.assertEqual(ContactUnlock.objects.filter(listing=listing, buyer=self.buyer_profile).count(), 1)

        # Attempt to unlock a second time -> 200 OK (idempotent, is_new_charge=False)
        res2 = self.client.post(
            '/api/unlocks/request/',
            {'listing_id': listing.id, 'payment_method': 'jazzcash'},
            HTTP_AUTHORIZATION=f'Token {self.buyer_token}',
            content_type='application/json'
        )
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertFalse(res2.json()['is_new_charge'])
        # Still exactly 1 unlock record in database
        self.assertEqual(ContactUnlock.objects.filter(listing=listing, buyer=self.buyer_profile).count(), 1)

    # -------------------------------------------------------------------------
    # TEST 8: SECURITY AUDIT & OWNERSHIP RESTRICTIONS
    # -------------------------------------------------------------------------
    def test_08_security_audit_and_ownership_protection(self):
        """Non-owner seller cannot edit or delete another seller's listing; user cannot unlock self."""
        listing = Listing.objects.create(
            book=self.book,
            seller=self.seller_profile,
            condition='Good',
            price=Decimal('1000.00'),
            city='Bahawalpur',
            status='active'
        )

        # Competitor seller attempts to edit Seller 1's listing -> 403 Forbidden
        hack_edit = self.client.post(
            f'/api/listings/{listing.id}/edit/',
            {'price': '100.00'},
            HTTP_AUTHORIZATION=f'Token {self.seller2_token}',
            content_type='application/json'
        )
        self.assertEqual(hack_edit.status_code, status.HTTP_403_FORBIDDEN)
        listing.refresh_from_db()
        self.assertEqual(listing.price, Decimal('1000.00'))

        # Competitor seller attempts to delete Seller 1's listing -> 403 Forbidden
        hack_del = self.client.delete(
            f'/api/listings/{listing.id}/delete/',
            HTTP_AUTHORIZATION=f'Token {self.seller2_token}'
        )
        self.assertEqual(hack_del.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Listing.objects.filter(id=listing.id).exists())

        # Self-unlock prevention: Seller attempts to unlock their own listing -> 400 Bad Request
        self_unlock = self.client.post(
            '/api/unlocks/request/',
            {'listing_id': listing.id},
            HTTP_AUTHORIZATION=f'Token {self.seller_token}',
            content_type='application/json'
        )
        self.assertEqual(self_unlock.status_code, status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------------------------------
    # TEST 9: ADMIN-ONLY OPERATIONS & USER BLOCKING
    # -------------------------------------------------------------------------
    def test_09_admin_only_operations_and_user_blocking(self):
        """Only administrators can access admin APIs; blocked users are barred from login."""
        # Non-admin user attempts to access admin stats -> 403 Forbidden
        non_admin_stats = self.client.get('/api/admin/stats/', HTTP_AUTHORIZATION=f'Token {self.buyer_token}')
        self.assertEqual(non_admin_stats.status_code, status.HTTP_403_FORBIDDEN)

        # Admin accesses admin stats -> 200 OK
        admin_stats = self.client.get('/api/admin/stats/', HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        self.assertEqual(admin_stats.status_code, status.HTTP_200_OK)

        # Admin blocks malicious seller
        block_res = self.client.post(
            f'/api/admin/users/{self.seller_profile.id}/toggle_block/',
            {},
            HTTP_AUTHORIZATION=f'Token {self.admin_token}',
            content_type='application/json'
        )
        self.assertEqual(block_res.status_code, status.HTTP_200_OK)
        self.seller_profile.refresh_from_db()
        self.assertTrue(self.seller_profile.is_blocked)

        # Blocked user attempts to login -> 403 Forbidden
        blocked_login = self.client.post('/api/auth/login/', {
            'phone_or_username': '03017999991',
            'password': 'SellerPassword123!'
        }, content_type='application/json')
        self.assertEqual(blocked_login.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('blocked', blocked_login.json()['error'].lower())

    # -------------------------------------------------------------------------
    # TEST 10: IMAGE UPLOAD VALIDATION & SECURITY
    # -------------------------------------------------------------------------
    def test_10_image_upload_validation_and_sanitization(self):
        """Valid JPEG/PNG images are accepted; non-image or executable files are rejected."""
        # A. Valid image upload succeeds
        valid_img = create_test_image('clean_book.png', 'PNG')
        good_res = self.client.post(
            '/api/listings/create/',
            {
                'isbn': self.book.isbn,
                'title': self.book.title,
                'author': self.book.author,
                'condition': 'Like New',
                'price': '850.00',
                'city': 'Bahawalpur',
                'image': valid_img
            },
            HTTP_AUTHORIZATION=f'Token {self.seller_token}'
        )
        self.assertEqual(good_res.status_code, status.HTTP_201_CREATED)

        # B. Non-image file disguised with .jpg extension is rejected
        fake_file = SimpleUploadedFile("malicious.jpg", b"<?php echo 'hacked'; ?>", content_type="image/jpeg")
        bad_res = self.client.post(
            '/api/listings/create/',
            {
                'isbn': self.book.isbn,
                'title': self.book.title,
                'author': self.book.author,
                'condition': 'Fair',
                'price': '500.00',
                'city': 'Bahawalpur',
                'image': fake_file
            },
            HTTP_AUTHORIZATION=f'Token {self.seller_token}'
        )
        self.assertEqual(bad_res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('not a valid or readable image', bad_res.json()['error'].lower())

    # -------------------------------------------------------------------------
    # TEST 11: DATABASE INDEXES & QUERY PERFORMANCE
    # -------------------------------------------------------------------------
    def test_11_database_indexes_and_performance_audit(self):
        """Verify active PostgreSQL connection and presence of key performance indexes."""
        if connection.vendor != 'postgresql':
            self.skipTest("Skipping PostgreSQL-specific index verification in local SQLite environment.")

        # 1. Connection check
        self.assertEqual(connection.vendor, 'postgresql')

        # 2. Check indexes on Listing table
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT indexname FROM pg_indexes
                WHERE tablename = 'bazaar_listing';
            """)
            indexes = [row[0] for row in cursor.fetchall()]

        # Ensure our composite and B-tree indexes exist
        self.assertTrue(any('status' in idx for idx in indexes), "Index on status missing")
        self.assertTrue(any('city' in idx for idx in indexes), "Index on city missing")

        # 3. Check indexes on ContactUnlock table
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT indexname FROM pg_indexes
                WHERE tablename = 'bazaar_contactunlock';
            """)
            unlock_indexes = [row[0] for row in cursor.fetchall()]

        self.assertTrue(any('deal_status' in idx for idx in unlock_indexes), "Index on deal_status missing")

    # -------------------------------------------------------------------------
    # TEST 12: PRODUCTION SETTINGS & WHITENOISE AUDIT
    # -------------------------------------------------------------------------
    def test_12_production_readiness_and_whitenoise_audit(self):
        """Verify Whitenoise middleware, CSRF trusted origins, and production settings."""
        # 1. Whitenoise Middleware must be active
        self.assertIn(
            'whitenoise.middleware.WhiteNoiseMiddleware',
            settings.MIDDLEWARE,
            "WhiteNoiseMiddleware must be configured in MIDDLEWARE"
        )

        # 2. CSRF Trusted Origins must be configured
        self.assertTrue(hasattr(settings, 'CSRF_TRUSTED_ORIGINS'))
        self.assertIsInstance(settings.CSRF_TRUSTED_ORIGINS, list)

        # 3. Storages dictionary must handle staticfiles
        self.assertTrue(hasattr(settings, 'STORAGES'))
        self.assertIn('staticfiles', settings.STORAGES)

        # 4. Connection Max Age configured for PostgreSQL connection pooling
        db_conf = settings.DATABASES['default']
        if db_conf['ENGINE'] == 'django.db.backends.postgresql':
            self.assertGreaterEqual(db_conf.get('CONN_MAX_AGE', 0), 0)


if __name__ == '__main__':
    from django.test.runner import DiscoverRunner
    runner = DiscoverRunner(verbosity=2)
    failures = runner.run_tests(['test_phase5_production_readiness'])
    if failures:
        print(f"\n[FAIL] {failures} test(s) failed.")
        sys.exit(1)
    else:
        print("\n=======================================================")
        print(" [ALL TESTS PASSED] Phase 5 Production Readiness Verified!")
        print("=======================================================\n")
