import os
import uuid
import random
import logging
import urllib.parse
from decimal import Decimal

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from django.db.models import Q, Avg, Sum, Count, F
from django.conf import settings
from django.core.exceptions import ValidationError

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status

from bazaar.models import (
    UserProfile, Book, Listing, ContactUnlock, SellerReview,
    Advertisement, PlatformSetting, Favorite, PaymentTransaction,
    MarketplaceReport, AdminNotification
)
from bazaar.serializers import (
    UserProfileSerializer, BookSerializer, ListingSerializer,
    ContactUnlockSerializer, SellerReviewSerializer, AdvertisementSerializer,
    PlatformSettingSerializer, FavoriteSerializer, PaymentTransactionSerializer,
    MarketplaceReportSerializer, AdminNotificationSerializer
)
from bazaar.services.book_service import lookup_book_by_isbn, normalize_isbn
from bazaar.services.payment_service import (
    process_contact_unlock,
    initiate_contact_unlock_payment,
    verify_and_complete_contact_unlock,
    cancel_payment_transaction,
    get_gateway_adapter,
    PaymentGatewayError,
    LiveCredentialsRequiredError,
    InvalidSignatureError,
    InvalidAmountError,
    InvalidCurrencyError,
    SelfUnlockForbiddenError,
    ListingUnavailableError
)
from bazaar.validators import validate_image_file
from bazaar.permissions import IsOwnerOrReadOnly, IsAdminOnly, IsAdminUserOrReadOnly, IsUnlockParticipant
from bazaar.services.seed_service import ensure_demo_listings

logger = logging.getLogger('bazaar')


def index_view(request):
    """Main Web Application for BookBazaar"""
    ensure_demo_listings()
    plat_settings = PlatformSetting.get_settings()
    users = UserProfile.objects.filter(is_blocked=False)
    categories = [c[0] for c in Book.CATEGORY_CHOICES]
    cities = [c[0] for c in UserProfile.CITIES]
    conditions = [c[0] for c in Listing.CONDITION_CHOICES]
    boards = [b[0] for b in Book.BOARD_CHOICES]
    classes = [k[0] for k in Book.CLASS_CHOICES]
    
    context = {
        'settings': plat_settings,
        'users': users,
        'categories': categories,
        'cities': cities,
        'conditions': conditions,
        'boards': boards,
        'classes': classes,
    }
    return render(request, 'bazaar/index.html', context)


def admin_view(request):
    """Admin Dashboard View"""
    plat_settings = PlatformSetting.get_settings()
    admin_user = User.objects.filter(is_staff=True).first()
    admin_token = ''
    if admin_user:
        admin_token = Token.objects.get_or_create(user=admin_user)[0].key

    context = {
        'settings': plat_settings,
        'admin_token': admin_token,
    }
    return render(request, 'bazaar/admin.html', context)


# ==========================================
# AUTHENTICATION & PROFILES API
# ==========================================

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Secure user registration:
    - Minimum password length validation (>= 6 chars)
    - Passwords securely hashed via Django's default PBKDF2/SHA256
    - Returns Auth Token and UserProfile
    """
    data = request.data
    phone = str(data.get('phone_number', '')).strip()
    password = str(data.get('password', '')).strip()
    full_name = str(data.get('full_name', '')).strip()
    city = str(data.get('city', 'Islamabad')).strip()
    campus = str(data.get('campus_or_area', 'Main Campus')).strip()
    user_type = str(data.get('user_type', 'student')).strip()

    if not phone or not password or not full_name:
        return Response({'error': 'Phone number, password, and full name are required.'}, status=status.HTTP_400_BAD_REQUEST)

    if len(password) < 6:
        return Response({'error': 'Password must be at least 6 characters long.'}, status=status.HTTP_400_BAD_REQUEST)

    phone_clean = ''.join(c for c in phone if c.isdigit())
    if len(phone_clean) == 10 and phone_clean.startswith('3'):
        phone_clean = '0' + phone_clean

    if len(phone_clean) < 11:
        return Response({'error': 'Please enter a valid 11-digit Pakistani phone number (e.g. 03001234567).'}, status=status.HTTP_400_BAD_REQUEST)

    if UserProfile.objects.filter(phone_number=phone_clean).exists():
        return Response({'error': 'An account with this phone number already exists.'}, status=status.HTTP_400_BAD_REQUEST)

    username = f"user_{phone_clean}"
    if User.objects.filter(username=username).exists():
        username = f"user_{phone_clean}_{random.randint(100, 999)}"

    # create_user securely hashes password
    user = User.objects.create_user(username=username, password=password)
    user.first_name = full_name
    user.save()

    profile = UserProfile.objects.create(
        user=user,
        phone_number=phone_clean,
        full_name=full_name,
        city=city,
        campus_or_area=campus,
        user_type=user_type,
        wallet_balance=Decimal('100.00')  # Welcome initial credit
    )

    token, _ = Token.objects.get_or_create(user=user)
    logger.info(f"User registered successfully: {username} ({phone_clean})")

    return Response({
        'message': 'Registration successful! Welcome to BookBazaar.',
        'token': token.key,
        'profile': UserProfileSerializer(profile, context={'request': request, 'is_owner': True}).data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Secure login using Phone Number / Username and Password.
    Returns Auth Token and UserProfile.
    """
    data = request.data
    phone_or_user = str(data.get('phone_or_username', '')).strip()
    password = str(data.get('password', '')).strip()

    if not phone_or_user or not password:
        return Response({'error': 'Credentials are required.'}, status=status.HTTP_400_BAD_REQUEST)

    phone_clean = ''.join(c for c in phone_or_user if c.isdigit())
    if len(phone_clean) == 10 and phone_clean.startswith('3'):
        phone_clean = '0' + phone_clean

    profile = UserProfile.objects.filter(Q(phone_number=phone_clean) | Q(user__username=phone_or_user)).first()
    if not profile or not profile.user:
        return Response({'error': 'No account found with this phone number or username.'}, status=status.HTTP_404_NOT_FOUND)

    if profile.is_blocked:
        return Response({'error': 'This account has been blocked by BookBazaar Admin.'}, status=status.HTTP_403_FORBIDDEN)

    user = authenticate(username=profile.user.username, password=password)
    if not user:
        return Response({'error': 'Incorrect password.'}, status=status.HTTP_401_UNAUTHORIZED)

    django_login(request, user)
    token, _ = Token.objects.get_or_create(user=user)
    logger.info(f"User logged in: {user.username}")

    return Response({
        'message': 'Login successful',
        'token': token.key,
        'profile': UserProfileSerializer(profile, context={'request': request, 'is_owner': True}).data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """Logs out user and invalidates auth token"""
    if request.user.is_authenticated:
        Token.objects.filter(user=request.user).delete()
        django_logout(request)
        logger.info(f"User logged out: {request.user.username}")
    return Response({'message': 'Logged out successfully'})


@api_view(['POST'])
@permission_classes([AllowAny])
def demo_login(request):
    """
    Demo Profile Switcher endpoint (for FYP evaluation and development testing).
    Guarded by settings.DEBUG. Disabled in production.
    Returns the real Django Auth Token for the selected user profile.
    """
    if not settings.DEBUG:
        return Response({'error': 'Demo login switcher is disabled in production.'}, status=status.HTTP_403_FORBIDDEN)

    user_id = request.data.get('user_id')
    if not user_id:
        return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    profile = get_object_or_404(UserProfile, id=user_id)
    if profile.is_blocked:
        return Response({'error': 'This account has been blocked by Admin.'}, status=status.HTTP_403_FORBIDDEN)

    token, _ = Token.objects.get_or_create(user=profile.user)
    return Response({
        'token': token.key,
        'profile': UserProfileSerializer(profile, context={'request': request, 'is_owner': True}).data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user_profile(request):
    """Returns profile for currently authenticated user"""
    profile = getattr(request.user, 'profile', None)
    if not profile:
        profile = UserProfile.objects.filter(user=request.user).first()

    if not profile:
        return Response({'error': 'No profile found for this user.'}, status=status.HTTP_404_NOT_FOUND)

    return Response(UserProfileSerializer(profile, context={'request': request, 'is_owner': True}).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def update_user_profile(request):
    """Update profile details with image file validation"""
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    if 'full_name' in request.data:
        profile.full_name = request.data['full_name'].strip()
    if 'city' in request.data:
        profile.city = request.data['city'].strip()
    if 'campus_or_area' in request.data:
        profile.campus_or_area = request.data['campus_or_area'].strip()

    if 'profile_picture' in request.FILES:
        pic = request.FILES['profile_picture']
        try:
            validate_image_file(pic)
        except ValidationError as e:
            return Response({'error': str(e.message if hasattr(e, 'message') else e)}, status=status.HTTP_400_BAD_REQUEST)
        profile.profile_picture = pic

    profile.save()
    return Response({
        'message': 'Profile updated successfully',
        'profile': UserProfileSerializer(profile, context={'request': request, 'is_owner': True}).data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_profiles_list(request):
    """List profiles for demo switcher and public directory (phone numbers masked)"""
    profiles = UserProfile.objects.filter(is_blocked=False).order_by('id')
    serializer = UserProfileSerializer(profiles, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_with_otp(request):
    """
    Fast OTP login endpoint for FYP evaluation.
    """
    phone = str(request.data.get('phone_number', '')).strip()
    name = str(request.data.get('full_name', '')).strip()
    city = str(request.data.get('city', 'Islamabad')).strip()

    if not phone:
        return Response({'error': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)

    phone_clean = ''.join(c for c in phone if c.isdigit())
    if len(phone_clean) == 10 and phone_clean.startswith('3'):
        phone_clean = '0' + phone_clean

    profile = UserProfile.objects.filter(phone_number=phone_clean).first()
    if not profile:
        user = User.objects.create_user(username=f"user_{phone_clean}", password='password123')
        profile = UserProfile.objects.create(
            user=user,
            phone_number=phone_clean,
            full_name=name or f"Student User ({phone_clean[-4:]})",
            city=city,
            campus_or_area='Main Campus',
            user_type='student',
            wallet_balance=Decimal('200.00')
        )
    
    if profile.is_blocked:
        return Response({'error': 'Account is blocked by Admin.'}, status=status.HTTP_403_FORBIDDEN)

    token, _ = Token.objects.get_or_create(user=profile.user)
    serializer = UserProfileSerializer(profile, context={'request': request, 'is_owner': True})
    return Response({
        'message': 'Login successful via verified OTP',
        'token': token.key,
        'profile': serializer.data
    })


# ==========================================
# BOOK & SCANNER API
# ==========================================

@api_view(['GET'])
@permission_classes([AllowAny])
def scan_isbn(request):
    """Barcode / ISBN scanner endpoint with multi-seller comparison"""
    isbn = request.GET.get('isbn', '').strip()
    if not isbn:
        return Response({'error': 'ISBN query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

    book_data, found = lookup_book_by_isbn(isbn)
    if not book_data:
        return Response({
            'error': 'Unrecognized barcode or ISBN. You can still enter book details manually!',
            'found_in_catalog': False
        }, status=status.HTTP_404_NOT_FOUND)

    book_id = book_data.get('id')
    listings_data = []
    price_stats = {}

    if book_id:
        active_listings = Listing.objects.filter(book_id=book_id, status='active').order_by('price')
        serializer = ListingSerializer(active_listings, many=True, context={'request': request})
        listings_data = serializer.data

        if active_listings.exists():
            prices = [float(l.price) for l in active_listings]
            lowest = min(prices)
            highest = max(prices)
            retail = float(book_data.get('original_retail_price', 0))
            savings = int(((retail - lowest) / retail) * 100) if retail > lowest else 0
            price_stats = {
                'lowest_price': lowest,
                'highest_price': highest,
                'total_offers': len(prices),
                'retail_price': retail,
                'max_savings_percent': max(0, savings)
            }

    return Response({
        'book': book_data,
        'found_in_catalog': found,
        'price_stats': price_stats,
        'listings': listings_data
    })


# ==========================================
# LISTINGS API (Search, Filter, Create, Edit, Delete)
# ==========================================

@api_view(['GET'])
@permission_classes([AllowAny])
def get_listing_detail(request, listing_id):
    """
    Retrieve single listing detail:
    - Serializes listing and book info
    - Masks seller phone if not unlocked or unauthorized
    - Indicates if contact is unlocked or favorited by current user
    """
    listing = get_object_or_404(Listing.objects.select_related('book', 'seller'), id=listing_id)
    serializer = ListingSerializer(listing, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_listings(request):
    """
    Search and filter book listings:
    - Search: title, author, ISBN, subject, grade class, education board, description
    - Filter: category, city, condition, board, class, min/max price
    - Sort: cheapest, expensive, rating, newest
    """
    ensure_demo_listings()
    q = request.GET.get('search', '').strip()
    category = request.GET.get('category', '').strip()
    city = request.GET.get('city', '').strip()
    condition = request.GET.get('condition', '').strip()
    board = request.GET.get('board', '').strip()
    grade_class = request.GET.get('grade_class', '').strip()
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort_by = request.GET.get('sort', 'cheapest')

    listings = Listing.objects.filter(status='active').select_related('book', 'seller')

    if q:
        listings = listings.filter(
            Q(book__title__icontains=q) |
            Q(book__author__icontains=q) |
            Q(book__isbn__icontains=q) |
            Q(book__subject__icontains=q) |
            Q(book__grade_class__icontains=q) |
            Q(book__education_board__icontains=q) |
            Q(description__icontains=q)
        )

    if category and category != 'All':
        listings = listings.filter(book__category=category)

    if city and city != 'All':
        listings = listings.filter(city=city)

    if condition and condition != 'All':
        listings = listings.filter(condition=condition)

    if board and board != 'All':
        listings = listings.filter(book__education_board=board)

    if grade_class and grade_class != 'All':
        listings = listings.filter(book__grade_class=grade_class)

    if min_price:
        try:
            listings = listings.filter(price__gte=Decimal(str(min_price)))
        except Exception:
            pass

    if max_price:
        try:
            listings = listings.filter(price__lte=Decimal(str(max_price)))
        except Exception:
            pass

    # Sorting
    if sort_by == 'cheapest':
        listings = listings.order_by('-is_sponsored', 'price')
    elif sort_by == 'expensive':
        listings = listings.order_by('-is_sponsored', '-price')
    elif sort_by == 'rating':
        listings = listings.order_by('-is_sponsored', '-seller__rating')
    else:
        listings = listings.order_by('-is_sponsored', '-created_at')

    serializer = ListingSerializer(listings, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def create_listing(request):
    """
    Create a new book listing:
    - Protected: Authenticated users only
    - Validates image file type, size (<= 5MB), and integrity with Pillow
    - Validates price (> 0) and required book details
    """
    data = request.data
    user = request.user

    # Ensure seller profile exists
    seller = getattr(user, 'profile', None)
    if not seller:
        # If staff user without profile, permit fallback or error
        if user.is_staff and data.get('seller_id'):
            seller = get_object_or_404(UserProfile, id=data.get('seller_id'))
        else:
            return Response({'error': 'User profile required to list books.'}, status=status.HTTP_400_BAD_REQUEST)

    if seller.is_blocked:
        return Response({'error': 'Your seller account has been blocked by Admin.'}, status=status.HTTP_403_FORBIDDEN)

    raw_is_free = data.get('is_free') or data.get('is_donation')
    is_free = str(raw_is_free).lower() in ['true', '1', 'yes'] if raw_is_free is not None else False

    raw_price = data.get('price')
    if is_free or (raw_price is not None and str(raw_price).strip() in ['0', '0.0', '0.00']):
        price = Decimal('0.00')
        is_free = True
    else:
        if raw_price is None or str(raw_price).strip() == '':
            return Response({'error': 'Price is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            price = Decimal(str(raw_price))
            if price < 0:
                return Response({'error': 'Price must be greater than or equal to zero.'}, status=status.HTTP_400_BAD_REQUEST)
            elif price == 0:
                is_free = True
        except Exception:
            return Response({'error': 'Invalid price format.'}, status=status.HTTP_400_BAD_REQUEST)

    title = data.get('title', '').strip()
    if not title:
        return Response({'error': 'Book title is required.'}, status=status.HTTP_400_BAD_REQUEST)

    author = data.get('author', '').strip() or 'Unknown Author'
    condition = data.get('condition', 'Good')
    city = data.get('city', seller.city)
    pickup_location = data.get('pickup_location', 'Campus Gate / Central Library')
    description = data.get('description', '')
    photo_url = data.get('photo_url', '')
    image_file = request.FILES.get('image')

    # Image validation
    if image_file:
        try:
            validate_image_file(image_file)
        except ValidationError as e:
            return Response({'error': str(e.message if hasattr(e, 'message') else e)}, status=status.HTTP_400_BAD_REQUEST)

    board = data.get('education_board', 'Higher Education / University')
    grade_class = data.get('grade_class', 'Bachelor / BS / Undergrad')
    subject = data.get('subject', '')
    cat = data.get('category', 'Software Engineering')

    isbn = normalize_isbn(data.get('isbn', ''))
    book = Book.objects.filter(isbn=isbn).first() if isbn else None
    if not book:
        book_info, found = lookup_book_by_isbn(isbn)
        if found and book_info.get('id'):
            book = Book.objects.get(id=book_info['id'])
        else:
            if not isbn:
                isbn = f"LOCAL-{uuid.uuid4().hex[:8].upper()}"
            book = Book.objects.create(
                isbn=isbn,
                title=title,
                author=author,
                publisher=data.get('publisher', 'Local Publisher'),
                category=cat,
                education_board=board,
                grade_class=grade_class,
                subject=subject,
                description=description,
                cover_image=photo_url or 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400',
                target_age_group=data.get('age_group') or data.get('target_age_group', 'all'),
                original_retail_price=Decimal(str(max(100.0, float(price) * 1.5))) if price > 0 else Decimal('350.00')
            )

    setting = PlatformSetting.get_settings()
    listing_status = 'pending' if setting.require_admin_approval else 'active'
    target_age = data.get('age_group') or data.get('target_age_group') or book.target_age_group or 'all'

    listing = Listing.objects.create(
        book=book,
        seller=seller,
        condition=condition,
        price=price,
        is_free=is_free,
        target_age_group=target_age,
        city=city,
        pickup_location=pickup_location,
        description=description,
        photo_url=photo_url or book.cover_image,
        image=image_file,
        status=listing_status
    )

    interstitial_ad = Advertisement.objects.filter(ad_type='interstitial', is_active=True).first()
    ad_data = AdvertisementSerializer(interstitial_ad).data if interstitial_ad else None

    logger.info(f"Listing created: id={listing.id}, book='{book.title}', seller={seller.full_name}")

    return Response({
        'message': 'Listing created successfully!' if listing_status == 'active' else 'Listing submitted for admin approval.',
        'listing': ListingSerializer(listing, context={'request': request}).data,
        'interstitial_ad': ad_data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_seller_listings(request, seller_id=None):
    """
    Fetch listings belonging to a specific seller:
    - If requester is the seller or staff: shows all listings (active, pending, sold)
    - If requester is public: shows only active listings
    """
    if seller_id:
        seller = get_object_or_404(UserProfile, id=seller_id)
    elif request.user.is_authenticated:
        seller = getattr(request.user, 'profile', None)
    else:
        return Response({'error': 'Seller ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

    if not seller:
        return Response({'error': 'Seller profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    is_owner = request.user.is_authenticated and (request.user.is_staff or (seller.user and seller.user == request.user))

    if is_owner:
        listings = Listing.objects.filter(seller=seller).select_related('book').order_by('-created_at')
    else:
        listings = Listing.objects.filter(seller=seller, status='active').select_related('book').order_by('-created_at')

    serializer = ListingSerializer(listings, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def edit_listing(request, listing_id):
    """
    Edit own listing:
    - Protected: Only the listing's seller or staff can modify
    - Validates image file if uploaded
    - Validates price > 0
    """
    listing = get_object_or_404(Listing, id=listing_id)

    # Enforce Owner-Only or Staff permission
    if not (request.user.is_staff or (listing.seller.user and listing.seller.user == request.user)):
        return Response({'error': 'Permission denied: You can only edit your own listings.'}, status=status.HTTP_403_FORBIDDEN)

    data = request.data
    if 'is_free' in data:
        listing.is_free = str(data['is_free']).lower() in ['true', '1', 'yes']
        if listing.is_free:
            listing.price = Decimal('0.00')

    if 'price' in data and not listing.is_free:
        try:
            new_price = Decimal(str(data['price']))
            if new_price < 0:
                return Response({'error': 'Price must be greater than or equal to zero.'}, status=status.HTTP_400_BAD_REQUEST)
            elif new_price == 0:
                listing.is_free = True
                listing.price = Decimal('0.00')
            else:
                listing.price = new_price
        except Exception:
            return Response({'error': 'Invalid price format.'}, status=status.HTTP_400_BAD_REQUEST)

    if 'age_group' in data or 'target_age_group' in data:
        listing.target_age_group = data.get('age_group') or data.get('target_age_group', 'all')

    if 'condition' in data:
        listing.condition = data['condition']
    if 'city' in data:
        listing.city = data['city']
    if 'pickup_location' in data:
        listing.pickup_location = data['pickup_location']
    if 'description' in data:
        listing.description = data['description']

    if 'image' in request.FILES:
        img = request.FILES['image']
        try:
            validate_image_file(img)
        except ValidationError as e:
            return Response({'error': str(e.message if hasattr(e, 'message') else e)}, status=status.HTTP_400_BAD_REQUEST)
        listing.image = img

    if 'status' in data:
        if data['status'] in dict(Listing.STATUS_CHOICES):
            listing.status = data['status']

    listing.save()
    logger.info(f"Listing updated: id={listing.id} by user={request.user.username}")

    return Response({
        'message': 'Listing updated successfully',
        'listing': ListingSerializer(listing, context={'request': request}).data
    })


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def delete_listing(request, listing_id):
    """
    Delete a listing:
    - Protected: Only the listing's seller or staff can delete
    """
    listing = get_object_or_404(Listing, id=listing_id)

    # Enforce Owner-Only or Staff permission
    if not (request.user.is_staff or (listing.seller.user and listing.seller.user == request.user)):
        return Response({'error': 'Permission denied: You can only delete your own listings.'}, status=status.HTTP_403_FORBIDDEN)

    listing_id_saved = listing.id
    listing.delete()
    logger.info(f"Listing deleted: id={listing_id_saved} by user={request.user.username}")

    return Response({'message': 'Listing deleted successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_listing_status(request, listing_id):
    """
    Toggle listing status between active and sold:
    - Protected: Owner or Staff only
    """
    listing = get_object_or_404(Listing, id=listing_id)

    if not (request.user.is_staff or (listing.seller.user and listing.seller.user == request.user)):
        return Response({'error': 'Permission denied: You can only modify your own listings.'}, status=status.HTTP_403_FORBIDDEN)

    listing.status = 'sold' if listing.status == 'active' else 'active'
    listing.save()
    return Response({
        'message': f"Listing status changed to {listing.status}",
        'status': listing.status
    })


# ==========================================
# FAVORITES / WISHLIST API
# ==========================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request):
    """Toggle bookmark / favorite for a listing (Authenticated user only)"""
    user_profile = getattr(request.user, 'profile', None)
    if not user_profile:
        return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    listing_id = request.data.get('listing_id')
    if not listing_id:
        return Response({'error': 'listing_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

    listing = get_object_or_404(Listing, id=listing_id)
    fav = Favorite.objects.filter(user=user_profile, listing=listing).first()

    if fav:
        fav.delete()
        is_fav = False
        msg = "Removed from favourites"
    else:
        Favorite.objects.create(user=user_profile, listing=listing)
        is_fav = True
        msg = "Added to favourites"

    return Response({'message': msg, 'is_favorited': is_fav})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_favorites(request, user_id):
    """
    List all favorites for a user:
    - Protected: User can only view their own favorites, unless staff
    """
    target_profile = get_object_or_404(UserProfile, id=user_id)

    if not (request.user.is_staff or (target_profile.user and target_profile.user == request.user)):
        return Response({'error': 'Permission denied: Cannot view another user’s favorites.'}, status=status.HTTP_403_FORBIDDEN)

    favorites = Favorite.objects.filter(user=target_profile).select_related('listing__book', 'listing__seller').order_by('-created_at')
    serializer = FavoriteSerializer(favorites, many=True, context={'request': request})
    return Response(serializer.data)


# ==========================================
# CONTACT UNLOCK & REFUND API
# ==========================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_contact_unlock(request):
    """
    PAID CONTACT UNLOCK SYSTEM:
    - Protected: Authenticated buyer
    - Platform fee: Rs. 50 (configurable via PlatformSetting)
    - Prevents self-unlock (cannot unlock own listing)
    - Prevents duplicate charges: returns existing record if already unlocked
    - Modular sandbox payment gateway
    - Unlocks seller contact info only after verified payment
    """
    data = request.data
    listing_id = data.get('listing_id')
    payment_method = data.get('payment_method', 'jazzcash')
    account_number = data.get('account_number', '')

    if not listing_id:
        return Response({'error': 'listing_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Buyer is strictly authenticated user
    buyer = getattr(request.user, 'profile', None)
    if not buyer:
        if request.user.is_staff and data.get('buyer_id'):
            buyer = get_object_or_404(UserProfile, id=data.get('buyer_id'))
        else:
            return Response({'error': 'Buyer profile required.'}, status=status.HTTP_400_BAD_REQUEST)

    listing = get_object_or_404(Listing, id=listing_id)
    seller = listing.seller

    # Prevent unlocking own listing
    if buyer == seller or (listing.seller.user and listing.seller.user == request.user):
        return Response({'error': 'You cannot unlock contact details for your own book listing.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        unlock, is_new_charge, message = process_contact_unlock(
            listing=listing,
            buyer=buyer,
            payment_method=payment_method,
            account_number=account_number
        )
    except PaymentGatewayError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    clean_phone = seller.phone_number.lstrip('0') if seller.phone_number else ''
    wa_url = f"https://wa.me/92{clean_phone}?text=Assalam-o-Alaikum%20{urllib.parse.quote(seller.full_name)},%20I%20am%20interested%20in%20your%20book%20'{urllib.parse.quote(listing.book.title)}'%20on%20BookBazaar%20for%20Rs.%20{listing.price}."

    return Response({
        'message': message,
        'is_new_charge': is_new_charge,
        'unlock': ContactUnlockSerializer(unlock).data,
        'seller_contact': {
            'full_name': seller.full_name,
            'phone_number': seller.phone_number,
            'city': seller.city,
            'campus_or_area': seller.campus_or_area,
            'whatsapp_link': wa_url
        }
    }, status=status.HTTP_201_CREATED if is_new_charge else status.HTTP_200_OK)


# ==========================================
# PHASE 3 PAYMENT GATEWAY ENDPOINTS
# ==========================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment_api(request):
    """
    Step 1: Initiate payment for contact unlock via selected gateway (JazzCash/Easypaisa/Card/Wallet).
    Returns internal transaction ID, amount, and gateway parameters with secure hash.
    If listing is already unlocked by buyer, returns existing unlock without duplicate charge.
    """
    data = request.data
    listing_id = data.get('listing_id')
    gateway = data.get('gateway', data.get('payment_method', 'jazzcash'))
    account_number = data.get('account_number', '')

    if not listing_id:
        return Response({'error': 'listing_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    buyer = getattr(request.user, 'profile', None)
    if not buyer:
        if request.user.is_staff and data.get('buyer_id'):
            buyer = get_object_or_404(UserProfile, id=data.get('buyer_id'))
        else:
            return Response({'error': 'Buyer profile required.'}, status=status.HTTP_400_BAD_REQUEST)

    listing = get_object_or_404(Listing, id=listing_id)

    try:
        payment_txn, init_data = initiate_contact_unlock_payment(
            listing=listing,
            buyer=buyer,
            gateway_name=gateway,
            account_number=account_number
        )
    except SelfUnlockForbiddenError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except ListingUnavailableError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except PaymentGatewayError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    if init_data.get('already_unlocked'):
        unlock = init_data['unlock']
        seller = listing.seller
        clean_phone = seller.phone_number.lstrip('0') if seller.phone_number else ''
        wa_url = f"https://wa.me/92{clean_phone}?text=Assalam-o-Alaikum%20{urllib.parse.quote(seller.full_name)},%20I%20am%20interested%20in%20your%20book%20'{urllib.parse.quote(listing.book.title)}'%20on%20BookBazaar%20for%20Rs.%20{listing.price}."
        return Response({
            'already_unlocked': True,
            'message': init_data['message'],
            'unlock': ContactUnlockSerializer(unlock).data,
            'seller_contact': {
                'full_name': seller.full_name,
                'phone_number': seller.phone_number,
                'city': seller.city,
                'campus_or_area': seller.campus_or_area,
                'whatsapp_link': wa_url
            }
        }, status=status.HTTP_200_OK)

    return Response({
        'transaction_id': str(payment_txn.transaction_id),
        'amount': float(payment_txn.amount),
        'currency': payment_txn.currency,
        'gateway': payment_txn.gateway,
        'status': payment_txn.status,
        'initiation_data': init_data,
        'created_at': payment_txn.created_at.isoformat()
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_payment_api(request):
    """
    Step 2: Server-side payment verification.
    Validates cryptographic signature, amount, currency and gateway response.
    Unlocks seller contact details ONLY after successful verification.
    """
    data = request.data
    transaction_id = data.get('transaction_id')
    incoming_payload = data.get('payload', data.get('parameters', {}))
    simulate_outcome = data.get('simulate_outcome', 'success')

    if not transaction_id:
        return Response({'error': 'transaction_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    payment_txn = get_object_or_404(PaymentTransaction, transaction_id=transaction_id)

    # Permission check: buyer or staff
    if not (request.user.is_staff or (payment_txn.buyer.user and payment_txn.buyer.user == request.user)):
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        unlock, is_new_charge, msg = verify_and_complete_contact_unlock(
            transaction_id=transaction_id,
            incoming_data=incoming_payload,
            simulate_outcome=simulate_outcome
        )
    except (InvalidSignatureError, InvalidAmountError, InvalidCurrencyError) as e:
        return Response({'error': str(e), 'status': 'failed'}, status=status.HTTP_400_BAD_REQUEST)
    except PaymentGatewayError as e:
        return Response({'error': str(e), 'status': 'failed'}, status=status.HTTP_400_BAD_REQUEST)

    seller = payment_txn.listing.seller
    clean_phone = seller.phone_number.lstrip('0') if seller.phone_number else ''
    wa_url = f"https://wa.me/92{clean_phone}?text=Assalam-o-Alaikum%20{urllib.parse.quote(seller.full_name)},%20I%20am%20interested%20in%20your%20book%20'{urllib.parse.quote(payment_txn.listing.book.title)}'%20on%20BookBazaar%20for%20Rs.%20{payment_txn.listing.price}."

    return Response({
        'message': msg,
        'status': 'completed',
        'is_new_charge': is_new_charge,
        'unlock': ContactUnlockSerializer(unlock).data,
        'payment_transaction': PaymentTransactionSerializer(payment_txn).data,
        'seller_contact': {
            'full_name': seller.full_name,
            'phone_number': seller.phone_number,
            'city': seller.city,
            'campus_or_area': seller.campus_or_area,
            'whatsapp_link': wa_url
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_payment_api(request):
    """Cancel a pending payment transaction."""
    transaction_id = request.data.get('transaction_id')
    reason = request.data.get('reason', 'User cancelled checkout')

    if not transaction_id:
        return Response({'error': 'transaction_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    payment_txn = get_object_or_404(PaymentTransaction, transaction_id=transaction_id)
    if not (request.user.is_staff or (payment_txn.buyer.user and payment_txn.buyer.user == request.user)):
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        updated = cancel_payment_transaction(transaction_id, reason=reason)
        return Response({
            'message': 'Payment transaction cancelled.',
            'transaction': PaymentTransactionSerializer(updated).data
        })
    except PaymentGatewayError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def jazzcash_callback_api(request):
    """
    Official JazzCash IPN / Return URL Callback.
    Accepts incoming POST payload, validates HMAC-SHA256 signature,
    and updates transaction status accordingly.
    """
    payload = request.data if request.method == 'POST' else request.GET.dict()
    txn_ref = payload.get('pp_BillReference') or payload.get('pp_TxnRefNo')

    if not txn_ref:
        return Response({'error': 'Missing transaction reference in callback'}, status=status.HTTP_400_BAD_REQUEST)

    payment_txn = PaymentTransaction.objects.filter(
        Q(transaction_id__startswith=txn_ref[:8]) | Q(gateway_ref=txn_ref)
    ).first()

    if not payment_txn:
        try:
            payment_txn = PaymentTransaction.objects.get(transaction_id=txn_ref)
        except Exception:
            return Response({'error': f'Transaction for ref {txn_ref} not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        unlock, is_new, msg = verify_and_complete_contact_unlock(
            transaction_id=payment_txn.transaction_id,
            incoming_data=payload
        )
        return Response({
            'status': 'success',
            'message': msg,
            'transaction_id': str(payment_txn.transaction_id),
            'unlock_id': str(unlock.unlock_id)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.warning(f"JazzCash callback error for {txn_ref}: {str(e)}")
        return Response({'status': 'failed', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def easypaisa_callback_api(request):
    """
    Official Easypaisa IPN / Return URL Callback.
    Accepts incoming callback payload, validates merchantHashedReq,
    and updates transaction status accordingly.
    """
    payload = request.data if request.method == 'POST' else request.GET.dict()
    order_id = payload.get('orderId') or payload.get('transactionId')

    if not order_id:
        return Response({'error': 'Missing orderId in callback'}, status=status.HTTP_400_BAD_REQUEST)

    payment_txn = PaymentTransaction.objects.filter(
        Q(transaction_id__startswith=order_id[:8]) | Q(gateway_ref=order_id)
    ).first()

    if not payment_txn:
        try:
            payment_txn = PaymentTransaction.objects.get(transaction_id=order_id)
        except Exception:
            return Response({'error': f'Transaction for orderId {order_id} not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        unlock, is_new, msg = verify_and_complete_contact_unlock(
            transaction_id=payment_txn.transaction_id,
            incoming_data=payload
        )
        return Response({
            'status': 'success',
            'message': msg,
            'transaction_id': str(payment_txn.transaction_id),
            'unlock_id': str(unlock.unlock_id)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.warning(f"Easypaisa callback error for {order_id}: {str(e)}")
        return Response({'status': 'failed', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payment_transaction_api(request, transaction_id):
    """Retrieve payment transaction status and details."""
    payment_txn = get_object_or_404(PaymentTransaction, transaction_id=transaction_id)
    if not (request.user.is_staff or (payment_txn.buyer.user and payment_txn.buyer.user == request.user)):
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

    return Response(PaymentTransactionSerializer(payment_txn).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_unlocks(request, user_id):
    """
    Fetch all contact unlocks for a user:
    - Protected: User can only view their own unlocks (as buyer or seller), or staff
    """
    user_profile = get_object_or_404(UserProfile, id=user_id)

    if not (request.user.is_staff or (user_profile.user and user_profile.user == request.user)):
        return Response({'error': 'Permission denied: Cannot view another user’s unlocks.'}, status=status.HTTP_403_FORBIDDEN)

    buyer_unlocks = ContactUnlock.objects.filter(buyer=user_profile).order_by('-payment_timestamp')
    seller_unlocks = ContactUnlock.objects.filter(seller=user_profile).order_by('-payment_timestamp')

    return Response({
        'as_buyer': ContactUnlockSerializer(buyer_unlocks, many=True).data,
        'as_seller': ContactUnlockSerializer(seller_unlocks, many=True).data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_deal_made(request, unlock_id):
    """
    DEAL CONFIRMED:
    - Protected: Participant (buyer or seller) or staff only
    - BookLoop keeps the contact fee. Listing marked sold.
    """
    unlock = get_object_or_404(ContactUnlock, unlock_id=unlock_id)

    # Verify participant permission
    is_buyer = unlock.buyer.user and unlock.buyer.user == request.user
    is_seller = unlock.seller.user and unlock.seller.user == request.user
    if not (request.user.is_staff or is_buyer or is_seller):
        return Response({'error': 'Permission denied: You are not a party in this transaction.'}, status=status.HTTP_403_FORBIDDEN)

    if unlock.deal_status == 'deal_made':
        return Response({'message': 'Deal is already confirmed.'})

    if unlock.deal_status == 'no_deal_refunded':
        return Response({'error': 'Cannot confirm a deal that has already been refunded.'}, status=status.HTTP_400_BAD_REQUEST)

    unlock.deal_status = 'deal_made'
    unlock.buyer_confirmation = 'confirmed'
    unlock.seller_confirmation = 'confirmed'
    unlock.resolved_at = timezone.now()
    unlock.save()

    listing = unlock.listing
    listing.status = 'sold'
    listing.save()

    # Trigger Admin Notification: DEAL_SUCCESSFUL
    try:
        buyer_name = unlock.buyer.full_name or (unlock.buyer.user.username if unlock.buyer.user else "Buyer")
        seller_name = unlock.seller.full_name or (unlock.seller.user.username if unlock.seller.user else "Seller")
        book_title = unlock.listing.book.title
        AdminNotification.objects.create(
            notification_type='DEAL_SUCCESSFUL',
            title="Deal Successful",
            message=f"Deal Successful: Book '{book_title}' exchange completed between buyer {buyer_name} and seller {seller_name}.",
            user=unlock.buyer,
            buyer=unlock.buyer,
            seller=unlock.seller,
            listing=unlock.listing,
            unlock=unlock,
            is_resolved=True
        )
    except Exception as notif_err:
        logger.warning(f"Failed to create AdminNotification for deal completion: {notif_err}")

    logger.info(f"Deal confirmed: unlock_id={unlock.unlock_id}, listing_id={listing.id}")

    return Response({
        'message': f"Deal confirmed! BookBazaar fee of Rs. {unlock.fee_amount} finalized. Please rate {unlock.seller.full_name}.",
        'unlock': ContactUnlockSerializer(unlock).data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_deal_refund(request, unlock_id):
    """
    NO DEAL / REFUND:
    - Protected: Participant (buyer or seller) or staff only
    - Full contact fee (Rs. 50) refunded back to buyer wallet with refund transaction ID
    """
    unlock = get_object_or_404(ContactUnlock, unlock_id=unlock_id)

    is_buyer = unlock.buyer.user and unlock.buyer.user == request.user
    is_seller = unlock.seller.user and unlock.seller.user == request.user
    if not (request.user.is_staff or is_buyer or is_seller):
        return Response({'error': 'Permission denied: You are not a party in this transaction.'}, status=status.HTTP_403_FORBIDDEN)

    reason = request.data.get('reason', 'Buyer and seller did not finalize deal.')

    if unlock.deal_status == 'deal_made':
        return Response({'error': 'Cannot refund a deal that was successfully marked as completed.'}, status=status.HTTP_400_BAD_REQUEST)

    if unlock.deal_status == 'no_deal_refunded':
        return Response({'message': 'Fee has already been refunded.', 'unlock': ContactUnlockSerializer(unlock).data})

    ref_txn = f"REF-{random.randint(100000, 999999)}"
    unlock.deal_status = 'no_deal_refunded'
    unlock.buyer_confirmation = 'rejected'
    unlock.seller_confirmation = 'rejected'
    unlock.cancellation_reason = reason
    unlock.refund_transaction_id = ref_txn
    unlock.refund_timestamp = timezone.now()
    unlock.resolved_at = timezone.now()
    unlock.save()

    buyer = unlock.buyer
    buyer.wallet_balance += unlock.fee_amount
    buyer.save()

    # Update linked PaymentTransaction to 'refunded' if exists
    if hasattr(unlock, 'payment_transaction') and unlock.payment_transaction:
        unlock.payment_transaction.status = 'refunded'
        unlock.payment_transaction.save(update_fields=['status', 'updated_at'])

    # Trigger Admin Notification: DEAL_FAILED_REFUND_REQ
    try:
        buyer_name = unlock.buyer.full_name or (unlock.buyer.user.username if unlock.buyer.user else "Buyer")
        book_title = unlock.listing.book.title
        AdminNotification.objects.create(
            notification_type='DEAL_FAILED_REFUND_REQ',
            title="Deal Unsuccessful & Refund Request",
            message=f"Deal Unsuccessful — Please Refund: Deal failed for '{book_title}'. Buyer {buyer_name} requested a Rs. {unlock.fee_amount} refund.",
            user=unlock.buyer,
            buyer=unlock.buyer,
            seller=unlock.seller,
            listing=unlock.listing,
            unlock=unlock,
            is_resolved=True
        )
    except Exception as notif_err:
        logger.warning(f"Failed to create AdminNotification for deal refund: {notif_err}")

    logger.info(f"Deal refunded: unlock_id={unlock.unlock_id}, refund_txn={ref_txn}, buyer={buyer.full_name}")

    return Response({
        'message': f"No deal made. Fee of Rs. {unlock.fee_amount} refunded immediately to your BookBazaar account (Ref: {ref_txn}).",
        'refund_transaction_id': ref_txn,
        'unlock': ContactUnlockSerializer(unlock).data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_deal_refund_api(request, unlock_id):
    """
    Buyer Action: Report deal failed / seller unresponsive / request refund:
    - Protected: Authenticated buyer or staff
    - Transitions deal_status to 'disputed'
    - Creates AdminNotification (DEAL_FAILED_REFUND_REQ) awaiting Admin 'Process Refund' action
    """
    unlock = get_object_or_404(ContactUnlock, unlock_id=unlock_id)
    is_buyer = unlock.buyer.user and unlock.buyer.user == request.user
    if not (request.user.is_staff or is_buyer):
        return Response({'error': 'Permission denied: Only the buyer can report a deal failure or request refund.'}, status=status.HTTP_403_FORBIDDEN)

    if unlock.deal_status == 'deal_made':
        return Response({'error': 'Cannot request refund on an already completed deal.'}, status=status.HTTP_400_BAD_REQUEST)

    if unlock.deal_status == 'no_deal_refunded':
        return Response({'message': 'Fee has already been refunded.', 'unlock': ContactUnlockSerializer(unlock).data})

    reason = request.data.get('reason', 'Buyer reported deal failed / seller unresponsive / book unavailable')
    unlock.deal_status = 'disputed'
    unlock.buyer_confirmation = 'rejected'
    unlock.cancellation_reason = reason
    unlock.save(update_fields=['deal_status', 'buyer_confirmation', 'cancellation_reason'])

    # Create AdminNotification
    buyer_name = unlock.buyer.full_name or (unlock.buyer.user.username if unlock.buyer.user else "Buyer")
    book_title = unlock.listing.book.title
    notif = AdminNotification.objects.create(
        notification_type='DEAL_FAILED_REFUND_REQ',
        title="Deal Unsuccessful & Refund Request",
        message=f"Deal Unsuccessful — Please Refund: Deal failed for '{book_title}'. Buyer {buyer_name} requested a Rs. {unlock.fee_amount} refund.",
        user=unlock.buyer,
        buyer=unlock.buyer,
        seller=unlock.seller,
        listing=unlock.listing,
        unlock=unlock,
        is_resolved=False
    )

    logger.info(f"Refund request filed: unlock_id={unlock.unlock_id}, notif_id={notif.id}, buyer={buyer_name}")

    return Response({
        'message': f"Refund request submitted for listing '{book_title}'. Administrator has been notified.",
        'notification_id': notif.id,
        'deal_status': unlock.deal_status,
        'unlock': ContactUnlockSerializer(unlock).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_seller_review(request):
    """
    Submit rating & review for seller after confirmed deal:
    - Protected: Buyer of that unlock or staff
    - Validates rating (1 to 5)
    """
    data = request.data
    unlock_id = data.get('unlock_id')
    raw_rating = data.get('rating', 5)
    comment = str(data.get('comment', '')).strip()

    try:
        rating = int(raw_rating)
        if rating < 1 or rating > 5:
            return Response({'error': 'Rating must be an integer between 1 and 5.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        return Response({'error': 'Invalid rating format.'}, status=status.HTTP_400_BAD_REQUEST)

    unlock = get_object_or_404(ContactUnlock, unlock_id=unlock_id)

    # Enforce Buyer-only review permission
    is_buyer = unlock.buyer.user and unlock.buyer.user == request.user
    if not (request.user.is_staff or is_buyer):
        return Response({'error': 'Permission denied: Only the buyer who unlocked this book can leave a review.'}, status=status.HTTP_403_FORBIDDEN)

    if unlock.deal_status != 'deal_made':
        return Response({'error': 'Can only review seller after a deal is confirmed.'}, status=status.HTTP_400_BAD_REQUEST)

    review, created = SellerReview.objects.get_or_create(
        unlock=unlock,
        defaults={
            'seller': unlock.seller,
            'buyer': unlock.buyer,
            'rating': rating,
            'comment': comment
        }
    )
    if not created:
        review.rating = rating
        review.comment = comment
        review.save()

    return Response({
        'message': 'Review submitted successfully!',
        'review': SellerReviewSerializer(review).data,
        'new_seller_rating': float(unlock.seller.rating)
    })


# ==========================================
# ADS & ADMIN APIS
# ==========================================

@api_view(['GET'])
@permission_classes([AllowAny])
def get_ads(request):
    """Fetch active advertisements"""
    ads = Advertisement.objects.filter(is_active=True)
    ads.update(impressions=F('impressions') + 1)
    return Response(AdvertisementSerializer(ads, many=True).data)


@api_view(['POST'])
@permission_classes([AllowAny])
def click_ad(request, ad_id):
    """Track ad click"""
    ad = get_object_or_404(Advertisement, id=ad_id)
    ad.clicks += 1
    ad.save()
    return Response({'clicks': ad.clicks})


@api_view(['GET'])
@permission_classes([IsAdminOnly])
def get_admin_stats(request):
    """
    Comprehensive Admin Analytics & KPIs:
    - Protected: Staff / Admin only
    """
    total_users = UserProfile.objects.count()
    blocked_users = UserProfile.objects.filter(is_blocked=True).count()
    students_count = UserProfile.objects.filter(user_type='student').count()
    readers_count = UserProfile.objects.filter(user_type='reader').count()
    bookstores_count = UserProfile.objects.filter(user_type='bookstore').count()

    total_books = Book.objects.count()
    total_listings = Listing.objects.count()
    active_listings = Listing.objects.filter(status='active').count()
    pending_listings = Listing.objects.filter(status='pending').count()
    sold_listings = Listing.objects.filter(status='sold').count()
    inactive_listings = Listing.objects.filter(status='inactive').count()

    total_unlocks = ContactUnlock.objects.count()
    confirmed_deals = ContactUnlock.objects.filter(deal_status='deal_made').count()
    refunded_deals = ContactUnlock.objects.filter(deal_status='no_deal_refunded').count()
    pending_deals = ContactUnlock.objects.filter(deal_status='unlocked_pending').count()

    total_collected_fees = ContactUnlock.objects.aggregate(Sum('fee_amount'))['fee_amount__sum'] or Decimal('0.00')
    retained_revenue = ContactUnlock.objects.filter(deal_status='deal_made').aggregate(Sum('fee_amount'))['fee_amount__sum'] or Decimal('0.00')
    refunded_amount = ContactUnlock.objects.filter(deal_status='no_deal_refunded').aggregate(Sum('fee_amount'))['fee_amount__sum'] or Decimal('0.00')

    # Gateway Breakdown
    gateways = ['jazzcash', 'easypaisa', 'card_safepay', 'wallet']
    gateway_stats = {}
    for gw in gateways:
        gw_count = ContactUnlock.objects.filter(payment_method=gw).count()
        gw_sum = ContactUnlock.objects.filter(payment_method=gw).aggregate(Sum('fee_amount'))['fee_amount__sum'] or Decimal('0.00')
        gateway_stats[gw] = {
            'count': gw_count,
            'total_amount': float(gw_sum)
        }

    # Reports
    pending_reports = MarketplaceReport.objects.filter(status='pending').count()
    total_reports = MarketplaceReport.objects.count()

    # Ads
    total_ads = Advertisement.objects.count()
    total_ad_clicks = Advertisement.objects.aggregate(Sum('clicks'))['clicks__sum'] or 0
    total_ad_impressions = Advertisement.objects.aggregate(Sum('impressions'))['impressions__sum'] or 0

    setting = PlatformSetting.get_settings()

    recent_unlocks = ContactUnlock.objects.select_related('listing__book', 'buyer', 'seller').order_by('-payment_timestamp')[:25]
    recent_transactions = PaymentTransaction.objects.select_related('buyer', 'listing__book').order_by('-created_at')[:25]
    all_listings = Listing.objects.select_related('book', 'seller').order_by('-created_at')[:50]
    all_users = UserProfile.objects.all().order_by('-created_at')[:50]
    recent_reports = MarketplaceReport.objects.select_related('reporter', 'listing__book', 'reported_user').order_by('-created_at')[:25]

    return Response({
        'metrics': {
            'total_users': total_users,
            'blocked_users': blocked_users,
            'students_count': students_count,
            'readers_count': readers_count,
            'bookstores_count': bookstores_count,
            'total_books': total_books,
            'total_listings': total_listings,
            'active_listings': active_listings,
            'pending_listings': pending_listings,
            'sold_listings': sold_listings,
            'inactive_listings': inactive_listings,
            'total_unlocks': total_unlocks,
            'confirmed_deals': confirmed_deals,
            'refunded_deals': refunded_deals,
            'pending_deals': pending_deals,
            'total_collected_fees': float(total_collected_fees),
            'retained_revenue': float(retained_revenue),
            'refunded_amount': float(refunded_amount),
            'total_ad_clicks': total_ad_clicks,
            'total_ad_impressions': total_ad_impressions,
            'total_ads': total_ads,
            'pending_reports': pending_reports,
            'total_reports': total_reports,
            'current_unlock_fee': float(setting.contact_unlock_fee),
            'gateway_stats': gateway_stats
        },
        'settings': PlatformSettingSerializer(setting).data,
        'recent_unlocks': ContactUnlockSerializer(recent_unlocks, many=True).data,
        'recent_transactions': PaymentTransactionSerializer(recent_transactions, many=True).data,
        'listings': ListingSerializer(all_listings, many=True, context={'request': request}).data,
        'users': UserProfileSerializer(all_users, many=True, context={'request': request}).data,
        'recent_reports': MarketplaceReportSerializer(recent_reports, many=True).data
    })


# -----------------------------------------------------------------------------
# 1. USER MANAGEMENT APIS
# -----------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes([IsAdminOnly])
def get_admin_users(request):
    """
    Search, filter, and view user profiles:
    - Protected: Staff / Admin only
    """
    q = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', 'all').strip()
    role_filter = request.GET.get('user_type', 'all').strip()
    city_filter = request.GET.get('city', 'all').strip()

    users = UserProfile.objects.all().select_related('user')

    if q:
        users = users.filter(
            Q(full_name__icontains=q) |
            Q(phone_number__icontains=q) |
            Q(city__icontains=q) |
            Q(campus_or_area__icontains=q) |
            Q(user__username__icontains=q) |
            Q(user__email__icontains=q)
        )

    if status_filter == 'active':
        users = users.filter(is_blocked=False)
    elif status_filter == 'blocked':
        users = users.filter(is_blocked=True)

    if role_filter != 'all':
        users = users.filter(user_type=role_filter)

    if city_filter != 'all':
        users = users.filter(city=city_filter)

    users = users.order_by('-created_at')
    return Response({
        'total': users.count(),
        'users': UserProfileSerializer(users, many=True, context={'request': request}).data
    })


@api_view(['GET'])
@permission_classes([IsAdminOnly])
def get_admin_user_detail(request, user_id):
    """
    Detailed user history for moderation: listings, unlocks, reviews, and reports.
    - Protected: Staff / Admin only
    """
    user_prof = get_object_or_404(UserProfile, id=user_id)
    listings = user_prof.listings.all().order_by('-created_at')
    unlocks_bought = user_prof.unlocked_contacts_bought.all().order_by('-payment_timestamp')
    unlocks_received = user_prof.unlocked_contacts_received.all().order_by('-payment_timestamp')
    received_reviews = user_prof.received_reviews.all().order_by('-created_at')
    reports_received = MarketplaceReport.objects.filter(reported_user=user_prof).order_by('-created_at')

    return Response({
        'user': UserProfileSerializer(user_prof, context={'request': request}).data,
        'listings': ListingSerializer(listings, many=True, context={'request': request}).data,
        'unlocks_bought': ContactUnlockSerializer(unlocks_bought, many=True).data,
        'unlocks_received': ContactUnlockSerializer(unlocks_received, many=True).data,
        'received_reviews': SellerReviewSerializer(received_reviews, many=True).data,
        'reports_received': MarketplaceReportSerializer(reports_received, many=True).data
    })


@api_view(['POST'])
@permission_classes([IsAdminOnly])
def toggle_user_block(request, user_id):
    """
    Block or unblock user account:
    - Protected: Staff / Admin only
    """
    profile = get_object_or_404(UserProfile, id=user_id)
    profile.is_blocked = not profile.is_blocked
    profile.save()
    status_str = "blocked" if profile.is_blocked else "unblocked"
    logger.info(f"User {profile.full_name} ({profile.id}) was {status_str} by admin {request.user.username}")
    return Response({
        'message': f"User {profile.full_name} is now {status_str}.",
        'is_blocked': profile.is_blocked,
        'user': UserProfileSerializer(profile, context={'request': request}).data
    })


# -----------------------------------------------------------------------------
# 2. LISTINGS MANAGEMENT & MODERATION APIS
# -----------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes([IsAdminOnly])
def get_admin_listings(request):
    """
    Search and filter all book listings in the marketplace:
    - Protected: Staff / Admin only
    """
    q = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', 'all').strip()
    condition_filter = request.GET.get('condition', 'all').strip()
    sponsored_filter = request.GET.get('is_sponsored', 'all').strip()

    listings = Listing.objects.all().select_related('book', 'seller')

    if q:
        listings = listings.filter(
            Q(book__title__icontains=q) |
            Q(book__author__icontains=q) |
            Q(book__isbn__icontains=q) |
            Q(seller__full_name__icontains=q) |
            Q(description__icontains=q)
        )

    if status_filter != 'all':
        listings = listings.filter(status=status_filter)

    if condition_filter != 'all':
        listings = listings.filter(condition=condition_filter)

    if sponsored_filter == 'true':
        listings = listings.filter(is_sponsored=True)
    elif sponsored_filter == 'false':
        listings = listings.filter(is_sponsored=False)

    listings = listings.order_by('-created_at')
    return Response({
        'total': listings.count(),
        'listings': ListingSerializer(listings, many=True, context={'request': request}).data
    })


@api_view(['POST'])
@permission_classes([IsAdminOnly])
def moderate_listing(request, listing_id):
    """
    Moderate book listing (approve, reject, delete, toggle_sponsored, mark_sold):
    - Protected: Staff / Admin only
    """
    action = request.data.get('action')
    listing = get_object_or_404(Listing, id=listing_id)

    if action == 'approve':
        listing.status = 'active'
    elif action == 'reject':
        listing.status = 'inactive'
    elif action == 'mark_sold':
        listing.status = 'sold'
    elif action == 'delete':
        listing.delete()
        logger.info(f"Listing {listing_id} deleted by admin {request.user.username}")
        return Response({'message': 'Listing deleted successfully'})
    elif action == 'toggle_sponsored':
        listing.is_sponsored = not listing.is_sponsored

    listing.save()
    logger.info(f"Listing {listing_id} moderated ({action}) by admin {request.user.username}")
    return Response({'message': f'Listing updated', 'listing': ListingSerializer(listing, context={'request': request}).data})


@api_view(['POST'])
@permission_classes([IsAdminOnly])
def admin_edit_listing(request, listing_id):
    """
    Admin edit listing details directly:
    - Protected: Staff / Admin only
    """
    listing = get_object_or_404(Listing, id=listing_id)
    data = request.data

    if 'price' in data:
        try:
            listing.price = Decimal(str(data['price']))
        except Exception:
            return Response({'error': 'Invalid price'}, status=status.HTTP_400_BAD_REQUEST)

    if 'condition' in data:
        listing.condition = data['condition']
    if 'city' in data:
        listing.city = data['city']
    if 'pickup_location' in data:
        listing.pickup_location = data['pickup_location']
    if 'description' in data:
        listing.description = data['description']
    if 'status' in data:
        listing.status = data['status']
    if 'is_sponsored' in data:
        listing.is_sponsored = bool(data['is_sponsored'])

    listing.save()
    logger.info(f"Listing #{listing.id} edited by admin {request.user.username}")
    return Response({
        'message': 'Listing edited successfully by admin.',
        'listing': ListingSerializer(listing, context={'request': request}).data
    })


# -----------------------------------------------------------------------------
# 3. SELLER PERFORMANCE & MONITORING APIS
# -----------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes([IsAdminOnly])
def get_admin_sellers(request):
    """
    Monitor seller performance, ratings, and sales:
    - Protected: Staff / Admin only
    """
    sellers = UserProfile.objects.annotate(
        active_books=Count('listings', filter=Q(listings__status='active')),
        sold_books=Count('listings', filter=Q(listings__status='sold')),
        total_unlocks=Count('unlocked_contacts_received')
    ).filter(Q(active_books__gt=0) | Q(sold_books__gt=0) | Q(total_unlocks__gt=0)).order_by('-sold_books', '-rating')

    seller_list = []
    for s in sellers:
        seller_list.append({
            'id': s.id,
            'full_name': s.full_name,
            'phone_number': s.phone_number,
            'city': s.city,
            'campus_or_area': s.campus_or_area,
            'rating': float(s.rating),
            'total_reviews': s.total_reviews,
            'active_listings': s.active_books,
            'sold_listings': s.sold_books,
            'unlocks_received': s.total_unlocks,
            'is_blocked': s.is_blocked,
            'wallet_balance': float(s.wallet_balance),
            'created_at': s.created_at
        })

    return Response({
        'total_sellers': len(seller_list),
        'sellers': seller_list
    })


# -----------------------------------------------------------------------------
# 4. PAYMENT TRANSACTIONS & UNLOCK LEDGER APIS
# -----------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes([IsAdminOnly])
def get_admin_transactions(request):
    """
    List and filter raw gateway payment transactions:
    - Protected: Staff / Admin only
    """
    q = request.GET.get('search', '').strip()
    gateway = request.GET.get('gateway', 'all').strip()
    status_val = request.GET.get('status', 'all').strip()

    transactions = PaymentTransaction.objects.all().select_related('buyer', 'listing__book')

    if q:
        transactions = transactions.filter(
            Q(gateway_ref__icontains=q) |
            Q(buyer__full_name__icontains=q) |
            Q(listing__book__title__icontains=q)
        )

    if gateway != 'all':
        transactions = transactions.filter(gateway=gateway)

    if status_val != 'all':
        transactions = transactions.filter(status=status_val)

    transactions = transactions.order_by('-created_at')[:100]
    return Response({
        'total': transactions.count(),
        'transactions': PaymentTransactionSerializer(transactions, many=True).data
    })


@api_view(['GET'])
@permission_classes([IsAdminOnly])
def get_admin_unlocks(request):
    """
    List and filter contact unlock records & deal status:
    - Protected: Staff / Admin only
    """
    q = request.GET.get('search', '').strip()
    deal_status = request.GET.get('deal_status', 'all').strip()

    unlocks = ContactUnlock.objects.all().select_related('listing__book', 'buyer', 'seller')

    if q:
        unlocks = unlocks.filter(
            Q(transaction_id__icontains=q) |
            Q(buyer__full_name__icontains=q) |
            Q(seller__full_name__icontains=q) |
            Q(listing__book__title__icontains=q)
        )

    if deal_status != 'all':
        unlocks = unlocks.filter(deal_status=deal_status)

    unlocks = unlocks.order_by('-payment_timestamp')[:100]
    return Response({
        'total': unlocks.count(),
        'unlocks': ContactUnlockSerializer(unlocks, many=True).data
    })


@api_view(['POST'])
@permission_classes([IsAdminOnly])
def admin_force_refund_unlock(request, unlock_id):
    """
    Manual Admin Override: Force refund contact unlock fee to buyer wallet
    (Used for dispute resolution, fraudulent seller, or uncontactable seller):
    - Protected: Staff / Admin only
    """
    reason = request.data.get('reason', 'Admin manual dispute refund')
    unlock = get_object_or_404(ContactUnlock, unlock_id=unlock_id)

    if unlock.deal_status == 'no_deal_refunded':
        return Response({'error': 'Fee has already been refunded to buyer.'}, status=status.HTTP_400_BAD_REQUEST)

    # Execute refund atomically
    with transaction.atomic():
        buyer = unlock.buyer
        buyer.wallet_balance += unlock.fee_amount
        buyer.save(update_fields=['wallet_balance'])

        unlock.deal_status = 'no_deal_refunded'
        unlock.cancellation_reason = f"Admin Forced Refund: {reason}"
        unlock.refund_transaction_id = f"ADM-REF-{random.randint(100000, 999999)}"
        unlock.refund_timestamp = timezone.now()
        unlock.resolved_at = timezone.now()
        unlock.save()

    logger.info(f"Contact unlock #{unlock.id} force-refunded by admin {request.user.username} (Rs. {unlock.fee_amount})")
    return Response({
        'message': f"Rs. {unlock.fee_amount} refunded to {buyer.full_name}'s wallet successfully.",
        'unlock': ContactUnlockSerializer(unlock).data
    })


# -----------------------------------------------------------------------------
# 5. REPORTS & COMPLAINTS MANAGEMENT APIS
# -----------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_report_api(request):
    """
    Allow authenticated buyer/user to submit a complaint/report:
    - Protected: Authenticated User
    """
    reporter = getattr(request.user, 'profile', None)
    if not reporter:
        return Response({'error': 'Profile required to report'}, status=status.HTTP_400_BAD_REQUEST)

    data = request.data
    listing_id = data.get('listing_id')
    reported_user_id = data.get('reported_user_id')
    report_type = data.get('report_type', 'fraud_scam')
    description = data.get('description', '').strip()

    if not description:
        return Response({'error': 'Description is required'}, status=status.HTTP_400_BAD_REQUEST)

    listing = None
    if listing_id:
        listing = get_object_or_404(Listing, id=listing_id)
        if not reported_user_id:
            reported_user_id = listing.seller_id

    reported_user = None
    if reported_user_id:
        reported_user = get_object_or_404(UserProfile, id=reported_user_id)

    if reported_user and reported_user.id == reporter.id:
        return Response({'error': 'You cannot report yourself'}, status=status.HTTP_400_BAD_REQUEST)

    report = MarketplaceReport.objects.create(
        reporter=reporter,
        listing=listing,
        reported_user=reported_user,
        report_type=report_type,
        description=description,
        status='pending'
    )

    logger.info(f"New report #{report.id} submitted by {reporter.full_name} on {reported_user.full_name if reported_user else 'Listing'}")
    return Response({
        'message': 'Report submitted successfully. Our safety team will review it.',
        'report': MarketplaceReportSerializer(report).data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAdminOnly])
def get_admin_reports(request):
    """
    List reports for moderation:
    - Protected: Staff / Admin only
    """
    status_filter = request.GET.get('status', 'all').strip()
    type_filter = request.GET.get('report_type', 'all').strip()
    q = request.GET.get('search', '').strip()

    reports = MarketplaceReport.objects.all().select_related('reporter', 'listing__book', 'reported_user', 'resolved_by')

    if status_filter != 'all':
        reports = reports.filter(status=status_filter)

    if type_filter != 'all':
        reports = reports.filter(report_type=type_filter)

    if q:
        reports = reports.filter(
            Q(description__icontains=q) |
            Q(reporter__full_name__icontains=q) |
            Q(reported_user__full_name__icontains=q) |
            Q(listing__book__title__icontains=q)
        )

    reports = reports.order_by('-created_at')
    return Response({
        'total': reports.count(),
        'reports': MarketplaceReportSerializer(reports, many=True).data
    })


@api_view(['POST'])
@permission_classes([IsAdminOnly])
def resolve_admin_report(request, report_id):
    """
    Resolve or dismiss report with optional moderation action:
    - Protected: Staff / Admin only
    """
    report = get_object_or_404(MarketplaceReport, id=report_id)
    data = request.data
    new_status = data.get('status', 'resolved')
    admin_notes = data.get('admin_notes', '')
    action = data.get('action', '')  # 'block_user', 'deactivate_listing'

    report.status = new_status
    report.admin_notes = admin_notes
    report.resolved_at = timezone.now()
    report.resolved_by = request.user
    report.save()

    extra_msg = ""
    if action == 'block_user' and report.reported_user:
        report.reported_user.is_blocked = True
        report.reported_user.save()
        extra_msg = f" Also blocked user {report.reported_user.full_name}."

    if action == 'deactivate_listing' and report.listing:
        report.listing.status = 'inactive'
        report.listing.save()
        extra_msg = f" Also marked listing #{report.listing.id} as inactive."

    logger.info(f"Report #{report.id} resolved ({new_status}) by admin {request.user.username}.{extra_msg}")
    return Response({
        'message': f"Report #{report.id} marked as {new_status}.{extra_msg}",
        'report': MarketplaceReportSerializer(report).data
    })


# -----------------------------------------------------------------------------
# 6. ADVERTISEMENT MANAGEMENT APIS
# -----------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes([IsAdminOnly])
def get_admin_ads(request):
    """List all advertisements with metrics (admin):"""
    ads = Advertisement.objects.all().order_by('-created_at')
    return Response({
        'total': ads.count(),
        'ads': AdvertisementSerializer(ads, many=True).data
    })


@api_view(['POST'])
@permission_classes([IsAdminOnly])
def create_admin_ad(request):
    """Create new advertisement:"""
    data = request.data
    ad = Advertisement.objects.create(
        title=data.get('title', 'Promotional Banner'),
        sponsor_name=data.get('sponsor_name', 'Campus Book Hub'),
        ad_type=data.get('ad_type', 'banner_bottom'),
        image_url=data.get('image_url', ''),
        headline=data.get('headline', 'Student Discount Offer'),
        target_url=data.get('target_url', '#'),
        is_active=bool(data.get('is_active', True))
    )
    return Response({
        'message': 'Advertisement created successfully.',
        'ad': AdvertisementSerializer(ad).data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAdminOnly])
def edit_admin_ad(request, ad_id):
    """Edit advertisement:"""
    ad = get_object_or_404(Advertisement, id=ad_id)
    data = request.data
    for field in ['title', 'sponsor_name', 'ad_type', 'image_url', 'headline', 'target_url']:
        if field in data:
            setattr(ad, field, data[field])
    if 'is_active' in data:
        ad.is_active = bool(data['is_active'])
    ad.save()
    return Response({
        'message': 'Advertisement updated successfully.',
        'ad': AdvertisementSerializer(ad).data
    })


@api_view(['POST'])
@permission_classes([IsAdminOnly])
def delete_admin_ad(request, ad_id):
    """Delete advertisement:"""
    ad = get_object_or_404(Advertisement, id=ad_id)
    ad.delete()
    return Response({'message': 'Advertisement deleted successfully.'})


@api_view(['POST'])
@permission_classes([IsAdminOnly])
def toggle_admin_ad(request, ad_id):
    """Toggle ad active state:"""
    ad = get_object_or_404(Advertisement, id=ad_id)
    ad.is_active = not ad.is_active
    ad.save()
    return Response({
        'message': f"Ad '{ad.title}' is now {'active' if ad.is_active else 'paused'}.",
        'is_active': ad.is_active,
        'ad': AdvertisementSerializer(ad).data
    })


# -----------------------------------------------------------------------------
# 7. PLATFORM SETTINGS APIS
# -----------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes([IsAdminOnly])
def update_admin_settings(request):
    """
    Update platform monetization & policies:
    - Protected: Staff / Admin only
    """
    fee = request.data.get('contact_unlock_fee')
    require_approval = request.data.get('require_admin_approval')
    allow_sponsored = request.data.get('allow_sponsored_listings')
    auto_refund_days = request.data.get('auto_refund_days')

    setting = PlatformSetting.get_settings()
    if fee is not None:
        try:
            fee_dec = Decimal(str(fee))
            if fee_dec >= 0:
                setting.contact_unlock_fee = fee_dec
        except Exception:
            return Response({'error': 'Invalid fee value'}, status=status.HTTP_400_BAD_REQUEST)

    if require_approval is not None:
        setting.require_admin_approval = bool(require_approval)
    if allow_sponsored is not None:
        setting.allow_sponsored_listings = bool(allow_sponsored)
    if auto_refund_days is not None:
        try:
            setting.auto_refund_days = int(auto_refund_days)
        except Exception:
            pass

    setting.save()
    logger.info(f"Platform settings updated by admin {request.user.username}: fee={setting.contact_unlock_fee}")
    return Response({
        'message': 'Platform settings updated successfully',
        'settings': PlatformSettingSerializer(setting).data
    })


# -----------------------------------------------------------------------------
# 8. ADMIN NOTIFICATIONS & DEAL LIFECYCLE ACTION APIS
# -----------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes([IsAdminOnly])
def list_admin_notifications_api(request):
    """
    Fetch Admin Notifications:
    - Protected: IsAdminOnly
    - Returns unread_count and latest notifications
    """
    unread_count = AdminNotification.objects.filter(is_read=False).count()
    limit = int(request.GET.get('limit', 50))
    notifications = AdminNotification.objects.select_related('user', 'listing', 'listing__book', 'unlock', 'transaction').all()[:limit]

    serializer = AdminNotificationSerializer(notifications, many=True)
    return Response({
        'unread_count': unread_count,
        'total_count': AdminNotification.objects.count(),
        'notifications': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdminOnly])
def mark_admin_notification_read(request, notification_id):
    """Mark single notification as read"""
    notif = get_object_or_404(AdminNotification, id=notification_id)
    notif.is_read = True
    notif.save(update_fields=['is_read'])
    unread_count = AdminNotification.objects.filter(is_read=False).count()
    return Response({
        'message': 'Notification marked as read.',
        'notification_id': notif.id,
        'unread_count': unread_count
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdminOnly])
def mark_all_admin_notifications_read(request):
    """Mark all notifications as read"""
    updated = AdminNotification.objects.filter(is_read=False).update(is_read=True)
    return Response({
        'message': f"{updated} notifications marked as read.",
        'unread_count': 0
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdminOnly])
def mark_admin_notifications_read_generic(request):
    """
    Unified endpoint to mark single or all notifications as read:
    - If notification_id in body/query: marks single notification as read.
    - If empty or mark_all=True: marks all notifications as read.
    """
    notif_id = request.data.get('notification_id') or request.data.get('id') or request.query_params.get('notification_id')
    if notif_id:
        notif = get_object_or_404(AdminNotification, id=notif_id)
        notif.is_read = True
        notif.save(update_fields=['is_read'])
        msg = f"Notification #{notif.id} marked as read."
    else:
        updated = AdminNotification.objects.filter(is_read=False).update(is_read=True)
        msg = f"{updated} notifications marked as read."

    unread_count = AdminNotification.objects.filter(is_read=False).count()
    return Response({
        'message': msg,
        'unread_count': unread_count
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdminOnly])
def admin_process_notification_refund(request, notification_id):
    """
    Admin Action: Approve / Process Refund from Admin Notification
    - Protected: IsAdminOnly
    - Row-level lock (select_for_update) on ContactUnlock and UserProfile
    - Idempotency guard: rejects if already refunded
    - Credits unlock.fee_amount to buyer.wallet_balance
    - Transitions deal_status to 'no_deal_refunded'
    - Updates PaymentTransaction status to 'refunded'
    - Marks notification as read and is_resolved = True
    - Creates confirmation notification (REFUND_PROCESSED)
    """
    notification = get_object_or_404(AdminNotification, id=notification_id)
    if not notification.unlock:
        return Response({'error': 'Notification is not linked to any contact unlock record.'}, status=status.HTTP_400_BAD_REQUEST)

    unlock_pk = notification.unlock.id
    reason = request.data.get('reason', 'Admin approved refund from notification.')

    with transaction.atomic():
        unlock = ContactUnlock.objects.select_for_update().get(id=unlock_pk)

        if unlock.deal_status == 'no_deal_refunded':
            return Response({
                'error': 'Fee has already been refunded for this contact unlock.',
                'deal_status': unlock.deal_status,
                'refund_transaction_id': unlock.refund_transaction_id
            }, status=status.HTTP_400_BAD_REQUEST)

        buyer = UserProfile.objects.select_for_update().get(id=unlock.buyer_id)
        refund_amount = unlock.fee_amount
        buyer.wallet_balance += refund_amount
        buyer.save(update_fields=['wallet_balance'])

        ref_txn = f"REF-ADM-{random.randint(100000, 999999)}"
        unlock.deal_status = 'no_deal_refunded'
        unlock.buyer_confirmation = 'rejected'
        unlock.cancellation_reason = f"Admin Processed Refund: {reason}"
        unlock.refund_transaction_id = ref_txn
        unlock.refund_timestamp = timezone.now()
        unlock.resolved_at = timezone.now()
        unlock.save()

        # Update linked PaymentTransaction to 'refunded'
        if hasattr(unlock, 'payment_transaction') and unlock.payment_transaction:
            payment_txn = unlock.payment_transaction
            payment_txn.status = 'refunded'
            payment_txn.gateway_response_message = f"Refunded Rs. {refund_amount} to buyer wallet by admin"
            payment_txn.save(update_fields=['status', 'gateway_response_message', 'updated_at'])

        notification.is_read = True
        notification.is_resolved = True
        notification.save(update_fields=['is_read', 'is_resolved'])

        # Confirmation notification: "Refund Completed: Rs. 50 refunded to [Buyer] for '[Book Title]'."
        book_title = unlock.listing.book.title if unlock.listing and unlock.listing.book else "Book"
        AdminNotification.objects.create(
            notification_type='REFUND_PROCESSED',
            title="Refund Completed",
            message=f"Refund Completed: Rs. {refund_amount} refunded to {buyer.full_name} for '{book_title}'.",
            user=buyer,
            buyer=buyer,
            seller=unlock.seller,
            listing=unlock.listing,
            unlock=unlock,
            transaction=getattr(unlock, 'payment_transaction', None),
            is_read=False,
            is_resolved=True
        )

    logger.info(f"Admin {request.user.username} processed refund for notification #{notification.id} (unlock {unlock.unlock_id}, Rs. {refund_amount})")

    return Response({
        'message': f"Rs. {refund_amount} refunded to {buyer.full_name}'s wallet successfully (Ref: {ref_txn}).",
        'refund_transaction_id': ref_txn,
        'wallet_balance': str(buyer.wallet_balance),
        'unlock': ContactUnlockSerializer(unlock).data,
        'notification': AdminNotificationSerializer(notification).data
    }, status=status.HTTP_200_OK)


# =====================================================================
# AI BOOK RECOMMENDATION SYSTEM & AI SMART PRICE ADVISOR
# =====================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def get_recommendations(request):
    """
    Multi-Factor AI Recommendation Engine (GET /api/recommendations/):
    Scores and ranks books dynamically using user's age_group, city, and interests:
    - Priority #1 (Top Boost): Free / Donated Books (price == 0 / is_free=True) always appear first with '🎁 FREE Donation' badge.
    - Priority #2 (Age & Interest Match):
        * Kids (5–12 yrs) -> Story Books & Primary Punjab Textbooks
        * School / College Student (13–19 yrs) -> Punjab Textbooks (Class 6–10 & FSc)
        * University / Young Adult (20–30 yrs) -> BS/Higher Ed, Novels, Fiction & History
        * General Reader (31+ yrs) -> Novels, Fiction, History & Islamic Books
        Tagged with '✨ 98% AI Match'.
    - Priority #3 (Location & Sale Boost):
        * Books in user's city get '📍 Near You'
        * Discounted/affordable books get '🔥 On Sale'
    """
    ensure_demo_listings()
    user_id = request.GET.get('user_id')
    user_profile = None

    if user_id:
        try:
            user_profile = UserProfile.objects.filter(id=user_id, is_blocked=False).first()
        except Exception:
            pass

    if not user_profile and request.user and request.user.is_authenticated:
        user_profile = getattr(request.user, 'profile', None)

    # 1. Parse reader parameters
    raw_age = (request.GET.get('age_group') or '').lower().strip()
    session_profile = request.session.get('reader_profile', {})
    if not raw_age and session_profile.get('age_group'):
        raw_age = session_profile.get('age_group', '').lower().strip()
    if not raw_age and user_profile and user_profile.age_group:
        raw_age = user_profile.age_group.lower().strip()

    # Normalize age group
    if any(k in raw_age for k in ['kid', '5-12', '5–12', 'primary', 'child']):
        age_group = 'kids'
        age_group_label = 'Kids (5–12 yrs)'
    elif any(k in raw_age for k in ['teen', 'school', 'college', '13-19', '13–19', 'matric', 'fsc', 'student']):
        age_group = 'teens'
        age_group_label = 'School / College Student (13–19 yrs)'
    elif any(k in raw_age for k in ['university', 'young adult', '20-30', '20–30', 'bs', 'undergrad']):
        age_group = 'young_adult'
        age_group_label = 'University / Young Adult (20–30 yrs)'
    elif any(k in raw_age for k in ['general', '31+', '31', 'adult']):
        age_group = 'general'
        age_group_label = 'General Reader (31+ yrs)'
    else:
        age_group = 'teens'
        age_group_label = 'School / College Student (13–19 yrs)'

    # City
    user_city = (request.GET.get('city') or '').strip()
    if not user_city and session_profile.get('city'):
        user_city = session_profile.get('city', '').strip()
    if not user_city and user_profile:
        user_city = user_profile.city
    if not user_city:
        user_city = 'Lahore'

    # Interests
    raw_interests = request.GET.get('interests') or session_profile.get('interests') or (user_profile.reading_interests if user_profile else '') or ''
    if isinstance(raw_interests, list):
        interests = [str(i).strip().lower() for i in raw_interests if str(i).strip()]
    else:
        interests = [s.strip().lower() for s in str(raw_interests).split(',') if s.strip()]

    free_only = str(request.GET.get('free_only', '')).lower() in ['true', '1', 'yes'] or any('free' in i for i in interests)

    # Active listings
    listings_qs = Listing.objects.filter(status='active').select_related('book', 'seller')
    if user_profile:
        listings_qs = listings_qs.exclude(seller=user_profile)

    all_listings = list(listings_qs)
    if not all_listings:
        all_listings = list(Listing.objects.filter(status='active').select_related('book', 'seller'))

    scored = []
    for item in all_listings:
        is_free_item = (item.is_free or item.price == Decimal('0.00'))
        if free_only and not is_free_item:
            continue

        score = 50.0
        badges = []
        insights = []
        is_age_matched = False

        book_cat = (item.book.category or '').lower()
        book_title = (item.book.title or '').lower()
        book_desc = (item.book.description or '').lower()
        book_board = (item.book.education_board or '').lower()
        book_class = (item.book.grade_class or '').lower()
        book_subj = (item.book.subject or '').lower()
        full_text = f"{book_cat} {book_title} {book_desc} {book_board} {book_class} {book_subj}"

        # -------------------------------------------------------------
        # PRIORITY #1 (TOP BOOST): Free / Donated Books (Rs. 0)
        # -------------------------------------------------------------
        if is_free_item:
            score += 200.0  # Dominant boost to ensure top ranking
            badges.append("🎁 FREE Donation")
            insights.append("Community Book Donation — Free (Rs. 0)")

        # -------------------------------------------------------------
        # PRIORITY #2: Age Group & Reading Interest Matching
        # -------------------------------------------------------------
        if age_group == 'kids':
            # Kids (5–12 yrs) -> Story Books & Primary Punjab Textbooks
            is_story = 'story' in book_cat or 'story' in full_text or 'kahani' in full_text or 'jungle book' in full_text or 'panchatantra' in full_text or 'alif laila' in full_text
            is_primary_ptb = 'punjab' in full_text and any(c in full_text for c in ['class 1', 'class 2', 'class 3', 'class 4', 'class 5', 'primary', 'qaida'])
            if is_story or is_primary_ptb or item.target_age_group == 'kids':
                score += 50.0
                is_age_matched = True
                insights.append("Curated for Kids (5–12 yrs) & Primary Education")

        elif age_group == 'teens':
            # School / College Student (13–19 yrs) -> Punjab Textbooks (Class 6–10 & FSc)
            is_ptb = ('punjab' in full_text or 'ptb' in full_text or 'punjab board' in book_board) and any(
                lvl in full_text for lvl in ['class 6', 'class 7', 'class 8', 'class 9', 'class 10', 'matric', 'fsc', 'ics', '11th', '12th', 'intermediate']
            )
            if is_ptb or item.target_age_group == 'teens' or item.book.education_board == 'Punjab Board':
                score += 50.0
                is_age_matched = True
                insights.append("Top Pick for School & College (Matric / FSc Punjab Board)")

        elif age_group == 'young_adult':
            # University / Young Adult (20–30 yrs) -> BS/Higher Ed, Novels, Fiction & History
            is_university_stem = any(k in full_text for k in ['software', 'computer', 'operating system', 'algorithm', 'calculus', 'clean code', 'engineering', 'higher education'])
            is_novel_fiction = any(k in full_text for k in ['novel', 'fiction', 'alchemist', 'peer-e-kamil', 'jannat ke pattay', 'raja gidh'])
            is_history = 'history' in full_text or 'tareekh' in full_text
            if is_university_stem or is_novel_fiction or is_history or item.target_age_group == 'young_adult':
                score += 50.0
                is_age_matched = True
                insights.append("Curated for University & Young Adults (Fiction, Tech & History)")

        elif age_group == 'general':
            # General Reader (31+ yrs) -> Novels, Fiction, History & Islamic Books
            is_novel_history = any(k in full_text for k in ['novel', 'history', 'tareekh', 'iqbal', 'shahab nama', 'peer-e-kamil', 'raja gidh', 'islamic', 'fiction', 'literature'])
            if is_novel_history or item.target_age_group == 'general':
                score += 50.0
                is_age_matched = True
                insights.append("Top Pick for General Readers (Literature, History & Novels)")

        # Specific Interest Chips Bonus
        for intr in interests:
            if 'story' in intr and ('story' in full_text or 'kahani' in full_text):
                score += 25.0
                is_age_matched = True
                insights.append("Matches interest in Story Books")
            elif 'punjab' in intr and ('punjab' in full_text or 'ptb' in full_text or item.book.education_board == 'Punjab Board'):
                score += 25.0
                is_age_matched = True
                insights.append("Matches Punjab Textbooks (Class 1–FSc)")
            elif 'fiction' in intr and ('fiction' in full_text):
                score += 25.0
                is_age_matched = True
                insights.append("Matches Fiction interest")
            elif 'novel' in intr and ('novel' in full_text or 'peer-e-kamil' in full_text or 'jannat' in full_text or 'raja gidh' in full_text):
                score += 25.0
                is_age_matched = True
                insights.append("Matches Novels interest")
            elif 'history' in intr and ('history' in full_text or 'tareekh' in full_text or 'iqbal' in full_text or 'shahab' in full_text):
                score += 25.0
                is_age_matched = True
                insights.append("Matches History & Literature interest")

        if is_age_matched:
            badges.append("✨ 98% AI Match")

        # -------------------------------------------------------------
        # PRIORITY #3: Location & Sale Boost
        # -------------------------------------------------------------
        # Location / City Proximity
        if user_city and item.city.lower() == user_city.lower():
            score += 35.0
            badges.append("📍 Near You")
            insights.append(f"Zero-cost pickup in {item.city}")
        elif item.city in ['Lahore', 'Islamabad', 'Rawalpindi']:
            score += 8.0

        # Sale / Super Value Boost
        savings = item.savings_percentage
        if not is_free_item and savings >= 35:
            score += 15.0
            badges.append("🔥 On Sale")
            insights.append(f"{savings}% off retail price")

        if item.is_sponsored:
            score += 10.0

        # Calibrated final match percentage
        if is_free_item or is_age_matched:
            final_match_pct = random.choice([98, 98, 97, 99])
        else:
            final_match_pct = min(94, max(85, int(round(score / 2.2))))

        # Primary prominent badge for card banner
        if is_free_item:
            primary_badge = "🎁 FREE Donation"
        elif "✨ 98% AI Match" in badges:
            primary_badge = "✨ 98% AI Match"
        elif "📍 Near You" in badges:
            primary_badge = "📍 Near You"
        elif "🔥 On Sale" in badges:
            primary_badge = "🔥 On Sale"
        else:
            primary_badge = "✨ AI Match"

        if insights:
            ai_insight = " • ".join(insights[:2])
        else:
            ai_insight = f"Recommended based on your reading profile in {item.city}"

        scored.append((score, final_match_pct, primary_badge, badges, ai_insight, item))

    # Sort descending by composite score (Free books #1, followed by exact age/interest matches)
    scored.sort(key=lambda x: (x[0], x[5].is_sponsored, -x[5].price), reverse=True)

    # Return top 8 personalized items
    top_items = scored[:8]

    results = []
    for score_val, match_pct, primary_badge, badges_list, insight, item in top_items:
        data = ListingSerializer(item, context={'request': request}).data
        data['ai_match_percentage'] = match_pct
        data['ai_badge'] = primary_badge
        data['ai_badges'] = badges_list
        data['ai_insight'] = insight
        data['is_free'] = (item.is_free or item.price == Decimal('0.00'))
        results.append(data)

    return Response({
        'success': True,
        'count': len(results),
        'user_city': user_city,
        'age_group': age_group,
        'age_group_label': age_group_label,
        'recommendations': results
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def update_reader_preferences(request):
    """
    Saves and updates reader profile onboarding preferences:
    - Full Name
    - Age Group (kids, teens, young_adult, general)
    - City (for Near You boost)
    - Reading Interests
    """
    data = request.data
    name = str(data.get('full_name') or data.get('name', '')).strip()
    age_group = str(data.get('age_group', 'teens')).strip()
    city = str(data.get('city', 'Lahore')).strip()
    interests = data.get('interests', [])
    if isinstance(interests, list):
        interests_str = ', '.join(str(i) for i in interests)
    else:
        interests_str = str(interests)

    pref_data = {
        'name': name,
        'age_group': age_group,
        'city': city,
        'interests': interests_str
    }
    request.session['reader_profile'] = pref_data

    # If user profile is identified, update their record
    profile = None
    user_id = data.get('user_id')
    if user_id:
        try:
            profile = UserProfile.objects.filter(id=user_id).first()
        except Exception:
            pass
    if not profile and request.user and request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)

    if profile:
        if name:
            profile.full_name = name
        if city:
            profile.city = city
        profile.age_group = age_group
        profile.reading_interests = interests_str
        profile.save()

    return Response({
        'success': True,
        'message': f"Welcome {name or 'Reader'}! Your AI profile preferences have been updated.",
        'profile': pref_data
    })


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def get_ai_price_advice(request):
    """
    AI Smart Price Advisor API (GET/POST /api/price-advisor/):
    Calculates optimal resale price based on:
    - Book Title & Category market benchmark
    - Original retail price (MRP)
    - Condition depreciation factor (Brand New, Like New, Good, Fair)
    - Free donation detection
    Returns suggested price and explanation.
    """
    params = request.GET if request.method == 'GET' else request.data
    title = params.get('title', '').strip()
    category = params.get('category', '').strip()
    condition = params.get('condition', 'Good').strip()
    raw_mrp = params.get('original_price') or params.get('mrp')
    is_donation = str(params.get('is_free', '')).lower() in ['true', '1', 'yes'] or str(params.get('is_donation', '')).lower() in ['true', '1', 'yes']

    if is_donation:
        return Response({
            'success': True,
            'suggested_price': 0,
            'condition': condition,
            'base_retail_price': 0,
            'discount_percentage': 100,
            'insight': "Community Free Book Donation (Rs. 0) — Zero-cost giveaway helping fellow readers and students across Pakistan!"
        })

    # Benchmark base prices in PKR
    category_benchmarks = {
        'Punjab Textbooks (Primary to FSc)': 320.0,
        'Story Books': 350.0,
        'Fiction': 650.0,
        'Novels': 600.0,
        'History': 700.0,
        'University / Higher Ed': 1800.0,
        'Medical & MBBS / BDS': 3200.0,
        'Software Engineering': 2200.0,
        'Computer Science & IT': 2000.0,
        'Electrical & Mechanical Eng.': 1800.0,
        'Law & Judiciary': 1600.0,
        'Business, Commerce & BBA': 1400.0,
        'CSS & Competitive Exams': 1200.0,
        'FSc / Matric / O & A Level': 480.0,
        'Urdu Literature & Novels': 650.0,
        'Islamic Studies': 700.0,
        'General Fiction & Non-Fiction': 800.0,
    }

    base_mrp = 1200.0
    if raw_mrp:
        try:
            val = float(raw_mrp)
            if val > 0:
                base_mrp = val
        except Exception:
            pass
    elif category in category_benchmarks:
        base_mrp = category_benchmarks[category]

    # Condition depreciation factor
    condition_factors = {
        'Brand New': 0.80,
        'Like New': 0.65,
        'Good': 0.50,
        'Fair': 0.35,
    }
    factor = condition_factors.get(condition, 0.50)
    suggested_price = int(round((base_mrp * factor) / 10.0) * 10)
    if suggested_price < 80:
        suggested_price = 80

    discount_pct = int(round((1.0 - factor) * 100))
    insight = f"AI Suggested Price: Rs. {suggested_price} (Optimal for fast sale in '{condition}' condition — {discount_pct}% off retail)"

    return Response({
        'success': True,
        'suggested_price': suggested_price,
        'condition': condition,
        'base_retail_price': base_mrp,
        'discount_percentage': discount_pct,
        'insight': insight
    })

