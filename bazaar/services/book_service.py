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
        'title': 'The Jungle Book & Illustrated Kids Stories',
        'author': 'Rudyard Kipling',
        'publisher': 'Puffin Classics',
        'edition': 'Illustrated Color Edition',
        'category': 'Story Books',
        'education_board': 'General / None',
        'grade_class': 'Primary & Middle (Class 1-8)',
        'target_age_group': 'kids',
        'subject': 'Adventure & Stories',
        'description': 'Timeless illustrated adventure classic following Mowgli, Baloo, and Bagheera in the wilderness. High quality color prints and easy English vocabulary for children.',
        'cover_image': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 550.00
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
        'cover_image': 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 350.00
    },
    '9789695840369': {
        'isbn': '9789695840369',
        'title': 'Alif Laila — Illustrated Moral Stories for Children (الف لیلیٰ برائے اطفال)',
        'author': 'Majlis Taraqqi-e-Adab, Lahore',
        'publisher': 'Majlis Taraqqi-e-Adab, Lahore',
        'edition': 'Children Illustrated Edition',
        'category': 'Story Books',
        'education_board': 'General / None',
        'grade_class': 'Primary & Middle (Class 1-8)',
        'target_age_group': 'kids',
        'subject': 'Classic Fairy Tales',
        'description': 'Selected classic Arabian Nights tales adapted in simple, entertaining Urdu for young readers. Includes Sindbad the Sailor, Aladdin, and Ali Baba.',
        'cover_image': 'https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=500&auto=format&fit=crop&q=80',
        'original_retail_price': 420.00
    },
    '9789695840376': {
        'isbn': '9789695840376',
        'title': 'Panchatantra Classic Moral Stories for Kids',
        'author': 'Pandit Vishnu Sharma / National Book Foundation',
        'publisher': 'National Book Foundation, Islamabad',
        'edition': 'Illustrated Edition',
        'category': 'Story Books',
        'education_board': 'General / None',
        'grade_class': 'Primary & Middle (Class 1-8)',
        'target_age_group': 'kids',
        'subject': 'Fables & Character Building',
        'description': 'Ancient animal fables teaching wisdom, leadership, friendship, and moral virtues. Engaging illustrations on every page suitable for age 5-12.',
        'cover_image': 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=500&auto=format&fit=crop&q=80',
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
