"""
BookBazaar - Pre-Phase 6 Automated Test Suite: Admin Notifications & Deal Lifecycle Actions
Verifies:
1. Notification creation on successful Rs. 50 contact unlock payment ('PAYMENT_RECEIVED').
2. Notification creation on deal confirmation ('DEAL_SUCCESSFUL').
3. Notification creation on failed deal refund request ('DEAL_FAILED_REFUND_REQ').
4. Admin one-click process refund action, wallet credit verification, and deal status transition.
5. Strict prevention of duplicate refunds (idempotency guard and database locking).
6. Admin notification listing, unread count badges, mark single as read, mark all as read.
7. Role-based access control (IsAdminOnly protection against unauthenticated/non-admin users).
"""

import os
import uuid
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookbazaar_backend.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import status

from bazaar.models import (
    UserProfile, Book, Listing, ContactUnlock,
    PlatformSetting, PaymentTransaction, AdminNotification
)


class AdminNotificationsAndLifecycleTests(TestCase):
    def setUp(self):
        self.client = Client()

        # 1. Platform Settings
        self.setting = PlatformSetting.get_settings()
        self.setting.contact_unlock_fee = Decimal('50.00')
        self.setting.platform_name = 'BookBazaar Pakistan'
        self.setting.save()

        # 2. Admin User
        self.admin_user = User.objects.create_superuser(
            username='admin_notif_tester',
            password='AdminPassword123!',
            email='admin_notif@bookbazaar.pk'
        )
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            full_name='Chief Administrator',
            phone_number='03009990000',
            city='Islamabad',
            campus_or_area='Headquarters',
            user_type='admin'
        )
        self.admin_token = Token.objects.create(user=self.admin_user).key

        # 3. Seller User
        self.seller_user = User.objects.create_user(
            username='seller_notif_tester',
            password='SellerPassword123!',
            email='seller_notif@bookbazaar.pk'
        )
        self.seller_profile = UserProfile.objects.create(
            user=self.seller_user,
            full_name='Hamza Malik (Seller)',
            phone_number='03011112222',
            city='Lahore',
            campus_or_area='PU Old Campus',
            user_type='student'
        )
        self.seller_token = Token.objects.create(user=self.seller_user).key

        # 4. Buyer User
        self.buyer_user = User.objects.create_user(
            username='buyer_notif_tester',
            password='BuyerPassword123!',
            email='buyer_notif@bookbazaar.pk'
        )
        self.buyer_profile = UserProfile.objects.create(
            user=self.buyer_user,
            full_name='Fatima Noor (Buyer)',
            phone_number='03023334444',
            city='Lahore',
            campus_or_area='Hostel 4',
            user_type='student',
            wallet_balance=Decimal('100.00')
        )
        self.buyer_token = Token.objects.create(user=self.buyer_user).key

        # 5. Book and Listing
        self.book = Book.objects.create(
            title='Data Structures and Algorithms in Python',
            author='Michael T. Goodrich',
            isbn='9781118290279',
            category='Computer Science',
            edition='1st Edition'
        )
        self.listing = Listing.objects.create(
            book=self.book,
            seller=self.seller_profile,
            condition='Like New',
            price=Decimal('850.00'),
            city='Lahore',
            pickup_location='CS Department Library',
            status='active'
        )

    # -------------------------------------------------------------
    # 1. Notification Creation on Successful Rs. 50 Payment
    # -------------------------------------------------------------
    def test_01_notification_created_on_successful_payment(self):
        # Step A: Initiate payment
        init_res = self.client.post(
            '/api/payments/initiate/',
            {'listing_id': self.listing.id, 'gateway': 'jazzcash'},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.buyer_token}'
        )
        self.assertEqual(init_res.status_code, status.HTTP_201_CREATED)
        txn_id = init_res.json()['transaction_id']

        # Step B: Verify payment (simulated success)
        verify_res = self.client.post(
            '/api/payments/verify/',
            {'transaction_id': txn_id, 'simulate_outcome': 'success'},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.buyer_token}'
        )
        self.assertEqual(verify_res.status_code, status.HTTP_200_OK)

        # Step C: Assert notification created for Admin
        notif = AdminNotification.objects.filter(
            notification_type='PAYMENT_RECEIVED',
            transaction__transaction_id=txn_id
        ).first()
        self.assertIsNotNone(notif, "AdminNotification of type PAYMENT_RECEIVED should be created.")
        self.assertIn("Payment Received", notif.title)
        self.assertIn("Fatima Noor", notif.message)
        self.assertIn("Data Structures and Algorithms", notif.message)
        self.assertFalse(notif.is_read)
        self.assertEqual(notif.user, self.buyer_profile)
        self.assertEqual(notif.buyer, self.buyer_profile)
        self.assertEqual(notif.seller, self.seller_profile)
        self.assertEqual(notif.listing, self.listing)
        self.assertTrue(notif.is_resolved)
        print("[PASS] 1. Notification creation on successful Rs. 50 payment verified.")

    # -------------------------------------------------------------
    # 2. Notification Creation on Deal Successful
    # -------------------------------------------------------------
    def test_02_notification_created_on_deal_completion(self):
        # Create completed unlock
        unlock = ContactUnlock.objects.create(
            listing=self.listing,
            buyer=self.buyer_profile,
            seller=self.seller_profile,
            deal_status='unlocked_pending',
            fee_amount=Decimal('50.00')
        )

        # Buyer confirms deal made
        deal_res = self.client.post(
            f'/api/unlocks/{unlock.unlock_id}/confirm_deal/',
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.buyer_token}'
        )
        self.assertEqual(deal_res.status_code, status.HTTP_200_OK)

        # Assert notification created
        notif = AdminNotification.objects.filter(
            notification_type='DEAL_SUCCESSFUL',
            unlock=unlock
        ).first()
        self.assertIsNotNone(notif, "AdminNotification of type DEAL_SUCCESSFUL should be created.")
        self.assertIn("Deal Successful", notif.title)
        self.assertIn("Fatima Noor", notif.message)
        self.assertIn("Hamza Malik", notif.message)
        self.assertFalse(notif.is_read)
        self.assertEqual(notif.buyer, self.buyer_profile)
        self.assertEqual(notif.seller, self.seller_profile)
        self.assertTrue(notif.is_resolved)
        print("[PASS] 2. Notification creation on deal completion verified.")

    # -------------------------------------------------------------
    # 3. Notification Creation on Failed Deal Refund Request
    # -------------------------------------------------------------
    def test_03_notification_created_on_failed_deal_refund_request(self):
        # Create completed unlock
        unlock = ContactUnlock.objects.create(
            listing=self.listing,
            buyer=self.buyer_profile,
            seller=self.seller_profile,
            deal_status='unlocked_pending',
            fee_amount=Decimal('50.00')
        )

        # Buyer requests refund
        req_res = self.client.post(
            f'/api/unlocks/{unlock.unlock_id}/request_refund/',
            {'reason': 'Seller unreachable on phone and did not arrive.'},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.buyer_token}'
        )
        self.assertEqual(req_res.status_code, status.HTTP_200_OK)

        # Assert notification created
        notif = AdminNotification.objects.filter(
            notification_type='DEAL_FAILED_REFUND_REQ',
            unlock=unlock
        ).first()
        self.assertIsNotNone(notif, "AdminNotification of type DEAL_FAILED_REFUND_REQ should be created.")
        self.assertIn("Deal Unsuccessful", notif.title)
        self.assertIn("Fatima Noor", notif.message)
        self.assertIn("refund", notif.message.lower())
        self.assertFalse(notif.is_read)
        self.assertEqual(notif.buyer, self.buyer_profile)
        self.assertEqual(notif.seller, self.seller_profile)
        self.assertFalse(notif.is_resolved)
        print("[PASS] 3. Notification creation on failed deal refund request verified.")

    # -------------------------------------------------------------
    # 4. Admin Processing Refund & Wallet Credit Verification
    # -------------------------------------------------------------
    def test_04_admin_process_notification_refund_and_wallet_credit(self):
        # Create unlock and payment transaction
        payment_txn = PaymentTransaction.objects.create(
            transaction_id=uuid.uuid4(),
            gateway='jazzcash',
            amount=Decimal('50.00'),
            currency='PKR',
            status='completed',
            buyer=self.buyer_profile,
            listing=self.listing
        )
        unlock = ContactUnlock.objects.create(
            listing=self.listing,
            buyer=self.buyer_profile,
            seller=self.seller_profile,
            deal_status='buyer_complaint_refund_pending',
            fee_amount=Decimal('50.00')
        )
        payment_txn.unlock = unlock
        payment_txn.save()

        # Create refund request notification
        notif = AdminNotification.objects.create(
            notification_type='DEAL_FAILED_REFUND_REQ',
            title="Deal Unsuccessful: Refund Requested",
            message="Buyer Fatima Noor requested Rs. 50 refund.",
            user=self.buyer_profile,
            listing=self.listing,
            unlock=unlock,
            transaction=payment_txn,
            is_read=False
        )

        initial_wallet = self.buyer_profile.wallet_balance
        self.assertEqual(initial_wallet, Decimal('100.00'))

        # Admin processes the refund via the notification action endpoint
        refund_res = self.client.post(
            f'/api/admin/notifications/{notif.id}/process_refund/',
            {'reason': 'Approved by administrator after reviewing chat logs.'},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.admin_token}'
        )
        self.assertEqual(refund_res.status_code, status.HTTP_200_OK)
        res_data = refund_res.json()
        self.assertIn("refunded", res_data['message'])
        self.assertIn("REF-ADM-", res_data['refund_transaction_id'])

        # Verify buyer wallet credited with Rs. 50
        self.buyer_profile.refresh_from_db()
        self.assertEqual(self.buyer_profile.wallet_balance, Decimal('150.00'))

        # Verify unlock status transitioned to 'no_deal_refunded'
        unlock.refresh_from_db()
        self.assertEqual(unlock.deal_status, 'no_deal_refunded')
        self.assertIsNotNone(unlock.refund_transaction_id)
        self.assertIsNotNone(unlock.refund_timestamp)

        # Verify payment transaction marked as 'refunded'
        payment_txn.refresh_from_db()
        self.assertEqual(payment_txn.status, 'refunded')

        # Verify notification marked as read and resolved
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)
        self.assertTrue(notif.is_resolved)

        # Verify confirmation notification created (REFUND_PROCESSED)
        confirm_notif = AdminNotification.objects.filter(
            notification_type='REFUND_PROCESSED',
            unlock=unlock
        ).first()
        self.assertIsNotNone(confirm_notif)
        self.assertIn("Refund Completed", confirm_notif.title)
        self.assertIn("Fatima Noor", confirm_notif.message)
        self.assertTrue(confirm_notif.is_resolved)

        print("[PASS] 4. Admin processing the refund and wallet credit verified.")

    # -------------------------------------------------------------
    # 5. Prevention of Duplicate Refunds (Idempotency & Row Locking)
    # -------------------------------------------------------------
    def test_05_prevent_duplicate_refunds(self):
        payment_txn = PaymentTransaction.objects.create(
            transaction_id=uuid.uuid4(),
            gateway='easypaisa',
            amount=Decimal('50.00'),
            currency='PKR',
            status='completed',
            buyer=self.buyer_profile,
            listing=self.listing
        )
        unlock = ContactUnlock.objects.create(
            listing=self.listing,
            buyer=self.buyer_profile,
            seller=self.seller_profile,
            deal_status='buyer_complaint_refund_pending',
            fee_amount=Decimal('50.00')
        )
        payment_txn.unlock = unlock
        payment_txn.save()

        notif = AdminNotification.objects.create(
            notification_type='DEAL_FAILED_REFUND_REQ',
            title="Deal Unsuccessful: Refund Requested",
            message="Buyer requested refund.",
            user=self.buyer_profile,
            listing=self.listing,
            unlock=unlock,
            transaction=payment_txn,
            is_read=False
        )

        # First refund attempt: Succeeds
        res1 = self.client.post(
            f'/api/admin/notifications/{notif.id}/process_refund/',
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.admin_token}'
        )
        self.assertEqual(res1.status_code, status.HTTP_200_OK)

        self.buyer_profile.refresh_from_db()
        balance_after_first = self.buyer_profile.wallet_balance
        self.assertEqual(balance_after_first, Decimal('150.00'))

        # Second refund attempt on same notification: MUST FAIL
        res2 = self.client.post(
            f'/api/admin/notifications/{notif.id}/process_refund/',
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.admin_token}'
        )
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already been refunded", res2.json()['error'])

        # Wallet balance MUST strictly remain 150.00 (not 200.00)
        self.buyer_profile.refresh_from_db()
        self.assertEqual(self.buyer_profile.wallet_balance, Decimal('150.00'))

        print("[PASS] 5. Duplicate refund attempt strictly blocked; wallet balance invariant preserved.")

    # -------------------------------------------------------------
    # 6. Admin Notification List, Unread Counts, Mark Single/All Read
    # -------------------------------------------------------------
    def test_06_admin_notification_api_list_and_read_management(self):
        # Clean previous and create 3 test notifications (2 unread, 1 read)
        AdminNotification.objects.all().delete()

        n1 = AdminNotification.objects.create(
            notification_type='PAYMENT_RECEIVED',
            title='Test Payment 1',
            message='Buyer paid 50',
            is_read=False
        )
        n2 = AdminNotification.objects.create(
            notification_type='DEAL_SUCCESSFUL',
            title='Test Deal 2',
            message='Deal finished',
            is_read=False
        )
        n3 = AdminNotification.objects.create(
            notification_type='SYSTEM_ALERT',
            title='Test System 3',
            message='System healthy',
            is_read=True
        )

        # GET /api/admin/notifications/
        list_res = self.client.get(
            '/api/admin/notifications/',
            HTTP_AUTHORIZATION=f'Token {self.admin_token}'
        )
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        data = list_res.json()
        self.assertEqual(data['unread_count'], 2)
        self.assertEqual(data['total_count'], 3)
        self.assertEqual(len(data['notifications']), 3)

        # Mark single notification as read: POST /api/admin/notifications/{id}/read/
        read_res = self.client.post(
            f'/api/admin/notifications/{n1.id}/read/',
            HTTP_AUTHORIZATION=f'Token {self.admin_token}'
        )
        self.assertEqual(read_res.status_code, status.HTTP_200_OK)
        self.assertEqual(read_res.json()['unread_count'], 1)

        n1.refresh_from_db()
        self.assertTrue(n1.is_read)

        # Mark all as read: POST /api/admin/notifications/mark_all_read/
        mark_all_res = self.client.post(
            '/api/admin/notifications/mark_all_read/',
            HTTP_AUTHORIZATION=f'Token {self.admin_token}'
        )
        self.assertEqual(mark_all_res.status_code, status.HTTP_200_OK)
        self.assertEqual(mark_all_res.json()['unread_count'], 0)

        self.assertEqual(AdminNotification.objects.filter(is_read=False).count(), 0)
        print("[PASS] 6. Admin notifications list, unread counts, and mark-read actions verified.")

    # -------------------------------------------------------------
    # 7. Role-Based Access Control (Security)
    # -------------------------------------------------------------
    def test_07_admin_notifications_permission_protection(self):
        # 1. Unauthenticated request to list notifications
        anon_res = self.client.get('/api/admin/notifications/')
        self.assertEqual(anon_res.status_code, status.HTTP_401_UNAUTHORIZED)

        # 2. Non-admin buyer request to list notifications
        buyer_list_res = self.client.get(
            '/api/admin/notifications/',
            HTTP_AUTHORIZATION=f'Token {self.buyer_token}'
        )
        self.assertEqual(buyer_list_res.status_code, status.HTTP_403_FORBIDDEN)

        # 3. Non-admin buyer request to process refund
        notif = AdminNotification.objects.create(
            notification_type='DEAL_FAILED_REFUND_REQ',
            title='Unauthorized Refund Test',
            message='Unauthorized',
            is_read=False
        )
        buyer_refund_res = self.client.post(
            f'/api/admin/notifications/{notif.id}/process_refund/',
            HTTP_AUTHORIZATION=f'Token {self.buyer_token}'
        )
        self.assertEqual(buyer_refund_res.status_code, status.HTTP_403_FORBIDDEN)
        print("[PASS] 7. RBAC security protection (401/403) for admin notifications endpoints verified.")

    # -------------------------------------------------------------
    # 8. Notification Creation on Payment Failed / Cancelled
    # -------------------------------------------------------------
    def test_08_notification_created_on_payment_failed_and_cancelled(self):
        # Step A: Initiate payment
        init_res = self.client.post(
            '/api/payments/initiate/',
            {'listing_id': self.listing.id, 'gateway': 'easypaisa'},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.buyer_token}'
        )
        self.assertEqual(init_res.status_code, status.HTTP_201_CREATED)
        txn_id = init_res.json()['transaction_id']

        # Step B: Cancel payment
        cancel_res = self.client.post(
            '/api/payments/cancel/',
            {'transaction_id': txn_id, 'reason': 'User changed mind'},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.buyer_token}'
        )
        self.assertEqual(cancel_res.status_code, status.HTTP_200_OK)

        # Step C: Assert PAYMENT_FAILED notification created
        notif = AdminNotification.objects.filter(
            notification_type='PAYMENT_FAILED',
            transaction__transaction_id=txn_id
        ).first()
        self.assertIsNotNone(notif, "AdminNotification of type PAYMENT_FAILED should be created.")
        self.assertIn("Payment Failed", notif.title)
        self.assertIn("Fatima Noor", notif.message)
        self.assertIn("Data Structures and Algorithms", notif.message)
        self.assertEqual(notif.buyer, self.buyer_profile)
        self.assertEqual(notif.seller, self.seller_profile)
        self.assertFalse(notif.is_resolved)
        print("[PASS] 8. Notification creation on failed/cancelled payment verified.")

    # -------------------------------------------------------------
    # 9. Generic Mark-Read Endpoint (/api/admin/notifications/mark-read/)
    # -------------------------------------------------------------
    def test_09_admin_mark_read_generic_endpoint(self):
        AdminNotification.objects.all().delete()
        n1 = AdminNotification.objects.create(
            notification_type='PAYMENT_RECEIVED',
            title='Mark Read Single Test',
            message='Testing mark read single',
            is_read=False
        )
        n2 = AdminNotification.objects.create(
            notification_type='DEAL_SUCCESSFUL',
            title='Mark Read Bulk Test',
            message='Testing mark read bulk',
            is_read=False
        )

        # Mark single notification as read via POST /api/admin/notifications/mark-read/
        single_res = self.client.post(
            '/api/admin/notifications/mark-read/',
            {'notification_id': n1.id},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.admin_token}'
        )
        self.assertEqual(single_res.status_code, status.HTTP_200_OK)
        self.assertEqual(single_res.json()['unread_count'], 1)
        n1.refresh_from_db()
        self.assertTrue(n1.is_read)

        # Mark all remaining notifications as read via POST /api/admin/notifications/mark-read/ (no ID)
        bulk_res = self.client.post(
            '/api/admin/notifications/mark-read/',
            {},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.admin_token}'
        )
        self.assertEqual(bulk_res.status_code, status.HTTP_200_OK)
        self.assertEqual(bulk_res.json()['unread_count'], 0)
        n2.refresh_from_db()
        self.assertTrue(n2.is_read)
        print("[PASS] 9. Generic mark-read endpoint (/api/admin/notifications/mark-read/) verified.")
