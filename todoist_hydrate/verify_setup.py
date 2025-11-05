#!/usr/bin/env python3
"""
Setup verification script for Todoist Task Hydration System.
Run this to verify your environment is configured correctly.
"""
import os
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)")
        return False

def check_dependencies():
    """Check if required packages are installed."""
    print("\n📦 Checking dependencies...")
    required = ['anthropic', 'requests', 'dotenv', 'pydantic']
    missing = []

    for package in required:
        try:
            if package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (not installed)")
            missing.append(package)

    if missing:
        print(f"\n   Install missing packages with:")
        print(f"   pip install -r requirements.txt")
        return False
    return True

def check_env_file():
    """Check if .env file exists and has required variables."""
    print("\n🔐 Checking environment configuration...")
    env_path = Path(".env")

    if not env_path.exists():
        print("   ❌ .env file not found")
        print("   Create one by copying .env.example:")
        print("   cp .env.example .env")
        return False

    print("   ✅ .env file exists")

    # Try to load and check variables
    try:
        from dotenv import load_dotenv
        load_dotenv()

        todoist_token = os.getenv("TODOIST_API_TOKEN")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")

        if not todoist_token or todoist_token == "your_todoist_api_token_here":
            print("   ⚠️  TODOIST_API_TOKEN not set or using example value")
            print("      Get your token from: https://todoist.com/prefs/integrations")
        else:
            print(f"   ✅ TODOIST_API_TOKEN set ({len(todoist_token)} chars)")

        if not anthropic_key or anthropic_key == "your_anthropic_api_key_here":
            print("   ⚠️  ANTHROPIC_API_KEY not set or using example value")
            print("      Get your key from: https://console.anthropic.com/")
        else:
            print(f"   ✅ ANTHROPIC_API_KEY set ({len(anthropic_key)} chars)")

        return bool(todoist_token and anthropic_key)
    except Exception as e:
        print(f"   ❌ Error loading .env: {e}")
        return False

def check_api_connections():
    """Test API connections."""
    print("\n🔌 Testing API connections...")

    try:
        from todoist_api import TodoistAPI
        print("   Testing Todoist API...")
        api = TodoistAPI()
        # Try to fetch tasks (this will fail if token is invalid)
        tasks = api.get_all_tasks()
        print(f"   ✅ Todoist API connected ({len(tasks)} tasks found)")
    except Exception as e:
        print(f"   ❌ Todoist API error: {e}")
        return False

    try:
        from hydrator import TaskHydrator
        print("   Testing Anthropic API...")
        hydrator = TaskHydrator()
        print("   ✅ Anthropic API initialized")
        print("   ⚠️  Note: Full API test requires making a request (skipped)")
    except Exception as e:
        print(f"   ❌ Anthropic API error: {e}")
        return False

    return True

def check_file_structure():
    """Verify all required files exist."""
    print("\n📁 Checking file structure...")
    required_files = [
        "__init__.py",
        "todoist_api.py",
        "hydrator.py",
        "notebooklm_export.py",
        "cli.py",
        "requirements.txt",
        ".env.example",
        "README.md"
    ]

    all_present = True
    for filename in required_files:
        if Path(filename).exists():
            print(f"   ✅ {filename}")
        else:
            print(f"   ❌ {filename} (missing)")
            all_present = False

    return all_present

def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Todoist Task Hydration System - Setup Verification")
    print("=" * 60)

    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment File", check_env_file),
        ("File Structure", check_file_structure),
    ]

    results = []
    for name, check_func in checks:
        try:
            results.append(check_func())
        except Exception as e:
            print(f"\n❌ {name} check failed with error: {e}")
            results.append(False)

    # Only check API connections if basic setup is complete
    if all(results):
        try:
            results.append(check_api_connections())
        except Exception as e:
            print(f"\n❌ API connection check failed: {e}")
            results.append(False)

    print("\n" + "=" * 60)
    if all(results):
        print("✅ All checks passed! You're ready to use the system.")
        print("\nTry running:")
        print("  python cli.py --help")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        sys.exit(1)
    print("=" * 60)

if __name__ == "__main__":
    main()
