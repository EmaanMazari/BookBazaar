import logging
from decimal import Decimal
from django.contrib.auth.models import User
from django.utils import timezone
from bazaar.models import UserProfile, Book, Listing, PlatformSetting
from bazaar.services.book_service import KNOWN_CATALOG

logger = logging.getLogger('bazaar')

# Target realistic Pakistani textbooks, storybooks, novels, history & free donations
DEMO_TEXTBOOKS = [
    # --- FREE DONATED BOOKS (Community Giveaways - Rs. 0) ---
    {
        'isbn': '9789695840208',
        'seller_username': 'ali_seller',
        'condition': 'Good',
        'price': Decimal('0.00'),
        'is_free': True,
        'target_age_group': 'kids',
        'city': 'Lahore',
        'pickup': 'Anarkali / Old Campus PU Gate',
        'desc': 'Community book donation for deserving students. Official English textbook for Class 5 by Punjab Textbook Board. Completely intact pages with clean exercises.',
        'photo': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 125
    },
    {
        'isbn': '9789695840215',
        'seller_username': 'zainab_rwp',
        'condition': 'Like New',
        'price': Decimal('0.00'),
        'is_free': True,
        'target_age_group': 'teens',
        'city': 'Rawalpindi',
        'pickup': 'Satellite Town / Gordon College Gate',
        'desc': 'Free giveaway for intermediate college students. Covers vectors, equilibrium, motion, work and energy, circular motion, fluid dynamics, and thermodynamics.',
        'photo': 'https://images.unsplash.com/photo-1632571401005-458e9d244591?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 210
    },
    {
        'isbn': '9789695840222',
        'seller_username': 'fatima_z',
        'condition': 'Like New',
        'price': Decimal('0.00'),
        'is_free': True,
        'target_age_group': 'kids',
        'city': 'Islamabad',
        'pickup': 'F-6 Super Market / National Library',
        'desc': 'Free book donation for young children. Illustrated Urdu moral stories with colorful characters promoting honesty, sharing, and kindness.',
        'photo': 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 185
    },
    {
        'isbn': '9789695840239',
        'seller_username': 'usman_mul',
        'condition': 'Good',
        'price': Decimal('0.00'),
        'is_free': True,
        'target_age_group': 'kids',
        'city': 'Multan',
        'pickup': 'Bahauddin Zakariya University (BZU) Gate 1',
        'desc': 'Free donation copy for primary school students. Includes plants, human body, ecosystems, matter and energy. Donated to help primary school students.',
        'photo': 'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 95
    },
    # --- PUNJAB TEXTBOOKS (Primary Class 1-5, Middle 6-8, Matric 9-10 & FSc 11-12) ---
    {
        'isbn': '9789695840246',
        'seller_username': 'ali_seller',
        'condition': 'Good',
        'price': Decimal('80.00'),
        'is_free': False,
        'target_age_group': 'kids',
        'city': 'Lahore',
        'pickup': 'Model Town / GCU Metro Stop',
        'desc': 'Official Punjab Board Urdu Qaida and Class 1 basic reading textbook with phonics, letters, and colorful illustrations for early learners.',
        'photo': 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 45
    },
    {
        'isbn': '9789695840253',
        'seller_username': 'ali_seller',
        'condition': 'Like New',
        'price': Decimal('110.00'),
        'is_free': False,
        'target_age_group': 'kids',
        'city': 'Faisalabad',
        'pickup': 'University of Agriculture Faisalabad (UAF) Gate 2',
        'desc': 'Official single national curriculum math textbook for grade 3. Addition, subtraction, multiplication tables, fractions, and introductory geometry.',
        'photo': 'https://images.unsplash.com/photo-1596495578065-6e0763fa1178?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 60
    },
    {
        'isbn': '9789695840260',
        'seller_username': 'ali_seller',
        'condition': 'Good',
        'price': Decimal('130.00'),
        'is_free': False,
        'target_age_group': 'kids',
        'city': 'Lahore',
        'pickup': 'PU New Campus / Wahdat Road',
        'desc': 'Complete Grade 5 Urdu curriculum with poems, national stories, moral essays, grammar, and comprehension exercises.',
        'photo': 'https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 52
    },
    {
        'isbn': '9789695840277',
        'seller_username': 'usman_mul',
        'condition': 'Good',
        'price': Decimal('140.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Multan',
        'pickup': 'Chowk Kachehri / BZU Multan',
        'desc': 'Cellular organization, human sense organs, photosynthesis, elements and compounds, mixtures, and energy transformations for 6th standard.',
        'photo': 'https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 38
    },
    {
        'isbn': '9789695840284',
        'seller_username': 'bilal_bwp',
        'condition': 'Good',
        'price': Decimal('160.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Bahawalpur',
        'pickup': 'IUB Baghdad Campus / Model Town B',
        'desc': 'Official 8th Class Punjab Board textbook. Human organ systems, heredity, biotechnology basics, chemical reactions, acids & bases, and space exploration.',
        'photo': 'https://images.unsplash.com/photo-1507668077129-56e32842fceb?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 47
    },
    {
        'isbn': '9789695840291',
        'seller_username': 'ali_seller',
        'condition': 'Like New',
        'price': Decimal('190.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Lahore',
        'pickup': 'Anarkali / Board Bazaar Lahore',
        'desc': 'Official Biology 9th Grade textbook for Matric students. Cell biology, tissues, bioenergetics, enzymes, human nutrition, and circulatory transport systems.',
        'photo': 'https://images.unsplash.com/photo-1530210124550-912dc1381cb8?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': True,
        'views': 78
    },
    {
        'isbn': '9789695840307',
        'seller_username': 'fatima_z',
        'condition': 'Good',
        'price': Decimal('200.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Islamabad',
        'pickup': 'G-9 Markaz / NUST Gate 2',
        'desc': 'Official Chemistry 10th Grade Punjab Board textbook. Chemical equilibrium, acids, bases and salts, organic chemistry, biochemistry, and atmospheric chemistry.',
        'photo': 'https://images.unsplash.com/photo-1603126857599-f6e157fa2fe6?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 82
    },
    {
        'isbn': '9789695840314',
        'seller_username': 'zainab_rwp',
        'condition': 'Good',
        'price': Decimal('220.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Rawalpindi',
        'pickup': 'Murree Road / Saddar Rawalpindi',
        'desc': 'Quadratic equations, theory of quadratic equations, variations, partial fractions, sets and functions, basic statistics, trigonometry, and circle geometry theorems.',
        'photo': 'https://images.unsplash.com/photo-1509228468518-180dd4864904?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 64
    },
    {
        'isbn': '9789695840321',
        'seller_username': 'ali_seller',
        'condition': 'Good',
        'price': Decimal('240.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Lahore',
        'pickup': 'Anarkali / GCU Lahore Main Gate',
        'desc': 'Official Punjab Board textbook for Intermediate Part-1. Measurements, vectors and equilibrium, motion and force, work and energy, circular motion, and physical optics.',
        'photo': 'https://images.unsplash.com/photo-1632571401005-458e9d244591?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': True,
        'views': 110
    },
    {
        'isbn': '9789695840338',
        'seller_username': 'ali_seller',
        'condition': 'Like New',
        'price': Decimal('240.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Lahore',
        'pickup': 'DHA Phase 5 / LUMS Gate',
        'desc': 'Official Punjab Board textbook for Intermediate Part-1. Number systems, matrices, quadratic equations, permutations and combinations, mathematical induction, and trigonometry identities.',
        'photo': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 90
    },
    {
        'isbn': '9789695840130',
        'seller_username': 'ali_seller',
        'condition': 'Good',
        'price': Decimal('180.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Lahore',
        'pickup': 'Board Bazaar / Anarkali / GCU Gate',
        'desc': 'Complete Punjab Board textbook with marked important numericals, short question highlights, and solved exercise notes in pencil. Clean pages.',
        'photo': 'https://images.unsplash.com/photo-1632571401005-458e9d244591?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': True,
        'views': 140
    },
    {
        'isbn': '9789695840345',
        'seller_username': 'ayesha_khi',
        'condition': 'Good',
        'price': Decimal('150.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Karachi',
        'pickup': 'NED University / Gulshan-e-Iqbal',
        'desc': 'Official English essays, biographical sketches, and complete Good-Bye Mr. Chips novel study for Intermediate Part-2. Key examination questions and vocabulary included.',
        'photo': 'https://images.unsplash.com/photo-1476275466078-4007374efbbe?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 72
    },
    # --- KIDS & STORY BOOKS ---
    {
        'isbn': '9780141325293',
        'seller_username': 'fatima_z',
        'condition': 'Like New',
        'price': Decimal('280.00'),
        'is_free': False,
        'target_age_group': 'kids',
        'city': 'Islamabad',
        'pickup': 'F-7 Markaz / Jinnah Super',
        'desc': 'Timeless illustrated adventure classic following Mowgli, Baloo, and Bagheera in the wilderness. High quality color prints and easy English vocabulary for children.',
        'photo': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 95
    },
    {
        'isbn': '9789695840352',
        'seller_username': 'ali_seller',
        'condition': 'Like New',
        'price': Decimal('190.00'),
        'is_free': False,
        'target_age_group': 'kids',
        'city': 'Lahore',
        'pickup': 'Model Town Library / Link Road',
        'desc': 'Delightful Urdu poems and moral story book for young kids by renowned poet Sufi Tabassum. Features Tot Batot tales, animals, humor, and moral lessons.',
        'photo': 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 88
    },
    {
        'isbn': '9789695840369',
        'seller_username': 'bilal_bwp',
        'condition': 'Good',
        'price': Decimal('220.00'),
        'is_free': False,
        'target_age_group': 'kids',
        'city': 'Bahawalpur',
        'pickup': 'Model Town A / University Road Bahawalpur',
        'desc': 'Selected classic Arabian Nights tales adapted in simple, entertaining Urdu for young readers. Includes Sindbad the Sailor, Aladdin, and Ali Baba.',
        'photo': 'https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 76
    },
    {
        'isbn': '9789695840376',
        'seller_username': 'ayesha_khi',
        'condition': 'Like New',
        'price': Decimal('250.00'),
        'is_free': False,
        'target_age_group': 'kids',
        'city': 'Karachi',
        'pickup': 'Clifton Block 2 / Boat Basin',
        'desc': 'Ancient animal fables teaching wisdom, leadership, friendship, and moral virtues. Engaging illustrations on every page suitable for age 5-12.',
        'photo': 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 65
    },
    # --- FICTION & NOVELS ---
    {
        'isbn': '9789694370002',
        'seller_username': 'ali_seller',
        'condition': 'Like New',
        'price': Decimal('400.00'),
        'is_free': False,
        'target_age_group': 'young_adult',
        'city': 'Lahore',
        'pickup': 'DHA Phase 5 / LUMS Gate or Model Town',
        'desc': 'Bestselling Urdu literary masterpiece. Original hardcover edition, kept inside glass bookshelf. Crisp uncreased pages and pristine binding.',
        'photo': 'https://images-na.ssl-images-amazon.com/images/I/51wXpYlX0GL._SX331_BO1,204,203,200_.jpg',
        'is_sponsored': False,
        'views': 310
    },
    {
        'isbn': '9789694370057',
        'seller_username': 'fatima_z',
        'condition': 'Like New',
        'price': Decimal('450.00'),
        'is_free': False,
        'target_age_group': 'young_adult',
        'city': 'Islamabad',
        'pickup': 'F-8 Markaz / Quaid-i-Azam University',
        'desc': 'Sensational Urdu novel following Haya Suleman\'s life journey to Turkey, espionage, resilience, faith, and personal transformation. Highly acclaimed across Pakistan.',
        'photo': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 280
    },
    {
        'isbn': '9780061122415',
        'seller_username': 'ayesha_khi',
        'condition': 'Good',
        'price': Decimal('350.00'),
        'is_free': False,
        'target_age_group': 'young_adult',
        'city': 'Karachi',
        'pickup': 'FAST-NUCES / Karachi University Gate',
        'desc': 'The magical story of Santiago, an Andalusian shepherd boy who yearns to travel in search of a worldly treasure. An inspiring tale about listening to our hearts.',
        'photo': 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 195
    },
    {
        'isbn': '9789693500202',
        'seller_username': 'ali_seller',
        'condition': 'Good',
        'price': Decimal('380.00'),
        'is_free': False,
        'target_age_group': 'general',
        'city': 'Lahore',
        'pickup': 'Mall Road / Anarkali Lahore',
        'desc': 'Renowned Urdu psychological and philosophical novel exploring moral and ethical choices in human life and society. Classic reading.',
        'photo': 'https://images-na.ssl-images-amazon.com/images/I/51D61o8P51L._SX331_BO1,204,203,200_.jpg',
        'is_sponsored': False,
        'views': 160
    },
    # --- HISTORY & LITERATURE ---
    {
        'isbn': '9789693501001',
        'seller_username': 'fatima_z',
        'condition': 'Good',
        'price': Decimal('450.00'),
        'is_free': False,
        'target_age_group': 'general',
        'city': 'Islamabad',
        'pickup': 'Quaid-i-Azam University / Blue Area',
        'desc': 'Authoritative academic history of the Indian subcontinent and Pakistan movement by University of Karachi former Vice-Chancellor. Standard university curriculum reference.',
        'photo': 'https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 140
    },
    {
        'isbn': '9789693501018',
        'seller_username': 'ali_seller',
        'condition': 'Like New',
        'price': Decimal('520.00'),
        'is_free': False,
        'target_age_group': 'general',
        'city': 'Lahore',
        'pickup': 'Punjab University Old Campus / Anarkali',
        'desc': 'In-depth historical documentation of constitutional developments, political movements, foreign policy, and leadership in Pakistan from 1947 to contemporary times.',
        'photo': 'https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 175
    },
    {
        'isbn': '9789693501025',
        'seller_username': 'zainab_rwp',
        'condition': 'Like New',
        'price': Decimal('480.00'),
        'is_free': False,
        'target_age_group': 'general',
        'city': 'Sialkot',
        'pickup': 'Iqbal Manzil / Paris Road Sialkot',
        'desc': 'Complete Urdu poetic works of the national poet Allama Muhammad Iqbal with authentic footnotes, philosophical commentary, and poetic glossary.',
        'photo': 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': True,
        'views': 230
    },
    {
        'isbn': '9789693501032',
        'seller_username': 'zainab_rwp',
        'condition': 'Good',
        'price': Decimal('600.00'),
        'is_free': False,
        'target_age_group': 'general',
        'city': 'Rawalpindi',
        'pickup': 'Saddar Rawalpindi / Peshawar Road',
        'desc': 'Iconic autobiography and civil service insider account of Pakistan\'s formative decades from 1947 through the 1960s. Extraordinary historical and personal narrative.',
        'photo': 'https://images.unsplash.com/photo-1476275466078-4007374efbbe?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 215
    },
    # --- HIGHER ED / COMPUTER SCIENCE ---
    {
        'isbn': '9789695840147',
        'seller_username': 'fatima_z',
        'condition': 'Good',
        'price': Decimal('380.00'),
        'is_free': False,
        'target_age_group': 'young_adult',
        'city': 'Islamabad',
        'pickup': 'NUST / QAU Campus Gate 1 or Blue Area',
        'desc': 'Standard calculus reference across all Pakistani universities. Differentiation, integration techniques, and analytical geometry. Complete and clean binding.',
        'photo': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 95
    },
    {
        'isbn': '9780133943030',
        'seller_username': 'bilal_bwp',
        'condition': 'Like New',
        'price': Decimal('850.00'),
        'is_free': False,
        'target_age_group': 'young_adult',
        'city': 'Bahawalpur',
        'pickup': 'Islamia University Bahawalpur (IUB) Baghdad Campus',
        'desc': '10th global edition by Sommerville in pristine condition. Covers agile development, software architecture, security, and verification. Used for BSSE 5th semester.',
        'photo': 'https://images.unsplash.com/photo-1532012164546-f432f2e3777f?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': True,
        'views': 120
    },
    {
        'isbn': '9781118063330',
        'seller_username': 'ayesha_khi',
        'condition': 'Good',
        'price': Decimal('650.00'),
        'is_free': False,
        'target_age_group': 'young_adult',
        'city': 'Karachi',
        'pickup': 'FAST-NUCES / Karachi University Campus Gate',
        'desc': 'Standard course book for Operating Systems. Processes, virtual memory, threads, synchronization, and storage. Very clean pages with sticky tags on key chapters.',
        'photo': 'https://images-na.ssl-images-amazon.com/images/I/51uU8vY5cFL._SX397_BO1,204,203,200_.jpg',
        'is_sponsored': False,
        'views': 110
    },
    {
        'isbn': '9789695840154',
        'seller_username': 'fatima_z',
        'condition': 'Good',
        'price': Decimal('550.00'),
        'is_free': False,
        'target_age_group': 'young_adult',
        'city': 'Islamabad',
        'pickup': 'F-8 Markaz / Quaid-i-Azam University',
        'desc': 'Essential preparation textbook for CSS compulsory paper. Covers environmental sciences, physical sciences, quantitative reasoning, and mental ability with past papers.',
        'photo': 'https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': True,
        'views': 150
    },
    {
        'isbn': '9780132350884',
        'seller_username': 'bilal_bwp',
        'condition': 'Good',
        'price': Decimal('700.00'),
        'is_free': False,
        'target_age_group': 'young_adult',
        'city': 'Bahawalpur',
        'pickup': 'Model Town A / University Road Bahawalpur',
        'desc': 'Must-have book for every junior software engineer and CS student. Clean naming, functions, classes, and unit testing practices. Very clean copy.',
        'photo': 'https://images-na.ssl-images-amazon.com/images/I/41xShlnTZTL._SX376_BO1,204,203,200_.jpg',
        'is_sponsored': False,
        'views': 180
    },
    {
        'isbn': '9780262033848',
        'seller_username': 'ayesha_khi',
        'condition': 'Like New',
        'price': Decimal('980.00'),
        'is_free': False,
        'target_age_group': 'young_adult',
        'city': 'Karachi',
        'pickup': 'NED University / Gulshan-e-Iqbal Block 5',
        'desc': 'The definitive reference for algorithms and data structures. Graph algorithms, dynamic programming, sorting, and complexity theory. Intact hardcover.',
        'photo': 'https://images-na.ssl-images-amazon.com/images/I/41SNoh5ZhOL._SX379_BO1,204,203,200_.jpg',
        'is_sponsored': False,
        'views': 220
    }
]

DEMO_USERS = [
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
        'username': 'bilal_bwp',
        'name': 'Bilal Siddiqui (IUB Student)',
        'phone': '03049988776',
        'city': 'Bahawalpur',
        'campus': 'Islamia University Bahawalpur (IUB) Baghdad Campus',
        'type': 'student',
        'rating': Decimal('4.9'),
        'reviews': 9,
        'wallet': Decimal('320.00')
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
        'username': 'zainab_rwp',
        'name': 'Zainab Bibi',
        'phone': '03335566778',
        'city': 'Rawalpindi',
        'campus': 'Satellite Town / Gordon College',
        'type': 'student',
        'rating': Decimal('4.9'),
        'reviews': 8,
        'wallet': Decimal('180.00')
    },
    {
        'username': 'usman_mul',
        'name': 'Usman Tariq',
        'phone': '03007788990',
        'city': 'Multan',
        'campus': 'Bahauddin Zakariya University (BZU)',
        'type': 'student',
        'rating': Decimal('4.7'),
        'reviews': 11,
        'wallet': Decimal('90.00')
    },
    {
        'username': 'buyer_test',
        'name': 'Demo Buyer',
        'phone': '03023344556',
        'city': 'Islamabad',
        'campus': 'Central Campus / Student Center',
        'type': 'student',
        'rating': Decimal('5.0'),
        'reviews': 2,
        'wallet': Decimal('300.00')
    }
]


import sys

def ensure_demo_listings(force=False):
    """
    Checks active listings in BookBazaar.
    Ensures complete catalog of Punjab Textbooks (Primary to FSc),
    Free Community Donations (Rs. 0), Kids & Story Books, Fiction & Novels,
    and History & Literature across Lahore, Islamabad, Karachi, Rawalpindi,
    Multan, Faisalabad, and Bahawalpur.
    """
    # Do not auto-seed during automated test suites unless explicitly forced
    if not force and ('test' in sys.argv or 'pytest' in sys.argv[0]):
        return 0

    try:
        active_count = Listing.objects.filter(status='active').count()
        if not force and active_count >= len(DEMO_TEXTBOOKS):
            return active_count

        logger.info(f"BookBazaar auto-seed triggered: active listings count ({active_count}) is below {len(DEMO_TEXTBOOKS)}.")

        # 1. Platform Settings
        setting, _ = PlatformSetting.objects.get_or_create(id=1)
        if not setting.platform_name or setting.platform_name == 'BookLoop Pakistan':
            setting.platform_name = 'BookBazaar AI'
            setting.contact_unlock_fee = Decimal('50.00')
            setting.auto_refund_days = 5
            setting.require_admin_approval = False
            setting.save()

        # 2. Ensure Admin User
        admin_user, created = User.objects.get_or_create(username='admin')
        if created or not admin_user.has_usable_password():
            admin_user.set_password('admin123')
            admin_user.is_superuser = True
            admin_user.is_staff = True
            admin_user.email = 'admin@bookbazaar.pk'
            admin_user.save()

        UserProfile.objects.get_or_create(
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

        # 3. Ensure Demo Users
        profiles = {}
        for udata in DEMO_USERS:
            u, _ = User.objects.get_or_create(username=udata['username'])
            if not u.has_usable_password():
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
            if prof.city != udata['city']:
                prof.city = udata['city']
                prof.save(update_fields=['city'])
            profiles[udata['username']] = prof

        # 4. Ensure Books from KNOWN_CATALOG
        books = {}
        for isbn, bdata in KNOWN_CATALOG.items():
            book, created = Book.objects.get_or_create(
                isbn=isbn,
                defaults={
                    'title': bdata['title'],
                    'author': bdata['author'],
                    'publisher': bdata['publisher'],
                    'edition': bdata['edition'],
                    'category': bdata['category'],
                    'education_board': bdata.get('education_board', 'General / None'),
                    'grade_class': bdata.get('grade_class', 'Bachelor / BS / Undergrad'),
                    'subject': bdata.get('subject', ''),
                    'target_age_group': bdata.get('target_age_group', 'all'),
                    'description': bdata['description'],
                    'cover_image': bdata['cover_image'],
                    'original_retail_price': Decimal(str(bdata['original_retail_price']))
                }
            )
            if not created:
                book.title = bdata['title']
                book.category = bdata['category']
                book.education_board = bdata.get('education_board', book.education_board)
                book.grade_class = bdata.get('grade_class', book.grade_class)
                book.target_age_group = bdata.get('target_age_group', 'all')
                book.subject = bdata.get('subject', book.subject)
                book.description = bdata.get('description', book.description)
                book.cover_image = bdata.get('cover_image', book.cover_image)
                book.save()
            books[isbn] = book

        # 5. Ensure All Realistic Pakistani Demo Listings
        for l in DEMO_TEXTBOOKS:
            book_obj = books.get(l['isbn'])
            seller_prof = profiles.get(l['seller_username'])
            is_free_val = l.get('is_free', l['price'] == Decimal('0.00'))
            age_grp_val = l.get('target_age_group', book_obj.target_age_group if book_obj else 'all')
            if book_obj and seller_prof:
                listing, created = Listing.objects.get_or_create(
                    book=book_obj,
                    seller=seller_prof,
                    defaults={
                        'price': l['price'],
                        'is_free': is_free_val,
                        'target_age_group': age_grp_val,
                        'condition': l['condition'],
                        'city': l['city'],
                        'pickup_location': l['pickup'],
                        'description': l['desc'],
                        'photo_url': l['photo'],
                        'status': 'active',
                        'is_sponsored': l['is_sponsored'],
                        'views_count': l.get('views', 42)
                    }
                )
                if not created:
                    needs_save = False
                    if listing.status != 'active':
                        listing.status = 'active'
                        needs_save = True
                    if listing.price != l['price']:
                        listing.price = l['price']
                        needs_save = True
                    if listing.is_free != is_free_val:
                        listing.is_free = is_free_val
                        needs_save = True
                    if listing.target_age_group != age_grp_val:
                        listing.target_age_group = age_grp_val
                        needs_save = True
                    if listing.city != l['city']:
                        listing.city = l['city']
                        needs_save = True
                    if needs_save:
                        listing.save(update_fields=['status', 'price', 'is_free', 'target_age_group', 'city'])

        final_count = Listing.objects.filter(status='active').count()
        logger.info(f"BookBazaar auto-seed completed successfully. Active listings: {final_count}")
        return final_count

    except Exception as e:
        logger.warning(f"Auto-seed check deferred (database may still be migrating): {e}")
        return 0
