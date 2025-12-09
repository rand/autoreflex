#!/usr/bin/env python3
import os
import sys
import subprocess
import signal
import time
import shutil

# Try to import click, if missing, guide user
try:
    import click
except ImportError:
    print("❌ Error: 'click' module not found.")
    print("Please ensure you have activated the virtual environment and installed dependencies.")
    print("Run:")
    print("  source venv/bin/activate")
    print("  pip install -r backend/requirements.txt")
    sys.exit(1)

BACKEND_DIR = os.path.join(os.getcwd(), "backend")
FRONTEND_DIR = os.path.join(os.getcwd(), "frontend")
VENV_PYTHON = os.path.join(os.getcwd(), "venv", "bin", "python")
VENV_UVICORN = os.path.join(os.getcwd(), "venv", "bin", "uvicorn")
VENV_PYTEST = os.path.join(os.getcwd(), "venv", "bin", "pytest")
VENV_MYPY = os.path.join(os.getcwd(), "venv", "bin", "mypy")

def check_venv():
    if not os.path.exists(VENV_PYTHON):
        click.echo("❌ Virtual environment not found at ./venv")
        click.echo("Please create it first: python3 -m venv venv")
        sys.exit(1)

@click.group()
def cli():
    """AutoReflex Local Development CLI"""
    pass

@cli.command()
def setup():
    """Install Backend and Frontend dependencies."""
    check_venv()
    
    click.echo("📦 Installing Backend Dependencies...")
    # Upgrade build tools to minimize wheel building issues
    subprocess.check_call([VENV_PYTHON, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])

    # Set environment variables to help build grpcio on macOS if wheels are missing
    env = os.environ.copy()
    env["GRPC_PYTHON_BUILD_SYSTEM_OPENSSL"] = "1"
    env["GRPC_PYTHON_BUILD_SYSTEM_ZLIB"] = "1"

    # Add Homebrew paths for OpenSSL on macOS (for Apple Silicon and Intel)
    if sys.platform == "darwin":
        # Check for Homebrew OpenSSL
        openssl_paths = [
            "/opt/homebrew/opt/openssl@3",
            "/opt/homebrew/opt/openssl",
            "/usr/local/opt/openssl@3",
            "/usr/local/opt/openssl"
        ]
        for openssl_dir in openssl_paths:
            if os.path.exists(openssl_dir):
                include_dir = os.path.join(openssl_dir, "include")
                lib_dir = os.path.join(openssl_dir, "lib")
                
                # Append to existing flags or set new ones
                env["CFLAGS"] = f"{env.get('CFLAGS', '')} -I{include_dir}"
                env["CPPFLAGS"] = f"{env.get('CPPFLAGS', '')} -I{include_dir}"
                env["LDFLAGS"] = f"{env.get('LDFLAGS', '')} -L{lib_dir}"
                break

    subprocess.check_call([VENV_PYTHON, "-m", "pip", "install", "-r", os.path.join(BACKEND_DIR, "requirements.txt")], env=env)
    
    click.echo("📦 Installing Frontend Dependencies...")
    subprocess.check_call(["npm", "install"], cwd=FRONTEND_DIR)
    
    click.echo("✅ Setup complete!")

@cli.command()
@click.option('--port', default=8000, help='Backend API port')
@click.option('--host', default='0.0.0.0', help='Backend API host')
def start(host, port):
    """Start the full stack (Backend + Frontend)."""
    check_venv()

    # Define processes
    backend_proc = None
    frontend_proc = None

    def cleanup(signum, frame):
        click.echo("\n🛑 Shutting down services...")
        if backend_proc:
            backend_proc.terminate()
        if frontend_proc:
            frontend_proc.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    try:
        click.echo(f"🚀 Starting Backend (Uvicorn) on http://{host}:{port}...")
        # Use sys.executable to run uvicorn module if direct binary fails, but binary is safer in venv
        backend_cmd = [VENV_UVICORN, "app.main:app", "--host", host, "--port", str(port), "--reload"]
        backend_proc = subprocess.Popen(backend_cmd, cwd=BACKEND_DIR)

        click.echo("🚀 Starting Frontend (Vite)...")
        frontend_proc = subprocess.Popen(["npm", "run", "dev"], cwd=FRONTEND_DIR)

        # Wait for both
        backend_proc.wait()
        frontend_proc.wait()

    except Exception as e:
        click.echo(f"❌ Error: {e}")
        cleanup(None, None)

@cli.command()
def test():
    """Run all tests (Backend, Frontend, E2E, Mypy)."""
    check_venv()
    
    # 1. Backend Mypy Check
    click.echo("🧪 Running Backend Mypy Check...")
    ret = subprocess.call([VENV_MYPY, "app"], cwd=BACKEND_DIR)
    if ret != 0:
        click.echo("❌ Mypy check failed!")
        sys.exit(ret)

    # 2. Backend Unit Tests
    click.echo("🧪 Running Backend Unit Tests...")
    ret = subprocess.call([VENV_PYTEST, "tests"], cwd=BACKEND_DIR)
    if ret != 0:
        click.echo("❌ Backend tests failed!")
        sys.exit(ret)

    # 3. Frontend Tests
    click.echo("🧪 Running Frontend Component Tests...")
    ret = subprocess.call(["npm", "test", "--", "--run"], cwd=FRONTEND_DIR)
    if ret != 0:
        click.echo("❌ Frontend tests failed!")
        sys.exit(ret)

    # 4. E2E Tests
    click.echo("🧪 Running End-to-End Verification...")
    # verify_e2e.py expects to run from root
    ret = subprocess.call([VENV_PYTHON, "verify_e2e.py"])
    if ret != 0:
        click.echo("❌ E2E tests failed!")
        sys.exit(ret)
        
    click.echo("✅ All Tests Passed!")

@cli.command()
def tui():
    """Start the Terminal User Interface (Textual)."""
    check_venv()
    click.echo("🖥️  Starting TUI...")
    # Run tui as a module
    subprocess.call([VENV_PYTHON, "-m", "tui.app"])

@cli.group()
def service():
    """Manage background daemon services."""
    pass

@service.command()
def install():
    """Generate systemd (Linux) or launchd (macOS) service files."""
    check_venv()
    
    user = os.getlogin()
    working_dir = os.getcwd()
    python_path = VENV_PYTHON
    # Ensure DB path is absolute for the daemon
    db_path = os.path.join(BACKEND_DIR, "autoreflex.db")
    db_url = f"sqlite:///{db_path}"

    replacements = {
        "{USER}": user,
        "{WORKING_DIR}": working_dir,
        "{PYTHON_PATH}": python_path,
        "{DB_URL}": db_url
    }

    if sys.platform == "darwin":
        template_path = os.path.join(os.getcwd(), "scripts", "com.autoreflex.daemon.plist.template")
        output_path = os.path.join(os.getcwd(), "scripts", "com.autoreflex.daemon.plist")
        
        if not os.path.exists(template_path):
            click.echo("❌ Template not found: scripts/com.autoreflex.daemon.plist.template")
            return

        with open(template_path, "r") as f:
            content = f.read()
        
        for k, v in replacements.items():
            content = content.replace(k, v)
            
        with open(output_path, "w") as f:
            f.write(content)
            
        click.echo(f"✅ Generated macOS Launch Agent: {output_path}")
        click.echo("\nTo install:")
        click.echo(f"  cp {output_path} ~/Library/LaunchAgents/")
        click.echo("  launchctl load ~/Library/LaunchAgents/com.autoreflex.daemon.plist")
        click.echo("  launchctl start com.autoreflex.daemon")

    elif sys.platform == "linux":
        template_path = os.path.join(os.getcwd(), "scripts", "autoreflex.service.template")
        output_path = os.path.join(os.getcwd(), "scripts", "autoreflex.service")
        
        if not os.path.exists(template_path):
            click.echo("❌ Template not found: scripts/autoreflex.service.template")
            return

        with open(template_path, "r") as f:
            content = f.read()
        
        for k, v in replacements.items():
            content = content.replace(k, v)
            
        with open(output_path, "w") as f:
            f.write(content)
            
        click.echo(f"✅ Generated Systemd Service: {output_path}")
        click.echo("\nTo install:")
        click.echo(f"  sudo cp {output_path} /etc/systemd/system/")
        click.echo("  sudo systemctl daemon-reload")
        click.echo("  sudo systemctl enable autoreflex")
        click.echo("  sudo systemctl start autoreflex")
    
    else:
        click.echo(f"⚠️  Unsupported platform for automatic service generation: {sys.platform}")

@service.command()
def status():
    """Check if the backend API is reachable."""
    import urllib.request
    try:
        # Simple health check
        with urllib.request.urlopen("http://localhost:8000/status", timeout=2) as response:
            if response.status == 200:
                click.echo("✅ Service is RUNNING")
            else:
                click.echo(f"⚠️  Service responded with code {response.status}")
    except Exception as e:
        click.echo("❌ Service is STOPPED or unreachable")
        click.echo(f"   ({e})")

@cli.command()
def clean():
    """Remove build artifacts and temp files."""
    patterns = [
        "**/__pycache__",
        "**/.pytest_cache",
        "**/*.pyc",
        "frontend/dist",
        "backend/autoreflex.db",
        "backend/logs",
        "server_e2e.log"
    ]
    
    click.echo("🧹 Cleaning up...")
    # Simple shell-based cleanup for glob patterns
    for p in patterns:
        subprocess.call(f"rm -rf {p}", shell=True)
    
    click.echo("✅ Cleaned.")

if __name__ == "__main__":
    cli()