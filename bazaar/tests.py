from django.test import TestCase, Client
from django.contrib.auth.models import User
from bazaar.models import UserProfile, Book, Listing
from decimal import Decimal

class BookBazaarAiTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create demo users
        self.user1 = User.objects.create_user(username='student_bwp', password='password123')
        self.profile1 = UserProfile.objects.create(
            user=self.user1, full_name='Bilal Ahmed', phone_number='03001111111',
            city='Bahawalpur', user_type='student', rating=Decimal('5.00'), total_reviews=3
        )

        self.user2 = User.objects.create_user(username='student_lhr', password='password123')
        self.profile2 = UserProfile.objects.create(
            user=self.user2, full_name='Ali Khan', phone_number='03002222222',
            city='Lahore', user_type='student', rating=Decimal('4.90'), total_reviews=5
        )

        # Create sample books
        self.book1 = Book.objects.create(
            isbn='9780133943030', title='Software Engineering 10th Edition', author='Ian Sommerville',
            category='Software Engineering', education_board='Higher Education / University',
            grade_class='Bachelor / BS / Undergrad', subject='Software Engineering',
            original_retail_price=Decimal('2400.00')
        )

        self.book2 = Book.objects.create(
            isbn='9789695840130', title='Physics for Class 12', author='Punjab Textbook Board',
            category='FSc / Matric / O & A Level', education_board='Punjab Board',
            grade_class='Intermediate / FSc / ICS (11th - 12th)', subject='Physics',
            original_retail_price=Decimal('420.00')
        )

        # Create listings
        self.listing1 = Listing.objects.create(
            book=self.book1, seller=self.profile2, condition='Like New',
            price=Decimal('850.00'), city='Lahore', status='active'
        )

        self.listing2 = Listing.objects.create(
            book=self.book2, seller=self.profile1, condition='Good',
            price=Decimal('180.00'), city='Bahawalpur', status='active'
        )

    def test_ai_recommendations_endpoint(self):
        """Test GET /api/recommendations/ returns scored recommendations with AI match % and insight"""
        response = self.client.get(f'/api/recommendations/?user_id={self.profile1.id}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertGreaterEqual(data.get('count'), 1)
        recs = data.get('recommendations')
        self.assertTrue(len(recs) > 0)
        first_rec = recs[0]
        self.assertIn('ai_match_percentage', first_rec)
        self.assertIn('ai_insight', first_rec)
        self.assertGreaterEqual(first_rec['ai_match_percentage'], 80)
        self.assertLessEqual(first_rec['ai_match_percentage'], 99)

    def test_ai_price_advisor_endpoint_get(self):
        """Test GET /api/price-advisor/ calculates resale price based on condition and retail price"""
        response = self.client.get('/api/price-advisor/', {
            'title': 'Software Engineering',
            'category': 'Software Engineering',
            'condition': 'Good',
            'original_price': '2000'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        # 50% of 2000 = 1000
        self.assertEqual(data.get('suggested_price'), 1000)
        self.assertEqual(data.get('condition'), 'Good')
        self.assertIn('AI Suggested Price: Rs. 1000', data.get('insight'))

    def test_ai_price_advisor_endpoint_post(self):
        """Test POST /api/price-advisor/ with JSON payload"""
        response = self.client.post('/api/price-advisor/', {
            'title': 'Medical Physiology',
            'category': 'Medical & MBBS / BDS',
            'condition': 'Brand New',
            'original_price': '3000'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        # 80% of 3000 = 2400
        self.assertEqual(data.get('suggested_price'), 2400)
        self.assertEqual(data.get('discount_percentage'), 20)

    def test_homepage_branding(self):
        """Test homepage contains Bookzy AI branding and AI sections with no developer labels or admin links"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Bookzy AI', content)
        self.assertIn('Smart Book Marketplace & AI Reader Recommendations', content)
        self.assertIn('id="reader-onboarding-modal"', content)
        self.assertIn('id="ai-recommendations-section"', content)
        self.assertIn('id="free-books-section"', content)
        self.assertIn('id="ptb-textbooks-section"', content)
        self.assertIn('id="ai-price-advisor-card"', content)
        self.assertIn('id="apply-ai-price-btn"', content)
        # Verify developer labels removed and admin completely hidden from homepage
        self.assertNotIn('Live Beta', content)
        self.assertNotIn('href="/admin-panel/"', content)
        self.assertIn('id="quick-free-books-card"', content)
        self.assertIn('🎁 Free Books', content)

    def test_admin_panel_restricted_access_and_authentication(self):
        """Test /admin-panel/ security lock, unauthorized restriction, and staff login"""
        # Create staff admin user
        staff_admin = User.objects.create_user(
            username='staff_test', email='staff@bookzy.pk', password='securepassword123', is_staff=True
        )

        # 1. Unauthenticated visitor gets restricted login screen
        resp = self.client.get('/admin-panel/')
        self.assertEqual(resp.status_code, 200)
        body = resp.content.decode('utf-8')
        self.assertIn('Restricted Admin Access', body)
        self.assertIn('Unlock Admin Dashboard', body)
        self.assertNotIn('PostgreSQL 18 Connected', body)
        self.assertNotIn('Phase 4 Complete System', body)

        # 2. Non-staff user attempt gets rejected with 401
        fail_resp = self.client.post('/admin-panel/', {
            'username': 'student_bwp',
            'password': 'password123'
        })
        self.assertEqual(fail_resp.status_code, 401)
        fail_body = fail_resp.content.decode('utf-8')
        self.assertIn('Invalid administrator credentials or unauthorized account', fail_body)

        # 3. Staff user authenticates successfully
        success_resp = self.client.post('/admin-panel/', {
            'username': 'staff_test',
            'password': 'securepassword123'
        })
        self.assertEqual(success_resp.status_code, 200)
        success_body = success_resp.content.decode('utf-8')
        self.assertIn('System Online', success_body)
        self.assertIn('Central Operations Hub', success_body)
        self.assertIn('Lock Admin', success_body)

        # 4. Logout action resets admin session
        logout_resp = self.client.get('/admin-panel/?action=logout')
        self.assertEqual(logout_resp.status_code, 302)
        follow_resp = self.client.get('/admin-panel/')
        self.assertIn('Restricted Admin Access', follow_resp.content.decode('utf-8'))

    def test_age_and_free_book_ai_recommendations(self):
        """Test multi-factor AI recommender prioritizes free books and matches age groups"""
        # Create a free book
        free_book = Book.objects.create(
            isbn='9789690099881', title='Primary Math Class 3 (Free Donation)', author='PTB',
            category='Punjab Textbooks (Primary to FSc)', education_board='Punjab Board',
            grade_class='Class 3 (Primary)', target_age_group='kids',
            original_retail_price=Decimal('250.00')
        )
        Listing.objects.create(
            book=free_book, seller=self.profile2, condition='Good',
            price=Decimal('0.00'), is_free=True, target_age_group='kids',
            city='Lahore', status='active'
        )

        response = self.client.get('/api/recommendations/?age_group=kids&city=Lahore')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        recs = data.get('recommendations')
        self.assertTrue(len(recs) > 0)
        # Top item should be free donation
        self.assertTrue(recs[0]['is_free'] or float(recs[0]['price']) == 0)
        self.assertEqual(recs[0]['ai_badge'], '🎁 FREE Donation')

    def test_update_reader_preferences_endpoint(self):
        """Test POST /api/user/preferences/ updates reader profile"""
        response = self.client.post('/api/user/preferences/', {
            'user_id': self.profile1.id,
            'full_name': 'Bilal Ahmed Khan',
            'age_group': 'young_adult',
            'city': 'Bahawalpur',
            'interests': ['novels', 'history', 'free_only']
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertEqual(data['profile']['age_group'], 'young_adult')
        self.profile1.refresh_from_db()
        self.assertEqual(self.profile1.age_group, 'young_adult')

