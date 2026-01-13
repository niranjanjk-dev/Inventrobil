import requests
import time
import subprocess
import sys
import os

BASE_URL = "http://localhost:8000"

def start_server():
    print("Starting server...")
    # Run in a separate process
    # Set FLASK_ENV to development to ensure SQLite is used (Config default logic)
    env = os.environ.copy()
    env["FLASK_ENV"] = "development"
    env["DATABASE_URL"] = "" # Force SQLite default
    env["ADMIN_USERNAME"] = "owner"
    env["ADMIN_PASSWORD"] = "owner123"
    
    process = subprocess.Popen([sys.executable, "app.py"], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(5) # Wait for startup
    return process

def stop_server(process):
    print("Stopping server...")
    process.terminate()

def test_login(session):
    print("Testing Login...")
    url = f"{BASE_URL}/login"
    payload = {"username": "owner", "password": "owner123"}
    response = session.post(url, json=payload)
    if response.status_code == 200 and response.json().get('success'):
        print("✅ Login Successful")
        return True
    else:
        print(f"❌ Login Failed: {response.status_code} {response.text}")
        return False

def test_get_user_info(session):
    print("Testing User Info...")
    url = f"{BASE_URL}/user-info"
    response = session.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['user']['username'] == 'owner':
            print("✅ User Info Verified")
            return True
    print(f"❌ User Info Failed: {response.text}")
    return False

def test_inventory(session):
    print("Testing Inventory API...")
    # Add Product
    add_url = f"{BASE_URL}/api/product"
    new_product = {
        "name": "Test Product",
        "category": "Test",
        "stock": 100,
        "price": 99.99,
        "sku": "TEST001"
    }
    response = session.post(add_url, json=new_product)
    if response.status_code != 201:
        print(f"❌ Add Product Failed: {response.text}")
        return False
    
    # Get Products
    get_url = f"{BASE_URL}/api/products"
    response = session.get(get_url)
    products = response.json()
    if any(p['sku'] == 'TEST001' for p in products):
        print("✅ Inventory Add/List Verified")
        return True
    
    print("❌ Product not found in list")
    return False

def run_tests():
    server_process = start_server()
    session = requests.Session()
    
    try:
        if not test_login(session):
            return
        
        if not test_get_user_info(session):
            return
            
        if not test_inventory(session):
            return
            
        print("\n🎉 ALL TESTS PASSED!")
    except Exception as e:
        print(f"\n❌ Exception during tests: {e}")
    finally:
        stop_server(server_process)

if __name__ == "__main__":
    run_tests()
