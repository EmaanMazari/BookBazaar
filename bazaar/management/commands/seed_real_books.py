from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from bazaar.models import UserProfile, Book, Listing
from decimal import Decimal
from django.utils import timezone


class Command(BaseCommand):
    help = 'Seeds 15+ authentic Pakistani student textbooks, novels, medical books and free study guides'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting authentic Pakistani books database seeding...")

        # 1. Ensure verified student sellers exist in major Pakistani cities
        sellers_data = [
            {'username': 'seller_ali_lhr', 'name': 'Ali Khan (GCU Student)', 'phone': '03017654321', 'city': 'Lahore', 'campus': 'GCU Lahore / Anarkali Book Market'},
            {'username': 'seller_fatima_isb', 'name': 'Fatima Zahra (NUST SE)', 'phone': '03129876543', 'city': 'Islamabad', 'campus': 'NUST H-12 Campus / F-10 Markaz'},
            {'username': 'seller_hamza_mux', 'name': 'Hamza Tariq (Nishtar Med)', 'phone': '03335551234', 'city': 'Multan', 'campus': 'Nishtar Medical University Gate 1'},
            {'username': 'seller_usman_lhr', 'name': 'Usman Gujjar (PU New Campus)', 'phone': '03451122334', 'city': 'Lahore', 'campus': 'Punjab University Canal Road Gate'},
            {'username': 'seller_ayesha_khi', 'name': 'Ayesha Siddiqui (Dow Med)', 'phone': '03214455667', 'city': 'Karachi', 'campus': 'Dow University / Urdu Bazaar Karachi'},
            {'username': 'seller_bilal_isb', 'name': 'Muhammad Bilal (COMSATS)', 'phone': '03023344556', 'city': 'Islamabad', 'campus': 'COMSATS University Park Road'}
        ]

        sellers = {}
        for s in sellers_data:
            profile = UserProfile.objects.filter(phone_number=s['phone']).first()
            if not profile:
                user, _ = User.objects.get_or_create(username=s['username'], defaults={'email': f"{s['username']}@bookzyai.pk"})
                profile, _ = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'full_name': s['name'],
                        'phone_number': s['phone'],
                        'city': s['city'],
                        'campus_or_area': s['campus'],
                        'user_type': 'seller',
                        'rating': Decimal('4.9'),
                        'total_reviews': 12
                    }
                )
            sellers[s['username']] = profile

        # 2. Authentic Pakistani Books Catalog & Listings
        books_to_seed = [
            # -----------------------------------------------------------------
            # Class 9th & 10th (Punjab & Federal Board)
            # -----------------------------------------------------------------
            {
                'isbn': '978-969-100901-1',
                'title': '9th Class Physics (Punjab Textbook Board)',
                'author': 'Prof. Dr. Tariq Mahmood & Dr. Muhammad Naeem',
                'publisher': 'Punjab Curriculum & Textbook Board (PCTB), Lahore',
                'category': 'Textbooks',
                'subject': 'Physics',
                'education_board': 'Punjab Board',
                'grade_class': 'Matric (9th - 10th)',
                'price': Decimal('180.00'),
                'is_free': False,
                'condition': 'Good',
                'seller': sellers['seller_ali_lhr'],
                'city': 'Lahore',
                'pickup': 'Anarkali Urdu Bazaar / GCU Gate 2',
                'desc': 'Authentic PTB 9th Physics book. Clean pages with minimal pencil underlines. Covers complete SI units, Kinematics, Dynamics and Gravitation units.',
                'image': 'https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=400'
            },
            {
                'isbn': '978-969-100902-8',
                'title': '9th Class Mathematics Science Group',
                'author': 'Prof. M. Habib & Prof. Dr. Karamat H. Dar',
                'publisher': 'Punjab Curriculum & Textbook Board (PCTB)',
                'category': 'Textbooks',
                'subject': 'Mathematics',
                'education_board': 'Punjab Board',
                'grade_class': 'Matric (9th - 10th)',
                'price': Decimal('200.00'),
                'is_free': False,
                'condition': 'Like New',
                'seller': sellers['seller_hamza_mux'],
                'city': 'Multan',
                'pickup': 'Bosan Road / Gol Bagh Multan',
                'desc': 'Complete solved exercises for Matrices, Real numbers, Logarithms, and Algebraic formulas. Binding is intact, no missing pages.',
                'image': 'https://images.unsplash.com/photo-1509228468518-180dd4864904?w=400'
            },
            {
                'isbn': '978-969-101001-7',
                'title': '10th Class Chemistry PTB',
                'author': 'Dr. Jalil Ahmad & Dr. Jamil Ahmad',
                'publisher': 'Punjab Curriculum & Textbook Board (PCTB)',
                'category': 'Textbooks',
                'subject': 'Chemistry',
                'education_board': 'Punjab Board',
                'grade_class': 'Matric (9th - 10th)',
                'price': Decimal('190.00'),
                'is_free': False,
                'condition': 'Good',
                'seller': sellers['seller_usman_lhr'],
                'city': 'Lahore',
                'pickup': 'PU New Campus / Wahdat Road',
                'desc': 'Chemistry 10th Grade English Medium. Covers Chemical Equilibrium, Acids/Bases, Organic Chemistry, and Environmental Chemistry. Includes practical handbook notes.',
                'image': 'https://images.unsplash.com/photo-1603126857599-f6e157fa2fe6?w=400'
            },
            {
                'isbn': '978-969-101002-4',
                'title': '10th Class English & Grammar Guide',
                'author': 'Prof. Khadim Hussain & M. Zahid',
                'publisher': 'Ilmi / Taleem Educational Publishers',
                'category': 'Textbooks',
                'subject': 'English',
                'education_board': 'Federal Board',
                'grade_class': 'Matric (9th - 10th)',
                'price': Decimal('220.00'),
                'is_free': False,
                'condition': 'Good',
                'seller': sellers['seller_fatima_isb'],
                'city': 'Islamabad',
                'pickup': 'F-10 Markaz / NUST Gate 2',
                'desc': 'Federal Board (FBISE) English textbook with complete grammar composition, active/passive voice, direct/indirect narration, and formal essay outlines.',
                'image': 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=400'
            },

            # -----------------------------------------------------------------
            # FSc Part 1 & Part 2 (Pre-Medical & Pre-Engineering)
            # -----------------------------------------------------------------
            {
                'isbn': '978-969-110001-5',
                'title': 'FSc Part-1 Biology (PTB)',
                'author': 'Dr. S.A. Malik & Dr. N.A. Khan',
                'publisher': 'Punjab Curriculum & Textbook Board (PCTB)',
                'category': 'Textbooks',
                'subject': 'Biology',
                'education_board': 'Punjab Board',
                'grade_class': 'Intermediate (FSc / ICS)',
                'price': Decimal('280.00'),
                'is_free': False,
                'condition': 'Good',
                'seller': sellers['seller_ayesha_khi'],
                'city': 'Karachi',
                'pickup': 'Gulshan-e-Iqbal / Karachi University Gate',
                'desc': 'Official PTB FSc Pre-Medical 11th Biology book. Thorough coverage of Cell Biology, Biological Molecules, Enzymes, Kingdom Animalia and Bioenergetics.',
                'image': 'https://images.unsplash.com/photo-1530210124550-912dc1381cb8?w=400'
            },
            {
                'isbn': '978-969-110002-2',
                'title': 'FSc Part-2 Physics (PTB)',
                'author': 'Prof. Dr. M. Zakria Butt & Prof. M. Ali',
                'publisher': 'Punjab Curriculum & Textbook Board (PCTB)',
                'category': 'Textbooks',
                'subject': 'Physics',
                'education_board': 'Punjab Board',
                'grade_class': 'Intermediate (FSc / ICS)',
                'price': Decimal('320.00'),
                'is_free': False,
                'condition': 'Like New',
                'seller': sellers['seller_ali_lhr'],
                'city': 'Lahore',
                'pickup': 'Mall Road / Anarkali',
                'desc': 'FSc 12th Class Physics. Covers Electrostatics, Electromagnetism, Electronics, Dawn of Modern Physics, and Nuclear Physics. Formula list pinned at back.',
                'image': 'https://images.unsplash.com/photo-1636466497217-26a8cbeaf0aa?w=400'
            },
            {
                'isbn': '978-969-220003-9',
                'title': 'KIPS MDCAT & ECAT Practice Past Papers',
                'author': 'KIPS Entry Test Specialist Faculty',
                'publisher': 'KIPS Publications Lahore',
                'category': 'Entry Test Preparation',
                'subject': 'MDCAT / ECAT',
                'education_board': 'Higher Education / University',
                'grade_class': 'Entry Test / MDCAT',
                'price': Decimal('550.00'),
                'is_free': False,
                'condition': 'Like New',
                'seller': sellers['seller_bilal_isb'],
                'city': 'Islamabad',
                'pickup': 'Park Road / COMSATS University Gate 1',
                'desc': 'Complete solved past 10 years MDCAT and ECAT papers with step-by-step conceptual explanations and speed shortcuts for Physics and Chemistry.',
                'image': 'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=400'
            },

            # -----------------------------------------------------------------
            # MBBS & Medical Textbooks
            # -----------------------------------------------------------------
            {
                'isbn': '978-938-591583-3',
                'title': "BD Chaurasia's Human Anatomy (Vol 1 & 2)",
                'author': 'Dr. B.D. Chaurasia / Edited by Dr. Krishna Garg',
                'publisher': 'CBS Publishers & Distributors',
                'category': 'Medical',
                'subject': 'Human Anatomy',
                'education_board': 'Higher Education / University',
                'grade_class': 'Bachelor / BS / Undergrad',
                'price': Decimal('1150.00'),
                'is_free': False,
                'condition': 'Good',
                'seller': sellers['seller_fatima_isb'],
                'city': 'Islamabad',
                'pickup': 'Holy Family Hospital / RMU Rawalpindi',
                'desc': 'Upper Limb, Thorax, Lower Limb, and Abdomen regional anatomy. Clean color plates with key clinical dissection insights for MBBS 1st and 2nd year students.',
                'image': 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=400'
            },
            {
                'isbn': '978-032-359712-8',
                'title': 'Guyton and Hall Textbook of Medical Physiology',
                'author': 'John E. Hall & Michael E. Hall',
                'publisher': 'Elsevier Health Sciences / Saunders',
                'category': 'Medical',
                'subject': 'Medical Physiology',
                'education_board': 'Higher Education / University',
                'grade_class': 'Bachelor / BS / Undergrad',
                'price': Decimal('1450.00'),
                'is_free': False,
                'condition': 'Like New',
                'seller': sellers['seller_ayesha_khi'],
                'city': 'Karachi',
                'pickup': 'Dow Medical College / Civil Hospital Gate',
                'desc': 'The international gold standard in medical physiology. Cardiovascular hemodynamics, Renal buffer systems, and Neurophysiology in pristine condition.',
                'image': 'https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?w=400'
            },
            {
                'isbn': '978-813-125374-8',
                'title': 'Robbins Basic Pathology (10th South Asia Edition)',
                'author': 'Vinay Kumar, Abul K. Abbas & Jon C. Aster',
                'publisher': 'Elsevier South Asia',
                'category': 'Medical',
                'subject': 'Pathology',
                'education_board': 'Higher Education / University',
                'grade_class': 'Bachelor / BS / Undergrad',
                'price': Decimal('1600.00'),
                'is_free': False,
                'condition': 'Good',
                'seller': sellers['seller_hamza_mux'],
                'city': 'Multan',
                'pickup': 'Nishtar Medical University Central Gate',
                'desc': 'Essential textbook for 3rd Year MBBS Pathology. Cell injury, Acute and Chronic Inflammation, Hemodynamic disorders, and Neoplasia. Hardcover binding intact.',
                'image': 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=400'
            },

            # -----------------------------------------------------------------
            # Novels & Literature
            # -----------------------------------------------------------------
            {
                'isbn': '978-969-583001-3',
                'title': 'Peer-e-Kamil (S.A.W) — Umera Ahmed',
                'author': 'Umera Ahmed',
                'publisher': 'Alif Kitab Publications / Ferozsons',
                'category': 'Literature & Fiction',
                'subject': 'Urdu Literature / Novel',
                'education_board': 'General / None',
                'grade_class': 'Matric (9th - 10th)',
                'price': Decimal('450.00'),
                'is_free': False,
                'condition': 'Like New',
                'seller': sellers['seller_usman_lhr'],
                'city': 'Lahore',
                'pickup': 'Model Town Link Road / PU Gate',
                'desc': 'Masterpiece spiritual journey of Imama Hashim and Salar Sikandar. High-quality original paper edition, uncreased spine, pristine readable condition.',
                'image': 'https://images.unsplash.com/photo-1474932430478-367dbb6832c1?w=400'
            },
            {
                'isbn': '978-969-583002-0',
                'title': 'Jannat Ke Pattay — Nemrah Ahmed',
                'author': 'Nemrah Ahmed',
                'publisher': 'Ilm-o-Irfan Publishers Lahore',
                'category': 'Literature & Fiction',
                'subject': 'Urdu Literature / Novel',
                'education_board': 'General / None',
                'grade_class': 'Matric (9th - 10th)',
                'price': Decimal('480.00'),
                'is_free': False,
                'condition': 'Good',
                'seller': sellers['seller_fatima_isb'],
                'city': 'Islamabad',
                'pickup': 'F-7 Jinnah Super / NUST H-12',
                'desc': 'Enthralling mystery and suspense novel chronicling Haya Suleman’s life journey in Turkey. Clean hardcover copy, perfect for literature enthusiasts.',
                'image': 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400'
            },
            {
                'isbn': '978-969-350001-7',
                'title': 'Raja Gidh — Bano Qudsia',
                'author': 'Bano Qudsia',
                'publisher': 'Sang-e-Meel Publications Lahore',
                'category': 'Literature & Fiction',
                'subject': 'Urdu Literature / Classic Novel',
                'education_board': 'General / None',
                'grade_class': 'Bachelor / BS / Undergrad',
                'price': Decimal('380.00'),
                'is_free': False,
                'condition': 'Good',
                'seller': sellers['seller_ali_lhr'],
                'city': 'Lahore',
                'pickup': 'Anarkali / Mall Road Lahore',
                'desc': 'Celebrated psychological and philosophical Urdu classic exploring human obsession, morality, and socio-cultural conflict. Well preserved edition.',
                'image': 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400'
            },
            {
                'isbn': '978-006-231500-7',
                'title': 'The Alchemist — Paulo Coelho',
                'author': 'Paulo Coelho',
                'publisher': 'HarperOne / HarperCollins',
                'category': 'Literature & Fiction',
                'subject': 'English Literature / Fiction',
                'education_board': 'General / None',
                'grade_class': 'Intermediate (FSc / ICS)',
                'price': Decimal('300.00'),
                'is_free': False,
                'condition': 'Like New',
                'seller': sellers['seller_bilal_isb'],
                'city': 'Islamabad',
                'pickup': 'Saeed Book Bank F-7 / Blue Area',
                'desc': 'The globally beloved tale of Santiago the shepherd boy journeying to the Egyptian pyramids in pursuit of his Personal Legend. English paperback edition.',
                'image': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400'
            },

            # -----------------------------------------------------------------
            # Free Donated Books (Rs. 0 with Real Downloadable Multi-Page PDFs)
            # -----------------------------------------------------------------
            {
                'isbn': '978-969-900001-1',
                'title': '9th Physics Complete Formula & Numericals Handbook — Free PDF',
                'author': 'Prof. Tariq Mahmood (Punjab Textbook Board)',
                'publisher': 'Bookzy AI Student Welfare Foundation',
                'category': 'Textbooks',
                'subject': 'Physics',
                'education_board': 'Punjab Board',
                'grade_class': 'Matric (9th - 10th)',
                'price': Decimal('0.00'),
                'is_free': True,
                'condition': 'Like New',
                'seller': sellers['seller_ali_lhr'],
                'city': 'Lahore',
                'pickup': 'Digital Soft Copy (Direct Instant Download)',
                'desc': 'Complete formulas, solved numericals, step-by-step derivations, and unit conversions for 9th Class Physics students. Free digital study resource.',
                'image': 'https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=400'
            },
            {
                'isbn': '978-969-900002-8',
                'title': '10th English Essays & Letters Board Notes — Free PDF',
                'author': 'Prof. Khadim Hussain (Federal & Punjab Board)',
                'publisher': 'Bookzy AI Student Welfare Foundation',
                'category': 'Textbooks',
                'subject': 'English',
                'education_board': 'Federal Board',
                'grade_class': 'Matric (9th - 10th)',
                'price': Decimal('0.00'),
                'is_free': True,
                'condition': 'Like New',
                'seller': sellers['seller_fatima_isb'],
                'city': 'Islamabad',
                'pickup': 'Digital Soft Copy (Direct Instant Download)',
                'desc': 'Standard high-scoring essays, formal letters, idioms, and paragraph translations for 10th Class FBISE & Punjab Board matric exams. Free download.',
                'image': 'https://images.unsplash.com/photo-1455390582262-044cdead277a?w=400'
            },
            {
                'isbn': '978-969-900003-5',
                'title': 'FSc Pre-Medical Important Diagrams & MCQs Handbook — Free PDF',
                'author': 'Dr. S.A. Malik & Dr. N.A. Khan',
                'publisher': 'Bookzy AI Student Welfare Foundation',
                'category': 'Textbooks',
                'subject': 'Biology',
                'education_board': 'Punjab Board',
                'grade_class': 'Intermediate (FSc / ICS)',
                'price': Decimal('0.00'),
                'is_free': True,
                'condition': 'Like New',
                'seller': sellers['seller_ayesha_khi'],
                'city': 'Karachi',
                'pickup': 'Digital Soft Copy (Direct Instant Download)',
                'desc': 'High-yield illustrated biological diagrams, anatomical charts, and topic-wise solved practice MCQs for FSc Pre-Medical and MDCAT preparation.',
                'image': 'https://images.unsplash.com/photo-1507668077129-56e32842fceb?w=400'
            },
            {
                'isbn': '978-969-900004-2',
                'title': 'MBBS 1st Year High-Yield Anatomy Summary — Free PDF',
                'author': 'Dr. Krishna Garg & Dr. B.D. Chaurasia Study Circle',
                'publisher': 'Bookzy AI Medical Student Wing',
                'category': 'Medical',
                'subject': 'Human Anatomy',
                'education_board': 'Higher Education / University',
                'grade_class': 'Bachelor / BS / Undergrad',
                'price': Decimal('0.00'),
                'is_free': True,
                'condition': 'Like New',
                'seller': sellers['seller_hamza_mux'],
                'city': 'Multan',
                'pickup': 'Digital Soft Copy (Direct Instant Download)',
                'desc': 'Comprehensive regional anatomy summaries, osteology tables, muscle attachments, and spotting guide for medical students across Pakistan.',
                'image': 'https://images.unsplash.com/photo-1532938911079-1b06ac7ceec7?w=400'
            },
            {
                'isbn': '978-969-900005-9',
                'title': 'Taleem-o-Tarbiyat Selected Moral Stories — Free PDF',
                'author': 'Ferozsons Editorial Board',
                'publisher': 'Ferozsons / Bookzy Community Library',
                'category': 'Kids & Story Books',
                'subject': 'Moral Stories & Values',
                'education_board': 'General / None',
                'grade_class': 'Matric (9th - 10th)',
                'price': Decimal('0.00'),
                'is_free': True,
                'condition': 'Like New',
                'seller': sellers['seller_usman_lhr'],
                'city': 'Lahore',
                'pickup': 'Digital Soft Copy (Direct Instant Download)',
                'desc': 'Inspiring moral stories, folklore tales, and educational virtues for young students. Free downloadable illustrated digital soft-copy.',
                'image': 'https://images.unsplash.com/photo-1516979187457-637abb4f9353?w=400'
            }
        ]

        created_count = 0
        updated_count = 0

        for b_data in books_to_seed:
            book, book_created = Book.objects.update_or_create(
                isbn=b_data['isbn'],
                defaults={
                    'title': b_data['title'],
                    'author': b_data['author'],
                    'publisher': b_data['publisher'],
                    'category': b_data['category'],
                    'subject': b_data['subject'],
                    'education_board': b_data['education_board'],
                    'grade_class': b_data['grade_class'],
                    'cover_image': b_data['image'],
                    'description': b_data['desc'],
                    'original_retail_price': b_data['price'] * Decimal('1.8') if b_data['price'] > 0 else Decimal('450.00'),
                    'target_age_group': 'all'
                }
            )

            # Update or create active listing
            listing, listing_created = Listing.objects.update_or_create(
                book=book,
                seller=b_data['seller'],
                defaults={
                    'price': b_data['price'],
                    'is_free': b_data['is_free'],
                    'condition': b_data['condition'],
                    'city': b_data['city'],
                    'pickup_location': b_data['pickup'],
                    'description': b_data['desc'],
                    'photo_url': b_data['image'],
                    'status': 'active'
                }
            )

            if listing_created or book_created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded {len(books_to_seed)} authentic Pakistani books! (Created: {created_count}, Updated: {updated_count})"
        ))
