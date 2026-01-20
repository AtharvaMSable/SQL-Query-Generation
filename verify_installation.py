"""
AskQL Installation Verification Script
Run this script to verify your environment is properly configured.
"""

import sys
import os

def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def check_python_version():
    """Check Python version."""
    print("✓ Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 11:
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"  ❌ Python {version.major}.{version.minor}.{version.micro} - Need 3.11+")
        return False

def check_dependencies():
    """Check required packages."""
    print("\n✓ Checking dependencies...")
    
    required = {
        'streamlit': '1.31.0',
        'sqlalchemy': '2.0.27',
        'pandas': '2.2.0',
        'plotly': '5.19.0',
        'google.generativeai': '0.4.0',
        'dotenv': '1.0.1',
    }
    
    all_ok = True
    for package, min_version in required.items():
        try:
            if package == 'google.generativeai':
                import google.generativeai as genai
                print(f"  ✅ google-generativeai - OK")
            elif package == 'dotenv':
                import dotenv
                print(f"  ✅ python-dotenv - OK")
            else:
                module = __import__(package)
                print(f"  ✅ {package} - OK")
        except ImportError:
            print(f"  ❌ {package} - NOT FOUND")
            all_ok = False
    
    return all_ok

def check_env_file():
    """Check .env file exists."""
    print("\n✓ Checking .env file...")
    
    if os.path.exists('.env'):
        print("  ✅ .env file found")
        
        # Check required variables
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = [
            'NEON_DB_HOST',
            'NEON_DB_NAME',
            'NEON_DB_USER',
            'NEON_DB_PASSWORD',
            'GEMINI_API_KEY'
        ]
        
        missing = []
        for var in required_vars:
            if not os.getenv(var):
                missing.append(var)
        
        if missing:
            print(f"  ⚠️  Missing variables: {', '.join(missing)}")
            print("  ℹ️  Edit .env and add these variables")
            return False
        else:
            print("  ✅ All required variables present")
            return True
    else:
        print("  ❌ .env file not found")
        print("  ℹ️  Run: copy .env.example .env")
        return False

def check_database_connection():
    """Check database connectivity."""
    print("\n✓ Checking database connection...")
    
    try:
        from config.database_config import DatabaseConfig
        
        if DatabaseConfig.test_connection():
            print("  ✅ Database connection successful")
            return True
        else:
            print("  ❌ Database connection failed")
            print("  ℹ️  Check your Neon DB credentials in .env")
            return False
    except Exception as e:
        print(f"  ❌ Error testing connection: {str(e)}")
        return False

def check_gemini_api():
    """Check Gemini API key."""
    print("\n✓ Checking Gemini API...")
    
    try:
        from llm.gemini_client import GeminiClient
        
        client = GeminiClient()
        if client.test_connection():
            print("  ✅ Gemini API connection successful")
            return True
        else:
            print("  ❌ Gemini API connection failed")
            print("  ℹ️  Check your GEMINI_API_KEY in .env")
            return False
    except Exception as e:
        print(f"  ❌ Error testing Gemini: {str(e)}")
        return False

def check_project_structure():
    """Check all required files exist."""
    print("\n✓ Checking project structure...")
    
    required_files = [
        'app.py',
        'requirements.txt',
        'README.md',
        'auth/user_auth.py',
        'auth/session_manager.py',
        'config/settings.py',
        'config/database_config.py',
        'database/schema_loader.py',
        'database/query_executor.py',
        'database/validators.py',
        'llm/gemini_client.py',
        'llm/prompt_templates.py',
        'analytics/chart_generator.py',
        'analytics/insight_generator.py',
        'utils/logger.py',
        'utils/helpers.py',
        'sql/init_schema.sql',
    ]
    
    all_present = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING")
            all_present = False
    
    return all_present

def main():
    """Run all verification checks."""
    print_header("AskQL Installation Verification")
    
    checks = {
        "Python Version": check_python_version(),
        "Dependencies": check_dependencies(),
        "Environment File": check_env_file(),
        "Project Structure": check_project_structure(),
    }
    
    # Optional checks (require .env to be configured)
    if checks["Environment File"]:
        checks["Database Connection"] = check_database_connection()
        checks["Gemini API"] = check_gemini_api()
    
    # Summary
    print_header("Verification Summary")
    
    for check_name, result in checks.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {check_name}: {status}")
    
    print("\n")
    
    if all(checks.values()):
        print("🎉 All checks passed! You're ready to run the application.")
        print("\nNext steps:")
        print("  1. Ensure database is initialized with sql/init_schema.sql")
        print("  2. Run: streamlit run app.py")
        print("  3. Login with demo credentials (see QUICKSTART.md)")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("\nHelp:")
        print("  - See SETUP.md for detailed setup instructions")
        print("  - See QUICKSTART.md for quick start guide")
        print("  - Check .env.example for required variables")

if __name__ == "__main__":
    main()
