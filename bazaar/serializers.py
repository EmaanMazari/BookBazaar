from decimal import Decimal
from rest_framework import serializers
from bazaar.models import (
    UserProfile, Book, Listing, ContactUnlock, SellerReview,
    Advertisement, PlatformSetting, Favorite, PaymentTransaction,
    MarketplaceReport, AdminNotification
)

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    profile_picture_url = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    active_listings_count = serializers.SerializerMethodField()
    sold_listings_count = serializers.SerializerMethodField()
    unlocks_bought_count = serializers.SerializerMethodField()
    unlocks_received_count = serializers.SerializerMethodField()
    free_trial_remaining = serializers.SerializerMethodField()
    is_free_trial_eligible = serializers.SerializerMethodField()
    trial_unlocks_used = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'full_name', 'phone_number', 'city', 
            'campus_or_area', 'profile_picture_url', 'user_type', 'age_group', 'reading_interests', 'rating', 'total_reviews', 
            'wallet_balance', 'is_blocked', 'created_at',
            'active_listings_count', 'sold_listings_count',
            'unlocks_bought_count', 'unlocks_received_count',
            'free_trial_remaining', 'is_free_trial_eligible', 'trial_unlocks_used'
        ]

    def get_free_trial_remaining(self, obj):
        used = obj.unlocked_contacts_bought.count()
        return max(0, 2 - used)

    def get_is_free_trial_eligible(self, obj):
        return obj.unlocked_contacts_bought.count() < 2

    def get_trial_unlocks_used(self, obj):
        return obj.unlocked_contacts_bought.count()

    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            return obj.profile_picture.url
        return None

    def get_active_listings_count(self, obj):
        return obj.listings.filter(status='active').count()

    def get_sold_listings_count(self, obj):
        return obj.listings.filter(status='sold').count()

    def get_unlocks_bought_count(self, obj):
        return obj.unlocked_contacts_bought.count()

    def get_unlocks_received_count(self, obj):
        return obj.unlocked_contacts_received.count()

    def get_phone_number(self, obj):
        """
        Privacy protection: Mask phone numbers for public list/profile endpoints.
        Full phone number is only visible to the user themselves, or staff/administrators.
        """
        request = self.context.get('request')
        is_owner = self.context.get('is_owner', False)
        if is_owner:
            return obj.phone_number
        if request and request.user and request.user.is_authenticated:
            if request.user.is_staff or (hasattr(obj, 'user') and obj.user == request.user):
                return obj.phone_number
        raw = obj.phone_number or ''
        if len(raw) >= 4:
            return f"{raw[:4]}-*******"
        return "03XX-*******"


class BookSerializer(serializers.ModelSerializer):
    lowest_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_offers = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Book
        fields = [
            'id', 'isbn', 'title', 'author', 'publisher', 'edition',
            'category', 'education_board', 'grade_class', 'subject',
            'description', 'cover_image', 'original_retail_price',
            'lowest_price', 'total_offers', 'target_age_group', 'created_at'
        ]


class ListingSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    seller_name = serializers.CharField(source='seller.full_name', read_only=True)
    seller_phone = serializers.SerializerMethodField()
    seller_rating = serializers.DecimalField(source='seller.rating', max_digits=3, decimal_places=2, read_only=True)
    seller_reviews_count = serializers.IntegerField(source='seller.total_reviews', read_only=True)
    seller_city = serializers.CharField(source='seller.city', read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    display_image = serializers.CharField(source='display_image_url', read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_contact_unlocked = serializers.SerializerMethodField()
    pdf_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Listing
        fields = [
            'id', 'book', 'seller_id', 'seller_name', 'seller_phone', 'seller_rating', 
            'seller_reviews_count', 'seller_city', 'condition', 'price', 
            'city', 'pickup_location', 'description', 'photo_url', 'image',
            'display_image', 'status', 'is_sponsored', 'is_free', 'target_age_group',
            'views_count', 'savings_percentage', 
            'is_favorited', 'is_contact_unlocked', 'pdf_url', 'created_at'
        ]

    def get_seller_phone(self, obj):
        """
        Security requirement:
        Only reveal phone if current user is seller, admin, or has a verified ContactUnlock.
        Otherwise mask the phone number.
        """
        request = self.context.get('request')
        if request and request.user and request.user.is_staff:
            return obj.seller.phone_number

        if request and request.user and request.user.is_authenticated:
            if hasattr(obj.seller, 'user') and obj.seller.user == request.user:
                return obj.seller.phone_number
            profile = getattr(request.user, 'profile', None)
            if profile and ContactUnlock.objects.filter(listing=obj, buyer=profile).exists():
                return obj.seller.phone_number

        # Mask phone number for public view
        raw = obj.seller.phone_number or ''
        if len(raw) >= 4:
            return f"{raw[:4]}-*******"
        return "03XX-*******"

    def get_is_contact_unlocked(self, obj):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            profile = getattr(request.user, 'profile', None)
            if profile:
                return ContactUnlock.objects.filter(listing=obj, buyer=profile).exists()
        return False

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            profile = getattr(request.user, 'profile', None)
            if profile:
                return Favorite.objects.filter(user=profile, listing=obj).exists()
        return False

    def get_pdf_url(self, obj):
        if obj.is_free or obj.price == Decimal('0.00') or obj.pdf_file:
            return f"/api/listings/{obj.id}/download-pdf/"
        return None


class FavoriteSerializer(serializers.ModelSerializer):
    listing = ListingSerializer(read_only=True)
    
    class Meta:
        model = Favorite
        fields = ['id', 'user_id', 'listing', 'created_at']


class PaymentTransactionSerializer(serializers.ModelSerializer):
    buyer_name = serializers.CharField(source='buyer.full_name', read_only=True)
    listing_title = serializers.CharField(source='listing.book.title', read_only=True)
    listing_isbn = serializers.CharField(source='listing.book.isbn', read_only=True)
    seller_name = serializers.CharField(source='listing.seller.full_name', read_only=True)

    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'transaction_id', 'gateway_ref', 'buyer', 'buyer_name',
            'listing', 'listing_title', 'listing_isbn', 'seller_name',
            'amount', 'currency', 'gateway', 'status',
            'gateway_response_code', 'gateway_response_message',
            'created_at', 'updated_at', 'verified_at', 'unlock'
        ]
        read_only_fields = fields


class ContactUnlockSerializer(serializers.ModelSerializer):
    listing_title = serializers.CharField(source='listing.book.title', read_only=True)
    listing_isbn = serializers.CharField(source='listing.book.isbn', read_only=True)
    listing_price = serializers.DecimalField(source='listing.price', max_digits=10, decimal_places=2, read_only=True)
    buyer_name = serializers.CharField(source='buyer.full_name', read_only=True)
    buyer_phone = serializers.CharField(source='buyer.phone_number', read_only=True)
    seller_name = serializers.CharField(source='seller.full_name', read_only=True)
    seller_phone = serializers.CharField(source='seller.phone_number', read_only=True)
    seller_city = serializers.CharField(source='seller.city', read_only=True)
    pickup_location = serializers.CharField(source='listing.pickup_location', read_only=True)
    has_review = serializers.SerializerMethodField()

    class Meta:
        model = ContactUnlock
        fields = [
            'id', 'unlock_id', 'listing_id', 'listing_title', 'listing_isbn', 
            'listing_price', 'buyer_id', 'buyer_name', 'buyer_phone',
            'seller_id', 'seller_name', 'seller_phone', 'seller_city', 
            'pickup_location', 'fee_amount', 'payment_method', 'transaction_id', 
            'payment_timestamp', 'deal_status', 'buyer_confirmation', 
            'seller_confirmation', 'cancellation_reason', 'refund_transaction_id', 
            'refund_timestamp', 'has_review'
        ]

    def get_has_review(self, obj):
        return hasattr(obj, 'review') and obj.review is not None


class SellerReviewSerializer(serializers.ModelSerializer):
    buyer_name = serializers.CharField(source='buyer.full_name', read_only=True)
    seller_name = serializers.CharField(source='seller.full_name', read_only=True)

    class Meta:
        model = SellerReview
        fields = ['id', 'unlock', 'seller', 'seller_name', 'buyer', 'buyer_name', 'rating', 'comment', 'created_at']


class AdvertisementSerializer(serializers.ModelSerializer):
    ctr = serializers.SerializerMethodField()

    class Meta:
        model = Advertisement
        fields = [
            'id', 'title', 'sponsor_name', 'ad_type', 'image_url', 'headline',
            'target_url', 'impressions', 'clicks', 'is_active', 'created_at', 'ctr'
        ]

    def get_ctr(self, obj):
        if obj.impressions > 0:
            return round((obj.clicks / obj.impressions) * 100, 1)
        return 0.0


class PlatformSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformSetting
        fields = ['platform_name', 'contact_unlock_fee', 'auto_refund_days', 'require_admin_approval', 'allow_sponsored_listings']


class MarketplaceReportSerializer(serializers.ModelSerializer):
    reporter_name = serializers.CharField(source='reporter.full_name', read_only=True)
    reporter_phone = serializers.CharField(source='reporter.phone_number', read_only=True)
    listing_title = serializers.CharField(source='listing.book.title', read_only=True)
    listing_isbn = serializers.CharField(source='listing.book.isbn', read_only=True)
    reported_user_name = serializers.CharField(source='reported_user.full_name', read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    resolved_by_username = serializers.CharField(source='resolved_by.username', read_only=True)

    class Meta:
        model = MarketplaceReport
        fields = [
            'id', 'report_id', 'reporter', 'reporter_name', 'reporter_phone',
            'listing', 'listing_title', 'listing_isbn',
            'reported_user', 'reported_user_name',
            'report_type', 'report_type_display',
            'description', 'status', 'status_display',
            'admin_notes', 'created_at', 'resolved_at', 'resolved_by', 'resolved_by_username'
        ]
        read_only_fields = ['id', 'report_id', 'created_at', 'resolved_at', 'resolved_by']


class AdminNotificationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True, default='')
    user_phone = serializers.CharField(source='user.phone_number', read_only=True, default='')
    buyer_name = serializers.CharField(source='buyer.full_name', read_only=True, default='')
    buyer_phone = serializers.CharField(source='buyer.phone_number', read_only=True, default='')
    seller_name = serializers.CharField(source='seller.full_name', read_only=True, default='')
    seller_phone = serializers.CharField(source='seller.phone_number', read_only=True, default='')
    book_title = serializers.CharField(source='listing.book.title', read_only=True, default='')
    listing_id = serializers.IntegerField(source='listing.id', read_only=True, default=None)
    unlock_uuid = serializers.UUIDField(source='unlock.unlock_id', read_only=True, default=None)
    unlock_deal_status = serializers.CharField(source='unlock.deal_status', read_only=True, default='')
    fee_amount = serializers.DecimalField(source='unlock.fee_amount', max_digits=10, decimal_places=2, read_only=True, default=None)
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)

    class Meta:
        model = AdminNotification
        fields = [
            'id', 'notification_type', 'notification_type_display', 'title', 'message',
            'user', 'user_name', 'user_phone',
            'buyer', 'buyer_name', 'buyer_phone',
            'seller', 'seller_name', 'seller_phone',
            'listing', 'listing_id', 'book_title',
            'transaction', 'unlock', 'unlock_uuid', 'unlock_deal_status', 'fee_amount',
            'is_read', 'is_resolved', 'created_at'
        ]
