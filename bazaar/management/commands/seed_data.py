from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from bazaar.models import UserProfile, Book, Listing, ContactUnlock, SellerReview, Advertisement, PlatformSetting
from bazaar.services.book_service import KNOWN_CATALOG
from bazaar.services.seed_service import ensure_demo_listings
from decimal import Decimal
import uuid
from django.utils import timezone

class Command(BaseCommand):
    help = 'Seeds initial realistic data for Bookzy AI (Pakistan Used Books Marketplace)'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting Bookzy AI database seeding...")

        # 1. Platform Settings
        setting, _ = PlatformSetting.objects.get_or_create(id=1)
        setting.platform_name = 'Bookzy AI'
        setting.contact_unlock_fee = Decimal('50.00')
        setting.auto_refund_days = 5
        setting.require_admin_approval = False
        setting.save()
        self.stdout.write(f"-> Platform settings ready (Unlock fee: Rs. {setting.contact_unlock_fee})")

        # 2. Admin User
        admin_user, created = User.objects.get_or_create(username='admin')
        if created or not admin_user.has_usable_password():
            admin_user.set_password('admin123')
            admin_user.is_superuser = True
            admin_user.is_staff = True
            admin_user.email = 'admin@bookbazaar.pk'
            admin_user.save()

        admin_profile, _ = UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={
                'full_name': 'System Administrator',
                'phone_number': '03000000000',
                'city': 'Islamabad',
                'campus_or_area': 'National Operations Center',
                'user_type': 'admin',
                'wallet_balance': Decimal('1500.00')
            }
        )

        # 3. Realistic Student & Reader Users
        sample_users_data = [
            {
                'username': 'ali_seller',
                'name': 'Ali Khan (Verified Seller)',
                'phone': '03017654321',
                'city': 'Lahore',
                'campus': 'Main Campus / Student Center',
                'type': 'student',
                'rating': Decimal('4.9'),
                'reviews': 12,
                'wallet': Decimal('250.00')
            },
            {
                'username': 'fatima_z',
                'name': 'Fatima Zahra',
                'phone': '03129876543',
                'city': 'Islamabad',
                'campus': 'University Road / Student Library',
                'type': 'student',
                'rating': Decimal('5.0'),
                'reviews': 18,
                'wallet': Decimal('140.00')
            },
            {
                'username': 'hamza_multan',
                'name': 'Hamza Tariq',
                'phone': '03335551234',
                'city': 'Multan',
                'campus': 'Bahauddin Zakariya University / Bosan Road',
                'type': 'reader',
                'rating': Decimal('4.7'),
                'reviews': 8,
                'wallet': Decimal('0.00')
            },
            {
                'username': 'usman_lhr',
                'name': 'Usman Gujjar',
                'phone': '03451122334',
                'city': 'Lahore',
                'campus': 'Urdu Bazaar / Anarkali',
                'type': 'bookstore',
                'rating': Decimal('4.8'),
                'reviews': 45,
                'wallet': Decimal('1200.00')
            },
            {
                'username': 'ayesha_khi',
                'name': 'Ayesha Siddiqui',
                'phone': '03214455667',
                'city': 'Karachi',
                'campus': 'NED University / Gulshan-e-Iqbal',
                'type': 'student',
                'rating': Decimal('4.8'),
                'reviews': 15,
                'wallet': Decimal('70.00')
            },
            {
                'username': 'buyer_test',
                'name': 'Ayesha Reader',
                'phone': '03023344556',
                'city': 'Islamabad',
                'campus': 'Central Campus / Student Center',
                'type': 'student',
                'rating': Decimal('5.0'),
                'reviews': 2,
                'wallet': Decimal('300.00')
            }
        ]

        profiles = {}
        for udata in sample_users_data:
            u, _ = User.objects.get_or_create(username=udata['username'])
            u.set_password('password123')
            u.save()

            prof, _ = UserProfile.objects.get_or_create(
                phone_number=udata['phone'],
                defaults={
                    'user': u,
                    'full_name': udata['name'],
                    'city': udata['city'],
                    'campus_or_area': udata['campus'],
                    'user_type': udata['type'],
                    'rating': udata['rating'],
                    'total_reviews': udata['reviews'],
                    'wallet_balance': udata['wallet']
                }
            )
            profiles[udata['username']] = prof

        self.stdout.write(f"-> Created {len(sample_users_data)} active student & seller profiles.")

        # 4. Seed Books
        books = {}
        for isbn, bdata in KNOWN_CATALOG.items():
            book, _ = Book.objects.get_or_create(
                isbn=isbn,
                defaults={
                    'title': bdata['title'],
                    'author': bdata['author'],
                    'publisher': bdata['publisher'],
                    'edition': bdata['edition'],
                    'category': bdata['category'],
                    'description': bdata['description'],
                    'cover_image': bdata['cover_image'],
                    'original_retail_price': Decimal(str(bdata['original_retail_price']))
                }
            )
            books[isbn] = book

        self.stdout.write(f"-> Seeded {len(books)} standard curriculum & popular books.")

        # 5. Seed Listings with Multi-seller price comparison
        listings_data = [
            # Clean Code (ISBN: 9780132350884 - Retail: Rs. 2200)
            {
                'isbn': '9780132350884',
                'seller': 'ali_seller',
                'condition': 'Good',
                'price': Decimal('650.00'),
                'city': 'Lahore',
                'pickup': 'Central Campus Library Cafeteria',
                'desc': 'Used for 4th semester Agile module. Very clean inside, pencil underlinings in Chapter 3 only. Ready for pickup today!',
                'photo': 'https://images-na.ssl-images-amazon.com/images/I/41xShlnTZTL._SX376_BO1,204,203,200_.jpg',
                'is_sponsored': True
            },
            {
                'isbn': '9780132350884',
                'seller': 'fatima_z',
                'condition': 'Like New',
                'price': Decimal('850.00'),
                'city': 'Islamabad',
                'pickup': 'Main Campus Department of Computing',
                'desc': 'Brand like new, zero markings. Bought last month, clearing bookshelf after passing course.',
                'photo': 'https://images-na.ssl-images-amazon.com/images/I/41xShlnTZTL._SX376_BO1,204,203,200_.jpg',
                'is_sponsored': False
            },
            {
                'isbn': '9780132350884',
                'seller': 'usman_lhr',
                'condition': 'Fair',
                'price': Decimal('500.00'),
                'city': 'Lahore',
                'pickup': 'Urdu Bazaar Lahore / Courier available',
                'desc': 'Affordable student copy. Outer corners slightly soft, text completely clean and readable.',
                'photo': 'https://images-na.ssl-images-amazon.com/images/I/41xShlnTZTL._SX376_BO1,204,203,200_.jpg',
                'is_sponsored': False
            },

            # Software Engineering: Pressman (ISBN: 9780078022128 - Retail: Rs. 1850)
            {
                'isbn': '9780078022128',
                'seller': 'ali_seller',
                'condition': 'Good',
                'price': Decimal('600.00'),
                'city': 'Lahore',
                'pickup': 'Hostel Gate or Software Engineering Lab',
                'desc': 'Standard reference book for Software Engineering students. Hardcover binding, intact spine.',
                'photo': 'https://images-na.ssl-images-amazon.com/images/I/51r-E1952WL._SX397_BO1,204,203,200_.jpg',
                'is_sponsored': False
            },
            {
                'isbn': '9780078022128',
                'seller': 'hamza_multan',
                'condition': 'Like New',
                'price': Decimal('750.00'),
                'city': 'Multan',
                'pickup': 'BZU Gate 1 or Gulgasht Colony',
                'desc': 'International student edition. Used carefully for one semester exam.',
                'photo': 'https://images-na.ssl-images-amazon.com/images/I/51r-E1952WL._SX397_BO1,204,203,200_.jpg',
                'is_sponsored': True
            },

            # Operating System Concepts (ISBN: 9781118063330 - Retail: Rs. 1950)
            {
                'isbn': '9781118063330',
                'seller': 'fatima_z',
                'condition': 'Good',
                'price': Decimal('550.00'),
                'city': 'Islamabad',
                'pickup': 'Central Library or University Main Gate',
                'desc': '9th edition Dinosaur book. Essential for OS midterm and final exams across Pakistani universities.',
                'photo': 'https://images-na.ssl-images-amazon.com/images/I/51uU8vY5cFL._SX397_BO1,204,203,200_.jpg',
                'is_sponsored': False
            },
            {
                'isbn': '9781118063330',
                'seller': 'usman_lhr',
                'condition': 'Brand New',
                'price': Decimal('1100.00'),
                'city': 'Lahore',
                'pickup': 'Urdu Bazaar Bookshop',
                'desc': 'Surplus stock from academic bookstore, pristine condition, unused.',
                'photo': 'https://images-na.ssl-images-amazon.com/images/I/51uU8vY5cFL._SX397_BO1,204,203,200_.jpg',
                'is_sponsored': True
            },

            # Introduction to Algorithms CLRS (ISBN: 9780262033848 - Retail: Rs. 2800)
            {
                'isbn': '9780262033848',
                'seller': 'ayesha_khi',
                'condition': 'Good',
                'price': Decimal('950.00'),
                'city': 'Karachi',
                'pickup': 'Gulshan-e-Iqbal Block 5',
                'desc': 'The bible of Algorithms. All pages present, excellent condition.',
                'photo': 'https://images-na.ssl-images-amazon.com/images/I/41SNoh5ZhOL._SX379_BO1,204,203,200_.jpg',
                'is_sponsored': False
            },

            # Peer-e-Kamil (ISBN: 9789694370002 - Retail: Rs. 950)
            {
                'isbn': '9789694370002',
                'seller': 'ali_seller',
                'condition': 'Like New',
                'price': Decimal('350.00'),
                'city': 'Lahore',
                'pickup': 'Model Town / Main Market',
                'desc': 'Original Ilm-o-Irfan edition. Read once and kept on shelf. Beautiful condition.',
                'photo': 'https://images-na.ssl-images-amazon.com/images/I/51wXpYlX0GL._SX331_BO1,204,203,200_.jpg',
                'is_sponsored': False
            },

            # Computer Science Class 12 PTB (ISBN: 9789695840123 - Retail: Rs. 350)
            {
                'isbn': '9789695840123',
                'seller': 'fatima_z',
                'condition': 'Good',
                'price': Decimal('120.00'),
                'city': 'Lahore',
                'pickup': 'Urdu Bazaar / Anarkali',
                'desc': 'Punjab board syllabus textbook. Solved past paper notes included in pencil.',
                'photo': 'https://images-na.ssl-images-amazon.com/images/I/41DqDq5HjHL._SX331_BO1,204,203,200_.jpg',
                'is_sponsored': False
            }
        ]

        created_listings = []
        for l in listings_data:
            book_obj = books.get(l['isbn'])
            seller_prof = profiles.get(l['seller'])
            if book_obj and seller_prof:
                listing, _ = Listing.objects.get_or_create(
                    book=book_obj,
                    seller=seller_prof,
                    price=l['price'],
                    defaults={
                        'condition': l['condition'],
                        'city': l['city'],
                        'pickup_location': l['pickup'],
                        'description': l['desc'],
                        'photo_url': l['photo'],
                        'status': 'active',
                        'is_sponsored': l['is_sponsored'],
                        'views_count': 35
                    }
                )
                created_listings.append(listing)

        # Ensure realistic Pakistani demo textbooks (Lahore, Islamabad, Bahawalpur, Karachi)
        ensure_demo_listings(force=True)
        self.stdout.write(f"-> Created {len(created_listings)} listings across various cities.")

        # 6. Seed Sample Contact Unlocks to showcase:
        # - 1 Pending Deal (Contact unlocked, waiting for deal or refund)
        # - 1 Confirmed Deal (Fee kept by BookBazaar, review left)
        # - 1 Refunded Deal (No deal made, fee refunded to buyer)
        buyer_demo = profiles['buyer_test']
        first_listing = created_listings[0]
        second_listing = created_listings[1]
        third_listing = created_listings[3]

        # Case A: Pending Contact Unlock
        unlock_pending, _ = ContactUnlock.objects.get_or_create(
            transaction_id='TXN-JC-9823412',
            defaults={
                'listing': first_listing,
                'buyer': buyer_demo,
                'seller': first_listing.seller,
                'fee_amount': Decimal('50.00'),
                'payment_method': 'jazzcash',
                'deal_status': 'unlocked_pending',
                'buyer_confirmation': 'pending',
                'seller_confirmation': 'pending'
            }
        )

        # Case B: Confirmed Deal
        unlock_confirmed, _ = ContactUnlock.objects.get_or_create(
            transaction_id='TXN-EP-4412093',
            defaults={
                'listing': second_listing,
                'buyer': buyer_demo,
                'seller': second_listing.seller,
                'fee_amount': Decimal('50.00'),
                'payment_method': 'easypaisa',
                'deal_status': 'deal_made',
                'buyer_confirmation': 'confirmed',
                'seller_confirmation': 'confirmed',
                'resolved_at': timezone.now()
            }
        )
        # Add a review for the confirmed deal
        SellerReview.objects.get_or_create(
            unlock=unlock_confirmed,
            seller=second_listing.seller,
            buyer=buyer_demo,
            defaults={
                'rating': 5,
                'comment': 'Met at Abbasia Campus. The book was exactly as described and seller was very polite!'
            }
        )

        # Case C: Cancelled / Refunded Deal
        ContactUnlock.objects.get_or_create(
            transaction_id='TXN-SP-1198302',
            defaults={
                'listing': third_listing,
                'buyer': buyer_demo,
                'seller': third_listing.seller,
                'fee_amount': Decimal('50.00'),
                'payment_method': 'card_safepay',
                'deal_status': 'no_deal_refunded',
                'buyer_confirmation': 'rejected',
                'seller_confirmation': 'rejected',
                'cancellation_reason': 'Seller had already committed the book to a classmate before our call. Refund processed immediately.',
                'refund_transaction_id': 'REF-EP-887123',
                'refund_timestamp': timezone.now(),
                'resolved_at': timezone.now()
            }
        )

        self.stdout.write("-> Seeded sample contact unlock scenarios (Pending, Deal Made, and Refunded).")

        # 7. Seed Advertisements (Banner, Interstitial, Native)
        ads_data = [
            {
                'title': 'Student Stationery & Binding Sale',
                'sponsor': 'National Campus Supplies Hub',
                'ad_type': 'banner_top',
                'headline': 'Special 20% Discount on Thesis Binding & Project Printing for University Students',
                'image': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=900&auto=format&fit=crop&q=80',
                'target': '#',
                'impressions': 1420,
                'clicks': 89
            },
            {
                'title': 'JazzCash Student Card Offer',
                'sponsor': 'JazzCash Pakistan',
                'ad_type': 'banner_bottom',
                'headline': 'Pay BookBazaar unlock fees with JazzCash & get 20% cashback in your mobile wallet!',
                'image': 'https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=900&auto=format&fit=crop&q=80',
                'target': '#',
                'impressions': 3100,
                'clicks': 214
            },
            {
                'title': 'Ilmi Kitab Khana Midterm Guidebooks',
                'sponsor': 'Ilmi Publishers Lahore',
                'ad_type': 'native_feed',
                'headline': 'Looking for solved past papers? Download official solved supplements.',
                'image': 'https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=600&auto=format&fit=crop&q=80',
                'target': '#',
                'impressions': 890,
                'clicks': 45
            },
            {
                'title': 'Congratulations on Listing Your Book!',
                'sponsor': 'KIPS & STEP Entry Test Preparation',
                'ad_type': 'interstitial',
                'headline': 'Preparing for Graduate Assessment Test (GAT) or CSS? Enroll with 15% student voucher.',
                'image': 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&auto=format&fit=crop&q=80',
                'target': '#',
                'impressions': 320,
                'clicks': 28
            }
        ]

        for ad in ads_data:
            Advertisement.objects.get_or_create(
                title=ad['title'],
                defaults={
                    'sponsor_name': ad['sponsor'],
                    'ad_type': ad['ad_type'],
                    'headline': ad['headline'],
                    'image_url': ad['image'],
                    'target_url': ad['target'],
                    'impressions': ad['impressions'],
                    'clicks': ad['clicks'],
                    'is_active': True
                }
            )

        self.stdout.write("-> Seeded advertisements (Banner, Interstitial, Native).")
        self.stdout.write(self.style.SUCCESS("All Bookzy AI demo data seeded successfully!"))
