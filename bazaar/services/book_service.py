import json
import urllib.request
import urllib.parse
from bazaar.models import Book

# Pre-cached catalog of prominent Pakistani curriculum and international standard textbooks
KNOWN_CATALOG = {
    '9780132350884': {
        'isbn': '9780132350884',
        'title': 'Clean Code: A Handbook of Agile Software Craftsmanship',
        'author': 'Robert C. Martin',
        'publisher': 'Prentice Hall',
        'edition': '1st Edition',
        'category': 'Software Engineering',
        'education_board': 'Higher Education / University',
        'grade_class': 'Bachelor / BS / Undergrad',
        'subject': 'Software Engineering',
        'description': 'Even bad code can function. But if code isn\'t clean, it can bring a development organization to its knees. Every year, countless hours and significant resources are lost because of poorly written code. This book is a must-read for any developer, software engineer, or student.',
        'cover_image': 'https://images-na.ssl-images-amazon.com/images/I/41xShlnTZTL._SX376_BO1,204,203,200_.jpg',
        'original_retail_price': 2200.00
    },
    '9780078022128': {
        'isbn': '9780078022128',
        'title': "Software Engineering: A Practitioner's Approach",
        'author': 'Roger S. Pressman, Bruce R. Maxim',
        'publisher': 'McGraw-Hill Education',
        'edition': '8th Edition',
        'category': 'Software Engineering',
        'education_board': 'Higher Education / University',
        'grade_class': 'Bachelor / BS / Undergrad',
        'subject': 'Software Engineering',
        'description': 'For almost three decades, Roger Pressman\'s Software Engineering: A Practitioner\'s Approach has been the world\'s leading textbook in software engineering. Standard reference for software engineering and computer science programs across Pakistani universities.',
        'cover_image': 'https://images-na.ssl-images-amazon.com/images/I/51r-E1952WL._SX397_BO1,204,203,200_.jpg',
        'original_retail_price': 1850.00
    },
    '9781118063330': {
        'isbn': '9781118063330',
        'title': 'Operating System Concepts (Dinosaur Book)',
        'author': 'Abraham Silberschatz, Peter B. Galvin, Greg Gagne',
        'publisher': 'Wiley',
        'edition': '9th Edition',
        'category': 'Computer Science & IT',
        'education_board': 'Higher Education / University',
        'grade_class': 'Bachelor / BS / Undergrad',
        'subject': 'Operating Systems',
        'description': 'Operating System Concepts continues to provide a solid theoretical foundation for understanding operating systems. Covers processes, memory management, file systems, and distributed systems.',
        'cover_image': 'https://images-na.ssl-images-amazon.com/images/I/51uU8vY5cFL._SX397_BO1,204,203,200_.jpg',
        'original_retail_price': 1950.00
    },
    '9780262033848': {
        'isbn': '9780262033848',
        'title': 'Introduction to Algorithms (CLRS)',
        'author': 'Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein',
        'publisher': 'The MIT Press',
        'edition': '3rd Edition',
        'category': 'Computer Science & IT',
        'education_board': 'Higher Education / University',
        'grade_class': 'Bachelor / BS / Undergrad',
        'subject': 'Data Structures & Algorithms',
        'description': 'Some books on algorithms are rigorous but incomplete; others cover masses of material but lack rigor. Introduction to Algorithms uniquely combines rigor and comprehensiveness.',
        'cover_image': 'https://images-na.ssl-images-amazon.com/images/I/41SNoh5ZhOL._SX379_BO1,204,203,200_.jpg',
        'original_retail_price': 2800.00
    },
    '9780132126953': {
        'isbn': '9780132126953',
        'title': 'Computer Networks',
        'author': 'Andrew S. Tanenbaum, David J. Wetherall',
        'publisher': 'Pearson',
        'edition': '5th Edition',
        'category': 'Computer Science & IT',
        'education_board': 'Higher Education / University',
        'grade_class': 'Bachelor / BS / Undergrad',
        'subject': 'Computer Networks',
        'description': 'The classic introduction to computer networks. Explores the hardware and software principles of modern networking from physical to application layer.',
        'cover_image': 'https://images-na.ssl-images-amazon.com/images/I/51kLhW05UGL._SX382_BO1,204,203,200_.jpg',
        'original_retail_price': 1750.00
    },
    '9780073523323': {
        'isbn': '9780073523323',
        'title': 'Database System Concepts',
        'author': 'Abraham Silberschatz, Henry F. Korth, S. Sudarshan',
        'publisher': 'McGraw-Hill',
        'edition': '6th Edition',
        'category': 'Computer Science & IT',
        'education_board': 'Higher Education / University',
        'grade_class': 'Bachelor / BS / Undergrad',
        'subject': 'Database Systems',
        'description': 'Presents the fundamental concepts of database management in an intuitive manner geared toward allowing students to begin working with databases immediately.',
        'cover_image': 'https://images-na.ssl-images-amazon.com/images/I/51c4a0n0U2L._SX396_BO1,204,203,200_.jpg',
        'original_retail_price': 1650.00
    },
    '9789694370002': {
        'isbn': '9789694370002',
        'title': 'Peer-e-Kamil (پیر کامل)',
        'author': 'Umera Ahmed (عمیرہ احمد)',
        'publisher': 'Ilm-o-Irfan Publishers, Lahore',
        'edition': 'Classic Edition',
        'category': 'Urdu Literature & Novels',
        'education_board': 'General / None',
        'grade_class': 'General Reading',
        'subject': 'Urdu Novel',
        'description': 'A masterpiece Pakistani Urdu novel depicting spiritual awakening and deep character evolution. One of the highest-rated Urdu novels in modern Pakistan.',
        'cover_image': 'https://images-na.ssl-images-amazon.com/images/I/51wXpYlX0GL._SX331_BO1,204,203,200_.jpg',
        'original_retail_price': 950.00
    },
    '9789693500202': {
        'isbn': '9789693500202',
        'title': 'Raja Gidh (راجہ گدھ)',
        'author': 'Bano Qudsia (بانو قدسیہ)',
        'publisher': 'Sang-e-Meel Publications, Lahore',
        'edition': 'Revised Edition',
        'category': 'Urdu Literature & Novels',
        'education_board': 'General / None',
        'grade_class': 'General Reading',
        'subject': 'Urdu Philosophy & Literature',
        'description': 'Renowned Urdu psychological and philosophical novel exploring moral and ethical choices in human life and society.',
        'cover_image': 'https://images-na.ssl-images-amazon.com/images/I/51D61o8P51L._SX331_BO1,204,203,200_.jpg',
        'original_retail_price': 850.00
    },
    '9789695840123': {
        'isbn': '9789695840123',
        'title': 'Computer Science for Class 12 (ICS Part-II)',
        'author': 'Punjab Textbook Board (PTB)',
        'publisher': 'Punjab Curriculum and Textbook Board, Lahore',
        'edition': 'Latest Curriculum',
        'category': 'FSc / Matric / O & A Level',
        'education_board': 'Punjab Board',
        'grade_class': 'Intermediate / FSc / ICS (11th - 12th)',
        'subject': 'Computer Science',
        'description': 'Official ICS curriculum textbook for Intermediate Part-2 covering MS Access and C Language Programming.',
        'cover_image': 'https://images-na.ssl-images-amazon.com/images/I/41DqDq5HjHL._SX331_BO1,204,203,200_.jpg',
        'original_retail_price': 350.00
    },
    '9780323597128': {
        'isbn': '9780323597128',
        'title': 'Guyton and Hall Textbook of Medical Physiology',
        'author': 'John E. Hall, Michael E. Hall',
        'publisher': 'Elsevier',
        'edition': '14th Edition',
        'category': 'Medical & MBBS / BDS',
        'education_board': 'Higher Education / University',
        'grade_class': 'Bachelor / BS / Undergrad',
        'subject': 'Physiology',
        'description': 'The world\'s foremost medical physiology textbook, preferred by King Edward Medical University, Dow University of Health Sciences, and medical colleges across Pakistan.',
        'cover_image': 'https://images-na.ssl-images-amazon.com/images/I/51WqW+4iSML._SX389_BO1,204,203,200_.jpg',
        'original_retail_price': 3400.00
    },
    '9789695840130': {
        'isbn': '9789695840130',
        'title': 'Physics for Class 12 (FSc Pre-Engineering Part-II)',
        'author': 'Prof. Dr. M. Akram, Punjab Textbook Board (PTB)',
        'publisher': 'Punjab Curriculum and Textbook Board, Lahore',
        'edition': 'Latest PTB Curriculum',
        'category': 'FSc / Matric / O & A Level',
        'education_board': 'Punjab Board',
        'grade_class': 'Intermediate / FSc / ICS (11th - 12th)',
        'subject': 'Physics',
        'description': 'Official Punjab Textbook Board Physics textbook for Intermediate Part-2. Covers electrostatics, current electricity, electromagnetism, electronics, and nuclear physics.',
        'cover_image': 'https://images.unsplash.com/photo-1632571401005-458e9d244591?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 420.00
    },
    '9789695840147': {
        'isbn': '9789695840147',
        'title': 'Calculus and Analytic Geometry (B.Sc / BS Mathematics)',
        'author': 'Dr. S.M. Yusuf & Prof. Muhammad Amin',
        'publisher': 'Ilmi Kitab Khana, Lahore',
        'edition': 'Revised Edition',
        'category': 'Mathematics & Statistics',
        'education_board': 'Higher Education / University',
        'grade_class': 'Bachelor / BS / Undergrad',
        'subject': 'Mathematics',
        'description': 'Essential calculus and analytical geometry textbook across all major Pakistani colleges and universities. Complete guide for limits, differentiation, and definite integrals.',
        'cover_image': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 850.00
    },
    '9780133943030': {
        'isbn': '9780133943030',
        'title': 'Software Engineering (10th Global Edition)',
        'author': 'Ian Sommerville',
        'publisher': 'Pearson Education',
        'edition': '10th Edition',
        'category': 'Software Engineering',
        'education_board': 'Higher Education / University',
        'grade_class': 'Bachelor / BS / Undergrad',
        'subject': 'Software Engineering',
        'description': 'The definitive introduction to software engineering by Ian Sommerville. In-depth coverage of agile methods, cloud computing, microservices, dependability, and security engineering.',
        'cover_image': 'https://images.unsplash.com/photo-1532012164546-f432f2e3777f?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 2400.00
    },
    '9789695840154': {
        'isbn': '9789695840154',
        'title': 'General Science & Ability for CSS / PMS Aspirants',
        'author': 'Mian Shafiq (Jahangir World Times)',
        'publisher': 'Jahangir World Times Publications, Lahore',
        'edition': 'Latest FPSC Edition',
        'category': 'CSS / Competitive Exams',
        'education_board': 'FPSC / PPSC',
        'grade_class': 'CSS / PMS / Entry Tests',
        'subject': 'General Science & Ability',
        'description': 'Top-rated guide for CSS compulsory General Science & Ability exam. Complete syllabus coverage including physical science, biological science, environmental science, and quantitative reasoning.',
        'cover_image': 'https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 1200.00
    },
    # --- FREE DONATED BOOKS (Community Giveaways - Rs. 0) ---
    '9789695840208': {
        'isbn': '9789695840208',
        'title': 'Punjab Textbook Board English Class 5 (Free Community Donation)',
        'author': 'Punjab Curriculum and Textbook Board (PCTB)',
        'publisher': 'Punjab Curriculum and Textbook Board, Lahore',
        'edition': 'Single National Curriculum',
        'category': 'Punjab Textbooks (Primary to FSc)',
        'education_board': 'Punjab Board',
        'grade_class': 'Primary & Middle (Class 1-8)',
        'target_age_group': 'kids',
        'subject': 'English',
        'description': 'Free community book donation for deserving students. Official English textbook for Class 5 by Punjab Textbook Board. Completely intact pages with clean exercises.',
        'cover_image': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 180.00
    },
    '9789695840215': {
        'isbn': '9789695840215',
        'title': 'Physics for Class 11 (FSc Pre-Engineering Part-1) [Free Community Giveaway]',
        'author': 'Prof. Dr. M. Zakria Butt, Punjab Board',
        'publisher': 'Punjab Curriculum and Textbook Board, Lahore',
        'edition': 'PTB Curriculum',
        'category': 'Punjab Textbooks (Primary to FSc)',
        'education_board': 'Punjab Board',
        'grade_class': 'Intermediate / FSc / ICS (11th - 12th)',
        'target_age_group': 'teens',
        'subject': 'Physics',
        'description': 'Free giveaway for intermediate college students. Covers vectors, equilibrium, motion, work and energy, circular motion, fluid dynamics, and thermodynamics.',
        'cover_image': 'https://images.unsplash.com/photo-1632571401005-458e9d244591?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 380.00
    },
    '9789695840222': {
        'isbn': '9789695840222',
        'title': 'Bachon Ki Kahaniyan — Urdu Story Book (Free Giveaway)',
        'author': 'Ferozsons Children Classics',
        'publisher': 'Ferozsons Publishers, Lahore',
        'edition': 'Illustrated Color Edition',
        'category': 'Story Books',
        'education_board': 'General / None',
        'grade_class': 'Primary & Middle (Class 1-8)',
        'target_age_group': 'kids',
        'subject': 'Kids Stories',
        'description': 'Free book donation for young children. Illustrated Urdu moral stories with colorful characters promoting honesty, sharing, and kindness.',
        'cover_image': 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 250.00
    },
    '9789695840239': {
        'isbn': '9789695840239',
        'title': 'General Science Class 4 Punjab Textbook Board (Free Donation)',
        'author': 'Punjab Curriculum and Textbook Board, Lahore',
        'publisher': 'Punjab Curriculum and Textbook Board, Lahore',
        'edition': 'Single National Curriculum',
        'category': 'Punjab Textbooks (Primary to FSc)',
        'education_board': 'Punjab Board',
        'grade_class': 'Primary & Middle (Class 1-8)',
        'target_age_group': 'kids',
        'subject': 'General Science',
        'description': 'Free donation copy for primary school students. Includes plants, human body, ecosystems, matter and energy. Donated to help primary school students.',
        'cover_image': 'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 160.00
    },
    # --- PUNJAB TEXTBOOKS (Primary Class 1-5, Middle 6-8, Matric 9-10 & FSc 11-12) ---
    '9789695840246': {
        'isbn': '9789695840246',
        'title': 'Urdu Qaida & Primary Urdu Class 1 (Punjab Curriculum Board)',
        'author': 'Punjab Curriculum and Textbook Board, Lahore',
        'publisher': 'Punjab Curriculum and Textbook Board, Lahore',
        'edition': 'SNC Edition',
        'category': 'Punjab Textbooks (Primary to FSc)',
        'education_board': 'Punjab Board',
        'grade_class': 'Primary & Middle (Class 1-8)',
        'target_age_group': 'kids',
        'subject': 'Urdu',
        'description': 'Official Punjab Board Urdu Qaida and Class 1 basic reading textbook with phonics, letters, and colorful illustrations for early learners.',
        'cover_image': 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 120.00
    },
    '9789695840253': {
        'isbn': '9789695840253',
        'title': 'Mathematics for Class 3 (Punjab Textbook Board)',
        'author': 'Prof. M. Sharif, Punjab Board',
        'publisher': 'Punjab Curriculum and Textbook Board, Lahore',
        'edition': 'Latest PTB Curriculum',
        'category': 'Punjab Textbooks (Primary to FSc)',
        'education_board': 'Punjab Board',
        'grade_class': 'Primary & Middle (Class 1-8)',
        'target_age_group': 'kids',
        'subject': 'Mathematics',
        'description': 'Official single national curriculum math textbook for grade 3. Addition, subtraction, multiplication tables, fractions, and introductory geometry.',
        'cover_image': 'https://images.unsplash.com/photo-1596495578065-6e0763fa1178?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 160.00
    },
    '9789695840260': {
        'isbn': '9789695840260',
        'title': 'Urdu for Class 5 (Punjab Textbook Board)',
        'author': 'Dr. Khawaja Zakariya, PCTB Lahore',
        'publisher': 'Punjab Curriculum and Textbook Board, Lahore',
        'edition': 'Latest PTB Edition',
        'category': 'Punjab Textbooks (Primary to FSc)',
        'education_board': 'Punjab Board',
        'grade_class': 'Primary & Middle (Class 1-8)',
        'target_age_group': 'kids',
        'subject': 'Urdu',
        'description': 'Complete Grade 5 Urdu curriculum with poems, national stories, moral essays, grammar, and comprehension exercises.',
        'cover_image': 'https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 190.00
    },
    '9789695840277': {
        'isbn': '9789695840277',
        'title': 'General Science for Class 6 (Punjab Curriculum Board)',
        'author': 'Punjab Curriculum and Textbook Board, Lahore',
        'publisher': 'Punjab Curriculum and Textbook Board, Lahore',
        'edition': 'PTB Curriculum',
        'category': 'Punjab Textbooks (Primary to FSc)',
        'education_board': 'Punjab Board',
        'grade_class': 'Primary & Middle (Class 1-8)',
        'target_age_group': 'teens',
        'subject': 'General Science',
        'description': 'Cellular organization, human sense organs, photosynthesis, elements and compounds, mixtures, and energy transformations for 6th standard.',
        'cover_image': 'https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 220.00
    },
    '9789695840284': {
        'isbn': '9789695840284',
        'title': 'General Science for Class 8 (Punjab Textbook Board)',
        'author': 'Prof. Tariq Mahmood, PCTB Lahore',
        'publisher': 'Punjab Curriculum and Textbook Board, Lahore',
        'edition': 'Latest PTB Edition',
        'category': 'Punjab Textbooks (Primary to FSc)',
        'education_board': 'Punjab Board',
        'grade_class': 'Primary & Middle (Class 1-8)',
        'target_age_group': 'teens',
        'subject': 'General Science',
        'description': 'Official 8th Class Punjab Board textbook. Human organ systems, heredity, biotechnology basics, chemical reactions, acids & bases, and space exploration.',
        'cover_image': 'https://images.unsplash.com/photo-1507668077129-56e32842fceb?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 240.00
    },
    '9789695840291': {
        'isbn': '9789695840291',
        'title': 'Biology for Class 9 (Punjab Textbook Board, Science Group)',
        'author': 'Dr. Zahid Rizvi & Dr. Hamid Saeed, PCTB Lahore',
        'publisher': 'Punjab Curriculum and Textbook Board, Lahore',
        'edition': 'Science Curriculum Edition',
        'category': 'Punjab Textbooks (Primary to FSc)',
        'education_board': 'Punjab Board',
        'grade_class': 'Matric (9th - 10th)',
        'target_age_group': 'teens',
        'subject': 'Biology',
        'description': 'Official Biology 9th Grade textbook for Matric students. Cell biology, tissues, bioenergetics, enzymes, human nutrition, and circulatory transport systems.',
        'cover_image': 'https://images.unsplash.com/photo-1530210124550-912dc1381cb8?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 280.00
    },
    '9789695840307': {
        'isbn': '9789695840307',
        'title': 'Chemistry for Class 10 (Punjab Textbook Board)',
        'author': 'Dr. Jalil Ahmad & Dr. Jamil Anwar, PCTB Lahore',
        'publisher': 'Punjab Curriculum and Textbook Board, Lahore',
        'edition': 'PTB Matric Edition',
        'category': 'Punjab Textbooks (Primary to FSc)',
        'education_board': 'Punjab Board',
        'grade_class': 'Matric (9th - 10th)',
        'target_age_group': 'teens',
        'subject': 'Chemistry',
        'description': 'Official Chemistry 10th Grade Punjab Board textbook. Chemical equilibrium, acids, bases and salts, organic chemistry, biochemistry, and atmospheric chemistry.',
        'cover_image': 'https://images.unsplash.com/photo-1603126857599-f6e157fa2fe6?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 290.00
    },
    '9789695840314': {
        'isbn': '9789695840314',
        'title': 'Mathematics for Class 10 (Science Group, Punjab Board)',
        'author': 'Prof. Muhammad Habib, PCTB Lahore',
        'publisher': 'Punjab Curriculum and Textbook Board, Lahore',
        'edition': 'Science Group Edition',
        'category': 'Punjab Textbooks (Primary to FSc)',
        'education_board': 'Punjab Board',
        'grade_class': 'Matric (9th - 10th)',
        'target_age_group': 'teens',
        'subject': 'Mathematics',
        'description': 'Quadratic equations, theory of quadratic equations, variations, partial fractions, sets and functions, basic statistics, trigonometry, and circle geometry theorems.',
        'cover_image': 'https://images.unsplash.com/photo-1509228468518-180dd4864904?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 320.00
    },
    '9789695840321': {
        'isbn': '9789695840321',
        'title': 'Physics for Class 11 (FSc Pre-Engineering Part-I, Punjab Board)',
        'author': 'Prof. Dr. M. Zakria Butt, Punjab Board',
        'publisher': 'Punjab Curriculum and Textbook Board, Lahore',
        'edition': 'Intermediate Part-1 Edition',
        'category': 'Punjab Textbooks (Primary to FSc)',
        'education_board': 'Punjab Board',
        'grade_class': 'Intermediate / FSc / ICS (11th - 12th)',
        'target_age_group': 'teens',
        'subject': 'Physics',
        'description': 'Official Punjab Board textbook for Intermediate Part-1. Measurements, vectors and equilibrium, motion and force, work and energy, circular motion, and physical optics.',
        'cover_image': 'https://images.unsplash.com/photo-1632571401005-458e9d244591?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 380.00
    },
    '9789695840338': {
        'isbn': '9789695840338',
        'title': 'Mathematics for Class 11 (FSc / ICS Part-I, Punjab Board)',
        'author': 'Prof. Dr. M. Akram & Dr. M. Yousaf, PCTB Lahore',
        'publisher': 'Punjab Curriculum and Textbook Board, Lahore',
        'edition': 'Intermediate Part-1 Edition',
        'category': 'Punjab Textbooks (Primary to FSc)',
        'education_board': 'Punjab Board',
        'grade_class': 'Intermediate / FSc / ICS (11th - 12th)',
        'target_age_group': 'teens',
        'subject': 'Mathematics',
        'description': 'Official Punjab Board textbook for Intermediate Part-1. Number systems, matrices, quadratic equations, permutations and combinations, mathematical induction, and trigonometry identities.',
        'cover_image': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 360.00
    },
    '9789695840345': {
        'isbn': '9789695840345',
        'title': 'English Book-II & Good-Bye Mr. Chips (Class 12, Punjab Board)',
        'author': 'Punjab Curriculum and Textbook Board, Lahore',
        'publisher': 'Punjab Curriculum and Textbook Board, Lahore',
        'edition': 'Intermediate Part-2 Edition',
        'category': 'Punjab Textbooks (Primary to FSc)',
        'education_board': 'Punjab Board',
        'grade_class': 'Intermediate / FSc / ICS (11th - 12th)',
        'target_age_group': 'teens',
        'subject': 'English',
        'description': 'Official English essays, biographical sketches, and complete Good-Bye Mr. Chips novel study for Intermediate Part-2. Key examination questions and vocabulary included.',
        'cover_image': 'https://images.unsplash.com/photo-1476275466078-4007374efbbe?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 260.00
    },
    # --- KIDS & STORY BOOKS ---
    '9780141325293': {
        'isbn': '9780141325293',
        'title': 'The Jungle Book (Illustrated Kids Edition)',
        'author': 'Rudyard Kipling',
        'publisher': 'Puffin Classics / Ferozsons',
        'edition': 'Illustrated Color Edition',
        'category': 'Story Books',
        'education_board': 'General / None',
        'grade_class': 'Primary & Middle (Class 1-8)',
        'target_age_group': 'kids',
        'subject': 'Adventure & Stories',
        'description': 'Timeless illustrated adventure classic following Mowgli, Baloo, and Bagheera in the wilderness. High quality color prints and easy English vocabulary for children.',
        'cover_image': '/static/img/covers/jungle_book.svg',
        'original_retail_price': 550.00
    },
    '9780141325309': {
        'isbn': '9780141325309',
        'title': 'Cinderella & Classic Fairy Tales',
        'author': 'Brothers Grimm & Charles Perrault',
        'publisher': 'Ladybird / Classic Children Books',
        'edition': 'Deluxe Illustrated Edition',
        'category': 'Story Books',
        'education_board': 'General / None',
        'grade_class': 'Primary & Middle (Class 1-8)',
        'target_age_group': 'kids',
        'subject': 'Enchanting Classic Fairy Tales',
        'description': 'Beloved timeless fairy tales including Cinderella, Sleeping Beauty, and Snow White with charming full-color illustrations for young dreamers.',
        'cover_image': '/static/img/covers/cinderella.svg',
        'original_retail_price': 420.00
    },
    '9789695840352': {
        'isbn': '9789695840352',
        'title': 'Bachon Ki Kahaniyan — Sheikhi Khor Hans aur Dilchasp Kahaniyan',
        'author': 'Sufi Ghulam Mustafa Tabassum',
        'publisher': 'Ferozsons, Lahore',
        'edition': 'Classic Edition',
        'category': 'Story Books',
        'education_board': 'General / None',
        'grade_class': 'Primary & Middle (Class 1-8)',
        'target_age_group': 'kids',
        'subject': 'Urdu Children Stories',
        'description': 'Delightful Urdu poems and moral story book for young kids by renowned poet Sufi Tabassum. Features Tot Batot tales, animals, humor, and moral lessons.',
        'cover_image': '/static/img/covers/sheikh_chilli.svg',
        'original_retail_price': 350.00
    },
    '9789695840369': {
        'isbn': '9789695840369',
        'title': 'Alif Laila: Illustrated Stories for Children',
        'author': 'Classic Arabian Nights (Children Illustrated Edition)',
        'publisher': 'Majlis Taraqqi-e-Adab, Lahore',
        'edition': 'Children Illustrated Edition',
        'category': 'Story Books',
        'education_board': 'General / None',
        'grade_class': 'Primary & Middle (Class 1-8)',
        'target_age_group': 'kids',
        'subject': 'Classic Fairy Tales',
        'description': 'Selected classic Arabian Nights tales adapted in simple, entertaining Urdu for young readers. Includes Sindbad the Sailor, Aladdin, and Ali Baba.',
        'cover_image': '/static/img/covers/alif_laila.svg',
        'original_retail_price': 420.00
    },
    '9789695840376': {
        'isbn': '9789695840376',
        'title': "Aesop's Fables Illustrated for Young Readers",
        'author': 'Aesop (Children Illustrated Edition)',
        'publisher': 'National Book Foundation / Oxford',
        'edition': 'Illustrated Edition',
        'category': 'Story Books',
        'education_board': 'General / None',
        'grade_class': 'Primary & Middle (Class 1-8)',
        'target_age_group': 'kids',
        'subject': 'Fables & Character Building',
        'description': 'Ancient animal fables teaching wisdom, leadership, friendship, and moral virtues. Engaging illustrations on every page suitable for age 5-12.',
        'cover_image': '/static/img/covers/aesop_fables.svg',
        'original_retail_price': 450.00
    },
    # --- FICTION & NOVELS ---
    '9789694370057': {
        'isbn': '9789694370057',
        'title': 'Jannat Ke Pattay (جنت کے پتے)',
        'author': 'Nimra Ahmed (نمرہ احمد)',
        'publisher': 'Ilm-o-Irfan Publishers, Lahore',
        'edition': 'Collector Edition',
        'category': 'Novels',
        'education_board': 'General / None',
        'grade_class': 'General Reading',
        'target_age_group': 'young_adult',
        'subject': 'Urdu Suspense & Romance',
        'description': 'Sensational Urdu novel following Haya Suleman\'s life journey to Turkey, espionage, resilience, faith, and personal transformation. Highly acclaimed across Pakistan.',
        'cover_image': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 980.00
    },
    '9780061122415': {
        'isbn': '9780061122415',
        'title': 'The Alchemist (International Bestseller)',
        'author': 'Paulo Coelho',
        'publisher': 'HarperOne',
        'edition': '25th Anniversary Edition',
        'category': 'Fiction',
        'education_board': 'General / None',
        'grade_class': 'General Reading',
        'target_age_group': 'young_adult',
        'subject': 'Philosophical Fiction',
        'description': 'The magical story of Santiago, an Andalusian shepherd boy who yearns to travel in search of a worldly treasure. An inspiring tale about listening to our hearts.',
        'cover_image': 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 850.00
    },
    # --- HISTORY & LITERATURE ---
    '9789693501001': {
        'isbn': '9789693501001',
        'title': 'A Short History of Pakistan',
        'author': 'Dr. I.H. Qureshi',
        'publisher': 'University of Karachi Press',
        'edition': 'Academic Edition',
        'category': 'History',
        'education_board': 'Higher Education / University',
        'grade_class': 'Bachelor / BS / Undergrad',
        'target_age_group': 'general',
        'subject': 'Pakistan History',
        'description': 'Authoritative academic history of the Indian subcontinent and Pakistan movement by University of Karachi former Vice-Chancellor. Standard university curriculum reference.',
        'cover_image': 'https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 950.00
    },
    '9789693501018': {
        'isbn': '9789693501018',
        'title': 'Tareekh-e-Pakistan (History of Pakistan 1947–Present)',
        'author': 'Dr. K.K. Aziz',
        'publisher': 'Sang-e-Meel Publications, Lahore',
        'edition': 'Expanded Edition',
        'category': 'History',
        'education_board': 'General / None',
        'grade_class': 'General Reading',
        'target_age_group': 'general',
        'subject': 'Political History',
        'description': 'In-depth historical documentation of constitutional developments, political movements, foreign policy, and leadership in Pakistan from 1947 to contemporary times.',
        'cover_image': 'https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 1100.00
    },
    '9789693501025': {
        'isbn': '9789693501025',
        'title': 'Kulliyat-e-Iqbal (کلیات اقبال: بانگ درا، بال جبریل، ضرب کلیم)',
        'author': 'Allama Muhammad Iqbal (علامہ اقبال)',
        'publisher': 'Iqbal Academy Pakistan, Lahore',
        'edition': 'Authentic Hardcover Edition',
        'category': 'History',
        'education_board': 'General / None',
        'grade_class': 'General Reading',
        'target_age_group': 'general',
        'subject': 'Urdu Poetry & Philosophy',
        'description': 'Complete Urdu poetic works of the national poet Allama Muhammad Iqbal with authentic footnotes, philosophical commentary, and poetic glossary.',
        'cover_image': 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 1250.00
    },
    '9789693501032': {
        'isbn': '9789693501032',
        'title': 'Shahab Nama (شہاب نامہ)',
        'author': 'Qudrat Ullah Shahab',
        'publisher': 'Sang-e-Meel Publications, Lahore',
        'edition': 'Hardbound Edition',
        'category': 'History',
        'education_board': 'General / None',
        'grade_class': 'General Reading',
        'target_age_group': 'general',
        'subject': 'Autobiography & History',
        'description': 'Iconic autobiography and civil service insider account of Pakistan\'s formative decades from 1947 through the 1960s. Extraordinary historical and personal narrative.',
        'cover_image': 'https://images.unsplash.com/photo-1476275466078-4007374efbbe?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 1300.00
    },
    # --- BALOCHISTAN HISTORY & REGIONAL BOOKS ---
    '9789694073514': {
        'isbn': '9789694073514',
        'title': 'The History of Balochistan',
        'author': 'Muhammad Sardar Khan Baluch',
        'publisher': 'Nisa Traders / Baluchi Academy, Quetta',
        'edition': 'Comprehensive Historical Edition',
        'category': 'History',
        'education_board': 'Balochistan Board',
        'grade_class': 'Intermediate / Bachelor',
        'target_age_group': 'general',
        'subject': 'Balochistan History & Regional Heritage',
        'description': 'Comprehensive historical chronicle covering the origins, tribal lineage, culture, medieval treaties, and modern history of Balochistan by eminent historian Muhammad Sardar Khan Baluch.',
        'cover_image': '/static/img/covers/history_balochistan.svg',
        'original_retail_price': 1400.00
    },
    '9789694073521': {
        'isbn': '9789694073521',
        'title': 'Tareekh-e-Balochistan (تاریخِ بلوچستان)',
        'author': 'Mir Gul Khan Naseer (میر گل خان نصیر)',
        'publisher': 'Balochi Academy / Kalat Publishers, Quetta',
        'edition': '2-Volume Complete Classic Edition',
        'category': 'History',
        'education_board': 'General / None',
        'grade_class': 'General Reading',
        'target_age_group': 'general',
        'subject': 'Balochistan History & Urdu Literature',
        'description': 'The definitive historical reference on Balochistan in Urdu by celebrated national poet and historian Mir Gul Khan Naseer. Documents archaeological records, khanates of Kalat, and socio-political history.',
        'cover_image': 'https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 1250.00
    },
    '9789694073538': {
        'isbn': '9789694073538',
        'title': 'Balochistan: Cultural Heritage & Ancient Civilization (Mehrgarh)',
        'author': 'Archaeological Research Group (Balochistan Heritage)',
        'publisher': 'Department of Archaeology & Museums, Balochistan',
        'edition': 'Illustrated Heritage Edition',
        'category': 'History',
        'education_board': 'Higher Education / University',
        'grade_class': 'General Reading',
        'target_age_group': 'general',
        'subject': 'Archaeology, Mehrgarh Civilization & Antiquities',
        'description': 'In-depth academic survey of the Neolithic Mehrgarh civilization (7000 BCE–2500 BCE) on the Kachi plain of Balochistan. Covers early pottery, agriculture, and prehistoric civilizational evolution.',
        'cover_image': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 1500.00
    },
    '9789694073545': {
        'isbn': '9789694073545',
        'title': 'Balochistan Board Class 10 Pakistan Studies & History',
        'author': 'Balochistan Textbook Board (BTBB), Quetta',
        'publisher': 'Balochistan Textbook Board (BTBB), Quetta',
        'edition': 'Single National Curriculum Edition',
        'category': 'Punjab Textbooks (Primary to FSc)',
        'education_board': 'Balochistan Board',
        'grade_class': 'Matric (9th - 10th)',
        'target_age_group': 'teens',
        'subject': 'Pakistan Studies & Regional History',
        'description': 'Official Class 10 Pakistan Studies textbook approved by Balochistan Textbook Board (BTBB) Quetta for Matric SSC examinations. Covers ideology of Pakistan, history, constitution, and geography.',
        'cover_image': 'https://images.unsplash.com/photo-1532012164546-f432f2e3777f?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 280.00
    },

    # ========================================================
    # 📚 PUNJAB BOARD (PCTB)
    # ========================================================
    '9789695840307': {
        'isbn': '9789695840307',
        'title': 'Punjab Board Physics Class 11 (FSc Part-1)',
        'author': 'Punjab Curriculum and Textbook Board (PCTB)',
        'publisher': 'PCTB Lahore',
        'edition': '2024 Revised Edition',
        'category': 'Punjab Textbooks (Primary to FSc)',
        'education_board': 'Punjab Board',
        'grade_class': 'Intermediate / FSc / ICS (11th - 12th)',
        'target_age_group': 'teens',
        'subject': 'Physics',
        'description': 'Official Physics textbook for Intermediate Part-1 (Class 11) approved by Punjab Textbook Board. Covers measurement, vectors, equilibrium, motion and force, work and energy, circular motion, oscillations, waves, physical optics, and thermodynamics.',
        'cover_image': 'https://images.unsplash.com/photo-1632571401005-458e9d244591?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 280.00
    },
    '9789695840314': {
        'isbn': '9789695840314',
        'title': 'Punjab Board Chemistry Class 12 (FSc Part-2)',
        'author': 'Punjab Curriculum and Textbook Board (PCTB)',
        'publisher': 'PCTB Lahore',
        'edition': '2024 Syllabus Edition',
        'category': 'Punjab Textbooks (Primary to FSc)',
        'education_board': 'Punjab Board',
        'grade_class': 'Intermediate / FSc / ICS (11th - 12th)',
        'target_age_group': 'teens',
        'subject': 'Chemistry',
        'description': 'Official Chemistry textbook for Intermediate Part-2 (Class 12) students by PCTB Lahore. Covers periodic classification of elements, s-block and p-block elements, transition metals, organic chemistry, hydrocarbons, macromolecules, and environmental chemistry.',
        'cover_image': 'https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 310.00
    },
    '9789695840321': {
        'isbn': '9789695840321',
        'title': 'Punjab Board Mathematics Class 10 (Science Group)',
        'author': 'Punjab Curriculum and Textbook Board (PCTB)',
        'publisher': 'PCTB Lahore',
        'edition': '2024 Edition',
        'category': 'Punjab Textbooks (Primary to FSc)',
        'education_board': 'Punjab Board',
        'grade_class': 'Matric (9th - 10th)',
        'target_age_group': 'teens',
        'subject': 'Mathematics',
        'description': 'Official Class 10 Mathematics textbook for Matric science students in Punjab. Includes quadratic equations, theory of quadratic equations, variations, partial fractions, sets and functions, basic statistics, trigonometry, circle geometry, and practical geometry.',
        'cover_image': 'https://images.unsplash.com/photo-1596495578065-6e0763fa1178?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 290.00
    },
    '9789695840338': {
        'isbn': '9789695840338',
        'title': 'Punjab Board English Class 12 (Modern Prose & Poems)',
        'author': 'Punjab Curriculum and Textbook Board (PCTB)',
        'publisher': 'PCTB Lahore',
        'edition': 'Single National Curriculum',
        'category': 'Punjab Textbooks (Primary to FSc)',
        'education_board': 'Punjab Board',
        'grade_class': 'Intermediate / FSc / ICS (11th - 12th)',
        'target_age_group': 'teens',
        'subject': 'English',
        'description': 'Official English textbook for Class 12 FSc/ICS/FA students across Punjab colleges. Contains modern prose essays, heroes biographies (Mustafa Kamal, Alexander Fleming, Louis Pasteur), and Goodbye Mr. Chips novel study.',
        'cover_image': 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 240.00
    },

    # ========================================================
    # 🏛️ FEDERAL BOARD (FBISE)
    # ========================================================
    '9789698760012': {
        'isbn': '9789698760012',
        'title': 'FBISE Physics Class 11 (HSSC-I Federal Board)',
        'author': 'National Book Foundation (NBF) Islamabad',
        'publisher': 'National Book Foundation (FBISE Curriculum)',
        'edition': 'Federal Curriculum 2024',
        'category': 'FSc / Matric / O & A Level',
        'education_board': 'Federal Board',
        'grade_class': 'Intermediate / FSc / ICS (11th - 12th)',
        'target_age_group': 'teens',
        'subject': 'Physics',
        'description': 'Official textbook published by the National Book Foundation (NBF) as the Federal Textbook Board for HSSC-I Physics under FBISE Islamabad. Conceptual approach to classical mechanics, wave optics, and thermal physics.',
        'cover_image': 'https://images.unsplash.com/photo-1632571401005-458e9d244591?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 380.00
    },
    '9789698760029': {
        'isbn': '9789698760029',
        'title': 'Computer Science Class 10 (SSC-II Federal Board)',
        'author': 'National Book Foundation Islamabad',
        'publisher': 'NBF Islamabad',
        'edition': '2024 Edition',
        'category': 'Computer Science & IT',
        'education_board': 'Federal Board',
        'grade_class': 'Matric (9th - 10th)',
        'target_age_group': 'teens',
        'subject': 'Computer Science',
        'description': 'Prescribed textbook by the Federal Board of Intermediate and Secondary Education (FBISE) for SSC-II Computer Science. Comprehensive coverage of problem solving, C language programming, control structures, and loops.',
        'cover_image': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 340.00
    },
    '9789698760036': {
        'isbn': '9789698760036',
        'title': 'Pakistan Studies Class 12 (HSSC-II Federal Board)',
        'author': 'National Book Foundation Islamabad',
        'publisher': 'NBF Islamabad',
        'edition': '2023-24 Revised Edition',
        'category': 'History',
        'education_board': 'Federal Board',
        'grade_class': 'Intermediate / FSc / ICS (11th - 12th)',
        'target_age_group': 'teens',
        'subject': 'Pakistan Studies',
        'description': 'Official textbook for FBISE HSSC-II Pakistan Studies. Explores the Pakistan Movement, political history, geographical significance, foreign policy, and socio-economic challenges.',
        'cover_image': 'https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 290.00
    },
    '9789698760043': {
        'isbn': '9789698760043',
        'title': 'Urdu Lazmi Class 11 (Sarmaya-e-Urdu HSSC-I FBISE)',
        'author': 'National Book Foundation Islamabad',
        'publisher': 'NBF Islamabad',
        'edition': 'National Foundation Edition',
        'category': 'Urdu Literature & Novels',
        'education_board': 'Federal Board',
        'grade_class': 'Intermediate / FSc / ICS (11th - 12th)',
        'target_age_group': 'teens',
        'subject': 'Urdu',
        'description': 'Prescribed textbook of Urdu compulsory for Class 11 FBISE students. Features prose selections, classic ghazals, modern nazms, grammar, letter writing, and literary comprehension.',
        'cover_image': 'https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 310.00
    },
    '9789698760050': {
        'isbn': '9789698760050',
        'title': 'Islamiyat Lazmi Class 9 (SSC Part-1 Federal Board)',
        'author': 'National Book Foundation Islamabad',
        'publisher': 'NBF Islamabad',
        'edition': 'Single National Curriculum',
        'category': 'Islamic Studies',
        'education_board': 'Federal Board',
        'grade_class': 'Matric (9th - 10th)',
        'target_age_group': 'teens',
        'subject': 'Islamic Studies',
        'description': 'Official Islamiyat Lazmi textbook for Grade 9 under the Federal Board curriculum. Includes Quranic Surahs translation, Hadith selections, Seerat-un-Nabi (PBUH), and ethics.',
        'cover_image': 'https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 250.00
    },

    # ========================================================
    # 🌊 SINDH BOARD (BSEK / BIEK Karachi)
    # ========================================================
    '9789694400013': {
        'isbn': '9789694400013',
        'title': 'Sindh Board Physics Class 11 (Intermediate Part-I)',
        'author': 'Sindh Textbook Board (STBB) Jamshoro',
        'publisher': 'STBB Jamshoro / Karachi',
        'edition': 'Curriculum 2024',
        'category': 'FSc / Matric / O & A Level',
        'education_board': 'Sindh Board',
        'grade_class': 'Intermediate / FSc / ICS (11th - 12th)',
        'target_age_group': 'teens',
        'subject': 'Physics',
        'description': 'Official textbook by the Sindh Textbook Board Jamshoro for Class 11 Pre-Engineering and Pre-Medical students in Karachi, Hyderabad, and Sukkur boards. Complete physics syllabus.',
        'cover_image': 'https://images.unsplash.com/photo-1632571401005-458e9d244591?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 320.00
    },
    '9789694400020': {
        'isbn': '9789694400020',
        'title': 'Sindh Board Chemistry Class 9 (Secondary Stage Science)',
        'author': 'Sindh Textbook Board (STBB) Jamshoro',
        'publisher': 'STBB Jamshoro',
        'edition': '2024 Revised Edition',
        'category': 'FSc / Matric / O & A Level',
        'education_board': 'Sindh Board',
        'grade_class': 'Matric (9th - 10th)',
        'target_age_group': 'teens',
        'subject': 'Chemistry',
        'description': 'Sindh Board syllabus book for Grade 9 Chemistry. Fundamentals of chemistry, atomic structure, periodic table, chemical bonding, physical states of matter, and electrochemistry.',
        'cover_image': 'https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 270.00
    },
    '9789694400037': {
        'isbn': '9789694400037',
        'title': 'Sindh Board Biology Class 10 (Secondary Stage Science Group)',
        'author': 'Sindh Textbook Board (STBB) Jamshoro',
        'publisher': 'STBB Jamshoro',
        'edition': 'Modern Stage Edition',
        'category': 'FSc / Matric / O & A Level',
        'education_board': 'Sindh Board',
        'grade_class': 'Matric (9th - 10th)',
        'target_age_group': 'teens',
        'subject': 'Biology',
        'description': 'Official Class 10 Biology book for BSEK Karachi matric students. Covers gaseous exchange, homeostasis, coordination and control, support and movement, reproduction, and genetics.',
        'cover_image': 'https://images.unsplash.com/photo-1530210124550-912dc1381cb8?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 290.00
    },
    '9789694400044': {
        'isbn': '9789694400044',
        'title': 'Sindh Board Mathematics Class 12 (Higher Secondary Part-II)',
        'author': 'Sindh Textbook Board (STBB) Jamshoro',
        'publisher': 'STBB Jamshoro',
        'edition': '2024 Edition',
        'category': 'FSc / Matric / O & A Level',
        'education_board': 'Sindh Board',
        'grade_class': 'Intermediate / FSc / ICS (11th - 12th)',
        'target_age_group': 'teens',
        'subject': 'Mathematics',
        'description': 'Prescribed textbook of Mathematics for Class 12 Intermediate science group across all boards in Sindh. Covers analytic geometry, differentiation, integration, conic sections, and vectors.',
        'cover_image': 'https://images.unsplash.com/photo-1596495578065-6e0763fa1178?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 350.00
    },
    '9789694400051': {
        'isbn': '9789694400051',
        'title': 'Sindh Board English Compulsory Class 11 (Intermediate Prose)',
        'author': 'Sindh Textbook Board (STBB) Jamshoro',
        'publisher': 'STBB Jamshoro',
        'edition': '2023-24 Edition',
        'category': 'FSc / Matric / O & A Level',
        'education_board': 'Sindh Board',
        'grade_class': 'Intermediate / FSc / ICS (11th - 12th)',
        'target_age_group': 'teens',
        'subject': 'English',
        'description': 'Standard English textbook for First Year Intermediate students in Sindh. Contains inspiring prose, poetry selections, grammatical foundations, and composition exercises.',
        'cover_image': 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 260.00
    },

    # ========================================================
    # 🏔️ KPK BOARD (BISE Peshawar / Abbottabad)
    # ========================================================
    '9789694500010': {
        'isbn': '9789694500010',
        'title': 'KPK Board Biology Class 11 (HSSC Part-1 Pre-Medical)',
        'author': 'Khyber Pakhtunkhwa Textbook Board (KPTBB) Peshawar',
        'publisher': 'KPTBB Peshawar',
        'edition': '2024 Syllabus',
        'category': 'FSc / Matric / O & A Level',
        'education_board': 'KPK Board',
        'grade_class': 'Intermediate / FSc / ICS (11th - 12th)',
        'target_age_group': 'teens',
        'subject': 'Biology',
        'description': 'Official Biology textbook by the Khyber Pakhtunkhwa Textbook Board Peshawar for FSc Pre-Medical students. Biological molecules, enzymes, cell structure, kingdom plantae, and animalia.',
        'cover_image': 'https://images.unsplash.com/photo-1530210124550-912dc1381cb8?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 340.00
    },
    '9789694500027': {
        'isbn': '9789694500027',
        'title': 'KPK Board Chemistry Class 12 (HSSC Part-2 Science)',
        'author': 'Khyber Pakhtunkhwa Textbook Board (KPTBB) Peshawar',
        'publisher': 'KPTBB Peshawar',
        'edition': '2024 Edition',
        'category': 'FSc / Matric / O & A Level',
        'education_board': 'KPK Board',
        'grade_class': 'Intermediate / FSc / ICS (11th - 12th)',
        'target_age_group': 'teens',
        'subject': 'Chemistry',
        'description': 'Prescribed Chemistry textbook for Class 12 students in Khyber Pakhtunkhwa. In-depth inorganic chemistry, modern reaction mechanisms in organic chemistry, and industrial biochemistry.',
        'cover_image': 'https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 370.00
    },
    '9789694500034': {
        'isbn': '9789694500034',
        'title': 'KPK Board Physics Class 9 (SSC Part-1 Science Group)',
        'author': 'Khyber Pakhtunkhwa Textbook Board (KPTBB) Peshawar',
        'publisher': 'KPTBB Peshawar',
        'edition': 'Single National Curriculum',
        'category': 'FSc / Matric / O & A Level',
        'education_board': 'KPK Board',
        'grade_class': 'Matric (9th - 10th)',
        'target_age_group': 'teens',
        'subject': 'Physics',
        'description': 'Official Class 9 Physics textbook for Matric students under KPK education boards. Covers physical quantities, kinematics, dynamics, turning effect of forces, gravitation, and properties of matter.',
        'cover_image': 'https://images.unsplash.com/photo-1632571401005-458e9d244591?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 270.00
    },
    '9789694500041': {
        'isbn': '9789694500041',
        'title': 'KPK Board Mathematics Class 10 (SSC Part-2 Science Group)',
        'author': 'Khyber Pakhtunkhwa Textbook Board (KPTBB) Peshawar',
        'publisher': 'KPTBB Peshawar',
        'edition': '2024 Edition',
        'category': 'FSc / Matric / O & A Level',
        'education_board': 'KPK Board',
        'grade_class': 'Matric (9th - 10th)',
        'target_age_group': 'teens',
        'subject': 'Mathematics',
        'description': 'Standard Grade 10 Mathematics textbook by KPTBB. Clear conceptual explanations of quadratic equations, partial fractions, coordinate geometry, trigonometry, and circle theorems.',
        'cover_image': 'https://images.unsplash.com/photo-1596495578065-6e0763fa1178?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 310.00
    },
    '9789694500058': {
        'isbn': '9789694500058',
        'title': 'KPK Board Computer Science Class 11 (HSSC-I ICS Group)',
        'author': 'Khyber Pakhtunkhwa Textbook Board (KPTBB) Peshawar',
        'publisher': 'KPTBB Peshawar',
        'edition': '2023-24 Edition',
        'category': 'Computer Science & IT',
        'education_board': 'KPK Board',
        'grade_class': 'Intermediate / FSc / ICS (11th - 12th)',
        'target_age_group': 'teens',
        'subject': 'Computer Science',
        'description': 'First year computer science textbook for ICS students in KPK. Fundamentals of information technology, computer architectures, system software, networking, and security concepts.',
        'cover_image': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 330.00
    },

    # ========================================================
    # 🌾 BALOCHISTAN BOARD (BISE Quetta)
    # ========================================================
    '9789694600017': {
        'isbn': '9789694600017',
        'title': 'Balochistan Board General Science Class 8 (Middle Stage)',
        'author': 'Balochistan Textbook Board (BTBB) Quetta',
        'publisher': 'BTBB Quetta',
        'edition': 'Single National Curriculum',
        'category': 'FSc / Matric / O & A Level',
        'education_board': 'Balochistan Board',
        'grade_class': 'Primary & Middle (Class 1-8)',
        'target_age_group': 'kids',
        'subject': 'General Science',
        'description': 'Official Grade 8 General Science textbook by the Balochistan Textbook Board Quetta. Human body systems, heredity, biotechnology basics, chemical reactions, and environmental science.',
        'cover_image': 'https://images.unsplash.com/photo-1507668077129-56e32842fceb?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 230.00
    },
    '9789694600024': {
        'isbn': '9789694600024',
        'title': 'Balochistan Board Physics Class 11 (HSSC-I Science)',
        'author': 'Balochistan Textbook Board (BTBB) Quetta',
        'publisher': 'BTBB Quetta',
        'edition': '2024 Edition',
        'category': 'FSc / Matric / O & A Level',
        'education_board': 'Balochistan Board',
        'grade_class': 'Intermediate / FSc / ICS (11th - 12th)',
        'target_age_group': 'teens',
        'subject': 'Physics',
        'description': 'Prescribed textbook of Physics for Class 11 students across Balochistan. Fully aligned with the national curriculum and BISE Quetta intermediate board examinations.',
        'cover_image': 'https://images.unsplash.com/photo-1632571401005-458e9d244591?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 330.00
    },
    '9789694600031': {
        'isbn': '9789694600031',
        'title': 'Balochistan Board Chemistry Class 10 (SSC Part-2 Science)',
        'author': 'Balochistan Textbook Board (BTBB) Quetta',
        'publisher': 'BTBB Quetta',
        'edition': '2024 Edition',
        'category': 'FSc / Matric / O & A Level',
        'education_board': 'Balochistan Board',
        'grade_class': 'Matric (9th - 10th)',
        'target_age_group': 'teens',
        'subject': 'Chemistry',
        'description': 'Official Grade 10 Chemistry textbook by BTBB Quetta. Covers chemical equilibrium, acids, bases and salts, organic chemistry, hydrocarbons, biochemistry, atmosphere, and water.',
        'cover_image': 'https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 290.00
    },
    '9789694600048': {
        'isbn': '9789694600048',
        'title': 'Balochistan Board Pakistan Studies Class 12 (HSSC-II)',
        'author': 'Balochistan Textbook Board (BTBB) Quetta',
        'publisher': 'BTBB Quetta',
        'edition': '2023-24 Revised Edition',
        'category': 'History',
        'education_board': 'Balochistan Board',
        'grade_class': 'Intermediate / FSc / ICS (11th - 12th)',
        'target_age_group': 'teens',
        'subject': 'Pakistan Studies',
        'description': 'Comprehensive textbook for Intermediate Part-2 students in Balochistan. Covers historical perspective of Pakistan, the constitution, national economy, and regional development in Balochistan.',
        'cover_image': 'https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 240.00
    },
    '9789694600055': {
        'isbn': '9789694600055',
        'title': 'Balochistan Board Mathematics Class 9 (SSC Part-1 Science)',
        'author': 'Balochistan Textbook Board (BTBB) Quetta',
        'publisher': 'BTBB Quetta',
        'edition': 'Single National Curriculum',
        'category': 'FSc / Matric / O & A Level',
        'education_board': 'Balochistan Board',
        'grade_class': 'Matric (9th - 10th)',
        'target_age_group': 'teens',
        'subject': 'Mathematics',
        'description': 'Official Class 9 Mathematics textbook by BTBB Quetta for secondary schools. Covers real and complex numbers, logarithms, algebraic expressions, linear equations, and geometric congruence.',
        'cover_image': 'https://images.unsplash.com/photo-1596495578065-6e0763fa1178?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 280.00
    },

    # ========================================================
    # 🎓 CAMBRIDGE (O/A Levels)
    # ========================================================
    '9780199407408': {
        'isbn': '9780199407408',
        'title': 'Cambridge O-Level Mathematics (Syllabus D) Book 4 (7th Edition)',
        'author': 'Dr. Joseph Yeo, Teh Keng Seng, Loh Cheng Yee',
        'publisher': 'Oxford University Press / Cambridge',
        'edition': '7th Edition',
        'category': 'FSc / Matric / O & A Level',
        'education_board': 'Cambridge',
        'grade_class': 'Matric (9th - 10th)',
        'target_age_group': 'teens',
        'subject': 'Mathematics (Syllabus D)',
        'description': 'The most popular textbook for Cambridge O-Level Mathematics Syllabus D (4024). Thoroughly covers vector geometry, probability, statistics, matrices, transformation geometry, and trigonometry.',
        'cover_image': 'https://images.unsplash.com/photo-1596495578065-6e0763fa1178?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 2200.00
    },
    '9781108847063': {
        'isbn': '9781108847063',
        'title': 'Cambridge International AS & A Level Economics Coursebook',
        'author': 'Colin Bamford, Susan Grant',
        'publisher': 'Cambridge University Press',
        'edition': '4th Edition',
        'category': 'Business, Commerce & BBA',
        'education_board': 'Cambridge',
        'grade_class': 'Intermediate / FSc / ICS (11th - 12th)',
        'target_age_group': 'teens',
        'subject': 'Economics (9708)',
        'description': 'Endorsed by Cambridge Assessment International Education for full syllabus coverage (9708). In-depth explanations of microeconomics, market failure, macroeconomic policies, international trade, and development economics.',
        'cover_image': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 2800.00
    },
    '9781108436991': {
        'isbn': '9781108436991',
        'title': 'Cambridge O Level Physics Coursebook (5054)',
        'author': 'David Sang, Graham Jones',
        'publisher': 'Cambridge University Press',
        'edition': '3rd Edition',
        'category': 'FSc / Matric / O & A Level',
        'education_board': 'Cambridge',
        'grade_class': 'Matric (9th - 10th)',
        'target_age_group': 'teens',
        'subject': 'Physics (5054)',
        'description': 'Comprehensive coursebook tailored for Cambridge O Level Physics 5054 examinations. Features experimental investigations, mathematical skill-builders, and past paper practice questions.',
        'cover_image': 'https://images.unsplash.com/photo-1632571401005-458e9d244591?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 2500.00
    },
    '9781108951609': {
        'isbn': '9781108951609',
        'title': 'Cambridge IGCSE & O Level Chemistry Coursebook',
        'author': 'Richard Harwood, Ian Lodge',
        'publisher': 'Cambridge University Press',
        'edition': '5th Edition',
        'category': 'FSc / Matric / O & A Level',
        'education_board': 'Cambridge',
        'grade_class': 'Matric (9th - 10th)',
        'target_age_group': 'teens',
        'subject': 'Chemistry (0620 / 5070)',
        'description': 'Renowned Cambridge coursebook for IGCSE and O-Level Chemistry. Covers chemical energetics, rates of reaction, organic chemistry, qualitative analysis, and stoichiometric calculations.',
        'cover_image': 'https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 2400.00
    },
    '9781108740524': {
        'isbn': '9781108740524',
        'title': 'Cambridge International AS & A Level Accounting Coursebook',
        'author': 'Harold Randall, David Hopkins',
        'publisher': 'Cambridge University Press',
        'edition': '3rd Edition',
        'category': 'Business, Commerce & BBA',
        'education_board': 'Cambridge',
        'grade_class': 'Intermediate / FSc / ICS (11th - 12th)',
        'target_age_group': 'teens',
        'subject': 'Accounting (9706)',
        'description': 'Authoritative guide for Cambridge A Level Accounting (9706). Explains financial accounting, cost and management accounting, capital structure, budgeting, and ratio analysis.',
        'cover_image': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 2700.00
    },

    # ========================================================
    # 🧸 KIDS & STORY BOOKS (Age 5-12)
    # ========================================================
    '9789695840413': {
        'isbn': '9789695840413',
        'title': 'Taleem-o-Tarbiyat: Moral Stories for Kids (Ferozsons)',
        'author': 'Ferozsons Children Editorial Board',
        'publisher': 'Ferozsons Lahore',
        'edition': 'Special Illustrated Gift Edition',
        'category': 'Story Books',
        'education_board': 'General / None',
        'grade_class': 'Primary & Middle (Class 1-8)',
        'target_age_group': 'kids',
        'subject': 'Urdu Children Literature & Morals',
        'description': 'Timeless moral stories from Pakistan\'s most beloved children\'s magazine Taleem-o-Tarbiyat. Includes illustrated tales promoting honesty, hard work, kindness to animals, and respect for elders.',
        'cover_image': '/static/img/covers/taleem_tarbiyat.svg',
        'original_retail_price': 350.00
    },
    '9789695840420': {
        'isbn': '9789695840420',
        'title': 'Sheikh Chilli ke Qissay (Classic Pakistani Folk Tales)',
        'author': 'Sufi Ghulam Mustafa Tabassum',
        'publisher': 'Ferozsons / Maqbool Books Lahore',
        'edition': 'Illustrated Color Edition',
        'category': 'Story Books',
        'education_board': 'General / None',
        'grade_class': 'Primary & Middle (Class 1-8)',
        'target_age_group': 'kids',
        'subject': 'Humorous Folk Tales for Young Readers',
        'description': 'Hilarious and witty traditional tales of Sheikh Chilli adapted for children. Full of lighthearted humor, foolish wisdom, and colorful full-page illustrations for ages 6-12.',
        'cover_image': '/static/img/covers/sheikh_chilli.svg',
        'original_retail_price': 320.00
    },
    '9789695840437': {
        'isbn': '9789695840437',
        'title': "Aesop's Fables Illustrated for Young Readers",
        'author': 'Aesop (Children Illustrated Edition)',
        'publisher': 'Oxford University Press / Ferozsons',
        'edition': 'Bilingual Illustrated Edition',
        'category': 'Story Books',
        'education_board': 'General / None',
        'grade_class': 'Primary & Middle (Class 1-8)',
        'target_age_group': 'kids',
        'subject': 'Bilingual Children Fables & Morals',
        'description': 'Famous fables including The Tortoise and the Hare, The Boy Who Cried Wolf, and The Lion and the Mouse presented with parallel Urdu and English text and vibrant illustrations.',
        'cover_image': '/static/img/covers/aesop_fables.svg',
        'original_retail_price': 450.00
    },
    '9789695840444': {
        'isbn': '9789695840444',
        'title': 'Alif Laila: Illustrated Stories for Children',
        'author': 'Classic Arabian Nights (Children Illustrated Edition)',
        'publisher': 'Maqbool Books / Ferozsons Lahore',
        'edition': 'Children Edition (4-Color)',
        'category': 'Story Books',
        'education_board': 'General / None',
        'grade_class': 'Primary & Middle (Class 1-8)',
        'target_age_group': 'kids',
        'subject': 'Eastern Classic Tales for Children',
        'description': 'Magical tales of Aladdin and the Magic Lamp, Ali Baba and Forty Thieves, and Sinbad the Sailor carefully rewritten in simple, engaging Urdu for kids aged 7 to 12.',
        'cover_image': '/static/img/covers/alif_laila.svg',
        'original_retail_price': 400.00
    },
    '9789695840451': {
        'isbn': '9789695840451',
        'title': 'Chalawa / Bachon Ki Kahaniyan by Ishtiaq Ahmed',
        'author': 'Ishtiaq Ahmed (اشتیاق احمد)',
        'publisher': 'Maktaba-e-Dastan / Atlantic Publishers',
        'edition': 'Classic Stories Collection',
        'category': 'Story Books',
        'education_board': 'General / None',
        'grade_class': 'Primary & Middle (Class 1-8)',
        'target_age_group': 'kids',
        'subject': 'Children Morals, Character & Adventure',
        'description': 'Inspiring moral stories by renowned children author Ishtiaq Ahmed. Teaches patriotism, honesty, empathy, courage, and Islamic manners through adventurous, fast-paced tales.',
        'cover_image': '/static/img/covers/chalawa.svg',
        'original_retail_price': 380.00
    },
    '9780141325309': {
        'isbn': '9780141325309',
        'title': 'Cinderella & Classic Fairy Tales',
        'author': 'Brothers Grimm & Charles Perrault',
        'publisher': 'Ladybird / Classic Children Books',
        'edition': 'Deluxe Illustrated Edition',
        'category': 'Story Books',
        'education_board': 'General / None',
        'grade_class': 'Primary & Middle (Class 1-8)',
        'target_age_group': 'kids',
        'subject': 'Enchanting Classic Fairy Tales',
        'description': 'Beloved timeless fairy tales including Cinderella, Sleeping Beauty, and Snow White with charming full-color illustrations for young dreamers.',
        'cover_image': '/static/img/covers/cinderella.svg',
        'original_retail_price': 420.00
    },
    '9789695840468': {
        'isbn': '9789695840468',
        'title': 'The Jungle Book (Illustrated Kids Edition)',
        'author': 'Rudyard Kipling',
        'publisher': 'Puffin Classics / Ferozsons Lahore',
        'edition': 'Deluxe Picture Book Edition',
        'category': 'Story Books',
        'education_board': 'General / None',
        'grade_class': 'Primary & Middle (Class 1-8)',
        'target_age_group': 'kids',
        'subject': 'Jungle Stories, Animal Kingdom & Nature',
        'description': 'Fun adventures of Mowgli, Baloo, Bagheera, and jungle animals. Educates children on wilderness, courage, and friendship.',
        'cover_image': '/static/img/covers/jungle_book.svg',
        'original_retail_price': 360.00
    },

    # ========================================================
    # 📖 FICTION & NOVELS
    # ========================================================
    '9789694370026': {
        'isbn': '9789694370026',
        'title': 'Jannat Kay Pattay (جنت کے پتے)',
        'author': 'Nemrah Ahmed (نمرہ احمد)',
        'publisher': 'Al-Quraish Publications, Lahore',
        'edition': 'Best Selling Edition',
        'category': 'Novels',
        'education_board': 'General / None',
        'grade_class': 'General Reading',
        'target_age_group': 'young_adult',
        'subject': 'Urdu Suspense, Mystery & Spiritual Romance',
        'description': 'A bestselling Pakistani mystery and romantic novel following Haya Suleman, a young law student who wins a scholarship to Turkey. Explores self-discovery, spiritual awakening, and cyber intrigue.',
        'cover_image': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 1100.00
    },
    '9789694370033': {
        'isbn': '9789694370033',
        'title': 'Raja Gidh (راجہ گدھ)',
        'author': 'Bano Qudsia (بانو قدسیہ)',
        'publisher': 'Sang-e-Meel Publications, Lahore',
        'edition': 'Literary Masterpiece Edition',
        'category': 'Novels',
        'education_board': 'General / None',
        'grade_class': 'General Reading',
        'target_age_group': 'general',
        'subject': 'Urdu Psychological & Philosophical Fiction',
        'description': 'One of the most acclaimed modern Urdu psychological and sociological novels. Explores the metaphor of the vulture feeding on haram sustenance and its psychological impact on human destiny.',
        'cover_image': 'https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 950.00
    },
    '9781594631931': {
        'isbn': '9781594631931',
        'title': 'The Kite Runner',
        'author': 'Khaled Hosseini',
        'publisher': 'Riverhead Books / Bloomsbury',
        'edition': 'International Bestseller Edition',
        'category': 'Fiction',
        'education_board': 'General / None',
        'grade_class': 'General Reading',
        'target_age_group': 'general',
        'subject': 'Contemporary South Asian & World Fiction',
        'description': 'An unforgettable, heartbreaking story of the unlikely friendship between a wealthy boy and the son of his father\'s servant, caught in the tragic sweep of history.',
        'cover_image': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 1200.00
    },
    '9780143118527': {
        'isbn': '9780143118527',
        'title': 'The Forty Rules of Love: A Novel of Rumi',
        'author': 'Elif Shafak',
        'publisher': 'Penguin Books',
        'edition': 'Paperback Bestseller Edition',
        'category': 'Fiction',
        'education_board': 'General / None',
        'grade_class': 'General Reading',
        'target_age_group': 'general',
        'subject': 'Historical Fiction, Sufism & Spirituality',
        'description': 'In this lyrical, exuberant follow-up to her 2007 novel The Bastard of Istanbul, acclaimed Turkish author Elif Shafak unfolds two tantalizing parallel narratives—one contemporary and the other set in the thirteenth century.',
        'cover_image': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 1350.00
    },
    '9789694370040': {
        'isbn': '9789694370040',
        'title': 'Aab-e-Hayat (آب حیات)',
        'author': 'Umera Ahmed (عمیرہ احمد)',
        'publisher': 'Ilm-o-Irfan Publishers, Lahore',
        'edition': 'Official Sequel Edition',
        'category': 'Novels',
        'education_board': 'General / None',
        'grade_class': 'General Reading',
        'target_age_group': 'young_adult',
        'subject': 'Urdu Spiritual Fiction & Family Drama',
        'description': 'The highly anticipated sequel to Peer-e-Kamil. Continues the life journey of Salar Sikandar and Imama Ambreen as they navigate family responsibilities, wealth, and faith.',
        'cover_image': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 1250.00
    },

    # ========================================================
    # 🏛️ HISTORY & LITERATURE
    # ========================================================
    '9789693500011': {
        'isbn': '9789693500011',
        'title': 'Bang-e-Dra (بانگِ درا)',
        'author': 'Allama Muhammad Iqbal (علامہ محمد اقبال)',
        'publisher': 'Iqbal Academy Pakistan, Lahore',
        'edition': 'Standard Definitive Edition',
        'category': 'History',
        'education_board': 'General / None',
        'grade_class': 'General Reading',
        'target_age_group': 'general',
        'subject': 'Iqbaliyat, Philosophy & Classical Urdu Poetry',
        'description': 'The foundational Urdu poetic collection of the national poet Allama Muhammad Iqbal. Contains masterworks including Tarana-e-Milli, Khizr-e-Rah, and Talu-e-Islam.',
        'cover_image': 'https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 750.00
    },
    '9780195775419': {
        'isbn': '9780195775419',
        'title': 'Jinnah of Pakistan',
        'author': 'Stanley Wolpert',
        'publisher': 'Oxford University Press (OUP Pakistan)',
        'edition': 'Classic Biography Edition',
        'category': 'History',
        'education_board': 'Higher Education / University',
        'grade_class': 'Bachelor / BS / Undergrad',
        'target_age_group': 'general',
        'subject': 'Pakistan Movement & Quaid-e-Azam Biography',
        'description': 'The definitive biography of Quaid-e-Azam Muhammad Ali Jinnah by renowned American historian Stanley Wolpert. "Few individuals significantly alter the course of history. Fewer still modify the map of the world. Hardly anyone can be credited with creating a nation-state. Mohammad Ali Jinnah did all three."',
        'cover_image': 'https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 1600.00
    },
    '9789694370057': {
        'isbn': '9789694370057',
        'title': 'Shahab Nama (شہاب نامہ)',
        'author': 'Qudratullah Shahab (قدرت اللہ شہاب)',
        'publisher': 'Sang-e-Meel Publications, Lahore',
        'edition': 'Classic Hardcover Edition',
        'category': 'History',
        'education_board': 'General / None',
        'grade_class': 'General Reading',
        'target_age_group': 'general',
        'subject': 'Pakistani Civil Service, Bureaucracy & Memoir',
        'description': 'The monumentally famous autobiography of eminent civil servant and writer Qudratullah Shahab. An eyewitness insider account of Pakistan\'s early governance under Jinnah, Ghulam Muhammad, Iskander Mirza, and Ayub Khan.',
        'cover_image': 'https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 1400.00
    },
    '9789693500028': {
        'isbn': '9789693500028',
        'title': 'Tareekh-e-Pakistan: Qayam se Daur-e-Hazir Tak',
        'author': 'Prof. Muhammad Yahya Amjad',
        'publisher': 'Ilmi Kitab Khana, Lahore',
        'edition': 'Comprehensive Reference Edition',
        'category': 'History',
        'education_board': 'Higher Education / University',
        'grade_class': 'CSS / PMS / Entry Test',
        'target_age_group': 'general',
        'subject': 'Political & Constitutional History of Pakistan',
        'description': 'Comprehensive historical and constitutional analysis of Pakistan from the 1857 War of Independence through the Pakistan Movement to modern political developments. Essential for CSS and PMS candidates.',
        'cover_image': 'https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 1100.00
    },
    '9780674052895': {
        'isbn': '9780674052895',
        'title': 'The Struggle for Pakistan: A Muslim Homeland and Global Politics',
        'author': 'Dr. Ayesha Jalal',
        'publisher': 'Harvard University Press / Sang-e-Meel',
        'edition': 'Academic Edition',
        'category': 'History',
        'education_board': 'Higher Education / University',
        'grade_class': 'Bachelor / BS / Undergrad',
        'target_age_group': 'general',
        'subject': 'Political Science, Geopolitics & Foreign Relations',
        'description': 'Acclaimed historian Ayesha Jalal delivers a seminal study of Pakistan\'s national identity, military institutions, democratic movements, and geopolitical alliances.',
        'cover_image': 'https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 1850.00
    },

    # ========================================================
    # 🎓 UNIVERSITY / HIGHER ED (Medical, BBA, CSS)
    # ========================================================
    '9780323597128': {
        'isbn': '9780323597128',
        'title': 'Guyton and Hall Textbook of Medical Physiology (14th Ed.)',
        'author': 'John E. Hall, Michael E. Hall',
        'publisher': 'Elsevier / Saunders',
        'edition': '14th International Edition',
        'category': 'Medical & MBBS / BDS',
        'education_board': 'Higher Education / University',
        'grade_class': 'Bachelor / BS / Undergrad',
        'target_age_group': 'young_adult',
        'subject': 'Human Physiology & Medical Sciences',
        'description': 'The world\'s foremost medical physiology textbook, essential for MBBS and BDS students across King Edward Medical University, Dow, Nishtar, and Army Medical College.',
        'cover_image': 'https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 3400.00
    },
    '9781496345646': {
        'isbn': '9781496345646',
        'title': 'Snell\'s Clinical Anatomy by Regions',
        'author': 'Lawrence E. Wineski',
        'publisher': 'Wolters Kluwer / Lippincott Williams & Wilkins',
        'edition': '10th Edition',
        'category': 'Medical & MBBS / BDS',
        'education_board': 'Higher Education / University',
        'grade_class': 'Bachelor / BS / Undergrad',
        'target_age_group': 'young_adult',
        'subject': 'Clinical Gross Anatomy',
        'description': 'Fundamental regional clinical anatomy for 1st & 2nd year MBBS students with clinical problem-solving cases and dissection guides across Pakistani medical colleges.',
        'cover_image': 'https://images.unsplash.com/photo-1532938911079-1b06ac7ceec7?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 3200.00
    },
    '9780323353175': {
        'isbn': '9780323353175',
        'title': 'Robbins Basic Pathology (10th Ed.)',
        'author': 'Vinay Kumar, Abul K. Abbas, Jon C. Aster',
        'publisher': 'Elsevier',
        'edition': '10th Edition',
        'category': 'Medical & MBBS / BDS',
        'education_board': 'Higher Education / University',
        'grade_class': 'Bachelor / BS / Undergrad',
        'target_age_group': 'young_adult',
        'subject': 'General & Systemic Pathology',
        'description': 'The gold standard medical pathology textbook for 3rd and 4th year MBBS students, detailing cellular mechanisms of disease and clinical diagnostic pathology.',
        'cover_image': 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 3500.00
    },
    '9781260464948': {
        'isbn': '9781260464948',
        'title': 'Harper\'s Illustrated Biochemistry',
        'author': 'Peter J. Kennelly, Kathleen M. Botham, Anthony Weil',
        'publisher': 'McGraw-Hill Education',
        'edition': '32nd Edition',
        'category': 'Medical & MBBS / BDS',
        'education_board': 'Higher Education / University',
        'grade_class': 'Bachelor / BS / Undergrad',
        'target_age_group': 'young_adult',
        'subject': 'Medical Biochemistry & Metabolism',
        'description': 'Comprehensive medical biochemistry for MBBS & BDS students integrating molecular biology, clinical enzymology, bioenergetics, and metabolic disease pathways.',
        'cover_image': 'https://images.unsplash.com/photo-1530497610245-94d3c16cda28?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 2900.00
    },
    '9789388902731': {
        'isbn': '9789388902731',
        'title': 'BD Chaurasia\'s Human Anatomy (Vol 1–3 Set)',
        'author': 'B. D. Chaurasia',
        'publisher': 'CBS Publishers & Distributors',
        'edition': '8th Regional Edition',
        'category': 'Medical & MBBS / BDS',
        'education_board': 'Higher Education / University',
        'grade_class': 'Bachelor / BS / Undergrad',
        'target_age_group': 'young_adult',
        'subject': 'Human Gross Anatomy & Dissection',
        'description': 'Complete 3-volume clinical anatomy set (Upper Limb & Thorax, Lower Limb & Abdomen, Head & Neck) with dissection notes and clinical anatomy correlations.',
        'cover_image': 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 2800.00
    },
    '9789697920111': {
        'isbn': '9789697920111',
        'title': 'KIPS MDCAT Complete Prep & Practice Set',
        'author': 'KIPS Entry Test Faculty',
        'publisher': 'KIPS Publications, Lahore',
        'edition': '2024-2025 Edition',
        'category': 'Medical & MBBS / BDS',
        'education_board': 'Federal Board / PMDC MDCAT',
        'grade_class': 'Class 12 / HSSC-II / FSc Pre-Medical',
        'target_age_group': 'teens',
        'subject': 'MDCAT Entry Test Preparation',
        'description': 'Complete MDCAT preparation set covering Biology, Chemistry, Physics, and English past papers, conceptual practice questions, and PMDC mock examination tests.',
        'cover_image': 'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 2200.00
    },
    '9789332587700': {
        'isbn': '9789332587700',
        'title': 'Principles of Marketing (South Asian Edition)',
        'author': 'Philip Kotler, Gary Armstrong, Prof. Ehsan ul Haque',
        'publisher': 'Pearson Education / LUMS',
        'edition': '17th South Asian Edition',
        'category': 'Business, Commerce & BBA',
        'education_board': 'Higher Education / University',
        'grade_class': 'Bachelor / BS / Undergrad',
        'target_age_group': 'young_adult',
        'subject': 'Marketing Management & Business Strategy',
        'description': 'The gold standard marketing textbook for BBA and MBA programs at LUMS, IBA Karachi, NUST, and Punjab University. Features localized Pakistani case studies.',
        'cover_image': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 2200.00
    },
    '9789699640018': {
        'isbn': '9789699640018',
        'title': 'CSS Current Affairs & Pakistan Affairs Comprehensive Guide',
        'author': 'Jahangir World Times (JWT) Editorial Board',
        'publisher': 'Jahangir World Times Publications, Lahore',
        'edition': '2025 Annual CSS Edition',
        'category': 'CSS & Competitive Exams',
        'education_board': 'Higher Education / University',
        'grade_class': 'CSS / PMS / Entry Test',
        'target_age_group': 'young_adult',
        'subject': 'CSS Compulsory Subjects: Current & Pakistan Affairs',
        'description': 'Authoritative preparation manual for the Federal Public Service Commission (FPSC) CSS and provincial PMS competitive examinations. Covers economic reforms, CPEC, foreign policy, and climate governance.',
        'cover_image': 'https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 1500.00
    },

    # ========================================================
    # 🎁 FREE DONATION COMMUNITY COPIES
    # ========================================================
    '9789694370019': {
        'isbn': '9789694370019',
        'title': 'Peer-e-Kamil (Community Reading Copy - Free Giveaway)',
        'author': 'Umera Ahmed (عمیرہ احمد)',
        'publisher': 'Ilm-o-Irfan Publishers, Lahore',
        'edition': 'Community Circulating Edition',
        'category': 'Novels',
        'education_board': 'General / None',
        'grade_class': 'General Reading',
        'target_age_group': 'young_adult',
        'subject': 'Urdu Spiritual Fiction',
        'description': 'Free donated copy passed forward by a graduated university student to share with other avid readers. In clean readable condition. 100% free community giveaway.',
        'cover_image': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 950.00
    },
    '9789695840406': {
        'isbn': '9789695840406',
        'title': "Taleem-o-Tarbiyat Children's Stories (Free Donation for Kids)",
        'author': 'Ferozsons Children Writers Guild',
        'publisher': 'Ferozsons Lahore',
        'edition': 'Free Children Edition',
        'category': 'Story Books',
        'education_board': 'General / None',
        'grade_class': 'Primary & Middle (Class 1-8)',
        'target_age_group': 'kids',
        'subject': 'Moral Stories for Young Readers',
        'description': 'Free community donation copy of illustrated Urdu moral stories. Given away to encourage young children to read and develop positive character values.',
        'cover_image': 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 300.00
    }
}


def normalize_isbn(isbn_str):
    if not isbn_str:
        return ''
    cleaned = ''.join(c for c in str(isbn_str).strip() if c.isalnum())
    return cleaned


def lookup_book_by_isbn(isbn_str):
    """
    Search order:
    1. Local database
    2. Built-in known catalog
    3. Google Books API (online)
    4. Open Library API (online)
    5. Fallback stub
    """
    clean_isbn = normalize_isbn(isbn_str)
    if not clean_isbn:
        return None, False

    # 1. Local Database
    book = Book.objects.filter(isbn=clean_isbn).first()
    if book:
        return {
            'id': book.id,
            'isbn': book.isbn,
            'title': book.title,
            'author': book.author,
            'publisher': book.publisher,
            'edition': book.edition,
            'category': book.category,
            'education_board': book.education_board,
            'grade_class': book.grade_class,
            'subject': book.subject,
            'description': book.description,
            'cover_image': book.cover_image,
            'original_retail_price': float(book.original_retail_price),
            'source': 'database'
        }, True

    # 2. Known Pakistani / Academic Catalog
    if clean_isbn in KNOWN_CATALOG:
        data = KNOWN_CATALOG[clean_isbn]
        book = Book.objects.create(
            isbn=clean_isbn,
            title=data['title'],
            author=data['author'],
            publisher=data['publisher'],
            edition=data['edition'],
            category=data['category'],
            education_board=data.get('education_board', 'Higher Education / University'),
            grade_class=data.get('grade_class', 'Bachelor / BS / Undergrad'),
            subject=data.get('subject', ''),
            description=data['description'],
            cover_image=data['cover_image'],
            original_retail_price=data['original_retail_price']
        )
        data['id'] = book.id
        data['source'] = 'curated_catalog'
        return data, True

    # 3. Google Books API
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{clean_isbn}"
        req = urllib.request.Request(url, headers={'User-Agent': 'BookLoop-Pakistan/1.0'})
        with urllib.request.urlopen(req, timeout=3) as resp:
            res_json = json.loads(resp.read().decode('utf-8'))
            if res_json.get('totalItems', 0) > 0:
                item = res_json['items'][0]['volumeInfo']
                title = item.get('title', 'Unknown Title')
                authors = ', '.join(item.get('authors', ['Unknown Author']))
                publisher = item.get('publisher', '')
                desc = item.get('description', '')
                image_links = item.get('imageLinks', {})
                cover = image_links.get('thumbnail') or image_links.get('smallThumbnail') or ''
                category = 'General Fiction & Non-Fiction'
                if item.get('categories'):
                    category_raw = item['categories'][0].lower()
                    if 'computer' in category_raw or 'software' in category_raw:
                        category = 'Software Engineering'
                    elif 'medical' in category_raw or 'health' in category_raw:
                        category = 'Medical & MBBS / BDS'

                book = Book.objects.create(
                    isbn=clean_isbn,
                    title=title,
                    author=authors,
                    publisher=publisher,
                    edition='',
                    category=category,
                    education_board='Higher Education / University',
                    grade_class='Bachelor / BS / Undergrad',
                    description=desc,
                    cover_image=cover,
                    original_retail_price=1500.00
                )
                return {
                    'id': book.id,
                    'isbn': book.isbn,
                    'title': book.title,
                    'author': book.author,
                    'publisher': book.publisher,
                    'edition': book.edition,
                    'category': book.category,
                    'education_board': book.education_board,
                    'grade_class': book.grade_class,
                    'subject': book.subject,
                    'description': book.description,
                    'cover_image': book.cover_image,
                    'original_retail_price': float(book.original_retail_price),
                    'source': 'google_books'
                }, True
    except Exception:
        pass

    # 4. Open Library API
    try:
        url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{clean_isbn}&format=json&jscmd=data"
        req = urllib.request.Request(url, headers={'User-Agent': 'BookLoop-Pakistan/1.0'})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data_map = json.loads(resp.read().decode('utf-8'))
            key = f"ISBN:{clean_isbn}"
            if key in data_map:
                info = data_map[key]
                title = info.get('title', 'Unknown Title')
                authors = ', '.join([a.get('name', '') for a in info.get('authors', [])]) or 'Unknown Author'
                publishers = ', '.join([p.get('name', '') for p in info.get('publishers', [])])
                cover = info.get('cover', {}).get('medium', '')

                book = Book.objects.create(
                    isbn=clean_isbn,
                    title=title,
                    author=authors,
                    publisher=publishers,
                    edition='',
                    category='General Fiction & Non-Fiction',
                    education_board='General / None',
                    grade_class='General Reading',
                    description=info.get('notes', ''),
                    cover_image=cover,
                    original_retail_price=1400.00
                )
                return {
                    'id': book.id,
                    'isbn': book.isbn,
                    'title': book.title,
                    'author': book.author,
                    'publisher': book.publisher,
                    'edition': book.edition,
                    'category': book.category,
                    'education_board': book.education_board,
                    'grade_class': book.grade_class,
                    'subject': book.subject,
                    'description': book.description,
                    'cover_image': book.cover_image,
                    'original_retail_price': float(book.original_retail_price),
                    'source': 'open_library'
                }, True
    except Exception:
        pass

    # 5. Not found in online APIs - return structured template for manual entry
    return {
        'id': None,
        'isbn': clean_isbn,
        'title': '',
        'author': '',
        'publisher': '',
        'edition': '',
        'category': 'Software Engineering',
        'education_board': 'Higher Education / University',
        'grade_class': 'Bachelor / BS / Undergrad',
        'subject': '',
        'description': '',
        'cover_image': '',
        'original_retail_price': 1200.00,
        'source': 'manual'
    }, False
