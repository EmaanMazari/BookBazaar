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
