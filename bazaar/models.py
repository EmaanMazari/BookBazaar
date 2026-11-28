from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import uuid

class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('reader', 'General Reader'),
        ('bookstore', 'Bookstore / Publisher'),
        ('admin', 'Administrator'),
    ]

    CITIES = [
        ('Islamabad', 'Islamabad'),
        ('Lahore', 'Lahore'),
        ('Karachi', 'Karachi'),
        ('Rawalpindi', 'Rawalpindi'),
        ('Quetta', 'Quetta'),
        ('Gwadar', 'Gwadar'),
        ('Turbat', 'Turbat'),
        ('Khuzdar', 'Khuzdar'),
        ('Sibi', 'Sibi'),
        ('Zhob', 'Zhob'),
        ('Balochistan', 'Balochistan'),
        ('Balochistan (All Cities)', 'Balochistan (All Cities)'),
        ('Multan', 'Multan'),
        ('Faisalabad', 'Faisalabad'),
        ('Peshawar', 'Peshawar'),
        ('Sialkot', 'Sialkot'),
        ('Gujranwala', 'Gujranwala'),
        ('Hyderabad', 'Hyderabad'),
        ('Rahim Yar Khan', 'Rahim Yar Khan'),
        ('Bahawalpur', 'Bahawalpur'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', null=True, blank=True)
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20, unique=True, help_text="e.g. 03001234567")
    city = models.CharField(max_length=80, choices=CITIES, default='Islamabad', db_index=True)
    campus_or_area = models.CharField(max_length=150, default='University Campus / Student Center', blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='student', db_index=True)
    age_group = models.CharField(max_length=30, default='teens', blank=True, help_text="e.g. kids, teens, young_adult, general")
    reading_interests = models.CharField(max_length=255, default='', blank=True, help_text="Comma-separated reading interests")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    total_reviews = models.IntegerField(default=0)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="PKR Balance")
    is_blocked = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.phone_number}) - {self.city}"

    def update_rating(self):
        reviews = SellerReview.objects.filter(seller=self)
        if reviews.exists():
            avg = reviews.aggregate(models.Avg('rating'))['rating__avg']
            self.rating = round(avg, 2)
            self.total_reviews = reviews.count()
            self.save()


class Book(models.Model):
    CATEGORY_CHOICES = [
        ('Punjab Textbooks (Primary to FSc)', 'Punjab Textbooks (Primary to FSc)'),
        ('Story Books', 'Story Books'),
        ('Fiction', 'Fiction'),
        ('Novels', 'Novels'),
        ('History', 'History'),
        ('University / Higher Ed', 'University / Higher Ed'),
        ('Computer Science & IT', 'Computer Science & IT'),
        ('Software Engineering', 'Software Engineering'),
        ('Electrical & Mechanical Eng.', 'Electrical & Mechanical Eng.'),
        ('Medical & MBBS / BDS', 'Medical & MBBS / BDS'),
        ('FSc / Matric / O & A Level', 'FSc / Matric / O & A Level'),
        ('Business, Commerce & BBA', 'Business, Commerce & BBA'),
        ('Urdu Literature & Novels', 'Urdu Literature & Novels'),
        ('Islamic Studies', 'Islamic Studies'),
        ('Law & Judiciary', 'Law & Judiciary'),
        ('CSS & Competitive Exams', 'CSS & Competitive Exams'),
        ('General Fiction & Non-Fiction', 'General Fiction & Non-Fiction'),
    ]

    BOARD_CHOICES = [
        ('Punjab Board', 'Punjab Board (BISE Lahore, Rawalpindi, Multan, Faisalabad, etc.)'),
        ('Federal Board', 'Federal Board (FBISE Islamabad)'),
        ('Sindh Board', 'Sindh Board (BIEK / BSEK Karachi)'),
        ('KPK Board', 'KPK Board (BISE Peshawar / Abbottabad)'),
        ('Balochistan Board', 'Balochistan Board (BISE Quetta)'),
        ('Cambridge', 'Cambridge / Edexcel (O Level / A Level / IGCSE)'),
        ('Higher Education / University', 'Higher Education / University (HEC, NUST, QAU, PU, FAST, etc.)'),
        ('General / None', 'General / None'),
    ]

    CLASS_CHOICES = [
        ('Primary & Middle (Class 1-8)', 'Primary & Middle (Class 1-8)'),
        ('Matric (9th - 10th)', 'Matric (9th - 10th)'),
        ('Intermediate / FSc / ICS (11th - 12th)', 'Intermediate / FSc / ICS (11th - 12th)'),
        ('Bachelor / BS / Undergrad', 'Bachelor / BS / Undergrad'),
        ('Master / Postgraduate', 'Master / Postgraduate'),
        ('CSS / PMS / Entry Test', 'CSS / PMS / Entry Test'),
        ('General Reading', 'General Reading'),
    ]

    isbn = models.CharField(max_length=20, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255, blank=True, default='')
    edition = models.CharField(max_length=50, blank=True, default='')
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='Software Engineering', db_index=True)
    education_board = models.CharField(max_length=100, choices=BOARD_CHOICES, default='Higher Education / University', blank=True, db_index=True)
    grade_class = models.CharField(max_length=100, choices=CLASS_CHOICES, default='Bachelor / BS / Undergrad', blank=True, db_index=True)
    subject = models.CharField(max_length=100, blank=True, default='')
    target_age_group = models.CharField(max_length=30, default='all', blank=True, db_index=True, help_text="kids, teens, young_adult, general, or all")
    description = models.TextField(blank=True, default='')
    cover_image = models.TextField(blank=True, default='', help_text="URL or Base64 data")
    original_retail_price = models.DecimalField(max_digits=10, decimal_places=2, default=1500.00, help_text="Estimated new book price in PKR")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} (ISBN: {self.isbn})"

    @property
    def lowest_price(self):
        active_listings = self.listings.filter(status='active')
        if active_listings.exists():
            return active_listings.order_by('price').first().price
        return None

    @property
    def total_offers(self):
        return self.listings.filter(status='active').count()


class Listing(models.Model):
    CONDITION_CHOICES = [
        ('Brand New', 'Brand New (Unused, flawless)'),
        ('Like New', 'Like New (Minimal shelf wear, no writing)'),
        ('Good', 'Good (Clean pages, minor highlight/notes)'),
        ('Fair', 'Fair (Readable, worn cover/pages)'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending', 'Pending Admin Approval'),
        ('sold', 'Sold / Handed Over'),
        ('inactive', 'Inactive / Paused'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='listings')
    seller = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='listings')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='Good')
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Seller chosen price in PKR")
    city = models.CharField(max_length=80, default='Islamabad', db_index=True)
    pickup_location = models.CharField(max_length=150, blank=True, default='Campus Gate 2 / Near University Library')
    description = models.TextField(blank=True, default='')
    photo_url = models.TextField(blank=True, default='')
    image = models.ImageField(upload_to='listings/', blank=True, null=True, help_text="Actual uploaded book photo")
    pdf_file = models.FileField(upload_to='book_pdfs/', blank=True, null=True, help_text="Optional soft copy PDF file")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', db_index=True)
    is_sponsored = models.BooleanField(default=False, help_text="Promoted sponsored listing shown at top", db_index=True)
    is_free = models.BooleanField(default=False, db_index=True, help_text="Community free book donation (Rs. 0)")
    target_age_group = models.CharField(max_length=30, default='all', blank=True, db_index=True)
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_free', '-is_sponsored', '-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['book', 'status']),
            models.Index(fields=['seller', 'status']),
            models.Index(fields=['city', 'status']),
            models.Index(fields=['is_free', 'status']),
        ]

    def __str__(self):
        prefix = "[FREE DONATION] " if self.is_free or self.price == Decimal('0.00') else ""
        return f"{prefix}Listing #{self.id}: {self.book.title} - Rs. {self.price} by {self.seller.full_name}"

    @property
    def savings_percentage(self):
        if self.is_free or self.price == Decimal('0.00'):
            return 100
        if self.book.original_retail_price and self.book.original_retail_price > self.price:
            diff = self.book.original_retail_price - self.price
            return int((diff / self.book.original_retail_price) * 100)
        return 0

    @property
    def display_image_url(self):
        if self.image:
            return self.image.url
        return self.photo_url or self.book.cover_image or ''


class Favorite(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='favorites')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'listing')

    def __str__(self):
        return f"{self.user.full_name} favorited #{self.listing.id}"


class ContactUnlock(models.Model):
    PAYMENT_METHODS = [
        ('free_trial', 'Free Trial Unlock (Rs. 0)'),
        ('jazzcash', 'JazzCash Mobile Account'),
        ('easypaisa', 'Easypaisa Mobile Wallet'),
        ('nayapay_sadapay', 'NayaPay / SadaPay'),
        ('raast_bank', 'Raast / Bank Transfer'),
        ('card_safepay', 'Debit/Credit Card (Safepay / PayFast)'),
        ('wallet', 'BookLoop In-App Balance'),
    ]

    DEAL_STATUSES = [
        ('unlocked_pending', 'Contact Unlocked (Pending Handover / Deal)'),
        ('deal_made', 'Deal Confirmed (Fee Kept by Platform)'),
        ('no_deal_refunded', 'No Deal Made (Fee Refunded to Buyer)'),
        ('disputed', 'Disputed / Under Admin Review'),
    ]

    CONFIRMATION_STATUSES = [
        ('pending', 'Pending Response'),
        ('confirmed', 'Confirmed Deal'),
        ('rejected', 'Declined / No Deal'),
    ]

    unlock_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='unlocks')
    buyer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='unlocked_contacts_bought')
    seller = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='unlocked_contacts_received')
    
    fee_amount = models.DecimalField(max_digits=6, decimal_places=2, default=50.00, help_text="PKR 50.00")
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHODS, default='jazzcash')
    transaction_id = models.CharField(max_length=100, unique=True, db_index=True)
    payment_timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    deal_status = models.CharField(max_length=30, choices=DEAL_STATUSES, default='unlocked_pending', db_index=True)
    buyer_confirmation = models.CharField(max_length=20, choices=CONFIRMATION_STATUSES, default='pending')
    seller_confirmation = models.CharField(max_length=20, choices=CONFIRMATION_STATUSES, default='pending')
    
    cancellation_reason = models.TextField(blank=True, default='')
    refund_transaction_id = models.CharField(max_length=100, blank=True, default='')
    refund_timestamp = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('listing', 'buyer')
        ordering = ['-payment_timestamp']
        indexes = [
            models.Index(fields=['deal_status', '-payment_timestamp']),
            models.Index(fields=['buyer', 'deal_status']),
            models.Index(fields=['seller', 'deal_status']),
        ]

    def __str__(self):
        return f"Unlock #{self.id} for Listing #{self.listing.id} (Buyer: {self.buyer.full_name}, Fee: Rs. {self.fee_amount})"


class PaymentTransaction(models.Model):
    GATEWAY_CHOICES = [
        ('free_trial', 'Free Trial Unlock (Rs. 0)'),
        ('jazzcash', 'JazzCash'),
        ('easypaisa', 'Easypaisa'),
        ('nayapay_sadapay', 'NayaPay / SadaPay'),
        ('raast_bank', 'Raast / Bank Transfer'),
        ('card_safepay', 'Debit/Credit Card (Safepay / PayFast)'),
        ('wallet', 'In-App Wallet Balance'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Authorization / Verification'),
        ('completed', 'Completed & Verified'),
        ('failed', 'Failed Authorization / Rejected'),
        ('cancelled', 'Cancelled by User / Expired'),
        ('refunded', 'Refunded to Buyer'),
    ]

    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    gateway_ref = models.CharField(max_length=120, blank=True, default='', db_index=True, help_text="Gateway-assigned reference / transaction ID")
    buyer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='payment_transactions')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='payment_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('50.00'), help_text="Amount in PKR")
    currency = models.CharField(max_length=10, default='PKR')
    gateway = models.CharField(max_length=30, choices=GATEWAY_CHOICES, default='jazzcash', db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    
    gateway_response_code = models.CharField(max_length=50, blank=True, default='')
    gateway_response_message = models.TextField(blank=True, default='')
    gateway_payload = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    unlock = models.OneToOneField(ContactUnlock, on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_transaction')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['gateway', 'status']),
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self):
        return f"Payment #{self.transaction_id} ({self.gateway.upper()}) - Rs. {self.amount} [{self.status}]"


class SellerReview(models.Model):
    unlock = models.ForeignKey(ContactUnlock, on_delete=models.SET_NULL, related_name='reviews', null=True, blank=True)
    seller = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='received_reviews')
    buyer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='given_reviews')
    listing = models.ForeignKey(Listing, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    rating = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=5)
    comment = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.seller.update_rating()

    def __str__(self):
        return f"Review {self.rating}* for {self.seller.full_name} by {self.buyer.full_name}"


class Advertisement(models.Model):
    AD_TYPES = [
        ('banner_top', 'Top Banner'),
        ('banner_bottom', 'Bottom Sticky Banner'),
        ('interstitial', 'Full Screen Interstitial (After Listing)'),
        ('native_feed', 'Native In-Feed Sponsored Card'),
        ('sponsored_listing', 'Sponsored Listing Banner'),
    ]

    title = models.CharField(max_length=150)
    sponsor_name = models.CharField(max_length=100, default='National Campus Book Hub')
    ad_type = models.CharField(max_length=30, choices=AD_TYPES, default='banner_bottom')
    image_url = models.TextField(blank=True, default='')
    headline = models.CharField(max_length=200, default='Get 30% Off New Semester Stationery & Guides')
    target_url = models.CharField(max_length=255, default='#')
    impressions = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_ad_type_display()}) - {self.clicks} clicks"


class PlatformSetting(models.Model):
    platform_name = models.CharField(max_length=100, default='Bookzy AI')
    contact_unlock_fee = models.DecimalField(max_digits=6, decimal_places=2, default=50.00, help_text="PKR 50.00 contact unlock fee")
    auto_refund_days = models.IntegerField(default=5, help_text="Days after which unconfirmed deal auto-refunds")
    require_admin_approval = models.BooleanField(default=False)
    allow_sponsored_listings = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.platform_name} Settings (Unlock Fee: Rs. {self.contact_unlock_fee})"

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(id=1, defaults={'contact_unlock_fee': Decimal('50.00'), 'platform_name': 'BookBazaar Pakistan'})
        return obj


class MarketplaceReport(models.Model):
    REPORT_TYPES = [
        ('fraud_scam', 'Fraud / Fake Listing'),
        ('wrong_price', 'Incorrect / Misleading Price'),
        ('fake_condition', 'Condition Not As Described'),
        ('unresponsive_seller', 'Seller Not Responding After Unlock'),
        ('abusive_behavior', 'Abusive / Inappropriate Behavior'),
        ('copyright_piracy', 'Pirated / Unauthorized Photocopy'),
        ('other', 'Other Issue'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('investigating', 'Under Investigation'),
        ('resolved', 'Resolved (Action Taken)'),
        ('dismissed', 'Dismissed (Invalid Report)'),
    ]

    report_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    reporter = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='submitted_reports')
    listing = models.ForeignKey(Listing, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports')
    reported_user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_reports')
    
    report_type = models.CharField(max_length=40, choices=REPORT_TYPES, default='fraud_scam')
    description = models.TextField(help_text="Detailed explanation of the issue")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    admin_notes = models.TextField(blank=True, default='', help_text="Internal notes by moderator")
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_reports')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self):
        return f"Report #{self.id} ({self.get_report_type_display()}) - [{self.status.upper()}]"


class AdminNotification(models.Model):
    NOTIFICATION_TYPES = [
        ('SELLER_REGISTERED', 'New Seller Registered'),
        ('BOOK_LISTED', 'New Book Listed'),
        ('CONTACT_UNLOCKED', 'Contact Unlocked'),
        ('PAYMENT_RECEIVED', 'Payment Received'),
        ('PAYMENT_FAILED', 'Payment Failed'),
        ('DEAL_SUCCESSFUL', 'Deal Successful'),
        ('DEAL_PENDING', 'Deal Pending'),
        ('DEAL_FAILED_REFUND_REQ', 'Deal Unsuccessful & Refund Request'),
        ('REFUND_PROCESSED', 'Refund Processed'),
        ('SYSTEM_ALERT', 'System Alert'),
    ]

    notification_type = models.CharField(max_length=40, choices=NOTIFICATION_TYPES, db_index=True)
    title = models.CharField(max_length=200)
    message = models.TextField()

    # Related entities
    user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_notifications')
    buyer = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='buyer_admin_notifications')
    seller = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='seller_admin_notifications')
    listing = models.ForeignKey(Listing, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_notifications')
    transaction = models.ForeignKey(PaymentTransaction, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_notifications')
    unlock = models.ForeignKey(ContactUnlock, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_notifications')

    is_read = models.BooleanField(default=False, db_index=True)
    is_resolved = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_read', '-created_at']),
            models.Index(fields=['notification_type', '-created_at']),
            models.Index(fields=['is_resolved', '-created_at']),
        ]

    def save(self, *args, **kwargs):
        if self.buyer and not self.user:
            self.user = self.buyer
        elif self.user and not self.buyer:
            self.buyer = self.user
        super().save(*args, **kwargs)

    def __str__(self):
        status_str = "Read" if self.is_read else "Unread"
        resolved_str = "Resolved" if self.is_resolved else "Pending"
        return f"[{self.notification_type}] {self.title} ({status_str}, {resolved_str})"

