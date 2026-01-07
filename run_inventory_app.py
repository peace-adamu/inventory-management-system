#!/usr/bin/env python3
"""
Inventory Management System Launcher
Launches the multi-agent inventory management Streamlit app.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """Check if required packages are installed."""
    required_packages = [
        'streamlit',
        'pandas', 
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_packages(packages):
    """Install missing packages."""
    print(f"📦 Installing missing packages: {', '.join(packages)}")
    
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install'
        ] + packages)
        print("✅ Packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def main():
    """Main launcher function."""
    
    print("🚀 INVENTORY MANAGEMENT SYSTEM LAUNCHER")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("inventory_management_app.py").exists():
        print("❌ inventory_management_app.py not found!")
        print("   Make sure you're running this from the project directory.")
        return
    
    # Check requirements
    print("📋 Checking requirements...")
    missing = check_requirements()
    
    if missing:
        print(f"⚠️ Missing packages: {', '.join(missing)}")
        
        install_choice = input("Install missing packages? (y/n): ").lower()
        if install_choice in ['y', 'yes', '']:
            if not install_packages(missing):
                print("❌ Installation failed. Please install manually:")
                print(f"   pip install {' '.join(missing)}")
                return
        else:
            print("❌ Cannot run without required packages.")
            return
    else:
        print("✅ All requirements satisfied!")
    
    # Check environment configuration
    print("\n🔧 Checking configuration...")
    
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
        
        # Load and check key variables
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            google_api_key = os.getenv("GOOGLE_API_KEY")
            sheets_id = os.getenv("GOOGLE_SHEETS_INVENTORY_ID")
            
            if google_api_key:
                print(f"✅ Google API Key configured: ...{google_api_key[-4:]}")
            else:
                print("⚠️ Google API Key not found (will use mock data)")
            
            if sheets_id:
                print(f"✅ Google Sheets ID configured: ...{sheets_id[-10:]}")
            else:
                print("⚠️ Google Sheets ID not found (will use mock data)")
                
        except Exception as e:
            print(f"⚠️ Configuration check failed: {e}")
    else:
        print("⚠️ .env file not found (will use mock data)")
        print("   Create .env file with your Google API key and Sheets ID for full functionality")
    
    # Test the system
    print("\n🧪 Testing system...")
    
    try:
        # Quick import test
        sys.path.append('src')
        from agents.inventory_coordinator_agent import InventoryCoordinatorAgent
        
        # Quick functionality test
        coordinator = InventoryCoordinatorAgent()
        status = coordinator.get_system_status()
        
        print("✅ Multi-agent system ready!")
        print(f"   Status: {status.get('coordinator_status', 'Unknown')}")
        
    except Exception as e:
        print(f"⚠️ System test warning: {str(e)[:100]}...")
        print("   The app may still work with limited functionality")
    
    # Launch Streamlit
    print("\n🚀 Launching Inventory Management System...")
    print("   Opening in your default browser...")
    print("   Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 
            'inventory_management_app.py',
            '--server.port', '8501',
            '--server.address', 'localhost'
        ])
        
    except KeyboardInterrupt:
        print("\n\n👋 Inventory Management System stopped.")
        print("   Thanks for using the multi-agent inventory system!")
        
    except Exception as e:
        print(f"\n❌ Error launching Streamlit: {e}")
        print("\nTry running manually:")
        print("   streamlit run inventory_management_app.py")

if __name__ == "__main__":
    main()