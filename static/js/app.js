/**
 * Bookzy AI Pakistan - Core Marketplace Logic
 * Pakistan's Academic & Used Books Marketplace
 */

const STATE = {
    currentUser: null,
    allUsers: [],
    currentLang: 'en',
    viewMode: 'full', // Default to clean full-screen responsive layout
    activeTab: 'home',
    listings: [],
    allListings: [],
    readerProfile: null,
    aiRecommendations: [],
    favorites: [],
    favoritesOnly: false,
    ads: [],
    platformFee: 50.0,
    authToken: localStorage.getItem('bookloop_token') || null,
    activeListingForUnlock: null,
    currentScanResult: null,
    cameraStream: null,
    scanInterval: null,
    barcodeDetector: null,
    torchOn: false
};

function getAuthHeaders(extra = {}) {
    const headers = { ...extra };
    const token = STATE.authToken || localStorage.getItem('bookloop_token');
    if (token) {
        headers['Authorization'] = `Token ${token}`;
    }
    return headers;
}

async function syncUserAuthToken(userId) {
    if (!userId) return;
    try {
        const res = await fetch('/api/auth/demo_login/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId })
        });
        if (res.ok) {
            const data = await res.json();
            STATE.authToken = data.token;
            localStorage.setItem('bookloop_token', data.token);
        }
    } catch (e) {
        console.warn("Auth token sync:", e);
    }
}

// Bilingual Translations (English & Urdu)
const I18N = {
    en: {
        brand_name: "Bookzy AI",
        brand_tagline: "Smart Used-Books Marketplace & Recommendation System",
        nav_home: "Home",
        nav_scan: "Scan ISBN",
        nav_sell: "Sell Book",
        nav_deals: "My Unlocks",
        nav_profile: "Profile",
        hero_title: "Buy & Sell Used Textbooks Across Pakistan",
        hero_subtitle: "Scan any book barcode to compare seller prices or sell your used books in seconds.",
        scan_now_btn: "Scan Book Barcode",
        sell_now_btn: "Sell a Used Book",
        search_placeholder: "Search by book title, author, or ISBN...",
        all_categories: "All Categories",
        all_cities: "All Cities",
        price_comparison_title: "Price Comparison & Offers",
        lowest_price: "Lowest Price",
        market_retail: "New Book Retail",
        save_percent: "Save up to",
        sellers_available: "Sellers available",
        unlock_contact_fee: "Unlock Contact",
        condition_label: "Condition",
        location_label: "Location",
        sponsored_badge: "Sponsored",
        deal_pending: "Contact Unlocked (Pending Deal)",
        deal_made: "Deal Completed",
        deal_refunded: "No Deal • Rs. 50 Refunded",
        confirm_deal_btn: "Deal Completed",
        cancel_refund_btn: "No Deal / Get Refund",
        seller_phone: "Seller Phone",
        call_seller: "Call Seller",
        whatsapp_seller: "WhatsApp Seller",
        refund_guarantee_badge: "100% Refundable Contact Fee (Rs. 50)",
        refund_guarantee_text: "Fee is kept by Bookzy AI only if deal is finalized; fully refunded if no deal is made.",
        select_payment_method: "Select Local Payment Method",
        jazzcash_wallet: "JazzCash Mobile Account",
        easypaisa_wallet: "Easypaisa Mobile Wallet",
        card_payment: "Debit / Credit Card (Safepay / PayFast)",
        wallet_balance: "Bookzy AI Wallet",
        pay_and_unlock: "Pay & Unlock Seller Contact",
        sell_step1: "Scan or Enter ISBN to Auto-fill Book",
        sell_btn: "Publish Book for Sale",
        view_toggle_mobile: "Phone View",
        view_toggle_full: "Full Screen"
    },
    ur: {
        brand_name: "Bookzy AI (بک زی)",
        brand_tagline: "سمارٹ مستعمل و درسی کتب مارکیٹ پلیس اور AI تجویزاتی نظام",
        nav_home: "ہوم",
        nav_scan: "بارکوڈ اسکین",
        nav_sell: "کتاب بیچیں",
        nav_deals: "میرے رابطے",
        nav_profile: "پروفائل",
        hero_title: "پاکستان میں درسی اور عام کتب پر بچت کریں",
        hero_subtitle: "کتاب کا بارکوڈ اسکین کریں، سستے ترین ریٹس موازنہ کریں یا پرانی کتاب چند لمحوں میں بیچیں۔",
        scan_now_btn: "کتاب کا بارکوڈ اسکین کریں",
        sell_now_btn: "استعمال شدہ کتاب بیچیں",
        search_placeholder: "کتاب کا نام، مصنف یا آئی ایس بی این تلاش کریں...",
        all_categories: "تمام کیٹیگریز",
        all_cities: "تمام شہر",
        price_comparison_title: "قیمت کا موازنہ اور دستیاب آفرز",
        lowest_price: "سب سے کم قیمت",
        market_retail: "نئی کتاب کی قیمت",
        save_percent: "تخمینی بچت",
        sellers_available: "دستیاب دکاندار و طلبہ",
        unlock_contact_fee: "رابطہ نمبر انلاک کریں",
        condition_label: "حالت",
        location_label: "مقام",
        sponsored_badge: "اسپانسرڈ",
        deal_pending: "رابطہ انلاک ہو گیا (بات چیت جاری)",
        deal_made: "سودا طے پا گیا (کامیاب)",
        deal_refunded: "سودا نہیں ہوا • فیس واپس منتقل ہو گئی",
        confirm_deal_btn: "سودا مکمل ہو گیا",
        cancel_refund_btn: "سودا نہیں ہوا / فیس واپس لیں",
        seller_phone: "بیچنے والے کا فون نمبر",
        call_seller: "براہِ راست کال کریں",
        whatsapp_seller: "واٹس ایپ پر میسج کریں",
        refund_guarantee_badge: "100٪ قابلِ واپسی فیس کی ضمانت (50 روپے)",
        refund_guarantee_text: "اگر بیچنے والے سے سودا نہ بنے تو آپ کی فیس فوری طور پر واپس کر دی جاتی ہے۔",
        select_payment_method: "مقامی ادائیگی کا طریقہ منتخب کریں",
        jazzcash_wallet: "جاز کیش موبائل اکاؤنٹ",
        easypaisa_wallet: "ایزی پیسہ والٹ",
        card_payment: "ڈیبٹ / کریڈٹ کارڈ (سیف پے / پے فاسٹ)",
        wallet_balance: "Bookzy والٹ بیلنس",
        pay_and_unlock: "فیس ادا کریں اور رابطہ حاصل کریں",
        sell_step1: "بارکوڈ اسکین کریں تاکہ معلومات خودبخود درج ہو جائیں",
        sell_btn: "کتاب فروخت کے لیے شائع کریں",
        view_toggle_mobile: "موبائل ویو",
        view_toggle_full: "فل اسکرین"
    }
};

// Live Status Bar Clock updater
function updateLiveClock() {
    const now = new Date();
    const hrs = String(now.getHours()).padStart(2, '0');
    const mins = String(now.getMinutes()).padStart(2, '0');
    const el = document.getElementById('live-time');
    if (el) el.textContent = `${hrs}:${mins}`;
}

// Initialize Application
document.addEventListener('DOMContentLoaded', async () => {
    updateLiveClock();
    setInterval(updateLiveClock, 1000);
    initReaderProfile();
    await loadInitialData();
    setupEventListeners();
    renderUserSwitcher();
    setupAiPriceAdvisor();
    await loadAiRecommendations();
    switchTab('home');
    updateLanguageTexts();
});

// Load profiles, listings, ads, platform fee
async function loadInitialData() {
    try {
        const [usersRes, listingsRes, adsRes] = await Promise.all([
            fetch('/api/auth/profiles/'),
            fetch('/api/listings/'),
            fetch('/api/ads/')
        ]);

        STATE.allUsers = await usersRes.json();
        STATE.allListings = await listingsRes.json();
        STATE.listings = STATE.allListings;
        STATE.ads = await adsRes.json();

        // Default active user is Demo Buyer or first available user
        const savedUserId = localStorage.getItem('bb_user_id');
        if (savedUserId) {
            STATE.currentUser = STATE.allUsers.find(u => u.id == savedUserId) || STATE.allUsers[0];
        } else {
            STATE.currentUser = STATE.allUsers.find(u => u.username === 'buyer_test') || STATE.allUsers[0];
        }

        // If reader profile doesn't exist yet, populate from currentUser if available
        if (!getSavedReaderProfile() && STATE.currentUser) {
            STATE.readerProfile = {
                name: STATE.currentUser.full_name || 'Ayesha',
                age_group: STATE.currentUser.age_group || 'teens',
                city: STATE.currentUser.city || 'Lahore',
                interests: (STATE.currentUser.reading_interests || 'free_only,ptb_textbooks').split(',').map(s => s.trim())
            };
        }

        renderAds();
        renderListings(STATE.listings);
        if (STATE.currentUser) {
            await syncUserAuthToken(STATE.currentUser.id);
        }
        updateUserUI();
        updateReaderHeaderUI();
    } catch (err) {
        console.error("Initialization error:", err);
    }
}

// User Switcher Setup (For rapid testing across mobile and desktop)
function renderUserSwitcher() {
    const switchers = [
        document.getElementById('user-selector'),
        document.getElementById('user-selector-mobile')
    ].filter(Boolean);

    if (!switchers.length) return;

    const optionsHtml = STATE.allUsers.map(u => `
        <option value="${u.id}" ${STATE.currentUser && STATE.currentUser.id === u.id ? 'selected' : ''}>
            ${u.full_name} (${u.user_type === 'admin' ? 'Admin' : u.city})
        </option>
    `).join('');

    switchers.forEach(sw => {
        sw.innerHTML = optionsHtml;
        if (STATE.currentUser) sw.value = STATE.currentUser.id;

        sw.addEventListener('change', async (e) => {
            const selectedId = e.target.value;
            STATE.currentUser = STATE.allUsers.find(u => u.id == selectedId);
            localStorage.setItem('bb_user_id', selectedId);
            switchers.forEach(s => s.value = selectedId);
            await syncUserAuthToken(selectedId);
            updateUserUI();
            if (typeof loadAiRecommendations === 'function') {
                loadAiRecommendations();
            }
            if (STATE.activeTab === 'deals') {
                loadUserDeals();
            } else if (STATE.activeTab === 'profile') {
                loadMySellerListings();
            }
        });
    });
}

function updateUserUI() {
    if (!STATE.currentUser) return;
    const nameEl = document.getElementById('current-user-name');
    const balEl = document.getElementById('current-user-balance');
    const topBal = document.getElementById('top-user-balance');

    if (nameEl) nameEl.textContent = STATE.currentUser.full_name;
    if (balEl) balEl.textContent = `Rs. ${parseFloat(STATE.currentUser.wallet_balance).toFixed(0)}`;
    if (topBal) topBal.textContent = `Rs. ${parseFloat(STATE.currentUser.wallet_balance).toFixed(0)}`;

    const profileName = document.getElementById('profile-tab-name');
    const profilePhone = document.getElementById('profile-tab-phone');
    const profileCity = document.getElementById('profile-tab-city');
    const profileRating = document.getElementById('profile-tab-rating');
    const profileWallet = document.getElementById('profile-tab-wallet');
    const authBtnLabel = document.getElementById('auth-btn-label');
    const dropName = document.getElementById('dropdown-user-name');
    const dropPhone = document.getElementById('dropdown-user-phone');
    const dropBal = document.getElementById('dropdown-user-balance');

    if (profileName) profileName.textContent = STATE.currentUser.full_name;
    if (profilePhone) profilePhone.textContent = STATE.currentUser.phone_number;
    if (profileCity) profileCity.textContent = `${STATE.currentUser.city} (${STATE.currentUser.campus_or_area})`;
    if (profileRating) profileRating.textContent = `★ ${STATE.currentUser.rating} (${STATE.currentUser.total_reviews} reviews)`;
    if (profileWallet) profileWallet.textContent = `Rs. ${parseFloat(STATE.currentUser.wallet_balance).toFixed(2)}`;
    if (authBtnLabel) {
        if (!STATE.currentUser || !STATE.currentUser.full_name || STATE.currentUser.full_name.toLowerCase().includes('demo')) {
            authBtnLabel.textContent = 'My Account';
        } else {
            authBtnLabel.textContent = STATE.currentUser.full_name.split(' ')[0] || 'My Account';
        }
    }
    if (dropName) dropName.textContent = STATE.currentUser.full_name;
    if (dropPhone) dropPhone.textContent = STATE.currentUser.phone_number;
    if (dropBal) dropBal.textContent = `Rs. ${parseFloat(STATE.currentUser.wallet_balance).toFixed(2)}`;

    updateReaderHeaderUI();
    loadMySellerListings();
}

// User Profile & Navigation Dropdown Controls (Fixes Top-Right Menu Visibility & Interaction)
function toggleUserDropdown() {
    const dropdown = document.getElementById('user-profile-dropdown');
    if (dropdown) dropdown.classList.toggle('hidden');
}

function closeUserDropdown() {
    const dropdown = document.getElementById('user-profile-dropdown');
    if (dropdown) dropdown.classList.add('hidden');
}

// Close User Dropdown on Click Outside
document.addEventListener('click', (e) => {
    const container = document.getElementById('user-menu-container');
    const dropdown = document.getElementById('user-profile-dropdown');
    if (container && dropdown && !container.contains(e.target)) {
        dropdown.classList.add('hidden');
    }
});

// Language Switching (English / Urdu)
function toggleLanguage() {
    STATE.currentLang = STATE.currentLang === 'en' ? 'ur' : 'en';
    const langBtn = document.getElementById('lang-toggle-btn');
    if (langBtn) {
        langBtn.textContent = STATE.currentLang === 'en' ? 'اردو' : 'English';
    }
    document.documentElement.lang = STATE.currentLang;
    document.documentElement.dir = STATE.currentLang === 'ur' ? 'rtl' : 'ltr';
    if (STATE.currentLang === 'ur') {
        document.body.classList.add('urdu-text');
    } else {
        document.body.classList.remove('urdu-text');
    }
    updateLanguageTexts();
}

function updateLanguageTexts() {
    const dict = I18N[STATE.currentLang];
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (dict[key]) {
            el.textContent = dict[key];
        }
    });
}

// Navigation & Scroll Helpers
function scrollToBrowse() {
    const el = document.getElementById('browse-section') || document.getElementById('all-offers-section') || document.getElementById('shelf-pills-bar');
    if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}
window.scrollToBrowse = scrollToBrowse;

function toggleMobileNavMenu() {
    const menu = document.getElementById('mobile-nav-dropdown');
    if (menu) {
        menu.classList.toggle('hidden');
    }
}
window.toggleMobileNavMenu = toggleMobileNavMenu;

// View Mode Toggle (Retained for backwards compatibility)
function toggleViewMode() {
    const wrapper = document.getElementById('app-wrapper');
    if (wrapper) {
        wrapper.classList.remove('mobile-device-frame');
    }
}
window.toggleViewMode = toggleViewMode;

// Open/activate Scanner section, smoothly scroll up and focus manual input
function openBarcodeScanner() {
    switchTab('scan');
}
window.openBarcodeScanner = openBarcodeScanner;
window.openScanModal = openBarcodeScanner;
window.closeScanModal = () => switchTab('home');

// Open/activate Sell or Donate section
function openSellSection() {
    switchTab('sell');
}
window.openSellSection = openSellSection;

// Open/activate My Deals & Unlocks section
function openDealsSection() {
    switchTab('deals');
}
window.openDealsSection = openDealsSection;

// Tab Switching (Centralized & Clean)
function switchTab(tabId) {
    // If navigating away from scanner and camera is active, turn it off
    if (STATE.activeTab === 'scan' && tabId !== 'scan') {
        if (typeof stopCameraScanner === 'function') {
            stopCameraScanner();
        }
    }

    STATE.activeTab = tabId;

    // Cleanly hide all tab sections and remove any conflicting inline display styles
    document.querySelectorAll('.tab-page').forEach(page => {
        page.classList.add('hidden');
        page.style.removeProperty('display');
    });

    const targetPage = document.getElementById(`tab-${tabId}`);
    if (targetPage) {
        targetPage.classList.remove('hidden');
        targetPage.style.display = 'flex';
    }

    // Scroll smoothly to top of viewport
    window.scrollTo({ top: 0, behavior: 'smooth' });
    const scrollContainer = document.querySelector('.app-content.overflow-y-auto') || document.querySelector('.overflow-y-auto');
    if (scrollContainer) {
        scrollContainer.scrollTop = 0;
    }

    // Update active nav link styling across desktop header and mobile bottom bar
    document.querySelectorAll('.nav-tab').forEach(tab => {
        const isHeader = Boolean(tab.closest('header'));
        if (tab.getAttribute('data-tab') === tabId) {
            tab.classList.add('active');
            if (isHeader) {
                tab.classList.add('text-white', 'bg-white/10');
                tab.classList.remove('text-blue-100');
            } else {
                tab.classList.add('text-blue-700');
                tab.classList.remove('text-slate-400');
            }
        } else {
            tab.classList.remove('active');
            if (isHeader) {
                tab.classList.remove('text-white', 'bg-white/10');
                tab.classList.add('text-blue-100');
            } else {
                tab.classList.remove('text-blue-700');
                tab.classList.add('text-slate-400');
            }
        }
    });

    // Tab-specific initializations
    if (tabId === 'scan') {
        setTimeout(() => {
            const input = document.getElementById('manual-isbn-input');
            if (input) input.focus();
        }, 150);
    } else if (tabId === 'sell') {
        setTimeout(() => {
            const titleInput = document.getElementById('sell-title-input');
            if (titleInput) titleInput.focus();
        }, 150);
    } else if (tabId === 'deals') {
        if (typeof loadUserDeals === 'function') {
            loadUserDeals();
        }
    } else if (tabId === 'profile') {
        if (typeof loadMySellerListings === 'function') {
            loadMySellerListings();
        }
    }
}
window.switchTab = switchTab;

// Dedicated Reusable Book Card Component
// Dedicated Reusable Minimalist Book Card Component (Requirement 5)
function createBookCardHtml(item, options = {}) {
    const isFree = Boolean(item.is_free || parseFloat(item.price) === 0);
    const displayImg = item.display_image || item.photo_url || (item.book && item.book.cover_image) || 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400';
    const title = item.book ? item.book.title : (item.title || 'Untitled Book');
    const isbn = item.book ? item.book.isbn : (item.isbn || '');
    const city = item.city || 'Pakistan';
    const condition = item.condition || 'Good';
    const priceNum = parseFloat(item.price || 0);

    return `
        <div class="bg-white rounded-2xl border border-slate-200 hover:border-blue-300 shadow-xs hover:shadow-lg transition-all duration-200 overflow-hidden flex flex-col justify-between group h-full">
            <div>
                <!-- Book Cover Image -->
                <div class="relative w-full aspect-[3/4] bg-slate-100 overflow-hidden cursor-pointer" onclick="openUnlockModal(${item.id})">
                    <img src="${displayImg}" 
                         alt="${title}" 
                         class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                         loading="lazy"
                         onerror="this.src='https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400'">
                    ${isFree ? `
                        <div class="absolute top-2.5 right-2.5">
                            <span class="bg-emerald-600 text-white font-extrabold text-[11px] px-2.5 py-0.5 rounded-full shadow-sm">
                                Free
                            </span>
                        </div>
                    ` : ''}
                </div>

                <!-- Book Details -->
                <div class="p-4 flex flex-col gap-1.5">
                    <!-- City & Condition Tag (e.g., "Lahore • Good") -->
                    <div class="text-xs font-semibold text-slate-500 flex items-center gap-1.5">
                        <i class="fa-solid fa-location-dot text-blue-600 text-[10px]"></i>
                        <span>${city} • ${condition}</span>
                    </div>

                    <!-- Book Title -->
                    <h3 class="font-extrabold text-slate-900 text-sm leading-snug line-clamp-2 hover:text-blue-700 cursor-pointer transition-colors"
                        title="${title}"
                        onclick="openUnlockModal(${item.id})">
                        ${title}
                    </h3>
                </div>
            </div>

            <!-- Price & Single Clean Action Button -->
            <div class="p-4 pt-0 mt-auto flex items-center justify-between gap-2 border-t border-slate-100 pt-3">
                <div>
                    ${isFree ? `
                        <span class="inline-block text-xs font-black uppercase text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-lg">
                            Free
                        </span>
                    ` : `
                        <div class="flex items-baseline gap-1">
                            <span class="text-base font-black text-blue-900">Rs. ${priceNum.toFixed(0)}</span>
                        </div>
                    `}
                </div>

                <button onclick="openUnlockModal(${item.id})" 
                        class="px-3.5 py-1.5 ${isFree ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-blue-600 hover:bg-blue-700'} text-white font-bold rounded-xl text-xs transition-colors shadow-xs hover:shadow flex items-center gap-1.5 active:scale-95">
                    <span>${isFree ? 'Claim' : 'View Details'}</span>
                </button>
            </div>
        </div>
    `;
}

// Render dedicated shelves on the homepage
function renderShelves(listings) {
    if (!listings || !listings.length) return;

    // 1. Free Donated Books (Rs. 0 / is_free)
    const freeContainer = document.getElementById('free-books-container');
    const freeSection = document.getElementById('free-books-section');
    if (freeContainer) {
        const freeItems = listings.filter(item => item.is_free || parseFloat(item.price) === 0);
        if (freeItems.length > 0) {
            freeContainer.innerHTML = freeItems.slice(0, 8).map(item => createBookCardHtml(item)).join('');
            if (freeSection) freeSection.classList.remove('hidden');
        } else {
            if (freeSection) freeSection.classList.add('hidden');
        }
    }

    // 2. Punjab Textbooks (Class 1 to FSc)
    renderPtbShelf(listings, CURRENT_PTB_FILTER);

    // 3. Kids & Story Books
    const kidsContainer = document.getElementById('kids-books-container');
    const kidsSection = document.getElementById('kids-books-section');
    if (kidsContainer) {
        const kidsItems = listings.filter(item => {
            const cat = item.book?.category || '';
            const age = item.target_age_group || item.book?.target_age_group || '';
            const title = (item.book?.title || '').toLowerCase();
            return cat === 'Story Books' || age === 'kids' || title.includes('kahani') || title.includes('story') || title.includes('bachon') || title.includes('jungle');
        });
        if (kidsItems.length > 0) {
            kidsContainer.innerHTML = kidsItems.slice(0, 8).map(item => createBookCardHtml(item)).join('');
            if (kidsSection) kidsSection.classList.remove('hidden');
        } else {
            if (kidsSection) kidsSection.classList.add('hidden');
        }
    }

    // 4. Fiction & Novels
    const novelsContainer = document.getElementById('fiction-novels-container');
    const novelsSection = document.getElementById('fiction-novels-section');
    if (novelsContainer) {
        const novelItems = listings.filter(item => {
            const cat = item.book?.category || '';
            return cat === 'Fiction' || cat === 'Novels' || cat === 'Urdu Literature & Novels';
        });
        if (novelItems.length > 0) {
            novelsContainer.innerHTML = novelItems.slice(0, 8).map(item => createBookCardHtml(item)).join('');
            if (novelsSection) novelsSection.classList.remove('hidden');
        } else {
            if (novelsSection) novelsSection.classList.add('hidden');
        }
    }

    // 5. History & Literature
    const historyContainer = document.getElementById('history-literature-container');
    const historySection = document.getElementById('history-literature-section');
    if (historyContainer) {
        const histItems = listings.filter(item => {
            const cat = item.book?.category || '';
            const title = (item.book?.title || '').toLowerCase();
            const subj = (item.book?.subject || '').toLowerCase();
            return cat === 'History' || subj.includes('history') || title.includes('history') || title.includes('tareekh') || title.includes('iqbal') || title.includes('balochistan') || title.includes('mehrgarh');
        });
        if (histItems.length > 0) {
            historyContainer.innerHTML = histItems.slice(0, 8).map(item => createBookCardHtml(item)).join('');
            if (historySection) historySection.classList.remove('hidden');
        } else {
            if (historySection) historySection.classList.add('hidden');
        }
    }
}

let CURRENT_PTB_FILTER = 'all';

function filterPtbByClass(classKey, btn) {
    CURRENT_PTB_FILTER = classKey;
    if (btn) {
        document.querySelectorAll('#ptb-filter-pills .ptb-class-pill').forEach(p => {
            p.classList.remove('active', 'bg-blue-600', 'text-white', 'shadow-xs');
            p.classList.add('bg-slate-100', 'text-slate-700');
        });
        btn.classList.add('active', 'bg-blue-600', 'text-white', 'shadow-xs');
        btn.classList.remove('bg-slate-100', 'text-slate-700');
    }
    renderPtbShelf(STATE.allListings && STATE.allListings.length ? STATE.allListings : STATE.listings, classKey);
}

function renderPtbShelf(listings, filterClass = 'all') {
    const container = document.getElementById('ptb-textbooks-container');
    const section = document.getElementById('ptb-textbooks-section');
    if (!container || !listings) return;

    // Filter to PTB / Regional Board items
    const ptbItems = listings.filter(item => {
        const cat = item.book?.category || '';
        const board = (item.book?.education_board || '').toLowerCase();
        const title = (item.book?.title || '').toLowerCase();
        return cat === 'Punjab Textbooks (Primary to FSc)' || board.includes('punjab') || board.includes('balochistan') || title.includes('punjab') || title.includes('ptb') || title.includes('balochistan');
    });

    if (ptbItems.length === 0) {
        if (section) section.classList.add('hidden');
        return;
    }
    if (section) section.classList.remove('hidden');

    // Apply class filter
    let filtered = ptbItems;
    if (filterClass === 'primary') {
        filtered = ptbItems.filter(item => {
            const cls = (item.book?.grade_class || '').toLowerCase();
            const title = (item.book?.title || '').toLowerCase();
            return cls.includes('primary') || cls.includes('class 1') || cls.includes('class 2') || cls.includes('class 3') || cls.includes('class 4') || cls.includes('class 5') || title.includes('class 1') || title.includes('class 2') || title.includes('class 3') || title.includes('class 4') || title.includes('class 5') || title.includes('primary');
        });
    } else if (filterClass === 'middle') {
        filtered = ptbItems.filter(item => {
            const cls = (item.book?.grade_class || '').toLowerCase();
            const title = (item.book?.title || '').toLowerCase();
            return cls.includes('middle') || cls.includes('class 6') || cls.includes('class 7') || cls.includes('class 8') || title.includes('class 6') || title.includes('class 7') || title.includes('class 8') || title.includes('middle');
        });
    } else if (filterClass === 'matric') {
        filtered = ptbItems.filter(item => {
            const cls = (item.book?.grade_class || '').toLowerCase();
            const title = (item.book?.title || '').toLowerCase();
            return cls.includes('matric') || cls.includes('class 9') || cls.includes('class 10') || cls.includes('ssc') || title.includes('matric') || title.includes('9th') || title.includes('10th') || title.includes('class 9') || title.includes('class 10');
        });
    } else if (filterClass === 'fsc') {
        filtered = ptbItems.filter(item => {
            const cls = (item.book?.grade_class || '').toLowerCase();
            const title = (item.book?.title || '').toLowerCase();
            return cls.includes('fsc') || cls.includes('class 11') || cls.includes('class 12') || cls.includes('hssc') || cls.includes('intermediate') || title.includes('fsc') || title.includes('11th') || title.includes('12th') || title.includes('part 1') || title.includes('part 2');
        });
    }

    if (filtered.length === 0) {
        container.innerHTML = `
            <div class="col-span-full p-8 text-center bg-slate-50 rounded-2xl border border-dashed border-slate-200">
                <p class="text-xs text-slate-500 font-medium">No Punjab Textbooks listed in this specific class tier yet.</p>
                <button type="button" onclick="switchTab('sell'); toggleSellFreeDonation(true);" class="mt-2 text-xs font-bold text-blue-700 hover:underline">Donate or Sell One Now</button>
            </div>
        `;
        return;
    }

    container.innerHTML = filtered.slice(0, 8).map(item => createBookCardHtml(item)).join('');
}

function filterShelfSection(shelfKey) {
    const pills = document.querySelectorAll('#shelf-pills-bar .shelf-pill-btn');
    pills.forEach(p => {
        p.classList.remove('active', 'bg-blue-600', 'text-white', 'shadow-xs');
        p.classList.add('bg-white', 'text-slate-700', 'border-slate-200');
    });
    const activePill = document.getElementById(`shelf-pill-${shelfKey}`);
    if (activePill) {
        activePill.classList.add('active', 'bg-blue-600', 'text-white', 'shadow-xs');
        activePill.classList.remove('bg-white', 'text-slate-700', 'border-slate-200');
    }

    const sections = {
        all: document.querySelectorAll('.shelf-section'),
        ai: document.getElementById('ai-recommendations-section'),
        free: document.getElementById('free-books-section'),
        ptb: document.getElementById('ptb-textbooks-section'),
        kids: document.getElementById('kids-books-section'),
        novels: document.getElementById('fiction-novels-section'),
        history: document.getElementById('history-literature-section')
    };

    if (shelfKey === 'all') {
        sections.all.forEach(sec => sec.classList.remove('hidden'));
    } else {
        sections.all.forEach(sec => sec.classList.add('hidden'));
        const target = sections[shelfKey];
        if (target) {
            target.classList.remove('hidden');
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
}

// Render Listings Feed with Image display & Favourites
function renderListings(listings) {
    const container = document.getElementById('listings-container');
    if (!container) return;

    // Keep shelves synced
    renderShelves(STATE.allListings && STATE.allListings.length ? STATE.allListings : listings);

    if (!listings || listings.length === 0) {
        container.innerHTML = `
            <div class="col-span-full p-12 text-center bg-white rounded-2xl border border-dashed border-slate-300">
                <i class="fa-solid fa-book-open text-4xl text-slate-300 mb-3"></i>
                <p class="text-slate-600 font-medium">No book listings match your filter.</p>
                <button onclick="resetFilters()" class="mt-3 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold">Clear Filters</button>
            </div>
        `;
        return;
    }

    const nativeAd = STATE.ads.find(a => a.ad_type === 'native_feed');

    let html = '';
    listings.forEach((item, index) => {
        // Native Ad injection (formatted cleanly as a grid card)
        if (index === 4 && nativeAd) {
            html += `
                <div class="bg-gradient-to-br from-amber-50 to-orange-50 border border-amber-200 rounded-2xl p-4 shadow-xs hover:shadow-md transition-all flex flex-col justify-between h-full">
                    <div>
                        <div class="flex items-center justify-between mb-2">
                            <span class="bg-amber-500 text-white text-[10px] uppercase font-bold px-2 py-0.5 rounded-full">Sponsored Ad</span>
                            <span class="text-xs font-bold text-slate-800 truncate">${nativeAd.sponsor_name}</span>
                        </div>
                        <img src="${nativeAd.image_url}" class="w-full aspect-[3/4] object-cover rounded-xl shadow-xs mb-3">
                        <h4 class="text-sm font-bold text-slate-900 line-clamp-2">${nativeAd.headline}</h4>
                    </div>
                    <div class="mt-4 pt-3 border-t border-amber-200/60 flex justify-end">
                        <button onclick="trackAdClick(${nativeAd.id})" class="px-3.5 py-1.5 bg-amber-600 hover:bg-amber-700 text-white text-xs font-semibold rounded-xl transition-colors">View Sponsor</button>
                    </div>
                </div>
            `;
        }

        html += createBookCardHtml(item);
    });

    container.innerHTML = html;
}

// Toggle Favorite for a Listing
async function toggleFavoriteListing(listingId) {
    if (!STATE.currentUser) {
        alert("Please sign in or select a profile to save favourites.");
        return;
    }

    try {
        const res = await fetch('/api/favorites/toggle/', {
            method: 'POST',
            headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
            body: JSON.stringify({ user_id: STATE.currentUser.id, listing_id: listingId })
        });
        const data = await res.json();
        // Update local listing state
        const item = STATE.listings.find(l => l.id === listingId);
        if (item) {
            item.is_favorited = data.is_favorited;
        }
        renderListings(STATE.listings);
    } catch (e) {
        console.error("Favorite toggle error:", e);
    }
}

// Toggle Favorites Only Filter
async function toggleFavoritesFilter() {
    STATE.favoritesOnly = !STATE.favoritesOnly;
    const btnText = document.getElementById('fav-filter-text');
    const btn = document.getElementById('favorites-filter-btn');

    if (STATE.favoritesOnly) {
        btn.classList.add('bg-rose-50', 'border-rose-300', 'text-rose-700');
        btnText.textContent = "Showing Favourites";
        try {
            const res = await fetch(`/api/favorites/user/${STATE.currentUser.id}/`, {
                headers: getAuthHeaders()
            });
            const favs = await res.json();
            const favListings = favs.map(f => {
                f.listing.is_favorited = true;
                return f.listing;
            });
            renderListings(favListings);
        } catch (e) {
            console.error(e);
        }
    } else {
        btn.classList.remove('bg-rose-50', 'border-rose-300', 'text-rose-700');
        btnText.textContent = "Favourites";
        applyFilters();
    }
}

function toggleAdvancedFilters() {
    const box = document.getElementById('advanced-filters-box');
    const arrow = document.getElementById('filter-arrow-icon');
    if (box) {
        const isHidden = box.classList.toggle('hidden');
        if (arrow) {
            arrow.style.transform = isHidden ? 'rotate(0deg)' : 'rotate(180deg)';
        }
    }
}

// Render Banner Ads
function renderAds() {
    const topAd = STATE.ads.find(a => a.ad_type === 'banner_top');
    const bottomAd = STATE.ads.find(a => a.ad_type === 'banner_bottom');

    const topContainer = document.getElementById('banner-top-ad');
    const bottomContainer = document.getElementById('banner-bottom-ad');

    if (topContainer && topAd) {
        topContainer.innerHTML = `
            <div class="bg-gradient-to-r from-blue-900 to-indigo-900 text-white p-2.5 rounded-xl shadow-xs flex items-center justify-between mb-3">
                <div class="flex items-center gap-2.5">
                    <span class="bg-emerald-500 text-[9px] uppercase font-extrabold px-1.5 py-0.5 rounded text-white tracking-wider">Ad</span>
                    <div>
                        <p class="text-xs font-bold leading-tight">${topAd.title}</p>
                        <p class="text-[11px] text-blue-100 line-clamp-1">${topAd.headline}</p>
                    </div>
                </div>
                <button onclick="trackAdClick(${topAd.id})" class="px-2.5 py-1 bg-white text-blue-900 text-xs font-bold rounded-lg hover:bg-blue-50">Explore</button>
            </div>
        `;
    }

    if (bottomContainer && bottomAd) {
        bottomContainer.innerHTML = `
            <div class="bg-red-700 text-white p-2 rounded-xl flex items-center justify-between shadow-xs">
                <div class="flex items-center gap-2">
                    <span class="bg-white text-red-700 text-[9px] font-extrabold px-1.5 py-0.5 rounded">Partner</span>
                    <p class="text-xs font-medium">${bottomAd.headline}</p>
                </div>
                <button onclick="trackAdClick(${bottomAd.id})" class="px-2 py-0.5 bg-yellow-400 text-slate-900 text-[11px] font-bold rounded hover:bg-yellow-300">Details</button>
            </div>
        `;
    }
}

async function trackAdClick(adId) {
    try {
        await fetch(`/api/ads/${adId}/click/`, { method: 'POST' });
        alert("Sponsor Offer: Thank you for viewing this student discount!");
    } catch (e) {
        console.error(e);
    }
}

// ==========================================
// BARCODE (ISBN) SCANNER, CAMERA & UPLOAD PROCESSING
// ==========================================

async function initBarcodeDetector() {
    if ('BarcodeDetector' in window) {
        try {
            const supported = await BarcodeDetector.getSupportedFormats();
            const preferred = ['ean_13', 'ean_8', 'upc_a', 'upc_e', 'code_128', 'code_39', 'qr_code'];
            const formats = preferred.filter(f => supported.includes(f));
            if (formats.length > 0) {
                STATE.barcodeDetector = new BarcodeDetector({ formats });
            }
        } catch (e) {
            console.warn("BarcodeDetector setup error:", e);
        }
    }
}

// Pure JS EAN-13 / UPC Barcode Decoder Fallback
function decodeEan13Scanline(imgData, width) {
    if (!imgData || width < 100) return null;

    const gray = new Uint8Array(width);
    let sumGray = 0;
    for (let x = 0; x < width; x++) {
        const idx = x * 4;
        const g = (imgData[idx] * 299 + imgData[idx + 1] * 587 + imgData[idx + 2] * 114) / 1000;
        gray[x] = g;
        sumGray += g;
    }
    const threshold = sumGray / width;

    const runs = [];
    let curBit = gray[0] < threshold ? 1 : 0;
    let curLen = 0;
    for (let x = 0; x < width; x++) {
        const bit = gray[x] < threshold ? 1 : 0;
        if (bit === curBit) {
            curLen++;
        } else {
            runs.push({ bit: curBit, len: curLen });
            curBit = bit;
            curLen = 1;
        }
    }
    runs.push({ bit: curBit, len: curLen });

    if (runs.length < 59) return null;

    const L_CODES = ['0001101', '0011001', '0010011', '0111101', '0100011', '0110001', '0101111', '0111011', '0110111', '0001011'];
    const G_CODES = ['0100111', '0110011', '0011011', '0100001', '0011101', '0111001', '0000101', '0010001', '0001001', '0010111'];
    const R_CODES = ['1110010', '1100110', '1101100', '1000010', '1011100', '1001110', '1010000', '1000100', '1001000', '1110100'];
    const FIRST_DIGIT_PARITY = [
        'LLLLLL', 'LLGLGG', 'LLGGLG', 'LLGGGL', 'LGLLGG',
        'LGGLLG', 'LGGGLL', 'LGLGLG', 'LGLGGL', 'LGGLGL'
    ];

    function matchPattern(fourRuns, moduleWidth, isRight) {
        let pattern = '';
        for (let r = 0; r < 4; r++) {
            const count = Math.max(1, Math.min(4, Math.round(fourRuns[r].len / moduleWidth)));
            pattern += String(fourRuns[r].bit).repeat(count);
        }
        if (pattern.length !== 7) return null;

        if (isRight) {
            const idx = R_CODES.indexOf(pattern);
            return idx !== -1 ? { digit: idx, parity: 'R' } : null;
        } else {
            let idx = L_CODES.indexOf(pattern);
            if (idx !== -1) return { digit: idx, parity: 'L' };
            idx = G_CODES.indexOf(pattern);
            if (idx !== -1) return { digit: idx, parity: 'G' };
            return null;
        }
    }

    for (let i = 1; i < runs.length - 58; i++) {
        if (runs[i].bit === 1 && runs[i + 1].bit === 0 && runs[i + 2].bit === 1) {
            const moduleWidth = (runs[i].len + runs[i + 1].len + runs[i + 2].len) / 3;
            if (moduleWidth < 0.5) continue;

            let idx = i + 3;
            const leftDigits = [];
            const leftParity = [];
            let valid = true;

            for (let d = 0; d < 6; d++) {
                if (idx + 3 >= runs.length) { valid = false; break; }
                const res = matchPattern([runs[idx], runs[idx + 1], runs[idx + 2], runs[idx + 3]], moduleWidth, false);
                if (!res) { valid = false; break; }
                leftDigits.push(res.digit);
                leftParity.push(res.parity);
                idx += 4;
            }
            if (!valid) continue;

            if (idx + 4 >= runs.length || runs[idx].bit !== 0 || runs[idx + 1].bit !== 1 || runs[idx + 2].bit !== 0 || runs[idx + 3].bit !== 1 || runs[idx + 4].bit !== 0) {
                continue;
            }
            idx += 5;

            const rightDigits = [];
            for (let d = 0; d < 6; d++) {
                if (idx + 3 >= runs.length) { valid = false; break; }
                const res = matchPattern([runs[idx], runs[idx + 1], runs[idx + 2], runs[idx + 3]], moduleWidth, true);
                if (!res) { valid = false; break; }
                rightDigits.push(res.digit);
                idx += 4;
            }
            if (!valid) continue;

            const parityStr = leftParity.join('');
            const firstDigit = FIRST_DIGIT_PARITY.indexOf(parityStr);
            if (firstDigit === -1) continue;

            const allDigits = [firstDigit, ...leftDigits, ...rightDigits];
            let sum = 0;
            for (let k = 0; k < 12; k++) {
                sum += allDigits[k] * (k % 2 === 0 ? 1 : 3);
            }
            const check = (10 - (sum % 10)) % 10;
            if (check === allDigits[12]) {
                return allDigits.join('');
            }
        }
    }
    return null;
}

function decodeBarcodeFromCanvas(canvas) {
    if (!canvas || canvas.width === 0 || canvas.height === 0) return null;
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    if (!ctx) return null;

    const width = canvas.width;
    const height = canvas.height;
    const scanRows = [
        Math.floor(height * 0.5),
        Math.floor(height * 0.4),
        Math.floor(height * 0.6),
        Math.floor(height * 0.45),
        Math.floor(height * 0.55),
        Math.floor(height * 0.35),
        Math.floor(height * 0.65)
    ];

    for (const y of scanRows) {
        const imgData = ctx.getImageData(0, y, width, 1).data;
        const result = decodeEan13Scanline(imgData, width);
        if (result && result.length >= 12) {
            return result;
        }
    }
    return null;
}

// Toggle Live Camera Stream
async function toggleCameraScanner() {
    if (STATE.cameraStream) {
        stopCameraScanner();
        return;
    }

    const video = document.getElementById('scanner-video');
    const placeholder = document.getElementById('scanner-placeholder');
    const previewImg = document.getElementById('scanner-preview-img');
    const laser = document.getElementById('scanner-laser');
    const guide = document.getElementById('scanner-guide');
    const captureBtn = document.getElementById('capture-scan-btn');
    const resetBtn = document.getElementById('scanner-reset-btn');
    const cameraBtnText = document.getElementById('camera-btn-text');
    const cameraBtnIcon = document.getElementById('camera-btn-icon');
    const status = document.getElementById('scanner-status');
    const pulse = document.getElementById('scanner-pulse');
    const feedbackBadge = document.getElementById('scan-feedback-badge');

    if (feedbackBadge) feedbackBadge.classList.add('hidden');

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        if (status) {
            status.innerHTML = `<span class="text-rose-600 font-bold"><i class="fa-solid fa-circle-exclamation"></i> Camera API not supported in this browser. Please use photo upload or manual lookup!</span>`;
        }
        return;
    }

    if (status) {
        status.innerHTML = `<span class="text-blue-600 font-bold"><i class="fa-solid fa-spinner fa-spin"></i> Initializing camera stream...</span>`;
    }

    try {
        const constraints = {
            video: {
                facingMode: { ideal: 'environment' },
                width: { ideal: 1280 },
                height: { ideal: 720 }
            }
        };

        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        STATE.cameraStream = stream;

        if (video) {
            video.srcObject = stream;
            video.classList.remove('hidden');
            await video.play().catch(e => console.warn("Video play error:", e));
        }

        if (placeholder) placeholder.classList.add('hidden');
        if (previewImg) previewImg.classList.add('hidden');
        if (laser) laser.classList.remove('hidden');
        if (guide) guide.classList.remove('hidden');
        if (captureBtn) captureBtn.classList.remove('hidden');
        if (resetBtn) resetBtn.classList.remove('hidden');

        if (cameraBtnText) cameraBtnText.textContent = "Stop Camera";
        if (cameraBtnIcon) cameraBtnIcon.className = "fa-solid fa-video-slash";
        if (pulse) pulse.className = "w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse shrink-0";
        if (status) {
            status.innerHTML = `<span class="text-emerald-700 font-bold"><i class="fa-solid fa-circle-dot"></i> Live camera active. Align ISBN barcode inside target frame.</span>`;
        }

        if (!STATE.barcodeDetector && 'BarcodeDetector' in window) {
            await initBarcodeDetector();
        }

        startLiveScanningLoop();
    } catch (err) {
        console.warn("Camera access failed:", err);
        if (status) {
            status.innerHTML = `<span class="text-amber-700 font-bold"><i class="fa-solid fa-triangle-exclamation"></i> Camera not accessible (${err.name || 'Permission denied'}). Use photo upload or test barcodes below!</span>`;
        }
        if (pulse) pulse.className = "w-2.5 h-2.5 rounded-full bg-amber-500 shrink-0";
    }
}
window.toggleCameraScanner = toggleCameraScanner;

// Stop Live Camera Stream
function stopCameraScanner() {
    if (STATE.scanInterval) {
        clearInterval(STATE.scanInterval);
        STATE.scanInterval = null;
    }

    if (STATE.cameraStream) {
        STATE.cameraStream.getTracks().forEach(t => t.stop());
        STATE.cameraStream = null;
    }

    const video = document.getElementById('scanner-video');
    const placeholder = document.getElementById('scanner-placeholder');
    const previewImg = document.getElementById('scanner-preview-img');
    const laser = document.getElementById('scanner-laser');
    const guide = document.getElementById('scanner-guide');
    const captureBtn = document.getElementById('capture-scan-btn');
    const cameraBtnText = document.getElementById('camera-btn-text');
    const cameraBtnIcon = document.getElementById('camera-btn-icon');
    const status = document.getElementById('scanner-status');
    const pulse = document.getElementById('scanner-pulse');

    if (video) {
        video.srcObject = null;
        video.classList.add('hidden');
    }

    if (!previewImg || previewImg.classList.contains('hidden')) {
        if (placeholder) placeholder.classList.remove('hidden');
    }

    if (laser) laser.classList.add('hidden');
    if (guide) guide.classList.add('hidden');
    if (captureBtn) captureBtn.classList.add('hidden');

    if (cameraBtnText) cameraBtnText.textContent = "Start Live Camera";
    if (cameraBtnIcon) cameraBtnIcon.className = "fa-solid fa-video";
    if (pulse) pulse.className = "w-2.5 h-2.5 rounded-full bg-slate-400 shrink-0";
    if (status && (!previewImg || previewImg.classList.contains('hidden'))) {
        status.textContent = "Camera Off. Turn on camera, upload a photo, or enter ISBN below.";
    }

    STATE.torchOn = false;
    const torchBtn = document.getElementById('torch-btn');
    if (torchBtn) {
        torchBtn.classList.remove('bg-amber-400', 'text-slate-900');
    }
}
window.stopCameraScanner = stopCameraScanner;

// Continuous Background Frame Detection Loop
function startLiveScanningLoop() {
    if (STATE.scanInterval) {
        clearInterval(STATE.scanInterval);
    }

    STATE.scanInterval = setInterval(async () => {
        if (!STATE.cameraStream) {
            clearInterval(STATE.scanInterval);
            return;
        }

        const video = document.getElementById('scanner-video');
        if (!video || video.readyState < 2) return;

        // 1. Native BarcodeDetector (Chrome/Edge/Android)
        if (STATE.barcodeDetector) {
            try {
                const barcodes = await STATE.barcodeDetector.detect(video);
                if (barcodes && barcodes.length > 0) {
                    const rawVal = barcodes[0].rawValue || '';
                    const clean = rawVal.replace(/[^0-9X]/gi, '');
                    if (clean.length >= 10) {
                        onBarcodeDetected(clean, 'Live Camera');
                        return;
                    }
                }
            } catch (e) {}
        }

        // 2. Fallback Canvas Frame Analysis
        const canvas = document.getElementById('scanner-canvas');
        if (canvas) {
            try {
                canvas.width = Math.min(video.videoWidth || 640, 640);
                canvas.height = Math.min(video.videoHeight || 480, 480);
                const ctx = canvas.getContext('2d', { willReadFrequently: true });
                if (ctx) {
                    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                    const decoded = decodeBarcodeFromCanvas(canvas);
                    if (decoded && decoded.length >= 10) {
                        onBarcodeDetected(decoded, 'Live Camera (Canvas)');
                    }
                }
            } catch (e) {}
        }
    }, 280);
}

// Manual Capture & Scan Button
async function captureAndScanBarcode() {
    const video = document.getElementById('scanner-video');
    const canvas = document.getElementById('scanner-canvas');
    const status = document.getElementById('scanner-status');
    const feedbackBadge = document.getElementById('scan-feedback-badge');

    if (!video || video.readyState < 2) {
        if (status) {
            status.innerHTML = `<span class="text-amber-600 font-bold"><i class="fa-solid fa-triangle-exclamation"></i> Camera not ready yet. Please wait a moment.</span>`;
        }
        return;
    }

    if (status) {
        status.innerHTML = `<span class="text-blue-600 font-bold"><i class="fa-solid fa-spinner fa-spin"></i> Processing captured frame...</span>`;
    }

    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const previewImg = document.getElementById('scanner-preview-img');
    if (previewImg) {
        previewImg.src = canvas.toDataURL('image/jpeg', 0.85);
        previewImg.classList.remove('hidden');
        video.classList.add('hidden');
    }

    // Try BarcodeDetector
    if (!STATE.barcodeDetector && 'BarcodeDetector' in window) {
        await initBarcodeDetector();
    }

    if (STATE.barcodeDetector) {
        try {
            const barcodes = await STATE.barcodeDetector.detect(canvas);
            if (barcodes && barcodes.length > 0) {
                const detected = barcodes[0].rawValue.replace(/[^0-9X]/gi, '');
                if (detected.length >= 10) {
                    onBarcodeDetected(detected, 'Captured Frame');
                    return;
                }
            }
        } catch (e) {
            console.warn("Capture BarcodeDetector:", e);
        }
    }

    // Try canvas 1D decoder
    const decoded = decodeBarcodeFromCanvas(canvas);
    if (decoded && decoded.length >= 10) {
        onBarcodeDetected(decoded, 'Captured Frame');
        return;
    }

    if (status) {
        status.innerHTML = `<span class="text-amber-700 font-bold"><i class="fa-solid fa-circle-question"></i> No barcode detected in captured frame. Hold closer or enter ISBN manually.</span>`;
    }
    if (feedbackBadge) {
        feedbackBadge.className = "text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-200";
        feedbackBadge.textContent = "Frame Captured (No Barcode)";
        feedbackBadge.classList.remove('hidden');
    }
    const input = document.getElementById('manual-isbn-input');
    if (input) input.focus();
}
window.captureAndScanBarcode = captureAndScanBarcode;

// Photo Upload Handler for Barcode & Book Photos
async function handleScanImageUpload(event) {
    const file = event.target.files && event.target.files[0];
    if (!file) return;

    stopCameraScanner();

    const placeholder = document.getElementById('scanner-placeholder');
    const previewImg = document.getElementById('scanner-preview-img');
    const laser = document.getElementById('scanner-laser');
    const resetBtn = document.getElementById('scanner-reset-btn');
    const status = document.getElementById('scanner-status');
    const pulse = document.getElementById('scanner-pulse');
    const feedbackBadge = document.getElementById('scan-feedback-badge');

    if (placeholder) placeholder.classList.add('hidden');
    if (laser) laser.classList.remove('hidden');
    if (resetBtn) resetBtn.classList.remove('hidden');
    if (pulse) pulse.className = "w-2.5 h-2.5 rounded-full bg-blue-500 animate-pulse shrink-0";
    if (status) {
        status.innerHTML = `<span class="text-blue-600 font-bold"><i class="fa-solid fa-spinner fa-spin"></i> Reading uploaded barcode image (${file.name})...</span>`;
    }

    const reader = new FileReader();
    reader.onload = async (e) => {
        const dataUrl = e.target.result;
        if (previewImg) {
            previewImg.src = dataUrl;
            previewImg.classList.remove('hidden');
        }

        const img = new Image();
        img.onload = async () => {
            const canvas = document.getElementById('scanner-canvas');
            canvas.width = img.naturalWidth || img.width;
            canvas.height = img.naturalHeight || img.height;
            const ctx = canvas.getContext('2d', { willReadFrequently: true });
            ctx.drawImage(img, 0, 0);

            if (!STATE.barcodeDetector && 'BarcodeDetector' in window) {
                await initBarcodeDetector();
            }

            if (STATE.barcodeDetector) {
                try {
                    const barcodes = await STATE.barcodeDetector.detect(img);
                    if (barcodes && barcodes.length > 0) {
                        const clean = barcodes[0].rawValue.replace(/[^0-9X]/gi, '');
                        if (clean.length >= 10) {
                            onBarcodeDetected(clean, 'Uploaded Image');
                            return;
                        }
                    }
                } catch (err) {
                    console.warn("Uploaded image BarcodeDetector error:", err);
                }
            }

            const decoded = decodeBarcodeFromCanvas(canvas);
            if (decoded && decoded.length >= 10) {
                onBarcodeDetected(decoded, 'Uploaded Image');
                return;
            }

            const filenameMatch = file.name.match(/(97[89][0-9]{10}|[0-9]{10})/);
            if (filenameMatch) {
                onBarcodeDetected(filenameMatch[1], 'Image Filename');
                return;
            }

            if (laser) laser.classList.add('hidden');
            if (pulse) pulse.className = "w-2.5 h-2.5 rounded-full bg-amber-500 shrink-0";
            if (status) {
                status.innerHTML = `<span class="text-amber-700 font-bold"><i class="fa-solid fa-triangle-exclamation"></i> Image loaded. Could not auto-detect barcode. Please enter ISBN printed on book.</span>`;
            }
            if (feedbackBadge) {
                feedbackBadge.className = "text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-200";
                feedbackBadge.textContent = "Photo Ready (Manual ISBN needed)";
                feedbackBadge.classList.remove('hidden');
            }
            const input = document.getElementById('manual-isbn-input');
            if (input) input.focus();
        };
        img.src = dataUrl;
    };
    reader.readAsDataURL(file);
}
window.handleScanImageUpload = handleScanImageUpload;

// Reset Scanner View
function resetScannerView() {
    stopCameraScanner();

    const video = document.getElementById('scanner-video');
    const placeholder = document.getElementById('scanner-placeholder');
    const previewImg = document.getElementById('scanner-preview-img');
    const laser = document.getElementById('scanner-laser');
    const guide = document.getElementById('scanner-guide');
    const captureBtn = document.getElementById('capture-scan-btn');
    const resetBtn = document.getElementById('scanner-reset-btn');
    const status = document.getElementById('scanner-status');
    const pulse = document.getElementById('scanner-pulse');
    const feedbackBadge = document.getElementById('scan-feedback-badge');
    const fileInput = document.getElementById('scan-file-input');

    if (video) video.classList.add('hidden');
    if (previewImg) {
        previewImg.src = '';
        previewImg.classList.add('hidden');
    }
    if (placeholder) placeholder.classList.remove('hidden');
    if (laser) laser.classList.add('hidden');
    if (guide) guide.classList.add('hidden');
    if (captureBtn) captureBtn.classList.add('hidden');
    if (resetBtn) resetBtn.classList.add('hidden');
    if (feedbackBadge) feedbackBadge.classList.add('hidden');
    if (fileInput) fileInput.value = '';

    if (pulse) pulse.className = "w-2.5 h-2.5 rounded-full bg-slate-400 shrink-0";
    if (status) status.textContent = "Ready. Turn on camera, upload a photo, or enter an ISBN below.";
}
window.resetScannerView = resetScannerView;

// Callback when Barcode is identified
function onBarcodeDetected(isbn, source = 'Scanner') {
    stopCameraScanner();

    const laser = document.getElementById('scanner-laser');
    if (laser) laser.classList.add('hidden');

    const pulse = document.getElementById('scanner-pulse');
    if (pulse) pulse.className = "w-2.5 h-2.5 rounded-full bg-emerald-500 shrink-0";

    const feedbackBadge = document.getElementById('scan-feedback-badge');
    if (feedbackBadge) {
        feedbackBadge.className = "text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200";
        feedbackBadge.textContent = `Barcode Detected via ${source}`;
        feedbackBadge.classList.remove('hidden');
    }

    const status = document.getElementById('scanner-status');
    if (status) {
        status.innerHTML = `<span class="text-emerald-700 font-bold"><i class="fa-solid fa-circle-check"></i> Scanned: <span class="font-mono">${isbn}</span>! Comparing offers...</span>`;
    }

    const input = document.getElementById('manual-isbn-input');
    if (input) input.value = isbn;

    scanIsbnQuery(isbn);
}
window.onBarcodeDetected = onBarcodeDetected;

// Flashlight / Torch Controller
async function toggleTorch() {
    STATE.torchOn = !STATE.torchOn;
    const btn = document.getElementById('torch-btn');
    if (btn) {
        btn.classList.toggle('bg-amber-400', STATE.torchOn);
        btn.classList.toggle('text-slate-900', STATE.torchOn);
    }

    if (STATE.cameraStream) {
        const track = STATE.cameraStream.getVideoTracks()[0];
        if (track && track.getCapabilities) {
            const capabilities = track.getCapabilities();
            if (capabilities.torch) {
                try {
                    await track.applyConstraints({ advanced: [{ torch: STATE.torchOn }] });
                } catch (e) {
                    console.warn("Torch constraint error:", e);
                }
            }
        }
    }
}
window.toggleTorch = toggleTorch;

// Sample Books Quick Click Handler
function quickScanSampleBook(isbn) {
    if (!isbn) return;
    const input = document.getElementById('manual-isbn-input');
    if (input) input.value = isbn;
    const status = document.getElementById('scanner-status');
    if (status) {
        status.innerHTML = `<span class="text-blue-700 font-bold"><i class="fa-solid fa-bolt"></i> Sample Book Selected (${isbn})</span>`;
    }
    scanIsbnQuery(isbn);
}
window.quickScanSampleBook = quickScanSampleBook;

function quickCompareBook(isbn) {
    switchTab('scan');
    quickScanSampleBook(isbn);
}
window.quickCompareBook = quickCompareBook;

// Query Scan API & Compare Seller Offers
async function scanIsbnQuery(isbn) {
    if (!isbn) {
        alert("Please enter or scan a valid ISBN.");
        return;
    }
    const cleanIsbn = String(isbn).trim().replace(/[^0-9X]/gi, '');
    if (!cleanIsbn) {
        alert("Please enter a valid numeric ISBN (10 or 13 digits).");
        return;
    }

    const input = document.getElementById('manual-isbn-input');
    if (input && input.value !== cleanIsbn) {
        input.value = cleanIsbn;
    }

    const resultBox = document.getElementById('scan-result-container');
    const loader = document.getElementById('scan-loader');
    const status = document.getElementById('scanner-status');
    const badge = document.getElementById('scan-feedback-badge');

    if (loader) loader.classList.remove('hidden');
    if (resultBox) resultBox.classList.add('hidden');
    if (status) {
        status.innerHTML = `<span class="text-blue-700 font-bold"><i class="fa-solid fa-spinner fa-spin"></i> Looking up ISBN: ${cleanIsbn}...</span>`;
    }
    if (badge) {
        badge.className = "text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-800 border border-blue-200";
        badge.textContent = `Querying: ${cleanIsbn}`;
        badge.classList.remove('hidden');
    }

    try {
        const res = await fetch(`/api/books/scan/?isbn=${encodeURIComponent(cleanIsbn)}`);
        const data = await res.json();
        if (loader) loader.classList.add('hidden');

        if (res.ok && data.book) {
            STATE.currentScanResult = data;
            if (status) {
                status.innerHTML = `<span class="text-emerald-700 font-bold"><i class="fa-solid fa-circle-check"></i> Found: ${data.book.title}</span>`;
            }
            if (badge) {
                badge.className = "text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200";
                badge.textContent = data.found_in_catalog ? 'Catalog Match' : 'Online Book Match';
                badge.classList.remove('hidden');
            }
            renderScanResult(data);
        } else {
            if (status) {
                status.innerHTML = `<span class="text-amber-700 font-bold"><i class="fa-solid fa-triangle-exclamation"></i> ${data.error || 'Book not found'}</span>`;
            }
            if (badge) {
                badge.className = "text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-200";
                badge.textContent = 'Not Found';
                badge.classList.remove('hidden');
            }
            alert(data.error || "Book not found in database. You can enter details manually in the Sell tab!");
        }
    } catch (err) {
        console.error("Scan query error:", err);
        if (loader) loader.classList.add('hidden');
        if (status) {
            status.innerHTML = `<span class="text-rose-700 font-bold"><i class="fa-solid fa-circle-xmark"></i> Network error during book lookup.</span>`;
        }
        alert("Lookup failed. Please check network or enter manual ISBN.");
    }
}
window.scanIsbnQuery = scanIsbnQuery;

// Render Detailed Scan Results & Multi-Seller Comparison
function renderScanResult(data) {
    const resultBox = document.getElementById('scan-result-container');
    if (!resultBox) return;

    const book = data.book;
    const stats = data.price_stats || {};
    const listings = data.listings || [];

    resultBox.classList.remove('hidden');
    resultBox.innerHTML = `
        <div class="bg-white rounded-2xl border border-blue-100 p-5 sm:p-6 shadow-md transition-all">
            <!-- Header Bar -->
            <div class="flex items-center justify-between pb-3.5 border-b border-slate-100 mb-4">
                <span class="text-xs font-bold text-blue-700 uppercase tracking-wide flex items-center gap-1.5">
                    <i class="fa-solid fa-barcode text-sm"></i> Barcode Verified: <span class="font-mono">${book.isbn}</span>
                </span>
                <span class="text-[11px] bg-blue-50 text-blue-700 font-bold px-2.5 py-0.5 rounded-full border border-blue-200">
                    ${data.found_in_catalog ? 'Catalog Match' : 'Verified Metadata'}
                </span>
            </div>

            <!-- Book Details Card -->
            <div class="flex flex-col sm:flex-row gap-5">
                <img src="${book.cover_image || 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=300'}" 
                     alt="${book.title}"
                     class="w-28 sm:w-32 h-40 sm:h-44 object-cover rounded-xl shadow-md border border-slate-200 flex-shrink-0 self-center sm:self-start">
                <div class="flex-1 min-w-0">
                    <h3 class="font-black text-base sm:text-lg text-slate-900 leading-snug">${book.title}</h3>
                    <p class="text-xs text-slate-600 mt-1"><span class="font-bold text-slate-700">Author:</span> ${book.author || 'Unknown Author'}</p>
                    <p class="text-xs text-slate-500 mt-0.5"><span class="font-bold text-slate-700">Publisher:</span> ${book.publisher || 'N/A'}</p>
                    <p class="text-xs text-slate-500 mt-0.5"><span class="font-bold text-slate-700">Category:</span> ${book.category || 'General'}</p>
                    ${book.education_board && book.education_board !== 'General / None' ? `
                        <p class="text-xs text-slate-500 mt-0.5"><span class="font-bold text-slate-700">Board / Class:</span> ${book.education_board} (${book.grade_class || 'All'})</p>
                    ` : ''}

                    <!-- Price Comparison Stats Banner -->
                    ${stats.lowest_price ? `
                        <div class="mt-3.5 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-3.5 flex items-center justify-between">
                            <div>
                                <span class="text-xs text-blue-900 font-extrabold block">Lowest Used Price</span>
                                <span class="text-lg font-black text-blue-900">Rs. ${parseFloat(stats.lowest_price).toFixed(0)}</span>
                            </div>
                            <div class="text-right">
                                <span class="text-[11px] text-slate-500 block">Retail: Rs. ${parseFloat(stats.retail_price || 0).toFixed(0)}</span>
                                <span class="text-xs font-black text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded border border-emerald-300">Save ${stats.max_savings_percent}%</span>
                            </div>
                        </div>
                    ` : `
                        <div class="mt-3.5 bg-amber-50 border border-amber-200 text-amber-900 rounded-xl p-3 text-xs flex items-center gap-2">
                            <i class="fa-solid fa-circle-info text-amber-600"></i>
                            <span>No active seller listings for this book currently. Be the first to list it!</span>
                        </div>
                    `}
                </div>
            </div>

            <!-- Price Comparison Table: Multiple sellers for same book -->
            <div class="mt-6 pt-5 border-t border-slate-100">
                <div class="flex items-center justify-between mb-3">
                    <h4 class="font-black text-xs uppercase tracking-wider text-slate-800 flex items-center gap-1.5">
                        <i class="fa-solid fa-users text-blue-600"></i> Available Seller Offers (${listings.length})
                    </h4>
                    <span class="text-[11px] text-slate-400">Sorted by lowest price</span>
                </div>

                ${listings.length > 0 ? `
                    <div class="space-y-2.5">
                        ${listings.map(l => {
                            const isFree = Boolean(l.is_free || parseFloat(l.price) === 0);
                            return `
                                <div class="p-3.5 bg-slate-50 hover:bg-blue-50/50 rounded-xl border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3 transition-colors">
                                    <div>
                                        <div class="flex items-center gap-2 flex-wrap">
                                            <span class="font-extrabold text-xs text-slate-900">${l.seller_name}</span>
                                            <span class="text-amber-500 font-bold text-xs">★ ${l.seller_rating}</span>
                                            <span class="text-[10px] bg-slate-200 text-slate-700 px-1.5 py-0.5 rounded font-bold">${l.condition}</span>
                                            ${isFree ? `<span class="text-[10px] bg-emerald-100 text-emerald-800 border border-emerald-300 px-1.5 py-0.5 rounded font-black">🎁 FREE DONATION</span>` : ''}
                                        </div>
                                        <p class="text-xs text-slate-500 mt-1 flex items-center gap-1">
                                            <i class="fa-solid fa-location-dot text-blue-600"></i> ${l.city} ${l.pickup_location ? `• ${l.pickup_location}` : ''}
                                        </p>
                                    </div>
                                    <div class="flex items-center justify-between sm:justify-end gap-3 pt-2 sm:pt-0 border-t sm:border-t-0 border-slate-200">
                                        <div class="text-left sm:text-right">
                                            <span class="block text-base font-black ${isFree ? 'text-emerald-700' : 'text-blue-900'}">${isFree ? 'Rs. 0' : 'Rs. ' + parseFloat(l.price).toFixed(0)}</span>
                                            <span class="text-[10px] text-slate-400">${l.seller_reviews_count || 0} reviews</span>
                                        </div>
                                        <button onclick="openUnlockModal(${l.id})" class="px-4 py-2 ${isFree ? 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700' : 'bg-gradient-to-r from-blue-700 to-blue-600 hover:from-blue-800'} text-white rounded-xl text-xs font-extrabold shadow-sm transition-all flex items-center gap-1.5 active:scale-95">
                                            <i class="fa-solid fa-lock-open text-xs"></i>
                                            <span>${isFree ? 'Claim Free' : 'Unlock Contact'}</span>
                                        </button>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                ` : ''}

                <!-- CTA to List This Book for Sale -->
                <div class="mt-4 pt-3.5 border-t border-slate-100 flex items-center justify-between flex-wrap gap-2">
                    <span class="text-xs text-slate-600">Have a copy of this book?</span>
                    <button type="button" onclick="prefillSellForm('${book.isbn}')" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold transition-all shadow-xs flex items-center gap-1.5 active:scale-95">
                        <i class="fa-solid fa-circle-plus"></i> List This Book For Sale or Free Donation
                    </button>
                </div>
            </div>
        </div>
    `;

    resultBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}
window.renderScanResult = renderScanResult;

// PAID CONTACT UNLOCK MODAL (Phase 1 Sandbox)
function openUnlockModal(listingId) {
    let listing = (STATE.allListings && STATE.allListings.find(l => l.id === listingId))
               || (STATE.listings && STATE.listings.find(l => l.id === listingId))
               || (STATE.aiRecommendations && STATE.aiRecommendations.find(l => l.id === listingId));
    if (!listing) return;

    if (STATE.currentUser && STATE.currentUser.id === listing.seller_id) {
        alert("You cannot unlock contact for your own book listing!");
        return;
    }

    STATE.activeListingForUnlock = listing;

    const modal = document.getElementById('unlock-modal');
    if (!modal) return;

    const isFree = Boolean(listing.is_free || parseFloat(listing.price) === 0);

    document.getElementById('modal-book-title').textContent = listing.book.title;
    document.getElementById('modal-book-price').textContent = isFree ? "Rs. 0 (Free Community Donation)" : `Rs. ${parseFloat(listing.price).toFixed(0)}`;
    document.getElementById('modal-seller-name').textContent = listing.seller_name;
    document.getElementById('modal-seller-city').textContent = `${listing.city} (${listing.pickup_location || 'Campus / Pickup'})`;
    document.getElementById('modal-fee-display').textContent = `Rs. ${STATE.platformFee.toFixed(0)}`;

    const errBanner = document.getElementById('unlock-error-banner');
    if (errBanner) {
        errBanner.classList.add('hidden');
        errBanner.classList.remove('flex');
        errBanner.style.setProperty('display', 'none', 'important');
    }
    const errMsg = document.getElementById('unlock-error-message');
    if (errMsg) errMsg.textContent = '';

    document.getElementById('unlock-payment-section').classList.remove('hidden');
    document.getElementById('unlock-result-section').classList.add('hidden');
    selectPaymentMethod('jazzcash');

    modal.classList.remove('hidden');
}

function closeUnlockModal() {
    const modal = document.getElementById('unlock-modal');
    if (modal) modal.classList.add('hidden');
    const errBanner = document.getElementById('unlock-error-banner');
    if (errBanner) {
        errBanner.classList.add('hidden');
        errBanner.classList.remove('flex');
        errBanner.style.setProperty('display', 'none', 'important');
    }
    const errMsg = document.getElementById('unlock-error-message');
    if (errMsg) errMsg.textContent = '';
}

function selectPaymentMethod(method) {
    STATE.selectedPaymentMethod = method;
    document.querySelectorAll('.pay-tab').forEach(t => {
        if (t.getAttribute('data-method') === method) {
            t.classList.add('border-blue-600', 'bg-blue-50', 'text-blue-800');
            t.classList.remove('border-slate-200', 'bg-white', 'text-slate-600');
        } else {
            t.classList.remove('border-blue-600', 'bg-blue-50', 'text-blue-800');
            t.classList.add('border-slate-200', 'bg-white', 'text-slate-600');
        }
    });

    const infoBox = document.getElementById('payment-method-details');
    if (!infoBox) return;

    if (method === 'jazzcash') {
        infoBox.innerHTML = `
            <div class="space-y-2">
                <label class="block text-xs font-semibold text-slate-700">JazzCash Mobile Account Number</label>
                <input type="text" id="pay-account-input" placeholder="03001234567" value="${STATE.currentUser ? STATE.currentUser.phone_number : '03023344556'}" 
                       class="w-full text-xs p-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-red-500 focus:outline-none">
                <label class="block text-xs font-semibold text-slate-700 mt-2">4-Digit MPIN</label>
                <input type="password" id="pay-pin-input" placeholder="••••" value="1234" maxlength="4"
                       class="w-full text-xs p-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-red-500 focus:outline-none">
                <p class="text-[10px] text-slate-400">Sandbox prompt: Rs. ${STATE.platformFee} will be authorized.</p>
            </div>
        `;
    } else if (method === 'easypaisa') {
        infoBox.innerHTML = `
            <div class="space-y-2">
                <label class="block text-xs font-semibold text-slate-700">Easypaisa Mobile Number</label>
                <input type="text" id="pay-account-input" placeholder="03451234567" value="${STATE.currentUser ? STATE.currentUser.phone_number : '03023344556'}" 
                       class="w-full text-xs p-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-500 focus:outline-none">
                <label class="block text-xs font-semibold text-slate-700 mt-2">5-Digit Easypaisa PIN</label>
                <input type="password" id="pay-pin-input" placeholder="•••••" value="12345" maxlength="5"
                       class="w-full text-xs p-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-500 focus:outline-none">
                <p class="text-[10px] text-slate-400">Sandbox prompt: Rs. ${STATE.platformFee} will be authorized.</p>
            </div>
        `;
    } else if (method === 'card_safepay') {
        infoBox.innerHTML = `
            <div class="space-y-2">
                <label class="block text-xs font-semibold text-slate-700">Debit / Credit Card (Safepay / PayFast)</label>
                <input type="text" placeholder="4242 •••• •••• 4242" value="4242 4242 4242 4242" 
                       class="w-full text-xs p-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:outline-none">
                <div class="grid grid-cols-2 gap-2">
                    <input type="text" placeholder="MM/YY" value="12/28" class="text-xs p-2.5 rounded-lg border border-slate-300">
                    <input type="password" placeholder="CVV" value="786" maxlength="4" class="text-xs p-2.5 rounded-lg border border-slate-300">
                </div>
            </div>
        `;
    } else {
        const bal = STATE.currentUser ? parseFloat(STATE.currentUser.wallet_balance) : 0;
        infoBox.innerHTML = `
            <div class="p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs">
                <div class="flex justify-between items-center mb-1">
                    <span class="text-slate-600 font-semibold">Available Wallet Balance:</span>
                    <span class="font-bold text-blue-900">Rs. ${bal.toFixed(2)}</span>
                </div>
                ${bal >= STATE.platformFee ? `
                    <p class="text-blue-700 text-[11px] font-semibold">Sufficient balance. Instant deduction with zero gateway surcharge.</p>
                ` : `
                    <p class="text-red-600 text-[11px] font-semibold">Insufficient wallet balance. Please choose JazzCash or Easypaisa.</p>
                `}
            </div>
        `;
    }
}

// Submit Payment & Unlock Contact
async function submitPaymentUnlock() {
    if (!STATE.activeListingForUnlock || !STATE.currentUser) return;

    const errBanner = document.getElementById('unlock-error-banner');
    const errMsg = document.getElementById('unlock-error-message');
    if (errBanner) {
        errBanner.classList.add('hidden');
        errBanner.classList.remove('flex');
        errBanner.style.setProperty('display', 'none', 'important');
    }
    if (errMsg) errMsg.textContent = '';

    const btn = document.getElementById('pay-submit-btn');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin mr-1.5"></i> Authorizing Gateway...`;
    }

    try {
        const res = await fetch('/api/unlocks/request/', {
            method: 'POST',
            headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
            body: JSON.stringify({
                listing_id: STATE.activeListingForUnlock.id,
                buyer_id: STATE.currentUser.id,
                payment_method: STATE.selectedPaymentMethod,
                account_number: document.getElementById('pay-account-input')?.value || STATE.currentUser.phone_number
            })
        });

        const data = await res.json();
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `<i class="fa-solid fa-lock-open mr-1.5"></i> Pay Rs. ${STATE.platformFee} & Unlock Contact`;
        }

        if (res.ok) {
            showUnlockedContactResult(data);
            const userRes = await fetch('/api/auth/profiles/');
            STATE.allUsers = await userRes.json();
            STATE.currentUser = STATE.allUsers.find(u => u.id === STATE.currentUser.id);
            updateUserUI();
        } else {
            const errText = data.error || "Payment failed. Please retry.";
            if (errBanner && errMsg) {
                errMsg.textContent = errText;
                errBanner.classList.remove('hidden');
                errBanner.classList.add('flex');
                errBanner.style.setProperty('display', 'flex', 'important');
            } else {
                alert(errText);
            }
        }
    } catch (err) {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `<i class="fa-solid fa-lock-open mr-1.5"></i> Pay Rs. ${STATE.platformFee} & Unlock Contact`;
        }
        if (errBanner && errMsg) {
            errMsg.textContent = "Payment network error. Please try again.";
            errBanner.classList.remove('hidden');
            errBanner.classList.add('flex');
            errBanner.style.setProperty('display', 'flex', 'important');
        } else {
            alert("Payment network error.");
        }
    }
}

function showUnlockedContactResult(data) {
    document.getElementById('unlock-payment-section').classList.add('hidden');
    const resultSec = document.getElementById('unlock-result-section');
    resultSec.classList.remove('hidden');

    const sc = data.seller_contact;
    const unlock = data.unlock;

    resultSec.innerHTML = `
        <div class="text-center py-2">
            <div class="w-12 h-12 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center mx-auto mb-2 text-xl shadow-xs">
                <i class="fa-solid fa-check"></i>
            </div>
            <h4 class="font-extrabold text-slate-900 text-base">Contact Unlocked!</h4>
            <p class="text-xs text-slate-500 mt-0.5">Fee: Rs. ${unlock.fee_amount} (${unlock.payment_method.toUpperCase()}) • Ref: ${unlock.transaction_id}</p>
        </div>

        <div class="bg-blue-50 border border-blue-200 rounded-2xl p-4 my-3 text-left">
            <div class="flex items-center justify-between pb-2 border-b border-blue-100">
                <span class="text-xs text-blue-900 font-bold">Seller Name</span>
                <span class="text-sm font-extrabold text-slate-900">${sc.full_name}</span>
            </div>
            <div class="flex items-center justify-between py-2 border-b border-blue-100">
                <span class="text-xs text-blue-900 font-bold">Direct Phone</span>
                <span class="text-base font-black text-blue-900 tracking-wider">${sc.phone_number}</span>
            </div>
            <div class="flex items-center justify-between pt-2">
                <span class="text-xs text-blue-900 font-bold">Location</span>
                <span class="text-xs font-semibold text-slate-700">${sc.city} - ${sc.campus_or_area}</span>
            </div>
        </div>

        <!-- Direct Contact Action Buttons -->
        <div class="grid grid-cols-2 gap-2.5 my-3">
            <a href="tel:${sc.phone_number}" class="py-2.5 bg-blue-700 hover:bg-blue-800 text-white rounded-xl text-xs font-bold text-center flex items-center justify-center gap-1.5 shadow-sm">
                <i class="fa-solid fa-phone"></i> Call Seller
            </a>
            <a href="${sc.whatsapp_link}" target="_blank" class="py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold text-center flex items-center justify-center gap-1.5 shadow-sm">
                <i class="fa-brands fa-whatsapp text-sm"></i> WhatsApp
            </a>
        </div>

        <button onclick="closeUnlockModal(); switchTab('deals');" class="w-full mt-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold">
            Done • View in My Unlocks
        </button>
    `;
}

// User Deals & Refund Workflow
async function loadUserDeals() {
    if (!STATE.currentUser) return;
    const container = document.getElementById('user-deals-container');
    if (!container) return;

    container.innerHTML = `
        <div class="p-8 text-center text-slate-400">
            <i class="fa-solid fa-spinner fa-spin text-2xl"></i>
            <p class="text-xs mt-2">Loading contact unlock records...</p>
        </div>
    `;

    try {
        const res = await fetch(`/api/unlocks/user/${STATE.currentUser.id}/`, {
            headers: getAuthHeaders()
        });
        const data = await res.json();
        renderDealsList(data);
    } catch (err) {
        container.innerHTML = `<p class="text-xs text-red-500 text-center p-4">Error loading records.</p>`;
    }
}

function renderDealsList(data) {
    const container = document.getElementById('user-deals-container');
    if (!container) return;

    const buyerUnlocks = data.as_buyer || [];
    const sellerUnlocks = data.as_seller || [];

    if (buyerUnlocks.length === 0 && sellerUnlocks.length === 0) {
        container.innerHTML = `
            <div class="p-8 text-center bg-white rounded-2xl border border-dashed border-slate-300">
                <i class="fa-solid fa-handshake text-3xl text-slate-300 mb-2"></i>
                <p class="text-sm font-semibold text-slate-700">No Contact Unlocks Yet</p>
                <p class="text-xs text-slate-500 mt-1">Unlocked seller contacts will appear here.</p>
                <button onclick="switchTab('home')" class="mt-3 px-4 py-2 bg-blue-700 text-white text-xs font-bold rounded-xl">Browse Books</button>
            </div>
        `;
        return;
    }

    let html = '';

    if (buyerUnlocks.length > 0) {
        html += `<h4 class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Contacts You Unlocked (As Buyer)</h4>`;
        buyerUnlocks.forEach(u => {
            html += generateDealCard(u, 'buyer');
        });
    }

    if (sellerUnlocks.length > 0) {
        html += `<h4 class="text-xs font-bold text-slate-500 uppercase tracking-wider mt-4 mb-2">Buyers Contacting You (As Seller)</h4>`;
        sellerUnlocks.forEach(u => {
            html += generateDealCard(u, 'seller');
        });
    }

    container.innerHTML = html;
}

function generateDealCard(u, role) {
    const statusBadges = {
        'unlocked_pending': '<span class="bg-amber-100 text-amber-800 border border-amber-300 text-[10px] font-bold px-2 py-0.5 rounded-full"><i class="fa-solid fa-clock"></i> Pending Deal</span>',
        'deal_made': '<span class="bg-emerald-100 text-emerald-800 border border-emerald-300 text-[10px] font-bold px-2 py-0.5 rounded-full"><i class="fa-solid fa-circle-check"></i> Deal Confirmed</span>',
        'no_deal_refunded': '<span class="bg-blue-100 text-blue-800 border border-blue-300 text-[10px] font-bold px-2 py-0.5 rounded-full"><i class="fa-solid fa-rotate-left"></i> Rs. 50 Refunded</span>',
        'disputed': '<span class="bg-red-100 text-red-800 border border-red-300 text-[10px] font-bold px-2 py-0.5 rounded-full"><i class="fa-solid fa-triangle-exclamation"></i> Disputed</span>',
    };

    const isPending = u.deal_status === 'unlocked_pending';
    const otherPerson = role === 'buyer' ? u.seller_name : u.buyer_name;
    const otherPhone = role === 'buyer' ? u.seller_phone : u.buyer_phone;

    return `
        <div class="bg-white rounded-xl border border-slate-200 p-3.5 shadow-xs mb-3">
            <div class="flex items-center justify-between pb-2 border-b border-slate-100">
                <span class="text-xs font-extrabold text-slate-900 line-clamp-1">${u.listing_title}</span>
                ${statusBadges[u.deal_status] || ''}
            </div>

            <div class="grid grid-cols-2 gap-2 my-2.5 text-xs">
                <div>
                    <span class="text-[10px] text-slate-400 block">${role === 'buyer' ? 'Seller' : 'Buyer'} Name</span>
                    <span class="font-bold text-slate-800">${otherPerson}</span>
                </div>
                <div>
                    <span class="text-[10px] text-slate-400 block">Phone / WhatsApp</span>
                    <span class="font-mono font-bold text-blue-700">${otherPhone}</span>
                </div>
                <div>
                    <span class="text-[10px] text-slate-400 block">Book Listed Price</span>
                    <span class="font-extrabold text-slate-800">Rs. ${u.listing_price}</span>
                </div>
                <div>
                    <span class="text-[10px] text-slate-400 block">Unlock Fee Paid</span>
                    <span class="font-bold text-slate-800">Rs. ${u.fee_amount} (${u.payment_method})</span>
                </div>
            </div>

            ${u.refund_transaction_id ? `
                <div class="bg-blue-50 border border-blue-200 rounded-lg p-2 text-[11px] text-blue-900 mb-2">
                    <i class="fa-solid fa-rotate-left mr-1"></i> <strong>Refund Processed:</strong> Ref #${u.refund_transaction_id} • Credited to wallet.
                </div>
            ` : ''}

            <!-- Action buttons for pending deal -->
            ${isPending ? `
                <div class="pt-2 border-t border-slate-100 flex gap-2">
                    <button onclick="confirmDeal('${u.unlock_id}')" class="flex-1 py-2 bg-blue-700 hover:bg-blue-800 text-white rounded-xl text-xs font-bold shadow-sm">
                        <i class="fa-solid fa-check mr-1"></i> Deal Completed
                    </button>
                    <button onclick="cancelDealRefundPrompt('${u.unlock_id}')" class="flex-1 py-2 bg-slate-100 hover:bg-rose-50 hover:text-rose-700 text-slate-700 rounded-lg text-xs font-bold border border-slate-300">
                        <i class="fa-solid fa-xmark mr-1"></i> No Deal (Refund Fee)
                    </button>
                </div>
            ` : ''}

            ${u.deal_status === 'deal_made' && role === 'buyer' && !u.has_review ? `
                <div class="pt-2 border-t border-slate-100">
                    <button onclick="openReviewModal('${u.unlock_id}', '${u.seller_name}')" class="w-full py-1.5 bg-amber-500 hover:bg-amber-600 text-white rounded-lg text-xs font-bold">
                        ★ Rate & Review Seller
                    </button>
                </div>
            ` : ''}
        </div>
    `;
}

// Confirm Deal Made
async function confirmDeal(unlockId) {
    if (!confirm("Are you sure the book deal was completed? Bookzy AI will finalize the Rs. 50 fee and mark the book as sold.")) {
        return;
    }

    try {
        const res = await fetch(`/api/unlocks/${unlockId}/confirm_deal/`, {
            method: 'POST',
            headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
            body: JSON.stringify({ user_id: STATE.currentUser.id })
        });
        const data = await res.json();
        alert(data.message);
        loadUserDeals();
    } catch (err) {
        alert("Error confirming deal.");
    }
}

// Cancel Deal & Trigger Instant Refund
async function cancelDealRefundPrompt(unlockId) {
    const reason = prompt("Reason for no deal (e.g. Seller unresponsive, Book already sold elsewhere):", "Seller had already sold the book.");
    if (reason === null) return;

    try {
        const res = await fetch(`/api/unlocks/${unlockId}/cancel_deal/`, {
            method: 'POST',
            headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
            body: JSON.stringify({ reason: reason })
        });
        const data = await res.json();
        alert(data.message);
        loadUserDeals();
        const usersRes = await fetch('/api/auth/profiles/');
        STATE.allUsers = await usersRes.json();
        STATE.currentUser = STATE.allUsers.find(u => u.id === STATE.currentUser.id);
        updateUserUI();
    } catch (err) {
        alert("Error processing refund.");
    }
}

// Seller Dashboard: "My Published Listings"
async function loadMySellerListings() {
    if (!STATE.currentUser) return;
    const container = document.getElementById('seller-my-listings-container');
    if (!container) return;

    try {
        const res = await fetch(`/api/listings/seller/${STATE.currentUser.id}/`, {
            headers: getAuthHeaders()
        });
        const listings = await res.json();

        if (listings.length === 0) {
            container.innerHTML = `
                <div class="p-4 text-center text-slate-400 text-xs">
                    You have not published any book listings yet. Click <strong>Sell</strong> to list a book!
                </div>
            `;
            return;
        }

        container.innerHTML = listings.map(l => `
            <div class="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between text-xs">
                <div class="flex items-center gap-2.5">
                    <img src="${l.display_image || l.photo_url || l.book.cover_image || 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=100'}" class="w-10 h-14 object-cover rounded-md shadow-xs">
                    <div>
                        <h5 class="font-bold text-slate-900 line-clamp-1">${l.book.title}</h5>
                        <p class="text-[11px] text-slate-500">Rs. ${l.price} • ${l.condition}</p>
                        <span class="inline-block mt-0.5 px-1.5 py-0.2 rounded text-[10px] font-bold ${l.status === 'active' ? 'bg-blue-100 text-blue-800' : 'bg-slate-200 text-slate-700'}">
                            ${l.status === 'active' ? 'Available' : 'Sold'}
                        </span>
                    </div>
                </div>

                <div class="flex items-center gap-1.5">
                    <button onclick="toggleListingStatusAction(${l.id})" class="px-2 py-1 bg-white border border-slate-300 hover:bg-slate-100 rounded text-[11px] font-semibold text-slate-700" title="Toggle Available / Sold">
                        ${l.status === 'active' ? 'Mark Sold' : 'Reactivate'}
                    </button>
                    <button onclick="openEditListingModal(${l.id})" class="px-2.5 py-1 bg-blue-700 hover:bg-blue-800 text-white rounded-lg text-[11px] font-bold" title="Edit Price/Condition">
                        Edit
                    </button>
                    <button onclick="deleteListingAction(${l.id})" class="p-1 text-red-500 hover:text-red-700" title="Delete">
                        <i class="fa-solid fa-trash text-xs"></i>
                    </button>
                </div>
            </div>
        `).join('');
    } catch (e) {
        console.error(e);
    }
}

async function toggleListingStatusAction(listingId) {
    try {
        const res = await fetch(`/api/listings/${listingId}/toggle_status/`, { 
            method: 'POST',
            headers: getAuthHeaders()
        });
        const data = await res.json();
        alert(data.message);
        loadMySellerListings();
        applyFilters();
    } catch (e) {
        alert("Error toggling status");
    }
}

async function deleteListingAction(listingId) {
    if (!confirm("Are you sure you want to delete this book listing?")) return;
    try {
        const res = await fetch(`/api/listings/${listingId}/delete/`, {
            method: 'POST',
            headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
            body: JSON.stringify({ seller_id: STATE.currentUser.id })
        });
        const data = await res.json();
        alert(data.message);
        loadMySellerListings();
        applyFilters();
    } catch (e) {
        alert("Error deleting listing");
    }
}

// Edit Listing Modal
function openEditListingModal(listingId) {
    const listing = STATE.listings.find(l => l.id === listingId);
    if (!listing) return;

    document.getElementById('edit-listing-id').value = listing.id;
    document.getElementById('edit-modal-title').textContent = listing.book.title;
    document.getElementById('edit-price-input').value = listing.price;
    document.getElementById('edit-condition-select').value = listing.condition;
    document.getElementById('edit-pickup-input').value = listing.pickup_location;
    document.getElementById('edit-desc-input').value = listing.description || '';
    document.getElementById('edit-status-select').value = listing.status;

    document.getElementById('edit-listing-modal').classList.remove('hidden');
}

function closeEditListingModal() {
    document.getElementById('edit-listing-modal').classList.add('hidden');
}

async function submitEditListing() {
    const id = document.getElementById('edit-listing-id').value;
    const price = document.getElementById('edit-price-input').value;
    const cond = document.getElementById('edit-condition-select').value;
    const pickup = document.getElementById('edit-pickup-input').value;
    const desc = document.getElementById('edit-desc-input').value;
    const status = document.getElementById('edit-status-select').value;

    try {
        const res = await fetch(`/api/listings/${id}/edit/`, {
            method: 'POST',
            headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
            body: JSON.stringify({
                seller_id: STATE.currentUser.id,
                price: price,
                condition: cond,
                pickup_location: pickup,
                description: desc,
                status: status
            })
        });
        const data = await res.json();
        alert(data.message);
        closeEditListingModal();
        loadMySellerListings();
        applyFilters();
    } catch (e) {
        alert("Error saving edits");
    }
}

// Real Auth Modal (Login & Register)
function openAuthModal(mode = 'login') {
    switchAuthTab(mode);
    document.getElementById('auth-modal').classList.remove('hidden');
}

function closeAuthModal() {
    document.getElementById('auth-modal').classList.add('hidden');
}

function switchAuthTab(mode) {
    const loginForm = document.getElementById('auth-login-form');
    const regForm = document.getElementById('auth-register-form');
    const loginTab = document.getElementById('auth-tab-login');
    const regTab = document.getElementById('auth-tab-register');

    if (mode === 'login') {
        loginForm.classList.remove('hidden');
        regForm.classList.add('hidden');
        loginTab.classList.add('text-blue-700', 'border-b-2', 'border-blue-700');
        loginTab.classList.remove('text-slate-400');
        regTab.classList.remove('text-blue-700', 'border-b-2', 'border-blue-700');
        regTab.classList.add('text-slate-400');
    } else {
        loginForm.classList.add('hidden');
        regForm.classList.remove('hidden');
        regTab.classList.add('text-blue-700', 'border-b-2', 'border-blue-700');
        regTab.classList.remove('text-slate-400');
        loginTab.classList.remove('text-blue-700', 'border-b-2', 'border-blue-700');
        loginTab.classList.add('text-slate-400');
    }
}

async function handleAuthLogin(e) {
    e.preventDefault();
    const ident = document.getElementById('login-identifier').value.trim();
    const pass = document.getElementById('login-password').value;

    try {
        const res = await fetch('/api/auth/login/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone_or_username: ident, password: pass })
        });
        const data = await res.json();
        if (res.ok) {
            sessionStorage.setItem('bookzy_session_active', 'true');
            localStorage.setItem('bookloop_token', data.token);
            localStorage.setItem('bb_user_id', data.profile.id);
            alert(`Welcome back, ${data.profile.full_name}!`);
            closeAuthModal();
            location.reload();
        } else {
            alert(data.error || "Login failed");
        }
    } catch (err) {
        alert("Login error");
    }
}

async function handleAuthRegister(e) {
    e.preventDefault();
    const fullname = document.getElementById('reg-fullname').value.trim();
    const phone = document.getElementById('reg-phone').value.trim();
    const city = document.getElementById('reg-city').value;
    const password = document.getElementById('reg-password').value;

    try {
        const res = await fetch('/api/auth/register/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ full_name: fullname, phone_number: phone, city: city, password: password })
        });
        const data = await res.json();
        if (res.ok) {
            sessionStorage.setItem('bookzy_session_active', 'true');
            localStorage.setItem('bookloop_token', data.token);
            localStorage.setItem('bb_user_id', data.profile.id);
            alert(data.message);
            closeAuthModal();
            location.reload();
        } else {
            alert(data.error || "Registration failed");
        }
    } catch (err) {
        alert("Registration error");
    }
}

// Seller Review Modal
function openReviewModal(unlockId, sellerName) {
    const modal = document.getElementById('review-modal');
    if (!modal) return;
    document.getElementById('review-unlock-id').value = unlockId;
    document.getElementById('review-seller-name').textContent = sellerName;
    modal.classList.remove('hidden');
}

function closeReviewModal() {
    const modal = document.getElementById('review-modal');
    if (modal) modal.classList.add('hidden');
}

async function submitReview() {
    const unlockId = document.getElementById('review-unlock-id').value;
    const rating = document.getElementById('review-rating-select').value;
    const comment = document.getElementById('review-comment-input').value;

    try {
        const res = await fetch('/api/reviews/create/', {
            method: 'POST',
            headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
            body: JSON.stringify({ unlock_id: unlockId, rating: rating, comment: comment })
        });
        const data = await res.json();
        alert(data.message);
        closeReviewModal();
        loadUserDeals();
    } catch (err) {
        alert("Error submitting review.");
    }
}

// Selling Flow with Multipart Image Upload & Interstitial Ad
function prefillSellForm(isbn) {
    switchTab('sell');
    const input = document.getElementById('sell-isbn-input');
    if (input) {
        input.value = isbn;
        autoFetchBookForSell(isbn);
    }
}

async function autoFetchBookForSell(isbn) {
    if (!isbn) return;
    try {
        const res = await fetch(`/api/books/scan/?isbn=${encodeURIComponent(isbn)}`);
        const data = await res.json();
        if (data && data.book) {
            const b = data.book;
            document.getElementById('sell-title-input').value = b.title || '';
            document.getElementById('sell-author-input').value = b.author || '';
            document.getElementById('sell-category-select').value = b.category || 'Software Engineering';
            document.getElementById('sell-board-select').value = b.education_board || 'Higher Education / University';
            document.getElementById('sell-class-select').value = b.grade_class || 'Bachelor / BS / Undergrad';
            document.getElementById('sell-subject-input').value = b.subject || '';
            document.getElementById('sell-photo-input').value = b.cover_image || '';
            if (b.original_retail_price) {
                const mrpInput = document.getElementById('sell-original-price-input');
                if (mrpInput) mrpInput.value = parseFloat(b.original_retail_price).toFixed(0);
            }
            if (typeof updateAiPriceAdvisor === 'function') {
                updateAiPriceAdvisor();
            }
        }
    } catch (e) {
        console.warn("Could not prefill", e);
    }
}

function toggleSellFreeDonation(isFree) {
    const toggle = document.getElementById('sell-is-free-toggle');
    if (toggle && toggle.checked !== isFree) {
        toggle.checked = isFree;
    }

    const priceInput = document.getElementById('sell-price-input');
    const priceWrapper = document.getElementById('sell-price-wrapper');
    const priceLabel = document.getElementById('sell-price-label');
    const priceSublabel = document.getElementById('sell-price-sublabel');
    const submitText = document.getElementById('sell-submit-text');
    const advisorInsight = document.getElementById('ai-price-insight');
    const advisorNum = document.getElementById('ai-price-num');
    const applyBtn = document.getElementById('apply-ai-price-btn');

    if (isFree) {
        if (priceInput) {
            priceInput.value = 0;
            priceInput.readOnly = true;
            priceInput.classList.add('bg-emerald-50', 'text-emerald-700', 'font-black');
        }
        if (priceLabel) priceLabel.textContent = "🎁 Free Community Donation (Rs. 0)";
        if (priceSublabel) priceSublabel.textContent = "Giving back to students in need";
        if (priceWrapper) {
            priceWrapper.classList.remove('from-blue-50', 'to-indigo-50', 'border-blue-200');
            priceWrapper.classList.add('from-emerald-50', 'to-teal-50', 'border-emerald-300');
        }
        if (submitText) submitText.textContent = "🎁 List Book as Free Donation (Rs. 0)";
        if (advisorNum) advisorNum.textContent = "Rs. 0";
        if (advisorInsight) {
            advisorInsight.innerHTML = `AI Advisor: <span class="font-bold text-emerald-300">Free Community Giveaway (Rs. 0)</span> — Promoted with #1 priority on homepage!`;
        }
        if (applyBtn) applyBtn.classList.add('hidden');
    } else {
        if (priceInput) {
            priceInput.readOnly = false;
            priceInput.classList.remove('bg-emerald-50', 'text-emerald-700');
            if (priceInput.value == 0) priceInput.value = CURRENT_AI_SUGGESTED_PRICE || 500;
        }
        if (priceLabel) priceLabel.textContent = "Your Selling Price (PKR) *";
        if (priceSublabel) priceSublabel.textContent = "You keep 100% of this amount";
        if (priceWrapper) {
            priceWrapper.classList.add('from-blue-50', 'to-indigo-50', 'border-blue-200');
            priceWrapper.classList.remove('from-emerald-50', 'to-teal-50', 'border-emerald-300');
        }
        if (submitText) submitText.textContent = "Publish Book for Sale";
        if (advisorNum) advisorNum.textContent = `Rs. ${CURRENT_AI_SUGGESTED_PRICE || 680}`;
        if (advisorInsight) {
            advisorInsight.innerHTML = `AI Suggested Price: <span class="font-bold text-amber-300" id="ai-price-num">Rs. ${CURRENT_AI_SUGGESTED_PRICE || 680}</span> (Optimal for fast sale in 'Good' condition)`;
        }
        if (applyBtn) applyBtn.classList.remove('hidden');
    }
}

// ==========================================
// SELL FORM: BOOK PHOTO CAMERA & GALLERY
// ==========================================
window.currentBookPhotoFile = null;
window._bookWebcamStream = null;
window._bookWebcamCurrentDeviceId = null;

function isMobileUserAgent() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
           (navigator.maxTouchPoints && navigator.maxTouchPoints > 2 && /Macintosh/i.test(navigator.userAgent));
}

function openBookPhotoCamera() {
    // 1. Mobile devices: native rear camera via capture="environment"
    if (isMobileUserAgent()) {
        const cameraInput = document.getElementById('sell-camera-file');
        if (cameraInput) {
            cameraInput.click();
            return;
        }
    }

    // 2. Desktop: live webcam capture modal if getUserMedia is supported
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        openBookWebcamModal();
    } else {
        // Fallback to camera or standard file input
        const cameraInput = document.getElementById('sell-camera-file');
        if (cameraInput) {
            cameraInput.click();
        } else {
            document.getElementById('sell-image-file')?.click();
        }
    }
}
window.openBookPhotoCamera = openBookPhotoCamera;

function openBookPhotoGallery() {
    const fileInput = document.getElementById('sell-image-file');
    if (fileInput) {
        fileInput.click();
    }
}
window.openBookPhotoGallery = openBookPhotoGallery;

function handleSelectedBookPhoto(file) {
    if (!file) return;

    // Check size limit: 5MB
    const MAX_SIZE = 5 * 1024 * 1024;
    if (file.size > MAX_SIZE) {
        alert(`The selected photo is too large (${(file.size / (1024 * 1024)).toFixed(2)} MB). Please select or take a photo under 5MB.`);
        return;
    }

    // Check file extension / MIME type
    const validTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg'];
    const fileName = file.name || 'book_photo.jpg';
    const ext = fileName.includes('.') ? fileName.substring(fileName.lastIndexOf('.')).toLowerCase() : '.jpg';
    const validExts = ['.jpg', '.jpeg', '.png', '.webp'];

    if (file.type && !validTypes.includes(file.type) && !validExts.includes(ext)) {
        alert("Please select a valid image file (.jpg, .jpeg, .png, or .webp).");
        return;
    }

    // Store in global state
    window.currentBookPhotoFile = file;

    // Try synchronizing with the file inputs if supported
    try {
        const dt = new DataTransfer();
        dt.items.add(file);
        const imageInput = document.getElementById('sell-image-file');
        if (imageInput) imageInput.files = dt.files;
    } catch (e) {
        // DataTransfer may not be supported on all browsers
    }

    // Live preview update
    const reader = new FileReader();
    reader.onload = function(evt) {
        const preview = document.getElementById('sell-image-preview');
        const img = document.getElementById('sell-preview-img');
        const filenameEl = document.getElementById('sell-preview-filename');
        const metaEl = document.getElementById('sell-preview-meta');

        if (img) img.src = evt.target.result;
        if (filenameEl) filenameEl.textContent = fileName;
        if (metaEl) {
            const sizeKb = (file.size / 1024).toFixed(1);
            metaEl.textContent = `${sizeKb} KB · Ready for upload`;
        }
        if (preview) preview.classList.remove('hidden');
    };
    reader.readAsDataURL(file);
}
window.handleSelectedBookPhoto = handleSelectedBookPhoto;

function retakeBookPhoto() {
    openBookPhotoCamera();
}
window.retakeBookPhoto = retakeBookPhoto;

function removeBookPhoto() {
    window.currentBookPhotoFile = null;
    const imageInput = document.getElementById('sell-image-file');
    const cameraInput = document.getElementById('sell-camera-file');
    const photoInput = document.getElementById('sell-photo-input');
    const preview = document.getElementById('sell-image-preview');
    const img = document.getElementById('sell-preview-img');
    const filenameEl = document.getElementById('sell-preview-filename');
    const metaEl = document.getElementById('sell-preview-meta');

    if (imageInput) imageInput.value = '';
    if (cameraInput) cameraInput.value = '';
    if (photoInput) photoInput.value = '';
    if (img) img.src = '';
    if (filenameEl) filenameEl.textContent = '';
    if (metaEl) metaEl.textContent = '';
    if (preview) preview.classList.add('hidden');
}
window.removeBookPhoto = removeBookPhoto;

// ==========================================
// DESKTOP LIVE WEBCAM CAPTURE MODAL
// ==========================================
async function openBookWebcamModal() {
    const modal = document.getElementById('book-webcam-modal');
    const video = document.getElementById('book-webcam-video');
    const loading = document.getElementById('book-webcam-loading');
    const switchBtn = document.getElementById('book-webcam-switch-btn');

    if (!modal) return;
    modal.classList.remove('hidden');
    if (loading) loading.classList.remove('hidden');

    try {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            throw new Error("Webcam not supported by browser");
        }

        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            const videoDevices = devices.filter(d => d.kind === 'videoinput');
            if (switchBtn) {
                switchBtn.classList.toggle('hidden', videoDevices.length <= 1);
            }
        } catch (e) {}

        const constraints = {
            video: {
                facingMode: { ideal: 'environment' },
                width: { ideal: 1280 },
                height: { ideal: 720 }
            }
        };

        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        window._bookWebcamStream = stream;
        if (video) {
            video.srcObject = stream;
            await video.play().catch(e => console.warn("Video play error:", e));
        }
        if (loading) loading.classList.add('hidden');
    } catch (err) {
        console.warn("Desktop webcam unavailable, falling back to file picker:", err);
        closeBookWebcamModal();
        // Fallback to camera / file input
        const cameraInput = document.getElementById('sell-camera-file');
        if (cameraInput) {
            cameraInput.click();
        } else {
            document.getElementById('sell-image-file')?.click();
        }
    }
}
window.openBookWebcamModal = openBookWebcamModal;

function closeBookWebcamModal() {
    const modal = document.getElementById('book-webcam-modal');
    if (modal) modal.classList.add('hidden');

    if (window._bookWebcamStream) {
        window._bookWebcamStream.getTracks().forEach(track => track.stop());
        window._bookWebcamStream = null;
    }
    const video = document.getElementById('book-webcam-video');
    if (video) video.srcObject = null;
}
window.closeBookWebcamModal = closeBookWebcamModal;

async function switchBookWebcamCamera() {
    try {
        if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) return;
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(d => d.kind === 'videoinput');
        if (videoDevices.length <= 1) return;

        const currentId = window._bookWebcamCurrentDeviceId;
        let nextIndex = 0;
        if (currentId) {
            const currentIndex = videoDevices.findIndex(d => d.deviceId === currentId);
            if (currentIndex !== -1) {
                nextIndex = (currentIndex + 1) % videoDevices.length;
            }
        }
        const nextDevice = videoDevices[nextIndex];
        window._bookWebcamCurrentDeviceId = nextDevice.deviceId;

        if (window._bookWebcamStream) {
            window._bookWebcamStream.getTracks().forEach(track => track.stop());
            window._bookWebcamStream = null;
        }

        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                deviceId: { exact: nextDevice.deviceId },
                width: { ideal: 1280 },
                height: { ideal: 720 }
            }
        });
        window._bookWebcamStream = stream;
        const video = document.getElementById('book-webcam-video');
        if (video) {
            video.srcObject = stream;
            await video.play().catch(e => console.warn(e));
        }
    } catch (e) {
        console.warn("Failed to switch camera:", e);
    }
}
window.switchBookWebcamCamera = switchBookWebcamCamera;

function captureBookWebcamPhoto() {
    const video = document.getElementById('book-webcam-video');
    if (!video || !video.videoWidth) {
        alert("Camera stream is not ready yet. Please wait a moment.");
        return;
    }

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
        if (!blob) {
            alert("Failed to capture image from camera.");
            return;
        }
        const fileName = `book_photo_${Date.now()}.jpg`;
        const file = new File([blob], fileName, { type: 'image/jpeg' });
        handleSelectedBookPhoto(file);
        closeBookWebcamModal();
    }, 'image/jpeg', 0.92);
}
window.captureBookWebcamPhoto = captureBookWebcamPhoto;

async function handleCreateListingSubmit(e) {
    e.preventDefault();
    if (!STATE.currentUser) {
        alert("Please select or sign into an active user profile first.");
        return;
    }

    const isFree = document.getElementById('sell-is-free-toggle')?.checked || false;
    const targetAgeGroup = document.getElementById('sell-age-group-select')?.value || 'all';

    const formData = new FormData();
    formData.append('seller_id', STATE.currentUser.id);
    formData.append('isbn', document.getElementById('sell-isbn-input').value.trim());
    formData.append('title', document.getElementById('sell-title-input').value.trim());
    formData.append('author', document.getElementById('sell-author-input').value.trim());
    formData.append('price', isFree ? '0' : document.getElementById('sell-price-input').value);
    formData.append('is_free', isFree ? 'true' : 'false');
    formData.append('target_age_group', targetAgeGroup);
    formData.append('condition', document.getElementById('sell-condition-select').value);
    formData.append('city', document.getElementById('sell-city-select').value);
    formData.append('pickup_location', document.getElementById('sell-pickup-input').value);
    formData.append('description', document.getElementById('sell-desc-input').value);
    formData.append('category', document.getElementById('sell-category-select').value);
    formData.append('education_board', document.getElementById('sell-board-select').value);
    formData.append('grade_class', document.getElementById('sell-class-select').value);
    formData.append('subject', document.getElementById('sell-subject-input').value.trim());
    formData.append('photo_url', document.getElementById('sell-photo-input').value);

    const imageFile = window.currentBookPhotoFile || 
                      document.getElementById('sell-camera-file')?.files[0] || 
                      document.getElementById('sell-image-file')?.files[0];
    if (imageFile) {
        formData.append('image', imageFile, imageFile.name || 'book_photo.jpg');
    }

    try {
        const res = await fetch('/api/listings/create/', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: formData
        });

        const data = await res.json();
        if (res.ok) {
            // Refresh catalog listings
            try {
                const listRes = await fetch('/api/listings/');
                if (listRes.ok) {
                    STATE.allListings = await listRes.json();
                    STATE.listings = STATE.allListings;
                }
            } catch (err) {}

            // Clean up photo preview and form
            removeBookPhoto();
            document.getElementById('sell-book-form')?.reset();

            if (data.interstitial_ad) {
                showInterstitialAd(data.interstitial_ad);
            } else {
                alert(isFree ? "🎁 Thank you! Your book was successfully listed as a Free Community Donation (Rs. 0)." : "Book listed successfully!");
                switchTab('home');
            }
            applyFilters();
            loadMySellerListings();
            loadAiRecommendations();
        } else {
            alert(data.error || "Failed to publish listing.");
        }
    } catch (err) {
        alert("Listing creation network error.");
    }
}

function showInterstitialAd(ad) {
    const modal = document.getElementById('interstitial-ad-modal');
    if (!modal) {
        alert("Book listed successfully!");
        switchTab('home');
        return;
    }

    document.getElementById('ad-sponsor-name').textContent = ad.sponsor_name;
    document.getElementById('ad-headline').textContent = ad.headline;
    document.getElementById('ad-image').src = ad.image_url;

    modal.classList.remove('hidden');

    let countdown = 3;
    const closeBtn = document.getElementById('ad-close-btn');
    closeBtn.disabled = true;
    closeBtn.textContent = `Skip Ad in ${countdown}s`;

    const timer = setInterval(() => {
        countdown--;
        if (countdown <= 0) {
            clearInterval(timer);
            closeBtn.disabled = false;
            closeBtn.textContent = "Continue to My Listing";
        } else {
            closeBtn.textContent = `Skip Ad in ${countdown}s`;
        }
    }, 1000);
}

function closeInterstitialAd() {
    const modal = document.getElementById('interstitial-ad-modal');
    if (modal) modal.classList.add('hidden');
    switchTab('home');
}

// Search and Filter logic
function setupEventListeners() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(applyFilters, 300));
    }

    const catSelect = document.getElementById('filter-category');
    if (catSelect) catSelect.addEventListener('change', applyFilters);

    const citySelect = document.getElementById('filter-city');
    if (citySelect) citySelect.addEventListener('change', applyFilters);

    const condSelect = document.getElementById('filter-condition');
    if (condSelect) condSelect.addEventListener('change', applyFilters);

    const boardSelect = document.getElementById('filter-board');
    if (boardSelect) boardSelect.addEventListener('change', applyFilters);

    const classSelect = document.getElementById('filter-class');
    if (classSelect) classSelect.addEventListener('change', applyFilters);

    const sortSelect = document.getElementById('filter-sort');
    if (sortSelect) sortSelect.addEventListener('change', applyFilters);

    const sellForm = document.getElementById('sell-book-form');
    if (sellForm) sellForm.addEventListener('submit', handleCreateListingSubmit);

    // Wire top Hero and Quick Action buttons (Scan, Sell, Deals)
    const heroScanBtn = document.getElementById('hero-scan-btn');
    if (heroScanBtn) {
        heroScanBtn.addEventListener('click', (e) => {
            e.preventDefault();
            openBarcodeScanner();
        });
    }

    const navScanBtn = document.getElementById('nav-scan-btn');
    if (navScanBtn) {
        navScanBtn.addEventListener('click', (e) => {
            e.preventDefault();
            openBarcodeScanner();
        });
    }

    const manualLookupBtn = document.getElementById('manual-lookup-btn');
    if (manualLookupBtn) {
        manualLookupBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const input = document.getElementById('manual-isbn-input');
            if (input) scanIsbnQuery(input.value);
        });
    }

    const manualIsbnInput = document.getElementById('manual-isbn-input');
    if (manualIsbnInput) {
        manualIsbnInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                scanIsbnQuery(manualIsbnInput.value);
            }
        });
    }

    const scanFileInput = document.getElementById('scan-file-input');
    if (scanFileInput) {
        scanFileInput.addEventListener('change', handleScanImageUpload);
    }

    const sellImageFile = document.getElementById('sell-image-file');
    if (sellImageFile) {
        sellImageFile.addEventListener('change', (e) => {
            const file = e.target.files && e.target.files[0];
            if (file) handleSelectedBookPhoto(file);
        });
    }

    const sellCameraFile = document.getElementById('sell-camera-file');
    if (sellCameraFile) {
        sellCameraFile.addEventListener('change', (e) => {
            const file = e.target.files && e.target.files[0];
            if (file) handleSelectedBookPhoto(file);
        });
    }

    const heroSellBtn = document.getElementById('hero-sell-btn');
    if (heroSellBtn) {
        heroSellBtn.addEventListener('click', (e) => {
            e.preventDefault();
            openSellSection();
        });
    }

    const quickScanCard = document.getElementById('quick-scan-card');
    if (quickScanCard) {
        quickScanCard.addEventListener('click', (e) => {
            e.preventDefault();
            openBarcodeScanner();
        });
    }

    const quickSellCard = document.getElementById('quick-sell-card');
    if (quickSellCard) {
        quickSellCard.addEventListener('click', (e) => {
            e.preventDefault();
            openSellSection();
        });
    }

    const quickDealsCard = document.getElementById('quick-deals-card');
    if (quickDealsCard) {
        quickDealsCard.addEventListener('click', (e) => {
            e.preventDefault();
            openDealsSection();
        });
    }
}

async function applyFilters() {
    const q = document.getElementById('search-input')?.value || '';
    const cat = document.getElementById('filter-category')?.value || 'All';
    const city = document.getElementById('filter-city')?.value || 'All';
    const cond = document.getElementById('filter-condition')?.value || 'All';
    const board = document.getElementById('filter-board')?.value || 'All';
    const gradeClass = document.getElementById('filter-class')?.value || 'All';
    const sort = document.getElementById('filter-sort')?.value || 'cheapest';

    const hasFilter = Boolean(q.trim() || cat !== 'All' || (city !== 'All' && city !== 'all') || cond !== 'All' || board !== 'All' || gradeClass !== 'All');
    const feedTitle = document.getElementById('listings-feed-title');

    const url = `/api/listings/?search=${encodeURIComponent(q)}&category=${encodeURIComponent(cat)}&city=${encodeURIComponent(city)}&condition=${encodeURIComponent(cond)}&board=${encodeURIComponent(board)}&grade_class=${encodeURIComponent(gradeClass)}&sort=${encodeURIComponent(sort)}`;
    try {
        const res = await fetch(url);
        const data = await res.json();
        STATE.listings = data;
        if (feedTitle) {
            feedTitle.innerHTML = hasFilter 
                ? `<i class="fa-solid fa-filter text-blue-600"></i> Filtered Results (${data.length} found)`
                : `<i class="fa-solid fa-layer-group text-blue-600"></i> All Available Book Offers`;
        }
        renderListings(data);
    } catch (e) {
        console.error(e);
    }
}

function resetFilters() {
    if (document.getElementById('search-input')) document.getElementById('search-input').value = '';
    if (document.getElementById('filter-category')) document.getElementById('filter-category').value = 'All';
    if (document.getElementById('filter-city')) document.getElementById('filter-city').value = 'All';
    if (document.getElementById('filter-condition')) document.getElementById('filter-condition').value = 'All';
    if (document.getElementById('filter-board')) document.getElementById('filter-board').value = 'All';
    if (document.getElementById('filter-class')) document.getElementById('filter-class').value = 'All';
    applyFilters();
}

function debounce(func, delay) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    };
}

// ==========================================
// REPORTS & COMPLAINTS (Safety & Trust)
// ==========================================
function openReportModal(listingId) {
    if (!STATE.currentUser) {
        openAuthModal('login');
        return;
    }
    const listing = STATE.listings.find(l => l.id === listingId);
    if (!listing) return;
    document.getElementById('report-listing-id').value = listing.id;
    document.getElementById('report-target-title').textContent = `Reporting: "${listing.book.title}" (Seller: ${listing.seller_name})`;
    document.getElementById('report-description-text').value = '';
    document.getElementById('report-issue-modal').classList.remove('hidden');
}

function closeReportModal() {
    const modal = document.getElementById('report-issue-modal');
    if (modal) modal.classList.add('hidden');
}

async function submitReportForm(e) {
    e.preventDefault();
    const listingId = document.getElementById('report-listing-id').value;
    const reportType = document.getElementById('report-type-select').value;
    const desc = document.getElementById('report-description-text').value.trim();
    const btn = document.getElementById('report-submit-btn');

    if (!desc) {
        alert("Please enter a description for the report.");
        return;
    }

    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin mr-1"></i> Submitting...`;
    }

    try {
        const res = await fetch('/api/reports/submit/', {
            method: 'POST',
            headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
            body: JSON.stringify({
                listing_id: listingId,
                report_type: reportType,
                description: desc
            })
        });
        const data = await res.json();
        if (btn) {
            btn.disabled = false;
            btn.textContent = 'Submit Report';
        }
        if (res.ok) {
            alert(data.message || "Report submitted successfully.");
            closeReportModal();
        } else {
            alert(data.error || "Failed to submit report.");
        }
    } catch (err) {
        if (btn) {
            btn.disabled = false;
            btn.textContent = 'Submit Report';
        }
        alert("Network error submitting report.");
    }
}

// =====================================================================
// FEATURE 1: AI BOOK RECOMMENDATION SYSTEM (GET /api/recommendations/)
// =====================================================================
async function loadAiRecommendations() {
    const container = document.getElementById('ai-recommendations-container');
    const section = document.getElementById('ai-recommendations-section');
    const subtitleEl = document.getElementById('ai-rec-subtitle');
    if (!container) return;

    try {
        const userId = STATE.currentUser ? STATE.currentUser.id : '';
        const profile = STATE.readerProfile || {
            name: STATE.currentUser ? STATE.currentUser.full_name : 'Ayesha',
            age_group: 'teens',
            city: STATE.currentUser ? STATE.currentUser.city : 'Lahore',
            interests: ['free_only', 'ptb_textbooks']
        };

        const params = new URLSearchParams();
        if (userId) params.set('user_id', userId);
        if (profile.age_group) params.set('age_group', profile.age_group);
        if (profile.city) params.set('city', profile.city);
        if (profile.interests && profile.interests.length) params.set('interests', profile.interests.join(','));

        const res = await fetch(`/api/recommendations/?${params.toString()}`);
        if (!res.ok) throw new Error("Failed to load recommendations");
        const data = await res.json();

        if (!data.success || !data.recommendations || data.recommendations.length === 0) {
            if (section) section.classList.add('hidden');
            return;
        }

        STATE.aiRecommendations = data.recommendations;

        if (section) section.classList.remove('hidden');

        if (subtitleEl) {
            const pName = profile.name || (STATE.currentUser ? STATE.currentUser.full_name : 'You');
            const ageLabel = AGE_GROUP_LABELS[profile.age_group] || data.age_group_label || 'Student (13–19)';
            subtitleEl.textContent = `Personalized for ${pName} (${ageLabel} • ${profile.city}) — Free donations prioritized on top`;
        }

        container.innerHTML = data.recommendations.slice(0, 4).map(item => createBookCardHtml(item)).join('');
    } catch (e) {
        console.warn("AI Recommendations load error:", e);
        if (section) section.classList.add('hidden');
    }
}

// =====================================================================
// FEATURE 2: AI SMART PRICE ADVISOR
// =====================================================================
let CURRENT_AI_SUGGESTED_PRICE = 680;

function setupAiPriceAdvisor() {
    const titleInput = document.getElementById('sell-title-input');
    const conditionSelect = document.getElementById('sell-condition-select');
    const categorySelect = document.getElementById('sell-category-select');
    const originalPriceInput = document.getElementById('sell-original-price-input');
    const freeToggle = document.getElementById('sell-is-free-toggle');

    const updateHandler = () => updateAiPriceAdvisor();

    if (titleInput) titleInput.addEventListener('input', updateHandler);
    if (conditionSelect) conditionSelect.addEventListener('change', updateHandler);
    if (categorySelect) categorySelect.addEventListener('change', updateHandler);
    if (originalPriceInput) originalPriceInput.addEventListener('input', updateHandler);
    if (freeToggle) freeToggle.addEventListener('change', updateHandler);

    // Initial calculation
    updateAiPriceAdvisor();
}

function updateAiPriceAdvisor() {
    const isFree = document.getElementById('sell-is-free-toggle')?.checked || false;
    const titleInput = document.getElementById('sell-title-input');
    const conditionSelect = document.getElementById('sell-condition-select');
    const categorySelect = document.getElementById('sell-category-select');
    const originalPriceInput = document.getElementById('sell-original-price-input');
    const priceNumEl = document.getElementById('ai-price-num');
    const insightEl = document.getElementById('ai-price-insight');

    if (!conditionSelect || !priceNumEl || !insightEl) return;

    if (isFree) {
        CURRENT_AI_SUGGESTED_PRICE = 0;
        priceNumEl.textContent = 'Rs. 0';
        insightEl.innerHTML = `AI Advisor: <span class="font-bold text-emerald-300">Free Community Giveaway (Rs. 0)</span> — Promoted with #1 priority on homepage!`;
        return;
    }

    const condition = conditionSelect.value || 'Good';
    const category = categorySelect ? categorySelect.value : '';
    const userOriginalPrice = originalPriceInput ? parseFloat(originalPriceInput.value) : 0;
    const title = titleInput ? titleInput.value.toLowerCase() : '';

    // Category retail benchmarks in PKR
    const benchmarks = {
        'Medical & MBBS / BDS': 3200,
        'Software Engineering': 2200,
        'Computer Science & IT': 2000,
        'Electrical & Mechanical Eng.': 1800,
        'University / Higher Ed': 1800,
        'Law & Judiciary': 1600,
        'Business, Commerce & BBA': 1400,
        'CSS & Competitive Exams': 1200,
        'Punjab Textbooks (Primary to FSc)': 350,
        'Story Books': 400,
        'Fiction': 650,
        'Novels': 600,
        'History': 750,
        'FSc / Matric / O & A Level': 550,
        'Urdu Literature & Novels': 650,
        'Islamic Studies': 700,
        'General Fiction & Non-Fiction': 800
    };

    let baseRetail = 1500;
    if (userOriginalPrice && userOriginalPrice > 0) {
        baseRetail = userOriginalPrice;
    } else if (benchmarks[category]) {
        baseRetail = benchmarks[category];
    } else if (title.includes('physics') || title.includes('chemistry') || title.includes('biology')) {
        baseRetail = 550;
    } else if (title.includes('calculus') || title.includes('math')) {
        baseRetail = 850;
    } else if (title.includes('algorithm') || title.includes('operating system') || title.includes('software')) {
        baseRetail = 1800;
    }

    // Condition depreciation factor
    const factors = {
        'Brand New': 0.80,
        'Like New': 0.65,
        'Good': 0.50,
        'Fair': 0.35
    };

    const factor = factors[condition] || 0.50;
    const calculated = Math.max(50, Math.round((baseRetail * factor) / 10) * 10);
    CURRENT_AI_SUGGESTED_PRICE = calculated;

    priceNumEl.textContent = `Rs. ${calculated}`;
    insightEl.innerHTML = `AI Suggested Price: <span class="font-bold text-amber-300">Rs. ${calculated}</span> (Optimal for fast sale in '${condition}' condition)`;
}

function applyAiSuggestedPrice() {
    const priceInput = document.getElementById('sell-price-input');
    const btn = document.getElementById('apply-ai-price-btn');
    if (!priceInput) return;

    priceInput.value = CURRENT_AI_SUGGESTED_PRICE;

    // Visual pulse feedback on input field
    priceInput.classList.add('ring-4', 'ring-emerald-400', 'bg-emerald-50');
    setTimeout(() => {
        priceInput.classList.remove('ring-4', 'ring-emerald-400', 'bg-emerald-50');
    }, 1200);

    // Button state update
    if (btn) {
        const originalHtml = btn.innerHTML;
        btn.innerHTML = `<i class="fa-solid fa-check text-xs"></i> <span>Applied Rs. ${CURRENT_AI_SUGGESTED_PRICE}!</span>`;
        btn.classList.add('from-emerald-600', 'to-teal-700');
        setTimeout(() => {
            btn.innerHTML = originalHtml;
            btn.classList.remove('from-emerald-600', 'to-teal-700');
        }, 1500);
    }
}

// =====================================================================
// FEATURE 3: STARTUP LOGIN & AI READER ONBOARDING MODAL
// =====================================================================
const AGE_GROUP_LABELS = {
    kids: 'Kids (5–12)',
    teens: 'Student (13–19)',
    young_adult: 'University (20–30)',
    general: 'General (31+)',
    all: 'All Readers'
};

function getSavedReaderProfile() {
    try {
        const raw = localStorage.getItem('bb_reader_profile');
        if (raw) return JSON.parse(raw);
    } catch (e) {
        console.warn("Could not parse saved reader profile:", e);
    }
    return null;
}

function initReaderProfile() {
    const saved = getSavedReaderProfile();
    const isSessionActive = sessionStorage.getItem('bookzy_session_active') || localStorage.getItem('bookloop_token');

    if (saved) {
        STATE.readerProfile = saved;
        updateReaderHeaderUI();
    } else {
        STATE.readerProfile = {
            name: 'Ayesha',
            age_group: 'teens',
            city: 'Lahore',
            interests: ['free_only', 'ptb_textbooks']
        };
        updateReaderHeaderUI();
    }

    // Enforce mandatory startup login / reader onboarding for unauthenticated visitors in current session
    if (!isSessionActive) {
        setTimeout(() => {
            openReaderOnboardingModal({ isStartup: true });
        }, 150);
    }
}

function updateReaderHeaderUI() {
    const profile = STATE.readerProfile || { name: 'Ayesha', age_group: 'teens', city: 'Lahore' };
    const ageLabel = AGE_GROUP_LABELS[profile.age_group] || 'Student (13–19)';

    const topName = document.getElementById('top-user-display-name');
    const topAge = document.getElementById('top-user-age-badge');
    const topCity = document.getElementById('top-user-city-display');
    const topWallet = document.getElementById('top-user-wallet-display');
    const mobileAge = document.getElementById('mobile-user-age-badge');

    if (topName) topName.textContent = profile.name || (STATE.currentUser ? STATE.currentUser.full_name : 'Reader');
    if (topAge) topAge.textContent = ageLabel;
    if (mobileAge) mobileAge.textContent = ageLabel;
    if (topCity) topCity.textContent = profile.city || (STATE.currentUser ? STATE.currentUser.city : 'Lahore');
    if (topWallet && STATE.currentUser) {
        topWallet.textContent = `Rs. ${parseFloat(STATE.currentUser.wallet_balance || 0).toFixed(0)}`;
    }
}

function switchOnboardTab(tabName) {
    const tabReader = document.getElementById('onboard-tab-reader');
    const tabExisting = document.getElementById('onboard-tab-existing');
    const tabAdmin = document.getElementById('onboard-tab-admin');
    const viewReader = document.getElementById('onboard-view-reader');
    const viewExisting = document.getElementById('onboard-view-existing');
    const viewAdmin = document.getElementById('onboard-view-admin');

    [tabReader, tabExisting, tabAdmin].forEach(t => {
        if (!t) return;
        t.className = 'flex-1 py-1.5 px-2 rounded-lg text-slate-600 hover:text-slate-900 text-center transition-all';
    });
    [viewReader, viewExisting, viewAdmin].forEach(v => {
        if (!v) return;
        v.classList.add('hidden');
    });

    if (tabName === 'existing') {
        if (tabExisting) tabExisting.className = 'flex-1 py-1.5 px-2 rounded-lg bg-white text-blue-700 shadow-xs text-center transition-all font-bold';
        if (viewExisting) viewExisting.classList.remove('hidden');
    } else if (tabName === 'admin') {
        if (tabAdmin) tabAdmin.className = 'flex-1 py-1.5 px-2 rounded-lg bg-white text-slate-900 shadow-xs text-center transition-all font-bold';
        if (viewAdmin) viewAdmin.classList.remove('hidden');
    } else {
        if (tabReader) tabReader.className = 'flex-1 py-1.5 px-2 rounded-lg bg-white text-blue-700 shadow-xs text-center transition-all font-bold';
        if (viewReader) viewReader.classList.remove('hidden');
    }
}

function openReaderOnboardingModal(options = {}) {
    const modal = document.getElementById('reader-onboarding-modal');
    if (!modal) return;

    const isStartup = Boolean(options.isStartup);
    modal.dataset.isStartup = isStartup ? 'true' : 'false';

    const closeBtn = document.getElementById('onboard-close-btn');
    if (closeBtn) {
        if (isStartup) {
            closeBtn.classList.add('hidden');
        } else {
            closeBtn.classList.remove('hidden');
        }
    }

    switchOnboardTab('reader');

    const profile = STATE.readerProfile || {
        name: STATE.currentUser ? STATE.currentUser.full_name : 'Ayesha',
        age_group: 'teens',
        city: STATE.currentUser ? STATE.currentUser.city : 'Lahore',
        interests: ['free_only', 'ptb_textbooks']
    };

    const nameInput = document.getElementById('onboard-name-input');
    const phoneInput = document.getElementById('onboard-phone-input');
    const citySelect = document.getElementById('onboard-city-select');
    const ageHidden = document.getElementById('onboard-age-group-value');

    if (nameInput) nameInput.value = profile.name || '';
    if (phoneInput && profile.phone_or_email) phoneInput.value = profile.phone_or_email;
    if (citySelect && profile.city) citySelect.value = profile.city;
    if (ageHidden) ageHidden.value = profile.age_group || 'teens';

    // Select the age card
    const targetAge = profile.age_group || 'teens';
    document.querySelectorAll('#onboard-age-group-cards .onboard-age-card').forEach(card => {
        if (card.getAttribute('data-age') === targetAge) {
            selectOnboardAgeGroup(targetAge, card);
        }
    });

    // Toggle interest chips
    const interests = profile.interests || ['free_only', 'ptb_textbooks'];
    document.querySelectorAll('#onboard-interest-chips .interest-chip').forEach(chip => {
        const key = chip.getAttribute('data-interest');
        if (interests.includes(key)) {
            chip.classList.add('active', 'border-2', 'border-blue-600', 'bg-blue-50', 'text-blue-800');
            chip.classList.remove('border-slate-300', 'bg-white', 'text-slate-700');
        } else {
            chip.classList.remove('active', 'border-2', 'border-blue-600', 'bg-blue-50', 'text-blue-800', 'border-emerald-500', 'bg-emerald-50', 'text-emerald-800');
            chip.classList.add('border-slate-300', 'bg-white', 'text-slate-700');
        }
    });

    modal.classList.remove('hidden');
}

function closeReaderOnboardingModal(force = false) {
    const isSessionActive = sessionStorage.getItem('bookzy_session_active') || localStorage.getItem('bookloop_token');
    if (!force && !isSessionActive) {
        // Mandatory startup login: visitors cannot dismiss before signing in or continuing as reader
        return;
    }
    const modal = document.getElementById('reader-onboarding-modal');
    if (modal) modal.classList.add('hidden');
}

function selectOnboardAgeGroup(ageKey, cardEl) {
    document.querySelectorAll('#onboard-age-group-cards .onboard-age-card').forEach(c => {
        c.classList.remove('active', 'border-blue-600', 'bg-blue-50/50');
        c.classList.add('border-slate-200');
    });
    if (cardEl) {
        cardEl.classList.add('active', 'border-blue-600', 'bg-blue-50/50');
        cardEl.classList.remove('border-slate-200');
    }
    const hiddenInput = document.getElementById('onboard-age-group-value');
    if (hiddenInput) hiddenInput.value = ageKey;
    const label = document.getElementById('onboard-age-selected-label');
    if (label) {
        label.textContent = AGE_GROUP_LABELS[ageKey] || ageKey;
    }
}

function toggleOnboardInterest(interestKey, chipEl) {
    if (!chipEl) return;
    chipEl.classList.toggle('active');
    if (chipEl.classList.contains('active')) {
        chipEl.classList.add('border-2', 'border-blue-600', 'bg-blue-50', 'text-blue-800');
        chipEl.classList.remove('border-slate-300', 'bg-white', 'text-slate-700');
    } else {
        chipEl.classList.remove('active', 'border-2', 'border-blue-600', 'bg-blue-50', 'text-blue-800', 'border-emerald-500', 'bg-emerald-50', 'text-emerald-800');
        chipEl.classList.add('border-slate-300', 'bg-white', 'text-slate-700');
    }
}

async function handleReaderOnboardingSubmit(e) {
    e.preventDefault();
    const name = document.getElementById('onboard-name-input')?.value.trim() || 'Reader';
    const phoneOrEmail = document.getElementById('onboard-phone-input')?.value.trim() || '';
    const ageGroup = document.getElementById('onboard-age-group-value')?.value || 'teens';
    const city = document.getElementById('onboard-city-select')?.value || 'Lahore';

    const selectedInterests = [];
    document.querySelectorAll('#onboard-interest-chips .interest-chip.active').forEach(chip => {
        const k = chip.getAttribute('data-interest');
        if (k) selectedInterests.push(k);
    });

    const profile = {
        name,
        phone_or_email: phoneOrEmail,
        age_group: ageGroup,
        city,
        interests: selectedInterests
    };

    STATE.readerProfile = profile;
    sessionStorage.setItem('bookzy_session_active', 'true');
    localStorage.setItem('bb_reader_profile', JSON.stringify(profile));
    localStorage.setItem('bb_reader_onboarded_dismissed', 'true');

    // Auto-link matching user profile if phone matches
    if (phoneOrEmail && STATE.allUsers && STATE.allUsers.length) {
        const cleanPhone = phoneOrEmail.replace(/\D/g, '');
        const matched = STATE.allUsers.find(u => 
            (cleanPhone && u.phone_number && u.phone_number.includes(cleanPhone)) ||
            (u.username && u.username.toLowerCase() === phoneOrEmail.toLowerCase())
        );
        if (matched) {
            STATE.currentUser = matched;
            localStorage.setItem('bb_user_id', matched.id);
            await syncUserAuthToken(matched.id);
            updateUserUI();
        }
    }

    updateReaderHeaderUI();

    // Sync preferences to backend if user profile exists
    try {
        await fetch('/api/user/preferences/', {
            method: 'POST',
            headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
            body: JSON.stringify({
                user_id: STATE.currentUser ? STATE.currentUser.id : '',
                full_name: name,
                age_group: ageGroup,
                city: city,
                interests: selectedInterests
            })
        });
    } catch (err) {
        console.warn("Preferences backend sync notice:", err);
    }

    closeReaderOnboardingModal(true);

    // Immediately show personalized feed
    await loadAiRecommendations();
}

async function handleOnboardExistingLogin(e) {
    e.preventDefault();
    const ident = document.getElementById('onboard-existing-ident')?.value.trim();
    const pass = document.getElementById('onboard-existing-pass')?.value;
    const errBanner = document.getElementById('onboard-existing-err');
    if (errBanner) errBanner.classList.add('hidden');

    try {
        const res = await fetch('/api/auth/login/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone_or_username: ident, password: pass })
        });
        const data = await res.json();
        if (res.ok) {
            sessionStorage.setItem('bookzy_session_active', 'true');
            localStorage.setItem('bookloop_token', data.token);
            localStorage.setItem('bb_user_id', data.profile.id);
            if (data.is_staff) {
                localStorage.setItem('bookbazaar_admin_token', data.token);
            }
            closeReaderOnboardingModal(true);
            location.reload();
        } else {
            if (errBanner) {
                errBanner.textContent = data.error || "Login failed. Check your credentials.";
                errBanner.classList.remove('hidden');
            } else {
                alert(data.error || "Login failed");
            }
        }
    } catch (err) {
        if (errBanner) {
            errBanner.textContent = "Network error during login. Please try again.";
            errBanner.classList.remove('hidden');
        }
    }
}

async function handleOnboardAdminLogin(e) {
    e.preventDefault();
    const ident = document.getElementById('onboard-admin-ident')?.value.trim();
    const pass = document.getElementById('onboard-admin-pass')?.value;
    const errBanner = document.getElementById('onboard-admin-err');
    if (errBanner) errBanner.classList.add('hidden');

    try {
        const res = await fetch('/api/auth/login/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone_or_username: ident, password: pass })
        });
        const data = await res.json();
        if (res.ok && data.is_staff) {
            sessionStorage.setItem('bookzy_session_active', 'true');
            localStorage.setItem('bookloop_token', data.token);
            localStorage.setItem('bookbazaar_admin_token', data.token);
            localStorage.setItem('bb_user_id', data.profile.id);
            window.location.href = '/admin-panel/';
        } else if (res.ok && !data.is_staff) {
            if (errBanner) {
                errBanner.textContent = "Access denied. This account does not have staff or administrator privileges.";
                errBanner.classList.remove('hidden');
            }
        } else {
            if (errBanner) {
                errBanner.textContent = data.error || "Invalid administrator credentials.";
                errBanner.classList.remove('hidden');
            }
        }
    } catch (err) {
        if (errBanner) {
            errBanner.textContent = "Connection error. Please try again.";
            errBanner.classList.remove('hidden');
        }
    }
}

function skipReaderOnboarding() {
    closeReaderOnboardingModal();
}
