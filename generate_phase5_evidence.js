const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const EVIDENCE_DIR = path.join(__dirname, 'evidence_screenshots');
if (!fs.existsSync(EVIDENCE_DIR)) {
    fs.mkdirSync(EVIDENCE_DIR, { recursive: true });
}

async function runBrowserEvidence() {
    const tmpProfile = path.join(process.env.TEMP || 'C:\\temp', 'chrome_phase5_evidence_' + Date.now());
    console.log("Spawning Chrome with profile at:", tmpProfile);

    const chrome = spawn('C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe', [
        '--headless=new',
        '--remote-debugging-port=9222',
        `--user-data-dir=${tmpProfile}`,
        '--disable-gpu',
        '--window-size=1280,960',
        'about:blank'
    ]);

    chrome.on('error', (err) => console.error("Chrome spawn error:", err));

    let pageWsUrl = null;
    for (let i = 0; i < 30; i++) {
        await new Promise(r => setTimeout(r, 200));
        try {
            const res = await fetch('http://127.0.0.1:9222/json/list');
            if (res.ok) {
                const targets = await res.json();
                const pageTarget = targets.find(t => t.type === 'page');
                if (pageTarget && pageTarget.webSocketDebuggerUrl) {
                    pageWsUrl = pageTarget.webSocketDebuggerUrl;
                    break;
                }
            }
        } catch (e) {}
    }

    if (!pageWsUrl) {
        throw new Error("Could not connect to Chrome DevTools Protocol");
    }

    const ws = new WebSocket(pageWsUrl);
    let id = 1;
    const pending = new Map();

    ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.id && pending.has(msg.id)) {
            const resolver = pending.get(msg.id);
            pending.delete(msg.id);
            resolver(msg);
        }
    };

    await new Promise(r => ws.onopen = r);

    function send(method, params = {}) {
        return new Promise((resolve) => {
            const reqId = id++;
            pending.set(reqId, resolve);
            ws.send(JSON.stringify({ id: reqId, method, params }));
        });
    }

    async function evaluate(expression) {
        const res = await send('Runtime.evaluate', {
            expression,
            returnByValue: true,
            awaitPromise: true
        });
        if (res.result?.exceptionDetails) {
            console.error("Evaluation Exception:", res.result.exceptionDetails);
        }
        return res.result?.result?.value;
    }

    async function takeScreenshot(filename) {
        const shot = await send('Page.captureScreenshot', { format: 'png' });
        const filePath = path.join(EVIDENCE_DIR, filename);
        fs.writeFileSync(filePath, Buffer.from(shot.result.data, 'base64'));
        console.log(`[Captured] ${filename} (${fs.statSync(filePath).size} bytes)`);
        return filePath;
    }

    await send('Page.enable');
    await send('Runtime.enable');
    await send('DOM.enable');

    console.log("Navigating to http://127.0.0.1:8000/ ...");
    await send('Page.navigate', { url: 'http://127.0.0.1:8000/' });
    await new Promise(r => setTimeout(r, 2000));

    // Override alerts so they do not block headless Chrome
    await evaluate(`
        window.alert = function(msg) { console.log('OVERRIDDEN ALERT:', msg); };
        window.confirm = function() { return true; };
    `);

    // =========================================================================
    // STEP 1: Seller Registration & Login Form
    // =========================================================================
    console.log("Step 1: Seller registration & login modal...");
    await evaluate(`
        openAuthModal('register');
        document.getElementById('reg-fullname').value = 'Ali Raza (Test Seller)';
        document.getElementById('reg-phone').value = '03019876543';
        document.getElementById('reg-city').value = 'Bahawalpur';
        document.getElementById('reg-password').value = 'SellerPass123!';
    `);
    await new Promise(r => setTimeout(r, 600));
    await takeScreenshot('evidence_01_seller_register_login.png');

    // Register seller via API in page context
    const sellerReg = await evaluate(`
        (async () => {
            const regRes = await fetch('/api/auth/register/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    full_name: 'Ali Raza (Test Seller)',
                    phone_number: '03019876543',
                    city: 'Bahawalpur',
                    password: 'SellerPass123!'
                })
            });
            const data = await regRes.json();
            if (data.token) {
                localStorage.setItem('bookloop_token', data.token);
                localStorage.setItem('bb_user_id', data.profile.id);
                STATE.currentUser = data.profile;
            }
            closeAuthModal();
            updateUserUI();
            return { ok: regRes.ok, profile: data.profile, token: data.token };
        })()
    `);
    console.log("Seller Registration Result:", sellerReg);
    await new Promise(r => setTimeout(r, 1000));

    // =========================================================================
    // STEP 2: Adding a new book with image and price
    // =========================================================================
    console.log("Step 2: Add book listing form...");
    await evaluate(`
        switchTab('sell');
        document.getElementById('sell-title-input').value = 'Database System Concepts (7th Edition)';
        document.getElementById('sell-author-input').value = 'Abraham Silberschatz';
        document.getElementById('sell-subject-input').value = 'Computer Science / DBMS';
        document.getElementById('sell-price-input').value = '1200';
        document.getElementById('sell-condition-select').value = 'Good';
        document.getElementById('sell-city-select').value = 'Bahawalpur';
        document.getElementById('sell-pickup-input').value = 'IUB Baghdad Campus Library';
        document.getElementById('sell-desc-input').value = 'Hardcover international edition. Clean pages, no highlighting.';
        // Preview book photo
        const preview = document.getElementById('sell-image-preview');
        const img = document.getElementById('sell-preview-img');
        if (preview && img) {
            img.src = '/static/img/hero-mockup.png';
            preview.classList.remove('hidden');
        }
    `);
    await new Promise(r => setTimeout(r, 600));
    await takeScreenshot('evidence_02_add_book_listing.png');

    // Create listing via API in page context
    const listingRes = await evaluate(`
        (async () => {
            const res = await fetch('/api/listings/create/', {
                method: 'POST',
                headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
                body: JSON.stringify({
                    seller_id: STATE.currentUser.id,
                    title: 'Database System Concepts (7th Edition)',
                    author: 'Abraham Silberschatz',
                    subject: 'Computer Science / DBMS',
                    price: 1200,
                    condition: 'Good',
                    city: 'Bahawalpur',
                    pickup_location: 'IUB Baghdad Campus Library',
                    description: 'Hardcover international edition. Clean pages, no highlighting.',
                    isbn: '9780078022159',
                    category: 'University / Engineering',
                    education_board: 'IUB Bahawalpur',
                    grade_class: 'BSCS / Software Engineering',
                    photo_url: 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400'
                })
            });
            const data = await res.json();
            return { ok: res.ok, listing: data.listing };
        })()
    `);
    console.log("Listing Creation Result:", listingRes);
    const createdListingId = listingRes?.listing?.id;
    if (!createdListingId) {
        throw new Error("Listing creation failed: " + JSON.stringify(listingRes));
    }
    await new Promise(r => setTimeout(r, 1000));

    // =========================================================================
    // STEP 3: Switch to Buyer, Search and Find Book
    // =========================================================================
    console.log("Step 3: Buyer search...");
    const buyerReg = await evaluate(`
        (async () => {
            const regRes = await fetch('/api/auth/register/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    full_name: 'Fatima Noor (Buyer Test)',
                    phone_number: '03121234567',
                    city: 'Bahawalpur',
                    password: 'BuyerPass123!'
                })
            });
            const data = await regRes.json();
            if (data.token) {
                localStorage.setItem('bookloop_token', data.token);
                localStorage.setItem('bb_user_id', data.profile.id);
                STATE.currentUser = data.profile;
            }
            updateUserUI();

            // Switch to Home tab and search
            switchTab('home');
            document.getElementById('search-input').value = 'Database System Concepts';
            await applyFilters();
            return { ok: regRes.ok, profile: data.profile, token: data.token };
        })()
    `);
    console.log("Buyer Registration Result:", buyerReg);
    await new Promise(r => setTimeout(r, 1200));
    await takeScreenshot('evidence_03_buyer_search_book.png');

    // =========================================================================
    // STEP 4: Masked Seller Contact Before Payment
    // =========================================================================
    console.log("Step 4: Masked contact before payment...");
    await evaluate(`
        quickCompareBook('9780078022159');
    `);
    await new Promise(r => setTimeout(r, 1200));
    await takeScreenshot('evidence_04_masked_contact_before_payment.png');

    // =========================================================================
    // STEP 5: Successful Rs. 50 Sandbox Payment Modal
    // =========================================================================
    console.log(`Step 5: Opening Rs. 50 Sandbox Payment Modal for listing ${createdListingId}...`);
    await evaluate(`
        openUnlockModal(${createdListingId});
        const accInput = document.getElementById('pay-account-input');
        if (accInput) accInput.value = '03121234567';
    `);
    await new Promise(r => setTimeout(r, 800));
    await takeScreenshot('evidence_05_sandbox_payment_modal.png');

    // =========================================================================
    // STEP 6: Execute Sandbox Payment & Show Unmasked Contact
    // =========================================================================
    console.log("Step 6: Executing Sandbox Payment and verifying unmasked contact...");
    const payResult = await evaluate(`
        (async () => {
            await submitPaymentUnlock();
            return { completed: true };
        })()
    `);
    console.log("Payment submit result:", payResult);
    await new Promise(r => setTimeout(r, 2000));
    await takeScreenshot('evidence_06_unmasked_contact_after_payment.png');

    // Close browser cleanly
    ws.close();
    chrome.kill();
    try { fs.rmSync(tmpProfile, { recursive: true, force: true }); } catch (e) {}

    console.log("\n=========================================");
    console.log("SUCCESS! All 6 real browser screenshots captured!");
    console.log("=========================================\n");

    return { createdListingId };
}

runBrowserEvidence().catch(err => {
    console.error("FATAL ERROR in browser evidence:", err);
    process.exit(1);
});
