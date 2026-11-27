import os
import sys
import json
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookbazaar_backend.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from bazaar.models import UserProfile

def run_auth_registration_tests():
    client = Client()
    print("==========================================================")
    print("   BOOKZY AI: AUTH REGISTRATION & LOGIN VERIFICATION      ")
    print("==========================================================")

    test_phone_raw = "0308-7020450"
    test_phone_clean = "03087020450"
    test_city = "Islamabad"
    test_password = "1234"
    test_fullname = "Usman Tariq"

    # Clean up prior test user if exists
    existing_user = User.objects.filter(username__startswith=f"user_{test_phone_clean}").first()
    if existing_user:
        existing_user.delete()
    UserProfile.objects.filter(phone_number=test_phone_clean).delete()

    # 1. Test short password < 4 chars rejection
    short_pw_resp = client.post('/api/auth/register/', data=json.dumps({
        'full_name': test_fullname,
        'phone_number': test_phone_raw,
        'city': test_city,
        'password': '12'
    }), content_type='application/json')
    assert short_pw_resp.status_code == 400, f"Expected 400 for short pw, got {short_pw_resp.status_code}"
    assert "at least 4 characters" in short_pw_resp.json().get('error', '')
    print("PASS: Password < 4 characters rejected with clear validation message")

    # 2. Test registration with '0308-7020450' and 4-char password '1234'
    reg_resp = client.post('/api/auth/register/', data=json.dumps({
        'full_name': test_fullname,
        'phone_number': test_phone_raw,
        'city': test_city,
        'password': test_password
    }), content_type='application/json')
    assert reg_resp.status_code in (200, 201), f"Expected 200/201, got {reg_resp.status_code}: {reg_resp.content}"
    reg_data = reg_resp.json()
    assert 'token' in reg_data, "Token must be returned"
    assert reg_data['token'], "Token must not be empty"
    assert reg_data['phone'] == test_phone_clean, f"Phone should be normalized to {test_phone_clean}, got {reg_data.get('phone')}"
    assert 'id' in reg_data
    assert reg_data['city'] == test_city
    assert 'wallet_balance' in reg_data
    assert 'free_unlocks_remaining' in reg_data
    assert 'profile' in reg_data
    assert reg_data['profile']['phone'] == test_phone_clean
    print(f"PASS: User registered successfully! Token: {reg_data['token'][:10]}..., Normalized Phone: {reg_data['phone']}")

    # Verify DB record
    profile = UserProfile.objects.filter(phone_number=test_phone_clean).first()
    assert profile is not None, "UserProfile should exist in DB with clean phone"
    assert profile.phone_number == test_phone_clean
    print(f"PASS: UserProfile verified in DB: id={profile.id}, full_name='{profile.full_name}'")

    # 3. Test duplicate registration attempt returns clear error
    dup_resp = client.post('/api/auth/register/', data=json.dumps({
        'full_name': 'Another Person',
        'phone_number': '+92-308-7020450',
        'city': 'Lahore',
        'password': 'password123'
    }), content_type='application/json')
    assert dup_resp.status_code == 400
    dup_err = dup_resp.json().get('error', '')
    assert "already registered" in dup_err.lower()
    print(f"PASS: Duplicate registration blocked with message: '{dup_err}'")

    # 4. Test login using formatted phone number (+92 308 7020450) and password '1234'
    login_resp = client.post('/api/auth/login/', data=json.dumps({
        'phone_or_username': '+92 308 7020450',
        'password': test_password
    }), content_type='application/json')
    assert login_resp.status_code == 200, f"Expected 200 login, got {login_resp.status_code}: {login_resp.content}"
    login_data = login_resp.json()
    assert 'token' in login_data
    assert login_data['profile']['phone'] == test_phone_clean
    print(f"PASS: Login with formatted '+92 308 7020450' succeeded! Token: {login_data['token'][:10]}...")

    # 5. Test login with unregistered phone shows helpful message
    unreg_login_resp = client.post('/api/auth/login/', data=json.dumps({
        'phone_or_username': '03099998877',
        'password': 'password123'
    }), content_type='application/json')
    assert unreg_login_resp.status_code == 404
    unreg_err = unreg_login_resp.json().get('error', '')
    assert "Account not found" in unreg_err
    print(f"PASS: Unregistered login returns 404 with helpful message: '{unreg_err}'")

    # Clean up test user
    if profile.user:
        profile.user.delete()
    profile.delete()
    print("PASS: Test user cleaned up.")

    print("\n==========================================================")
    print("   ALL AUTH REGISTRATION & LOGIN TESTS PASSED (100%)      ")
    print("==========================================================")

if __name__ == '__main__':
    run_auth_registration_tests()
