"""
Test upload endpoint directly
"""
import requests
import json

# First, try to register/login
def get_auth_token():
    """Get authentication token"""
    base_url = "http://localhost:8000"

    # Login with existing user credentials
    login_data = {
        "username": "testuser",
        "password": "testuser123"
    }

    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            data=login_data,  # Form data for OAuth2
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        print(f"[Login] Status: {response.status_code}")
        if response.status_code == 200:
            print(f"[OK] Logged in as testuser")
            return response.json()["access_token"]
        else:
            print(f"[ERROR] Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Login exception: {e}")
        return None

def test_upload(token):
    """Test file upload"""
    base_url = "http://localhost:8000"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    zip_path = "C:/aurigo/Pranav_Case_Data.zip"

    beneficiary_name = 'Pranav Khare'

    print(f"\n[Uploading] {zip_path}...")
    print(f"[Beneficiary] {beneficiary_name}")

    with open(zip_path, 'rb') as f:
        files = {
            'uploaded_folder': ('Pranav_Case_Data.zip', f, 'application/zip')
        }
        params = {
            'beneficiary_name': beneficiary_name
        }

        response = requests.post(
            f"{base_url}/api/cases/upload",
            headers=headers,
            files=files,
            params=params,  # Query parameters
            timeout=120  # Increase timeout for LLM calls
        )

        print(f"\n[Response Status] {response.status_code}")
        print(f"[Response Headers] {dict(response.headers)}")

        try:
            response_json = response.json()
            print(f"\n[Response JSON]")
            print(json.dumps(response_json, indent=2))
        except:
            print(f"\n[Response Text]")
            print(response.text)

        return response

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING UPLOAD ENDPOINT")
    print("=" * 60)

    # Get auth token
    print("\n[1/2] Getting authentication token...")
    token = get_auth_token()

    if not token:
        print("[ERROR] Could not get authentication token")
        exit(1)

    print(f"[OK] Token: {token[:20]}...")

    # Test upload
    print("\n[2/2] Testing upload...")
    response = test_upload(token)

    print("\n" + "=" * 60)
    if response.status_code == 200:
        print("[SUCCESS] UPLOAD SUCCESSFUL!")
    else:
        print("[FAILED] UPLOAD FAILED!")
    print("=" * 60)
