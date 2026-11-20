from django.urls import path
from bazaar import views

urlpatterns = [
    # Web views
    path('', views.index_view, name='index'),
    path('admin-panel/', views.admin_view, name='admin_panel'),
    path('quiz/', views.quiz_view, name='quiz_portal'),

    # Auth & Profile APIs (Phase 1 & Phase 2)
    path('api/auth/register/', views.register_user, name='api_register'),
    path('api/auth/login/', views.login_user, name='api_login'),
    path('api/auth/logout/', views.logout_user, name='api_logout'),
    path('api/auth/demo_login/', views.demo_login, name='api_demo_login'),
    path('api/auth/me/', views.get_current_user_profile, name='api_current_user'),
    path('api/auth/profile/update/', views.update_user_profile, name='api_update_profile'),
    path('api/auth/profiles/', views.get_profiles_list, name='api_profiles'),
    path('api/auth/login_otp/', views.login_with_otp, name='api_login_otp'),

    # Books & Barcode Scan APIs
    path('api/books/scan/', views.scan_isbn, name='api_scan_isbn'),

    # Listings APIs (Phase 1 Marketplace)
    path('api/listings/', views.get_listings, name='api_listings'),
    path('api/listings/<int:listing_id>/', views.get_listing_detail, name='api_listing_detail'),
    path('api/listings/create/', views.create_listing, name='api_create_listing'),
    path('api/listings/seller/<int:seller_id>/', views.get_seller_listings, name='api_seller_listings'),
    path('api/listings/<int:listing_id>/edit/', views.edit_listing, name='api_edit_listing'),
    path('api/listings/<int:listing_id>/delete/', views.delete_listing, name='api_delete_listing'),
    path('api/listings/<int:listing_id>/toggle_status/', views.toggle_listing_status, name='api_toggle_listing_status'),

    # Favorites / Wishlist APIs
    path('api/favorites/toggle/', views.toggle_favorite, name='api_toggle_favorite'),
    path('api/favorites/user/<int:user_id>/', views.get_user_favorites, name='api_user_favorites'),

    # Contact Unlock & Refund APIs (Phase 1 & Phase 3)
    path('api/unlocks/request/', views.request_contact_unlock, name='api_request_unlock'),
    path('api/unlocks/user/<int:user_id>/', views.get_user_unlocks, name='api_user_unlocks'),
    path('api/unlocks/<uuid:unlock_id>/confirm_deal/', views.confirm_deal_made, name='api_confirm_deal'),
    path('api/unlocks/<uuid:unlock_id>/cancel_deal/', views.cancel_deal_refund, name='api_cancel_deal'),
    path('api/unlocks/<uuid:unlock_id>/request_refund/', views.request_deal_refund_api, name='api_request_deal_refund'),
    path('api/reviews/create/', views.submit_seller_review, name='api_create_review'),

    # Phase 3 Payment Gateway APIs (JazzCash & Easypaisa)
    path('api/payments/initiate/', views.initiate_payment_api, name='api_payment_initiate'),
    path('api/payments/verify/', views.verify_payment_api, name='api_payment_verify'),
    path('api/payments/cancel/', views.cancel_payment_api, name='api_payment_cancel'),
    path('api/payments/jazzcash/callback/', views.jazzcash_callback_api, name='api_jazzcash_callback'),
    path('api/payments/easypaisa/callback/', views.easypaisa_callback_api, name='api_easypaisa_callback'),
    path('api/payments/transaction/<uuid:transaction_id>/', views.get_payment_transaction_api, name='api_payment_transaction'),

    # Advertisements APIs
    path('api/ads/', views.get_ads, name='api_ads'),
    path('api/ads/<int:ad_id>/click/', views.click_ad, name='api_click_ad'),

    # Reports & Complaints APIs (Phase 4)
    path('api/reports/submit/', views.submit_report_api, name='api_submit_report'),

    # Admin Management APIs (Phase 4 Complete System)
    path('api/admin/stats/', views.get_admin_stats, name='api_admin_stats'),
    path('api/admin/settings/', views.update_admin_settings, name='api_update_settings'),
    path('api/admin/users/', views.get_admin_users, name='api_admin_users'),
    path('api/admin/users/<int:user_id>/detail/', views.get_admin_user_detail, name='api_admin_user_detail'),
    path('api/admin/users/<int:user_id>/toggle_block/', views.toggle_user_block, name='api_toggle_user_block'),
    path('api/admin/listings/', views.get_admin_listings, name='api_admin_listings'),
    path('api/admin/listings/<int:listing_id>/moderate/', views.moderate_listing, name='api_moderate_listing'),
    path('api/admin/listings/<int:listing_id>/edit/', views.admin_edit_listing, name='api_admin_edit_listing'),
    path('api/admin/sellers/', views.get_admin_sellers, name='api_admin_sellers'),
    path('api/admin/transactions/', views.get_admin_transactions, name='api_admin_transactions'),
    path('api/admin/unlocks/', views.get_admin_unlocks, name='api_admin_unlocks'),
    path('api/admin/unlocks/<uuid:unlock_id>/force_refund/', views.admin_force_refund_unlock, name='api_admin_force_refund'),
    path('api/admin/reports/', views.get_admin_reports, name='api_admin_reports'),
    path('api/admin/reports/<int:report_id>/resolve/', views.resolve_admin_report, name='api_admin_resolve_report'),
    path('api/admin/ads/', views.get_admin_ads, name='api_admin_ads'),
    path('api/admin/ads/create/', views.create_admin_ad, name='api_admin_create_ad'),
    path('api/admin/ads/<int:ad_id>/edit/', views.edit_admin_ad, name='api_admin_edit_ad'),
    path('api/admin/ads/<int:ad_id>/delete/', views.delete_admin_ad, name='api_admin_delete_ad'),
    path('api/admin/ads/<int:ad_id>/toggle/', views.toggle_admin_ad, name='api_admin_toggle_ad'),

    # Admin Notifications & Lifecycle Action APIs (Pre-Phase 6)
    path('api/admin/notifications/', views.list_admin_notifications_api, name='api_admin_notifications'),
    path('api/admin/notifications/mark-read/', views.mark_admin_notifications_read_generic, name='api_admin_mark_notifications_read_generic'),
    path('api/admin/notifications/<int:notification_id>/read/', views.mark_admin_notification_read, name='api_admin_mark_notification_read'),
    path('api/admin/notifications/mark_all_read/', views.mark_all_admin_notifications_read, name='api_admin_mark_all_notifications_read'),
    path('api/admin/notifications/<int:notification_id>/process_refund/', views.admin_process_notification_refund, name='api_admin_process_notification_refund'),
]
