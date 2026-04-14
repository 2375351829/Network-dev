#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8000/api"

def log(message, success=True):
    prefix = "✓" if success else "✗"
    print(f"[{prefix}] {message}")

def test_health_check():
    log("Testing health check...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            log("Health check passed!")
            return True
        else:
            log(f"Health check failed with status: {response.status_code}", success=False)
            return False
    except Exception as e:
        log(f"Health check error: {e}", success=False)
        return False

def test_login():
    log("\nTesting login endpoint...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login/json",
            json={"username": "admin", "password": "admin123"}
        )
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                log("Login successful!")
                return data["access_token"]
            else:
                log("Login response missing access_token", success=False)
                return None
        else:
            log(f"Login failed with status: {response.status_code}", success=False)
            log(f"Response: {response.text}", success=False)
            return None
    except Exception as e:
        log(f"Login error: {e}", success=False)
        return None

def test_register():
    log("\nTesting register endpoint...")
    try:
        import random
        import string
        random_username = ''.join(random.choices(string.ascii_lowercase, k=8))
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "username": random_username,
                "password": "test123456",
                "email": f"{random_username}@test.com",
                "nickname": "Test User"
            }
        )
        if response.status_code == 200:
            log(f"Register successful for user: {random_username}")
            return True
        else:
            log(f"Register failed with status: {response.status_code}", success=False)
            log(f"Response: {response.text}", success=False)
            return False
    except Exception as e:
        log(f"Register error: {e}", success=False)
        return False

def test_users_endpoints(token):
    log("\nTesting users endpoints...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test get users
    try:
        response = requests.get(f"{BASE_URL}/users", headers=headers)
        if response.status_code == 200:
            users = response.json()
            log(f"Get users successful, found {len(users)} users")
            if users:
                user_id = users[0]["id"]
                
                # Test get single user
                response = requests.get(f"{BASE_URL}/users/{user_id}", headers=headers)
                if response.status_code == 200:
                    log(f"Get single user successful (id: {user_id})")
                else:
                    log(f"Get single user failed with status: {response.status_code}", success=False)
                
                # Test update user
                test_user = users[0]
                response = requests.put(
                    f"{BASE_URL}/users/{user_id}",
                    headers=headers,
                    json={
                        "username": test_user["username"],
                        "email": test_user["email"],
                        "nickname": test_user["nickname"] or test_user["username"],
                        "is_admin": test_user.get("is_admin", False),
                        "is_active": test_user.get("is_active", True)
                    }
                )
                if response.status_code == 200:
                    log(f"Update user successful (id: {user_id})")
                else:
                    log(f"Update user failed with status: {response.status_code}", success=False)
                    log(f"Response: {response.text}", success=False)
            return True
        else:
            log(f"Get users failed with status: {response.status_code}", success=False)
            log(f"Response: {response.text}", success=False)
            return False
    except Exception as e:
        log(f"Users endpoints error: {e}", success=False)
        return False

def test_files_endpoint(token):
    log("\nTesting files endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/files", headers=headers)
        if response.status_code == 200:
            log("Files endpoint accessible")
            return True
        else:
            log(f"Files endpoint returned status: {response.status_code}", success=False)
            return False
    except Exception as e:
        log(f"Files endpoint error: {e}", success=False)
        return False

def test_multimedia_endpoint(token):
    log("\nTesting multimedia endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/multimedia", headers=headers)
        if response.status_code in [200, 404, 405]:
            log(f"Multimedia endpoint responded with status: {response.status_code}")
            return True
        else:
            log(f"Multimedia endpoint returned unexpected status: {response.status_code}", success=False)
            return False
    except Exception as e:
        log(f"Multimedia endpoint error: {e}", success=False)
        return False

def main():
    print("="*60)
    print("LanFileHub API Testing")
    print("="*60)
    
    all_passed = True
    
    # Test 1: Health check
    if not test_health_check():
        all_passed = False
    
    # Test 2: Login
    token = test_login()
    if not token:
        all_passed = False
        print("\nCannot proceed with further tests without valid token")
        return
    
    # Test 3: Register
    if not test_register():
        all_passed = False
    
    # Test 4: Users endpoints
    if not test_users_endpoints(token):
        all_passed = False
    
    # Test 5: Files endpoint
    if not test_files_endpoint(token):
        all_passed = False
    
    # Test 6: Multimedia endpoint
    if not test_multimedia_endpoint(token):
        all_passed = False
    
    # Summary
    print("\n" + "="*60)
    if all_passed:
        print("✓ All API tests passed!")
    else:
        print("⚠️  Some tests failed, check above for details")
    print("="*60)

if __name__ == "__main__":
    main()
