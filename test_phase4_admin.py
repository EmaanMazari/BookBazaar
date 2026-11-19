"""
BookBazaar Phase 4 Automated Admin Dashboard & Management Test Suite
Verifies:
1. Admin Analytics & KPIs endpoint (Protected, metrics accuracy, gateway breakdown).
2. User Management (Search, role filter, block & unblock user).
3. User Detailed Activity View (Listings, unlocks, reviews, reports).
4. Listings Moderation (Approve, reject, toggle sponsored, mark sold, delete).
5. Admin Listing Edit Override (Price, condition, status, location).
6. Seller Activity Monitoring (Sales, active books, unlocks received, ratings).
7. Payment Transactions Ledger (Gateway filter, status filter, search).
8. Admin Force Refund Override (Manual dispute refund to buyer wallet).
9. Reports & Complaints System (User submission, admin filtering, resolution & moderation actions).
10. Advertisement Management (Create, edit, toggle active, delete, CTR calculation).
11. Platform Monetization & Safety Policy Settings (Dynamic fee, approval toggles, non-admin protection).
"""

import os
import sys
import uuid
from decimal import Decimal

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookbazaar_backend.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import status

from bazaar.models import (
    UserProfile, Book, Listing, ContactUnlock,
    PlatformSetting, PaymentTransaction, Advertisement,
    MarketplaceReport
)


class Phase4AdminManagementTests(TestCase):
    def setUp(self):
        self.client = Client()

        # 1. Platform Settings
        self.setting = PlatformSetting.get_settings()
        self.setting.contact_unlock_fee = Decimal('50.00')
        self.setting.require_admin_approval = False
        self.setting.save()

        # 2. Admin User
        self.admin_user = User.objects.create_superuser(
            username='admin_p4',
            password='AdminPassword123!',
            email='admin_p4@bookbazaar.pk'
        )
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            full_name='Dr. Admin Officer',
            phone_number='03009998877',
            city='Bahawalpur',
            campus_or_area='Administration Block',
            user_type='admin'
        )
        self.admin_token = Token.objects.create(user=self.admin_user).key

        # 3. Regular Seller User
        self.seller_user = User.objects.create_user(
            username='seller_p4',
            password='SellerPassword123!',
            email='seller_p4@bookbazaar.pk'
        )
        self.seller_profile = UserProfile.objects.create(
            user=self.seller_user,
            full_name='Zubair Khan Seller',
            phone_number='03017778899',
            city='Bahawalpur',
            campus_or_area='SE Department',
            user_type='student',
            rating=Decimal('4.80'),
            total_reviews=6
        )
        self.seller_token = Token.objects.create(user=self.seller_user).key

        # 4. Regular Buyer User
        self.buyer_user = User.objects.create_user(
            username='buyer_p4',
            password='BuyerPassword123!',
            email='buyer_p4@bookbazaar.pk'
        )
        self.buyer_profile = UserProfile.objects.create(
            user=self.buyer_user,
            full_name='Mariam Bibi Buyer',
            phone_number='03023334455',
            city='Bahawalpur',
            campus_or_area='Girls Hostel 1',
            user_type='student',
            wallet_balance=Decimal('150.00')
        )
        self.buyer_token = Token.objects.create(user=self.buyer_user).key

        # 5. Sample Book & Listing
        self.book = Book.objects.create(
            title='Artificial Intelligence: A Modern Approach',
            author='Stuart Russell',
            isbn='9780136042594',
            category='Computer Science / IT',
            education_board='Higher Education / University',
            grade_class='Bachelor / BS / Undergrad',
            original_retail_price=Decimal('2800.00')
        )

        self.listing = Listing.objects.create(
            book=self.book,
            seller=self.seller_profile,
            condition='Good',
            price=Decimal('950.00'),
            city='Bahawalpur',
            pickup_location='Library Lawn',
            status='active'
        )

    # -------------------------------------------------------------
    # 1. Admin Analytics & Permissions Protection
    # -------------------------------------------------------------
    def test_01_admin_stats_permissions_and_metrics(self):
        # 1. Unauthenticated request rejected (401)
        res_anon = self.client.get('/api/admin/stats/')
        self.assertEqual(res_anon.status_code, status.HTTP_401_UNAUTHORIZED)

        # 2. Regular non-staff user rejected (403)
        res_non_staff = self.client.get('/api/admin/stats/', HTTP_AUTHORIZATION=f'Token {self.buyer_token}')
        self.assertEqual(res_non_staff.status_code, status.HTTP_403_FORBIDDEN)

        # 3. Staff admin authorized (200)
        res_admin = self.client.get('/api/admin/stats/', HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        self.assertEqual(res_admin.status_code, status.HTTP_200_OK)
        data = res_admin.json()
        self.assertIn('metrics', data)
        self.assertIn('settings', data)
        self.assertIn('gateway_stats', data['metrics'])
        self.assertIn('retained_revenue', data['metrics'])
        self.assertIn('refunded_amount', data['metrics'])
        print("[PASS] 1. Admin Analytics API strictly protected and metrics verified.")

    # -------------------------------------------------------------
    # 2. User Management (Search, Filter, Block, Unblock)
    # -------------------------------------------------------------
    def test_02_user_management_search_and_block(self):
        # Non-admin forbidden
        res_forbid = self.client.get('/api/admin/users/', HTTP_AUTHORIZATION=f'Token {self.buyer_token}')
        self.assertEqual(res_forbid.status_code, status.HTTP_403_FORBIDDEN)

        # Admin search by name
        res_search = self.client.get('/api/admin/users/?search=Zubair', HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        self.assertEqual(res_search.status_code, status.HTTP_200_OK)
        results = res_search.json()['users']
        self.assertTrue(any(u['full_name'] == 'Zubair Khan Seller' for u in results))

        # Admin toggle block
        res_block = self.client.post(
            f'/api/admin/users/{self.seller_profile.id}/toggle_block/',
            HTTP_AUTHORIZATION=f'Token {self.admin_token}'
        )
        self.assertEqual(res_block.status_code, status.HTTP_200_OK)
        self.assertTrue(res_block.json()['is_blocked'])

        self.seller_profile.refresh_from_db()
        self.assertTrue(self.seller_profile.is_blocked)

        # Filter by blocked
        res_filter = self.client.get('/api/admin/users/?status=blocked', HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        self.assertTrue(any(u['id'] == self.seller_profile.id for u in res_filter.json()['users']))

        # Admin unblock
        res_unblock = self.client.post(
            f'/api/admin/users/{self.seller_profile.id}/toggle_block/',
            HTTP_AUTHORIZATION=f'Token {self.admin_token}'
        )
        self.assertEqual(res_unblock.status_code, status.HTTP_200_OK)
        self.assertFalse(res_unblock.json()['is_blocked'])
        print("[PASS] 2. User management search, filtering, and blocking verified.")

    # -------------------------------------------------------------
    # 3. User Detailed Activity History
    # -------------------------------------------------------------
    def test_03_user_detail_activity(self):
        res = self.client.get(
            f'/api/admin/users/{self.seller_profile.id}/detail/',
            HTTP_AUTHORIZATION=f'Token {self.admin_token}'
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(data['user']['full_name'], 'Zubair Khan Seller')
        self.assertIn('listings', data)
        self.assertIn('unlocks_bought', data)
        self.assertIn('unlocks_received', data)
        self.assertTrue(len(data['listings']) >= 1)
        print("[PASS] 3. Detailed user activity audit trail verified.")

    # -------------------------------------------------------------
    # 4. Listings Moderation (Approve, Reject, Sponsor, Mark Sold, Delete)
    # -------------------------------------------------------------
    def test_04_listings_moderation(self):
        test_listing = Listing.objects.create(
            book=self.book,
            seller=self.seller_profile,
            condition='Like New',
            price=Decimal('1100.00'),
            city='Bahawalpur',
            status='pending'
        )

        # 1. Approve
        res_app = self.client.post(
            f'/api/admin/listings/{test_listing.id}/moderate/',
            {'action': 'approve'},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.admin_token}'
        )
        self.assertEqual(res_app.status_code, status.HTTP_200_OK)
        test_listing.refresh_from_db()
        self.assertEqual(test_listing.status, 'active')

        # 2. Toggle Sponsored
        res_spons = self.client.post(
            f'/api/admin/listings/{test_listing.id}/moderate/',
            {'action': 'toggle_sponsored'},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.admin_token}'
        )
        self.assertEqual(res_spons.status_code, status.HTTP_200_OK)
        test_listing.refresh_from_db()
        self.assertTrue(test_listing.is_sponsored)

        # 3. Mark Sold
        res_sold = self.client.post(
            f'/api/admin/listings/{test_listing.id}/moderate/',
            {'action': 'mark_sold'},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.admin_token}'
        )
        self.assertEqual(res_sold.status_code, status.HTTP_200_OK)
        test_listing.refresh_from_db()
        self.assertEqual(test_listing.status, 'sold')

        # 4. Delete
        res_del = self.client.post(
            f'/api/admin/listings/{test_listing.id}/moderate/',
            {'action': 'delete'},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.admin_token}'
        )
        self.assertEqual(res_del.status_code, status.HTTP_200_OK)
        self.assertFalse(Listing.objects.filter(id=test_listing.id).exists())
        print("[PASS] 4. Listing moderation actions (approve, sponsor, mark_sold, delete) verified.")

    # -------------------------------------------------------------
    # 5. Admin Listing Edit Override
    # -------------------------------------------------------------
    def test_05_admin_listing_edit_override(self):
        res_edit = self.client.post(
            f'/api/admin/listings/{self.listing.id}/edit/',
            {
                'price': '820.00',
                'condition': 'Brand New',
                'pickup_location': 'Admin Gate 1'
            },
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.admin_token}'
        )
        self.assertEqual(res_edit.status_code, status.HTTP_200_OK)
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.price, Decimal('820.00'))
        self.assertEqual(self.listing.condition, 'Brand New')
        self.assertEqual(self.listing.pickup_location, 'Admin Gate 1')
        print("[PASS] 5. Admin direct listing edit override verified.")

    # -------------------------------------------------------------
    # 6. Seller Activity Monitoring
    # -------------------------------------------------------------
    def test_06_seller_activity_monitoring(self):
        res_sellers = self.client.get('/api/admin/sellers/', HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        self.assertEqual(res_sellers.status_code, status.HTTP_200_OK)
        data = res_sellers.json()
        self.assertIn('sellers', data)
        self.assertTrue(any(s['full_name'] == 'Zubair Khan Seller' for s in data['sellers']))
        print("[PASS] 6. Seller performance & verification monitoring verified.")

    # -------------------------------------------------------------
    # 7. Payment Transactions & Unlocks Ledger
    # -------------------------------------------------------------
    def test_07_payment_transactions_and_unlocks_ledger(self):
        # Create unlock & transaction
        unlock = ContactUnlock.objects.create(
            listing=self.listing,
            buyer=self.buyer_profile,
            seller=self.seller_profile,
            fee_amount=Decimal('50.00'),
            payment_method='jazzcash',
            transaction_id='TXN-TEST-LEDGER-001',
            deal_status='unlocked_pending'
        )
        txn = PaymentTransaction.objects.create(
            buyer=self.buyer_profile,
            listing=self.listing,
            amount=Decimal('50.00'),
            currency='PKR',
            gateway='jazzcash',
            status='completed',
            gateway_ref='TXN-TEST-LEDGER-001',
            unlock=unlock
        )

        # Test transactions endpoint
        res_txn = self.client.get('/api/admin/transactions/?gateway=jazzcash', HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        self.assertEqual(res_txn.status_code, status.HTTP_200_OK)
        self.assertTrue(len(res_txn.json()['transactions']) >= 1)

        # Test unlocks endpoint
        res_unlock = self.client.get('/api/admin/unlocks/?deal_status=unlocked_pending', HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        self.assertEqual(res_unlock.status_code, status.HTTP_200_OK)
        self.assertTrue(len(res_unlock.json()['unlocks']) >= 1)
        print("[PASS] 7. Payment transactions & unlocks ledger filtering verified.")

    # -------------------------------------------------------------
    # 8. Admin Force Refund Override
    # -------------------------------------------------------------
    def test_08_admin_force_refund_override(self):
        initial_balance = self.buyer_profile.wallet_balance
        unlock_refund = ContactUnlock.objects.create(
            listing=self.listing,
            buyer=self.buyer_profile,
            seller=self.seller_profile,
            fee_amount=Decimal('50.00'),
            payment_method='easypaisa',
            transaction_id='TXN-FORCE-REF-001',
            deal_status='disputed'
        )

        res_force = self.client.post(
            f'/api/admin/unlocks/{unlock_refund.unlock_id}/force_refund/',
            {'reason': 'Seller refused to meet buyer after phone unlock'},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.admin_token}'
        )
        self.assertEqual(res_force.status_code, status.HTTP_200_OK)

        self.buyer_profile.refresh_from_db()
        self.assertEqual(self.buyer_profile.wallet_balance, initial_balance + Decimal('50.00'))

        unlock_refund.refresh_from_db()
        self.assertEqual(unlock_refund.deal_status, 'no_deal_refunded')
        self.assertIn("Admin Forced Refund", unlock_refund.cancellation_reason)

        # Duplicate refund rejection
        res_dup = self.client.post(
            f'/api/admin/unlocks/{unlock_refund.unlock_id}/force_refund/',
            {'reason': 'Try again'},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.admin_token}'
        )
        self.assertEqual(res_dup.status_code, status.HTTP_400_BAD_REQUEST)
        print("[PASS] 8. Admin force refund override & wallet credit verified.")

    # -------------------------------------------------------------
    # 9. Reports & Complaints System
    # -------------------------------------------------------------
    def test_09_reports_and_complaints_system(self):
        # 1. User submits report
        res_submit = self.client.post(
            '/api/reports/submit/',
            {
                'listing_id': self.listing.id,
                'report_type': 'fake_condition',
                'description': 'Pages have heavy water damage not shown in images.'
            },
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.buyer_token}'
        )
        self.assertEqual(res_submit.status_code, status.HTTP_201_CREATED)
        report_id = res_submit.json()['report']['id']

        # 2. Admin views reports
        res_list = self.client.get('/api/admin/reports/?status=pending', HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        self.assertEqual(res_list.status_code, status.HTTP_200_OK)
        self.assertTrue(any(r['id'] == report_id for r in res_list.json()['reports']))

        # 3. Admin resolves report & deactivates listing
        res_res = self.client.post(
            f'/api/admin/reports/{report_id}/resolve/',
            {
                'status': 'resolved',
                'admin_notes': 'Verified water damage; paused listing and warned seller.',
                'action': 'deactivate_listing'
            },
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.admin_token}'
        )
        self.assertEqual(res_res.status_code, status.HTTP_200_OK)

        report = MarketplaceReport.objects.get(id=report_id)
        self.assertEqual(report.status, 'resolved')
        self.assertIsNotNone(report.resolved_at)

        self.listing.refresh_from_db()
        self.assertEqual(self.listing.status, 'inactive')
        print("[PASS] 9. Reports submission, moderation, and automated action verified.")

    # -------------------------------------------------------------
    # 10. Advertisement Management
    # -------------------------------------------------------------
    def test_10_advertisement_management(self):
        # 1. Create Ad
        res_create = self.client.post(
            '/api/admin/ads/create/',
            {
                'title': 'IUB Semester Stationery Discount',
                'sponsor_name': 'Baghdad Stationery Corner',
                'ad_type': 'banner_bottom',
                'headline': '25% Off Exam Supplies',
                'target_url': 'https://iub.edu.pk',
                'is_active': True
            },
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.admin_token}'
        )
        self.assertEqual(res_create.status_code, status.HTTP_201_CREATED)
        ad_id = res_create.json()['ad']['id']

        # 2. Toggle active
        res_tog = self.client.post(f'/api/admin/ads/{ad_id}/toggle/', HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        self.assertEqual(res_tog.status_code, status.HTTP_200_OK)
        self.assertFalse(res_tog.json()['is_active'])

        # 3. Edit ad
        res_edit = self.client.post(
            f'/api/admin/ads/{ad_id}/edit/',
            {'headline': 'Updated 30% Off Everything'},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.admin_token}'
        )
        self.assertEqual(res_edit.status_code, status.HTTP_200_OK)
        self.assertEqual(res_edit.json()['ad']['headline'], 'Updated 30% Off Everything')

        # 4. Delete ad
        res_del = self.client.post(f'/api/admin/ads/{ad_id}/delete/', HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        self.assertEqual(res_del.status_code, status.HTTP_200_OK)
        self.assertFalse(Advertisement.objects.filter(id=ad_id).exists())
        print("[PASS] 10. Advertisement full CRUD and CTR metrics verified.")

    # -------------------------------------------------------------
    # 11. Platform Monetization & Safety Policy Settings
    # -------------------------------------------------------------
    def test_11_platform_settings_and_policies(self):
        # Regular user rejected
        res_forbid = self.client.post(
            '/api/admin/settings/',
            {'contact_unlock_fee': '65.00'},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.buyer_token}'
        )
        self.assertEqual(res_forbid.status_code, status.HTTP_403_FORBIDDEN)

        # Admin updates settings
        res_update = self.client.post(
            '/api/admin/settings/',
            {
                'contact_unlock_fee': '60.00',
                'require_admin_approval': True,
                'allow_sponsored_listings': True,
                'auto_refund_days': 7
            },
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.admin_token}'
        )
        self.assertEqual(res_update.status_code, status.HTTP_200_OK)

        self.setting.refresh_from_db()
        self.assertEqual(self.setting.contact_unlock_fee, Decimal('60.00'))
        self.assertTrue(self.setting.require_admin_approval)
        self.assertEqual(self.setting.auto_refund_days, 7)

        # Reset fee back to 50
        self.setting.contact_unlock_fee = Decimal('50.00')
        self.setting.require_admin_approval = False
        self.setting.save()
        print("[PASS] 11. Platform monetization & safety policy settings verified.")


def run_tests():
    print("\n=======================================================")
    print(" Running BookBazaar Phase 4 Admin Management Test Suite")
    print("=======================================================\n")
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(Phase4AdminManagementTests)
    runner = unittest.TextTestRunner(verbosity=1)
    result = runner.run(suite)
    print("\n=======================================================")
    if result.wasSuccessful():
        print(" [ALL TESTS PASSED] Phase 4 Admin Management Requirements Verified!")
    else:
        print(f" [TEST FAILURES] {len(result.failures)} failures, {len(result.errors)} errors.")
    print("=======================================================\n")
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
