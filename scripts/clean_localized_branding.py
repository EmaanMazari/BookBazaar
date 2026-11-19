import os, sys, django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookbazaar_backend.settings')
django.setup()

from bazaar.models import UserProfile, Listing, Advertisement, Book
import re

print("Starting clean_localized_branding...")

# 1. Update User Profiles
cities_pool = ['Islamabad', 'Lahore', 'Karachi', 'Rawalpindi', 'Faisalabad']
for i, u in enumerate(UserProfile.objects.all()):
    changed = False
    
    # Remove Muhammad Bilal
    if 'bilal' in u.full_name.lower():
        u.full_name = 'Demo Buyer'
        changed = True
    elif u.user and u.user.username == 'admin':
        u.full_name = 'System Administrator'
        u.city = 'Islamabad'
        u.campus_or_area = 'National Operations Center'
        changed = True
    elif u.user and u.user.username == 'ali_iub':
        u.full_name = 'Demo Seller'
        u.city = 'Lahore'
        u.campus_or_area = 'Main Campus / Student Center'
        changed = True
    elif u.user and u.user.username == 'fatima_z':
        u.full_name = 'Fatima Zahra'
        u.city = 'Islamabad'
        u.campus_or_area = 'University Road / Student Library'
        changed = True

    if 'iub' in (u.full_name or '').lower():
        u.full_name = re.sub(r'\(?\s*IUB[^)]*\)?', '', u.full_name, flags=re.I).strip()
        changed = True

    if (u.city or '').lower() == 'bahawalpur':
        u.city = cities_pool[i % len(cities_pool)]
        changed = True

    if 'iub' in (u.campus_or_area or '').lower():
        u.campus_or_area = 'Main Campus / Student Library'
        changed = True

    if changed:
        u.save()
        print(f"Updated UserProfile {u.id} ({u.user.username if u.user else 'NoUser'}): name='{u.full_name}', city='{u.city}', campus='{u.campus_or_area}'")

# 2. Update Listings
pickup_replacements = [
    ('IUB Baghdad Campus Library cafeteria', 'Central Campus Library Cafeteria'),
    ('Abbasia Campus Department of Computing', 'Department of Computing / Main Library'),
    ('IUB Central Library or Abbasia Gate', 'Central University Library / Main Gate'),
    ('Hostel 3 or Software Engineering Lab', 'Hostel Gate or Software Engineering Lab'),
    ('Commercial Area Bahawalpur', 'Commercial Area / Campus Gate'),
    ('Model Town A, Bahawalpur', 'Model Town / Main Market'),
    ('model town A', 'Model Town / Main Market'),
    ('iub baghdaad campus', 'Main Campus Library'),
    ('IUB Baghdad Campus Library', 'Campus Gate 2 / Near University Library'),
]

for i, l in enumerate(Listing.objects.all()):
    changed = False
    
    # Check pickup location
    for old_val, new_val in pickup_replacements:
        if old_val.lower() in (l.pickup_location or '').lower():
            l.pickup_location = new_val
            changed = True
            break
            
    if 'iub' in (l.pickup_location or '').lower():
        l.pickup_location = re.sub(r'iub\s*', 'Campus ', l.pickup_location, flags=re.I).strip()
        changed = True
        
    if (l.city or '').lower() == 'bahawalpur':
        l.city = cities_pool[i % len(cities_pool)]
        changed = True

    # Check description
    if 'iub' in (l.description or '').lower() or 'bahawalpur' in (l.description or '').lower():
        desc = l.description
        desc = desc.replace('IUB Software Engineering students', 'Software Engineering students')
        desc = desc.replace('OS midterm and final exams at IUB', 'OS midterm and final exams across Pakistani universities')
        desc = re.sub(r'at IUB', 'at university', desc, flags=re.I)
        desc = re.sub(r'for IUB', 'for university', desc, flags=re.I)
        desc = re.sub(r'Bahawalpur', 'Pakistan', desc, flags=re.I)
        l.description = desc
        changed = True

    if changed:
        l.save()
        print(f"Updated Listing {l.id}: city='{l.city}', pickup='{l.pickup_location}'")

# 3. Update Advertisements
for a in Advertisement.objects.all():
    changed = False
    if 'iub' in (a.title or '').lower():
        a.title = 'Student Stationery & Binding Sale'
        changed = True
    if 'iub' in (a.sponsor_name or '').lower() or 'bahawalpur' in (a.sponsor_name or '').lower():
        a.sponsor_name = 'National Campus Supplies Hub'
        changed = True
    if 'se students' in (a.headline or '').lower() or 'iub' in (a.headline or '').lower():
        a.headline = 'Special 20% Discount on Thesis Binding & Project Printing for University Students'
        changed = True

    if changed:
        a.save()
        print(f"Updated Advertisement {a.id}: title='{a.title}', sponsor='{a.sponsor_name}'")

# 4. Update Books
for b in Book.objects.all():
    changed = False
    desc = b.description or ''
    if 'iub' in desc.lower():
        desc = desc.replace('Primary reference for IUB Department of Software Engineering.', 'Standard reference for software engineering and computer science programs across Pakistani universities.')
        desc = re.sub(r'IUB\s*', 'university ', desc, flags=re.I)
        b.description = desc
        changed = True
    if 'bahawalpur' in desc.lower():
        desc = desc.replace('Quaid-e-Azam Medical College Bahawalpur, King Edward Lahore', 'King Edward Medical University, Dow University of Health Sciences')
        desc = re.sub(r'Bahawalpur', 'Pakistan', desc, flags=re.I)
        b.description = desc
        changed = True
        
    if changed:
        b.save()
        print(f"Updated Book {b.id} ({b.title}): description updated.")

print("\nAll database records successfully generalized across Pakistan!")
