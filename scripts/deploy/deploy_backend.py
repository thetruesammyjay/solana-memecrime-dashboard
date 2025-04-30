import os
import subprocess
from pathlib import Path
from datetime import datetime
import shutil
import argparse
import httpx

def run_migrations():
    """Run database migrations"""
    print("🔄 Running database migrations...")
    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print("✅ Database migrations completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
        return False

def test_endpoints(base_url):
    """Verify critical API endpoints"""
    endpoints = [
        "/tokens/EPjFWdd5Auf4SSkTmfrXbM5W28Kz7Kj7oLh1gER9W5jM",  # USDC address
        "/wallets/vines1vzrYbzLMRdu58ou5XTby4qAqVRLmqo36NKPTg",
        "/alerts"
    ]
    
    for endpoint in endpoints:
        try:
            response = httpx.get(f"{base_url}{endpoint}", timeout=10)
            response.raise_for_status()
            print(f"✅ {endpoint} - {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - {str(e)}")
            return False
    return True

def backup_database():
    """Create database backup"""
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"db_backup_{timestamp}.sql"
    
    print(f"💾 Creating database backup at {backup_file}...")
    try:
        subprocess.run([
            "pg_dump",
            "-d", os.getenv("DATABASE_URL"),
            "-f", str(backup_file)
        ], check=True)
        print(f"✅ Backup created: {backup_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Backup failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Deploy MCSI backend")
    parser.add_argument("--skip-backup", action="store_true", help="Skip database backup")
    parser.add_argument("--skip-tests", action="store_true", help="Skip endpoint tests")
    args = parser.parse_args()

    # Step 1: Database backup
    if not args.skip_backup and not backup_database():
        exit(1)

    # Step 2: Run migrations
    if not run_migrations():
        exit(1)

    # Step 3: Verify endpoints
    if not args.skip_tests:
        base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        if not test_endpoints(base_url):
            exit(1)

    print("🚀 Deployment completed successfully")

if __name__ == "__main__":
    main()