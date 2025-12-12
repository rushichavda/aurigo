"""
Test full upload and processing flow
"""
import requests
import json
import time

def login():
    """Login and get token"""
    response = requests.post(
        "http://localhost:8000/api/auth/login",
        data={"username": "testuser", "password": "testuser123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"[ERROR] Login failed: {response.text}")
        return None

def upload_case(token):
    """Upload case"""
    headers = {"Authorization": f"Bearer {token}"}

    with open("C:/aurigo/Pranav_Case_Data.zip", 'rb') as f:
        files = {'uploaded_folder': ('Pranav_Case_Data.zip', f, 'application/zip')}
        params = {'beneficiary_name': 'Pranav Khare Test'}

        response = requests.post(
            "http://localhost:8000/api/cases/upload",
            headers=headers,
            files=files,
            params=params,
            timeout=120
        )

        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Upload successful! Case ID: {data['case_id']}")
            return data['case_id']
        else:
            print(f"[ERROR] Upload failed: {response.status_code}")
            print(response.text)
            return None

def start_processing(token, case_id):
    """Start processing"""
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.post(
        f"http://localhost:8000/api/cases/{case_id}/process",
        headers=headers,
        timeout=30
    )

    if response.status_code == 200:
        print(f"[OK] Processing started for case {case_id}")
        return True
    else:
        print(f"[ERROR] Processing failed: {response.status_code}")
        print(response.text)
        return False

def check_status(token, case_id):
    """Check processing status"""
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(
        f"http://localhost:8000/api/cases/{case_id}/status",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        print(f"[Status] {data['status']} - {data.get('current_step', 'N/A')} - {data['progress']}%")
        return data
    else:
        print(f"[ERROR] Status check failed: {response.status_code}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("FULL FLOW TEST")
    print("=" * 60)

    # Step 1: Login
    print("\n[1/4] Logging in...")
    token = login()
    if not token:
        exit(1)
    print(f"[OK] Token received")

    # Step 2: Upload
    print("\n[2/4] Uploading case...")
    case_id = upload_case(token)
    if not case_id:
        exit(1)

    # Step 3: Start processing
    print("\n[3/4] Starting processing...")
    if not start_processing(token, case_id):
        print("[WARNING] Processing may have failed to start")
        print("Check backend logs for details")

    # Step 4: Monitor status
    print("\n[4/4] Monitoring status...")
    for i in range(10):
        time.sleep(2)
        status = check_status(token, case_id)
        if status and status['status'] in ['completed', 'failed']:
            break

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
