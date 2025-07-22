#!/usr/bin/env python3
"""
Simple test script to validate the project foundation structure
"""
import os
import sys
from pathlib import Path

def test_project_structure():
    """Test that all required directories and files exist."""
    print("Testing project structure...")
    
    required_files = [
        "main.py",
        "requirements.txt",
        "alembic.ini",
        ".env.example",
        "README.md",
        "app/__init__.py",
        "app/core/__init__.py",
        "app/core/config.py",
        "app/core/database.py",
        "app/core/logging.py",
        "app/models/__init__.py",
        "app/models/user.py",
        "app/models/player.py",
        "app/models/livestock.py",
        "app/models/module.py",
        "app/models/item.py",
        "app/models/translation.py",
        "app/api/__init__.py",
        "app/api/routes.py",
        "alembic/env.py",
        "alembic/script.py.mako",
        "scripts/init_db.py",
        "scripts/start_dev.py",
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files exist")
        return True

def test_file_contents():
    """Test that key files have expected content."""
    print("Testing file contents...")
    
    # Test main.py has FastAPI app
    with open("main.py", "r") as f:
        main_content = f.read()
        if "FastAPI" not in main_content:
            print("❌ main.py doesn't contain FastAPI")
            return False
    
    # Test requirements.txt has FastAPI
    with open("requirements.txt", "r") as f:
        req_content = f.read()
        if "fastapi" not in req_content:
            print("❌ requirements.txt doesn't contain fastapi")
            return False
    
    # Test models directory structure
    model_files = ["user.py", "player.py", "livestock.py", "module.py", "item.py", "translation.py"]
    for model_file in model_files:
        model_path = Path(f"app/models/{model_file}")
        if not model_path.exists():
            print(f"❌ Missing model file: {model_file}")
            return False
        
        with open(model_path, "r") as f:
            content = f.read()
            if "class" not in content:
                print(f"❌ Model file {model_file} doesn't contain class definition")
                return False
    
    print("✅ File contents look good")
    return True

def main():
    """Run all foundation tests."""
    print("🚀 Testing Park Tycoon Game Foundation")
    print("=" * 50)
    
    tests = [
        test_project_structure,
        test_file_contents,
    ]
    
    all_passed = True
    for test in tests:
        try:
            if not test():
                all_passed = False
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            all_passed = False
        print()
    
    if all_passed:
        print("🎉 All foundation tests passed!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set up environment: cp .env.example .env")
        print("3. Initialize database: python scripts/init_db.py")
        print("4. Start development server: python scripts/start_dev.py")
    else:
        print("❌ Some tests failed. Please check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()