import requests
import time
import sys
import subprocess
import os
import signal
import socket

BASE_URL = "http://localhost:8000"
BACKEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")

def wait_for_port(port, host='localhost', timeout=10.0):
    """Wait until a port starts accepting connections."""
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except (OSError, ConnectionRefusedError):
            if time.time() - start_time >= timeout:
                return False
            time.sleep(0.1)

def start_server():
    """Start the uvicorn server as a subprocess."""
    print("🚀 Starting backend server...")
    # Use the same python interpreter running this script (from venv)
    cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
    
    # Open a log file for the server
    log_file = open("server_e2e.log", "w")
    
    process = subprocess.Popen(
        cmd,
        cwd=BACKEND_DIR,
        stdout=log_file,
        stderr=subprocess.STDOUT
    )
    return process, log_file

def run_e2e_test():
    print("Starting E2E Verification...")
    
    # 1. Health Check
    try:
        resp = requests.get(f"{BASE_URL}/")
        if resp.status_code != 200:
            print(f"❌ Health check failed: {resp.status_code}")
            return False
        print("✅ Health check passed")
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to {BASE_URL}. Is the backend running?")
        return False

    # 2. Create Task (Optimize)
    payload = {
        "description": "Write a hello world python script",
        "context_files": [],
        "constraints": "Use standard print"
    }
    resp = requests.post(f"{BASE_URL}/api/optimize", json=payload)
    if resp.status_code != 200:
        print(f"❌ Optimize endpoint failed: {resp.text}")
        return False
    data = resp.json()
    task_id = data.get("id")
    if not task_id:
        print("❌ No task ID returned")
        return False
    print(f"✅ Created Task ID: {task_id}")

    # 3. Verify History
    resp = requests.get(f"{BASE_URL}/api/history")
    history = resp.json()
    if not any(t["id"] == task_id for t in history):
        print("❌ Task not found in history")
        return False
    print("✅ Task verified in history")

    # 4. Run Agent
    # Note: In this prototype, we mocked the optimizer but the 'run' logic might still be skeletal
    # We will trigger it and expect a status update.
    run_payload = {
        "task_id": task_id
    }
    resp = requests.post(f"{BASE_URL}/api/run", json=run_payload)
    if resp.status_code != 200:
        print(f"❌ Run endpoint failed: {resp.text}")
        return False
    print("✅ Agent run triggered")

    # 5. Check Status (Simulate polling)
    time.sleep(1)
    resp = requests.get(f"{BASE_URL}/api/status")
    status_data = resp.json()
    print(f"✅ Current Status: {status_data.get('status')}")

    print("✅ E2E Verification Complete!")
    return True

if __name__ == "__main__":
    server_process, log_file = start_server()
    try:
        if wait_for_port(8000):
            print("✅ Server is ready.")
            success = run_e2e_test()
            if not success:
                print("❌ E2E Tests Failed.")
                sys.exit(1)
        else:
            print("❌ Server failed to start within timeout.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nAborted by user.")
    finally:
        print("🛑 Stopping server...")
        server_process.terminate()
        server_process.wait()
        log_file.close()
