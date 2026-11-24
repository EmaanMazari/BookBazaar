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
    },
    # --- BALOCHISTAN HISTORY & REGIONAL BOOKS ---
    {
        'isbn': '9789694073514',
        'seller_username': 'baloch_seller',
        'condition': 'Like New',
        'price': Decimal('580.00'),
        'is_free': False,
        'target_age_group': 'general',
        'city': 'Quetta',
        'pickup': 'University of Balochistan (UoB) Sariab Road / Jinnah Road',
        'desc': 'Original print of Sardar Khan Baluch’s masterwork on Balochistan history. Intact binding, clean pages, essential for CSS Pakistan Affairs and regional history researchers in Quetta.',
        'photo': 'https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': True,
        'views': 165
    },
    {
        'isbn': '9789694073521',
        'seller_username': 'baloch_seller',
        'condition': 'Good',
        'price': Decimal('450.00'),
        'is_free': False,
        'target_age_group': 'general',
        'city': 'Gwadar',
        'pickup': 'Gwadar Port Road / University of Gwadar Gate',
        'desc': 'Complete Urdu text of Tareekh-e-Balochistan by Mir Gul Khan Naseer. High quality archival binding, rare regional edition available for immediate handover near Gwadar Port.',
        'photo': 'https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 140
    },
    {
        'isbn': '9789694073538',
        'seller_username': 'baloch_seller',
        'condition': 'Like New',
        'price': Decimal('620.00'),
        'is_free': False,
        'target_age_group': 'general',
        'city': 'Khuzdar',
        'pickup': 'BUET Khuzdar Main Campus / RCD Highway',
        'desc': 'Illustrated study of Mehrgarh archaeological excavations in Balochistan with maps, pottery sketches, and chronology. Pristine condition, available at Balochistan UET Khuzdar campus.',
        'photo': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 125
    },
    {
        'isbn': '9789694073545',
        'seller_username': 'baloch_seller',
        'condition': 'Like New',
        'price': Decimal('120.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Quetta',
        'pickup': 'BISE Quetta Gate / Zarghoon Road',
        'desc': 'Official Balochistan Board Matric Class 10 Pakistan Studies & History textbook. Clean, unmarked, latest BTBB curriculum. Campus pickup near BISE Quetta office.',
        'photo': 'https://images.unsplash.com/photo-1532012164546-f432f2e3777f?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 190
    },

    # ========================================================
    # 📚 PUNJAB BOARD (PCTB)
    # ========================================================
    {
        'isbn': '9789695840307',
        'seller_username': 'ali_seller',
        'condition': 'Good',
        'price': Decimal('160.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Lahore',
        'pickup': 'PU New Campus / Wahdat Road Gate',
        'desc': 'Official Punjab Board Physics Class 11 (FSc Part 1). Vectors, circular motion, work & energy, oscillations, physical optics. Intact pages.',
        'photo': 'https://images.unsplash.com/photo-1632571401005-458e9d244591?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 82
    },
    {
        'isbn': '9789695840314',
        'seller_username': 'ali_seller',
        'condition': 'Like New',
        'price': Decimal('180.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Faisalabad',
        'pickup': 'University of Agriculture Faisalabad (UAF) Main Gate',
        'desc': 'Official Punjab Board Chemistry Class 12 (FSc Part 2). Periodic classification, transition elements, organic reactions and environmental chemistry.',
        'photo': 'https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 95
    },
    {
        'isbn': '9789695840321',
        'seller_username': 'zainab_rwp',
        'condition': 'Good',
        'price': Decimal('150.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Rawalpindi',
        'pickup': 'Gordon College / Liaquat Bagh Metro Stop',
        'desc': 'Punjab Board Mathematics Class 10 (Science Group). Solved exercise notes in pencil, quadratic equations, partial fractions, trigonometry.',
        'photo': 'https://images.unsplash.com/photo-1596495578065-6e0763fa1178?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 110
    },
    {
        'isbn': '9789695840338',
        'seller_username': 'bilal_bwp',
        'condition': 'Like New',
        'price': Decimal('130.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Bahawalpur',
        'pickup': 'Islamia University Bahawalpur (IUB) Baghdad Campus',
        'desc': 'Punjab Board English Class 12 (Modern Prose & Poems). Includes past paper essays, hero summaries, and Goodbye Mr Chips study guide.',
        'photo': 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 64
    },

    # ========================================================
    # 🏛️ FEDERAL BOARD (FBISE)
    # ========================================================
    {
        'isbn': '9789698760012',
        'seller_username': 'fatima_z',
        'condition': 'Like New',
        'price': Decimal('220.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Islamabad',
        'pickup': 'National Book Foundation / G-8 or University Road',
        'desc': 'Official FBISE Federal Board Physics Class 11 (HSSC-I). Published by National Book Foundation (NBF). Clean condition with zero pen marks.',
        'photo': 'https://images.unsplash.com/photo-1632571401005-458e9d244591?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': True,
        'views': 140
    },
    {
        'isbn': '9789698760029',
        'seller_username': 'buyer_test',
        'condition': 'Good',
        'price': Decimal('190.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Islamabad',
        'pickup': 'F-6 Super Market / Blue Area Metro Stop',
        'desc': 'FBISE Computer Science Class 10 (SSC-II). C programming fundamentals, loops, control structures, and logic development.',
        'photo': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 92
    },
    {
        'isbn': '9789698760036',
        'seller_username': 'zainab_rwp',
        'condition': 'Good',
        'price': Decimal('160.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Rawalpindi',
        'pickup': 'Satellite Town Commercial Market',
        'desc': 'Federal Board Pakistan Studies Class 12 (HSSC-II). Complete constitutional history, foreign policy, and economic survey for board exams.',
        'photo': 'https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 78
    },
    {
        'isbn': '9789698760043',
        'seller_username': 'fatima_z',
        'condition': 'Like New',
        'price': Decimal('170.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Islamabad',
        'pickup': 'NUST Gate 1 / H-12 Campus',
        'desc': 'Federal Board Urdu Lazmi Class 11 (Sarmaya-e-Urdu HSSC-I). Classical poetry, prose essays, grammar, and essay writing notes.',
        'photo': 'https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 85
    },
    {
        'isbn': '9789698760050',
        'seller_username': 'buyer_test',
        'condition': 'Good',
        'price': Decimal('140.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Islamabad',
        'pickup': 'G-9 Markaz / Karachi Company',
        'desc': 'Federal Board Islamiyat Lazmi Class 9 (SSC-I). Quranic verses translation, Hadith selections, Seerat-un-Nabi and ethical guidance.',
        'photo': 'https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 67
    },

    # ========================================================
    # 🌊 SINDH BOARD (BSEK / BIEK Karachi)
    # ========================================================
    {
        'isbn': '9789694400013',
        'seller_username': 'sindh_seller',
        'condition': 'Good',
        'price': Decimal('175.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Karachi',
        'pickup': 'DJ Sindh Govt Science College / Saddar',
        'desc': 'Sindh Textbook Board Physics Class 11 (Intermediate Part-1). Standard reference for BIEK Karachi intermediate pre-engineering students.',
        'photo': 'https://images.unsplash.com/photo-1632571401005-458e9d244591?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': True,
        'views': 115
    },
    {
        'isbn': '9789694400020',
        'seller_username': 'sindh_seller',
        'condition': 'Like New',
        'price': Decimal('150.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Karachi',
        'pickup': 'NED University / University Road Karachi',
        'desc': 'Sindh Board Chemistry Class 9 (Secondary Stage Science). Atomic structure, chemical reactions, states of matter, and periodic table.',
        'photo': 'https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 88
    },
    {
        'isbn': '9789694400037',
        'seller_username': 'ayesha_khi',
        'condition': 'Good',
        'price': Decimal('160.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Karachi',
        'pickup': 'Karachi University (KU) Silver Jubilee Gate',
        'desc': 'Sindh Board Biology Class 10 (Secondary Stage Science Group). Human organ systems, coordination, genetics, and biotechnology.',
        'photo': 'https://images.unsplash.com/photo-1530210124550-912dc1381cb8?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 76
    },
    {
        'isbn': '9789694400044',
        'seller_username': 'sindh_seller',
        'condition': 'Like New',
        'price': Decimal('190.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Hyderabad',
        'pickup': 'University of Sindh Old Campus / Saddar Hyderabad',
        'desc': 'Sindh Board Mathematics Class 12 (Higher Secondary Part-II). Analytic geometry, vectors, calculus, differentiation, and integration.',
        'photo': 'https://images.unsplash.com/photo-1596495578065-6e0763fa1178?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 94
    },
    {
        'isbn': '9789694400051',
        'seller_username': 'ayesha_khi',
        'condition': 'Good',
        'price': Decimal('140.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Karachi',
        'pickup': 'Gulshan-e-Iqbal Block 5 / NIPA Chowrangi',
        'desc': 'Sindh Board English Compulsory Class 11 (Intermediate Stage). Essays, short stories, grammar, and formal composition skills.',
        'photo': 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 62
    },

    # ========================================================
    # 🏔️ KPK BOARD (BISE Peshawar / Abbottabad)
    # ========================================================
    {
        'isbn': '9789694500010',
        'seller_username': 'kpk_seller',
        'condition': 'Like New',
        'price': Decimal('190.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Peshawar',
        'pickup': 'University of Peshawar (UoP) / Islamia College Gate',
        'desc': 'KPK Board Biology Class 11 (HSSC Part-1 Pre-Medical). Biological molecules, enzymes, plant anatomy, and animal diversity.',
        'photo': 'https://images.unsplash.com/photo-1530210124550-912dc1381cb8?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': True,
        'views': 130
    },
    {
        'isbn': '9789694500027',
        'seller_username': 'kpk_seller',
        'condition': 'Good',
        'price': Decimal('210.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Peshawar',
        'pickup': 'Khyber Medical College Gate / Jamrud Road',
        'desc': 'KPK Board Chemistry Class 12 (HSSC Part-2 Science). Inorganic metallurgy, organic reaction mechanisms, and biochemistry.',
        'photo': 'https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 84
    },
    {
        'isbn': '9789694500034',
        'seller_username': 'kpk_seller',
        'condition': 'Like New',
        'price': Decimal('150.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Peshawar',
        'pickup': 'Board of Intermediate & Secondary Education Peshawar',
        'desc': 'KPK Board Physics Class 9 (SSC Part-1 Science Group). Kinematics, dynamics, gravitation, and heat transfer. Intact book condition.',
        'photo': 'https://images.unsplash.com/photo-1632571401005-458e9d244591?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 91
    },
    {
        'isbn': '9789694500041',
        'seller_username': 'kpk_seller',
        'condition': 'Good',
        'price': Decimal('170.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Peshawar',
        'pickup': 'Qissa Khwani Bazaar / Academic Booksellers Street',
        'desc': 'KPK Board Mathematics Class 10 (SSC Part-2 Science Group). Quadratic equations, partial fractions, coordinate geometry, and circle theorems.',
        'photo': 'https://images.unsplash.com/photo-1596495578065-6e0763fa1178?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 73
    },
    {
        'isbn': '9789694500058',
        'seller_username': 'kpk_seller',
        'condition': 'Good',
        'price': Decimal('180.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Peshawar',
        'pickup': 'UET Peshawar Main Campus / University Town',
        'desc': 'KPK Board Computer Science Class 11 (HSSC-I ICS Group). Computing hardware, system software, networking, security, and digital data.',
        'photo': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 68
    },

    # ========================================================
    # 🌾 BALOCHISTAN BOARD (BISE Quetta)
    # ========================================================
    {
        'isbn': '9789694600017',
        'seller_username': 'baloch_seller',
        'condition': 'Good',
        'price': Decimal('120.00'),
        'is_free': False,
        'target_age_group': 'kids',
        'city': 'Quetta',
        'pickup': 'University of Balochistan (UoB) / Sariab Road',
        'desc': 'Balochistan Board General Science Class 8 (Middle Stage). Living systems, biotechnology basics, acids and bases, and space exploration.',
        'photo': 'https://images.unsplash.com/photo-1507668077129-56e32842fceb?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 58
    },
    {
        'isbn': '9789694600024',
        'seller_username': 'baloch_seller',
        'condition': 'Like New',
        'price': Decimal('180.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Quetta',
        'pickup': 'Jinnah Road / Model Town Quetta',
        'desc': 'Balochistan Board Physics Class 11 (HSSC-I Science). Approved by BTBB Quetta for FSc pre-engineering and pre-medical examinations.',
        'photo': 'https://images.unsplash.com/photo-1632571401005-458e9d244591?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': True,
        'views': 105
    },
    {
        'isbn': '9789694600031',
        'seller_username': 'baloch_seller',
        'condition': 'Good',
        'price': Decimal('160.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Khuzdar',
        'pickup': 'BUETK Khuzdar Main Campus Gate',
        'desc': 'Balochistan Board Chemistry Class 10 (SSC Part-2 Science). Chemical equilibrium, acids, bases, organic chemistry, and water resources.',
        'photo': 'https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 72
    },
    {
        'isbn': '9789694600048',
        'seller_username': 'baloch_seller',
        'condition': 'Like New',
        'price': Decimal('130.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Gwadar',
        'pickup': 'University of Gwadar / Airport Road Campus',
        'desc': 'Balochistan Board Pakistan Studies Class 12 (HSSC-II). Comprehensive overview of ideology, governance, economy, and provincial development.',
        'photo': 'https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 86
    },
    {
        'isbn': '9789694600055',
        'seller_username': 'baloch_seller',
        'condition': 'Good',
        'price': Decimal('150.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Turbat',
        'pickup': 'University of Turbat Main Campus Gate',
        'desc': 'Balochistan Board Mathematics Class 9 (SSC Part-1 Science). Real numbers, logarithms, algebraic formulas, linear equations, and geometry.',
        'photo': 'https://images.unsplash.com/photo-1596495578065-6e0763fa1178?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 64
    },

    # ========================================================
    # 🎓 CAMBRIDGE (O/A Levels)
    # ========================================================
    {
        'isbn': '9780199407408',
        'seller_username': 'cambridge_seller',
        'condition': 'Like New',
        'price': Decimal('850.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Lahore',
        'pickup': 'LGS Defence Phase 5 / Ring Road',
        'desc': 'Cambridge O-Level Mathematics D4 (7th Edition). Comprehensive syllabus coverage for 4024 with vectors, probability, and matrices.',
        'photo': 'https://images.unsplash.com/photo-1596495578065-6e0763fa1178?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': True,
        'views': 160
    },
    {
        'isbn': '9781108847063',
        'seller_username': 'cambridge_seller',
        'condition': 'Brand New',
        'price': Decimal('1100.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Islamabad',
        'pickup': 'Roots Millennium / F-8 Markaz Islamabad',
        'desc': 'Cambridge International AS & A Level Economics Coursebook (Colin Bamford, 4th Ed). Endorsed by Cambridge. Perfect condition.',
        'photo': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 120
    },
    {
        'isbn': '9781108436991',
        'seller_username': 'ayesha_khi',
        'condition': 'Like New',
        'price': Decimal('950.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Karachi',
        'pickup': 'Karachi Grammar School / Clifton Block 4',
        'desc': 'Cambridge O Level Physics Coursebook (5054). Essential guide for CAIE O-Level exams with worked past paper problems and diagrams.',
        'photo': 'https://images.unsplash.com/photo-1632571401005-458e9d244591?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 135
    },
    {
        'isbn': '9781108951609',
        'seller_username': 'cambridge_seller',
        'condition': 'Good',
        'price': Decimal('900.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Lahore',
        'pickup': 'Aitchison College Gate / Mall Road Lahore',
        'desc': 'Cambridge IGCSE & O Level Chemistry Coursebook (Richard Harwood). Organic chemistry, stoichiometry, and practical qualitative tests.',
        'photo': 'https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 98
    },
    {
        'isbn': '9781108740524',
        'seller_username': 'cambridge_seller',
        'condition': 'Like New',
        'price': Decimal('1050.00'),
        'is_free': False,
        'target_age_group': 'teens',
        'city': 'Islamabad',
        'pickup': 'Beaconhouse Margalla Campus / H-8 Islamabad',
        'desc': 'Cambridge International AS & A Level Accounting Coursebook (Harold Randall). Financial reporting, budget variance, and management accounts.',
        'photo': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 112
    },

    # ========================================================
    # 🎁 FREE DONATED BOOKS (Community Giveaways - Rs. 0)
    # ========================================================
    {
        'isbn': '9789694370019',
        'seller_username': 'ayesha_khi',
        'condition': 'Good',
        'price': Decimal('0.00'),
        'is_free': True,
        'target_age_group': 'young_adult',
        'city': 'Karachi',
        'pickup': 'NED University / Gulshan-e-Iqbal',
        'desc': 'Community book donation: Peer-e-Kamil reading copy. Passing it forward for another avid novel reader. 100% free giveaway.',
        'photo': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 240
    },
    {
        'isbn': '9789695840406',
        'seller_username': 'bilal_bwp',
        'condition': 'Good',
        'price': Decimal('0.00'),
        'is_free': True,
        'target_age_group': 'kids',
        'city': 'Bahawalpur',
        'pickup': 'IUB Abbasia Campus / Model Town B',
        'desc': 'Free community storybook for kids: Taleem-o-Tarbiyat moral stories collection. Donated to inspire young readers to read books.',
        'photo': 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 180
    },

    # ========================================================
    # 🧸 KIDS & STORY BOOKS (Age 5-12)
    # ========================================================
    {
        'isbn': '9789695840413',
        'seller_username': 'ali_seller',
        'condition': 'Like New',
        'price': Decimal('180.00'),
        'is_free': False,
        'target_age_group': 'kids',
        'city': 'Lahore',
        'pickup': 'Ferozsons Mall Road / Anarkali',
        'desc': 'Taleem-o-Tarbiyat: Selected Moral Stories for Children. Colorful full-page illustrations promoting honesty, hard work, and good manners.',
        'photo': 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 78
    },
    {
        'isbn': '9789695840420',
        'seller_username': 'zainab_rwp',
        'condition': 'Good',
        'price': Decimal('160.00'),
        'is_free': False,
        'target_age_group': 'kids',
        'city': 'Rawalpindi',
        'pickup': 'Saddar Rawalpindi / Cantt Library',
        'desc': 'Sheikh Chilli ke Qissay (Classic Folk Tales of Pakistan). Illustrated humorous traditional stories for kids aged 6 to 12.',
        'photo': 'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 85
    },
    {
        'isbn': '9789695840437',
        'seller_username': 'fatima_z',
        'condition': 'Brand New',
        'price': Decimal('220.00'),
        'is_free': False,
        'target_age_group': 'kids',
        'city': 'Islamabad',
        'pickup': 'F-7 Markaz / Jinnah Super Market',
        'desc': "Aesop's Fables Illustrated for Pakistani Children (Urdu & English). Bilingual illustrated edition with classic moral lessons.",
        'photo': 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': True,
        'views': 125
    },
    {
        'isbn': '9789695840444',
        'seller_username': 'usman_mul',
        'condition': 'Like New',
        'price': Decimal('250.00'),
        'is_free': False,
        'target_age_group': 'kids',
        'city': 'Multan',
        'pickup': 'Gulgasht Colony / BZU Multan',
        'desc': 'Alif Laila Kids Edition (One Thousand and One Nights). Aladdin, Ali Baba, and Sinbad tales adapted in simple Urdu for children.',
        'photo': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 94
    },
    {
        'isbn': '9789695840451',
        'seller_username': 'bilal_bwp',
        'condition': 'Good',
        'price': Decimal('190.00'),
        'is_free': False,
        'target_age_group': 'kids',
        'city': 'Bahawalpur',
        'pickup': 'IUB Baghdad Campus / Library',
        'desc': 'Moral Stories for Young Readers (Ikhlaqi Kahaniyan by Ishtiaq Ahmed). Exciting adventure stories teaching character and empathy.',
        'photo': 'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 72
    },
    {
        'isbn': '9789695840468',
        'seller_username': 'ayesha_khi',
        'condition': 'Like New',
        'price': Decimal('200.00'),
        'is_free': False,
        'target_age_group': 'kids',
        'city': 'Karachi',
        'pickup': 'Bahria University / Karsaz Karachi',
        'desc': 'Bachon Ki Dunya: Illustrated Animal Adventures. Exciting stories featuring Markhor, Snow Leopard, and Indus River Dolphin.',
        'photo': 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 88
    },

    # ========================================================
    # 📖 FICTION & NOVELS
    # ========================================================
    {
        'isbn': '9789694370026',
        'seller_username': 'fatima_z',
        'condition': 'Like New',
        'price': Decimal('420.00'),
        'is_free': False,
        'target_age_group': 'young_adult',
        'city': 'Islamabad',
        'pickup': 'University Road / National Library Islamabad',
        'desc': 'Jannat Kay Pattay (جنت کے پتے) by Nemrah Ahmed. Bestselling novel of mystery, spiritual transformation, and intrigue. Immaculate condition.',
        'photo': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': True,
        'views': 295
    },
    {
        'isbn': '9789694370033',
        'seller_username': 'usman_mul',
        'condition': 'Good',
        'price': Decimal('380.00'),
        'is_free': False,
        'target_age_group': 'general',
        'city': 'Lahore',
        'pickup': 'Urdu Bazaar / Anarkali Lahore',
        'desc': 'Raja Gidh (راجہ گدھ) by Bano Qudsia. Acclaimed modern Urdu literary masterpiece. Clean pages and intact binding.',
        'photo': 'https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 210
    },
    {
        'isbn': '9781594631931',
        'seller_username': 'ayesha_khi',
        'condition': 'Like New',
        'price': Decimal('450.00'),
        'is_free': False,
        'target_age_group': 'general',
        'city': 'Karachi',
        'pickup': 'Clifton Block 5 / Dolmen Mall area',
        'desc': 'The Kite Runner by Khaled Hosseini. Unforgettable world-renowned novel of brotherhood, betrayal, and redemption.',
        'photo': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 185
    },
    {
        'isbn': '9780143118527',
        'seller_username': 'cambridge_seller',
        'condition': 'Like New',
        'price': Decimal('490.00'),
        'is_free': False,
        'target_age_group': 'general',
        'city': 'Islamabad',
        'pickup': 'F-8 Markaz / Islamabad Club area',
        'desc': 'The Forty Rules of Love by Elif Shafak. Bestselling novel exploring love, friendship, and the spiritual bond of Rumi and Shams of Tabriz.',
        'photo': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 230
    },
    {
        'isbn': '9789694370040',
        'seller_username': 'bilal_bwp',
        'condition': 'Brand New',
        'price': Decimal('480.00'),
        'is_free': False,
        'target_age_group': 'young_adult',
        'city': 'Bahawalpur',
        'pickup': 'IUB Baghdad Campus / Student Hostel Gate',
        'desc': 'Aab-e-Hayat (آب حیات) by Umera Ahmed. Official sequel to Peer-e-Kamil. Unread, pristine copy.',
        'photo': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 260
    },

    # ========================================================
    # 🏛️ HISTORY & LITERATURE
    # ========================================================
    {
        'isbn': '9789693500011',
        'seller_username': 'ali_seller',
        'condition': 'Like New',
        'price': Decimal('320.00'),
        'is_free': False,
        'target_age_group': 'general',
        'city': 'Lahore',
        'pickup': 'GCU Lahore / Kachehri Road',
        'desc': 'Bang-e-Dra (بانگِ درا) by Allama Muhammad Iqbal. Definitive Iqbal Academy Pakistan edition with complete explanatory notes.',
        'photo': 'https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': True,
        'views': 175
    },
    {
        'isbn': '9780195775419',
        'seller_username': 'fatima_z',
        'condition': 'Good',
        'price': Decimal('650.00'),
        'is_free': False,
        'target_age_group': 'general',
        'city': 'Islamabad',
        'pickup': 'Quaid-i-Azam University (QAU) Campus',
        'desc': 'Jinnah of Pakistan by Stanley Wolpert (Oxford University Press). The authoritative biography of Quaid-e-Azam Muhammad Ali Jinnah.',
        'photo': 'https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 210
    },
    {
        'isbn': '9789694370057',
        'seller_username': 'zainab_rwp',
        'condition': 'Good',
        'price': Decimal('550.00'),
        'is_free': False,
        'target_age_group': 'general',
        'city': 'Rawalpindi',
        'pickup': 'Rawalpindi Arts Council / Stadium Road',
        'desc': 'Shahab Nama (شہاب نامہ) by Qudratullah Shahab. Legendary autobiographical memoir of Pakistani civil service and early history.',
        'photo': 'https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 320
    },
    {
        'isbn': '9789693500028',
        'seller_username': 'usman_mul',
        'condition': 'Like New',
        'price': Decimal('480.00'),
        'is_free': False,
        'target_age_group': 'general',
        'city': 'Lahore',
        'pickup': 'Urdu Bazaar / Ilmi Publishers Street',
        'desc': 'Tareekh-e-Pakistan: Qayam se Daur-e-Hazir Tak by Prof. Muhammad Yahya Amjad. Essential reference for CSS, PMS, and history scholars.',
        'photo': 'https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 155
    },
    {
        'isbn': '9780674052895',
        'seller_username': 'cambridge_seller',
        'condition': 'Brand New',
        'price': Decimal('580.00'),
        'is_free': False,
        'target_age_group': 'general',
        'city': 'Islamabad',
        'pickup': 'National Library / Constitution Avenue',
        'desc': 'The Struggle for Pakistan: A Muslim Homeland and Global Politics by Dr. Ayesha Jalal. Hardcover academic edition.',
        'photo': 'https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 165
    },

    # ========================================================
    # 🎓 UNIVERSITY / HIGHER ED (Medical, BBA, CSS)
    # ========================================================
    {
        'isbn': '9780323597128',
        'seller_username': 'usman_mul',
        'condition': 'Like New',
        'price': Decimal('1450.00'),
        'is_free': False,
        'target_age_group': 'young_adult',
        'city': 'Multan',
        'pickup': 'Nishtar Medical University Gate / Multan',
        'desc': 'Guyton and Hall Textbook of Medical Physiology (14th Edition). Standard medical textbook for 1st & 2nd year MBBS and BDS students.',
        'photo': 'https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': True,
        'views': 280
    },
    {
        'isbn': '9789332587700',
        'seller_username': 'ayesha_khi',
        'condition': 'Like New',
        'price': Decimal('850.00'),
        'is_free': False,
        'target_age_group': 'young_adult',
        'city': 'Karachi',
        'pickup': 'IBA Karachi Main Campus / University Road',
        'desc': 'Principles of Marketing (17th South Asian Edition) by Philip Kotler & Gary Armstrong. Key BBA & MBA marketing reference.',
        'photo': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 190
    },
    {
        'isbn': '9789699640018',
        'seller_username': 'ali_seller',
        'condition': 'Like New',
        'price': Decimal('750.00'),
        'is_free': False,
        'target_age_group': 'young_adult',
        'city': 'Lahore',
        'pickup': 'Civil Services Academy area / Mall Road Lahore',
        'desc': 'CSS Current Affairs & Pakistan Affairs Comprehensive Guide (Jahangir World Times). Indispensable for FPSC CSS 2025 aspirants.',
        'photo': 'https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=500&auto=format&fit=crop&q=80',
        'is_sponsored': False,
        'views': 225
    }
]

DEMO_USERS = [
    {
        'username': 'baloch_seller',
        'name': 'Mir Baloch (Quetta)',
        'phone': '03337890123',
        'city': 'Quetta',
        'campus': 'University of Balochistan (UoB) / Sariab Road',
        'type': 'student',
        'rating': Decimal('4.9'),
        'reviews': 16,
        'wallet': Decimal('450.00')
    },
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
        'name': 'Ayesha Reader',
        'phone': '03023344556',
        'city': 'Islamabad',
        'campus': 'Central Campus / Student Center',
        'type': 'student',
        'rating': Decimal('5.0'),
        'reviews': 2,
        'wallet': Decimal('300.00')
    },
    {
        'username': 'kpk_seller',
        'name': 'Tariq Khattak (Peshawar)',
        'phone': '03138899001',
        'city': 'Peshawar',
        'campus': 'University of Peshawar (UoP) Campus',
        'type': 'student',
        'rating': Decimal('4.9'),
        'reviews': 14,
        'wallet': Decimal('220.00')
    },
    {
        'username': 'sindh_seller',
        'name': 'Farhan Memon (Karachi)',
        'phone': '03321122445',
        'city': 'Karachi',
        'campus': 'DJ Sindh Govt Science College / Saddar',
        'type': 'student',
        'rating': Decimal('4.8'),
        'reviews': 10,
        'wallet': Decimal('190.00')
    },
    {
        'username': 'cambridge_seller',
        'name': 'Saad Qureshi (Cambridge A-Level)',
        'phone': '03051122334',
        'city': 'Islamabad',
        'campus': 'Roots Millennium / Beaconhouse Margalla',
        'type': 'student',
        'rating': Decimal('5.0'),
        'reviews': 7,
        'wallet': Decimal('400.00')
    }
]


import sys

def ensure_demo_listings(force=False):
    """
    Checks active listings in Bookzy AI.
    Ensures complete catalog of Textbooks (Primary to FSc, Balochistan Board),
    Free Community Donations (Rs. 0), Kids & Story Books, Fiction & Novels,
    and History & Literature across Quetta, Gwadar, Khuzdar, Lahore, Islamabad,
    Karachi, Rawalpindi, Multan, Faisalabad, and Bahawalpur.
    """
    # Do not auto-seed during automated test suites unless explicitly forced
    if not force and ('test' in sys.argv or 'pytest' in sys.argv[0]):
        return 0

    try:
        active_count = Listing.objects.filter(status='active').count()
        missing_isbns = set(item['isbn'] for item in DEMO_TEXTBOOKS) - set(Listing.objects.filter(status='active').values_list('book__isbn', flat=True))
        if not force and active_count >= len(DEMO_TEXTBOOKS) and not missing_isbns:
            return active_count

        logger.info(f"Bookzy AI auto-seed triggered: active listings count ({active_count}) / missing ({len(missing_isbns)}).")

        # 1. Platform Settings
        setting, _ = PlatformSetting.objects.get_or_create(id=1)
        if not setting.platform_name or setting.platform_name in ['BookLoop Pakistan', 'BookBazaar Pakistan', 'BookBazaar AI']:
            setting.platform_name = 'Bookzy AI'
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
                listing = Listing.objects.filter(book=book_obj, seller=seller_prof).first()
                if not listing:
                    listing = Listing.objects.create(
                        book=book_obj,
                        seller=seller_prof,
                        price=l['price'],
                        is_free=is_free_val,
                        target_age_group=age_grp_val,
                        condition=l['condition'],
                        city=l['city'],
                        pickup_location=l['pickup'],
                        description=l['desc'],
                        photo_url=l['photo'],
                        status='active',
                        is_sponsored=l['is_sponsored'],
                        views_count=l.get('views', 42)
                    )
                else:
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
        logger.info(f"Bookzy AI auto-seed completed successfully. Active listings: {final_count}")
        return final_count

    except Exception as e:
        logger.warning(f"Auto-seed check deferred (database may still be migrating): {e}")
        return 0
