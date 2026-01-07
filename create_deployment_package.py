#!/usr/bin/env python3
"""
Create a deployment package for GitHub upload.
"""

import os
import shutil
import zipfile
from pathlib import Path

def create_deployment_package():
    """Create a ZIP file with all necessary files for GitHub deployment."""
    
    print("📦 Creating Deployment Package")
    print("=" * 50)
    
    # Files and directories to include
    files_to_include = [
        "inventory_management_app.py",
        "requirements.txt", 
        "README.md",
        ".gitignore",
        ".env.example",
        "DEPLOYMENT.md",
        "sample_inventory_sheet.csv",
        "test_inventory_agents.py",
        "test_sheet_access.py",
        "run_inventory_app.py"
    ]
    
    directories_to_include = [
        "src/",
        ".streamlit/"
    ]
    
    # Create deployment directory
    deploy_dir = Path("deployment_package")
    if deploy_dir.exists():
        shutil.rmtree(deploy_dir)
    deploy_dir.mkdir()
    
    print("📁 Copying files...")
    
    # Copy individual files
    for file_name in files_to_include:
        if Path(file_name).exists():
            shutil.copy2(file_name, deploy_dir / file_name)
            print(f"✅ {file_name}")
        else:
            print(f"⚠️ {file_name} not found")
    
    # Copy directories
    for dir_name in directories_to_include:
        if Path(dir_name).exists():
            shutil.copytree(dir_name, deploy_dir / dir_name)
            print(f"✅ {dir_name}")
        else:
            print(f"⚠️ {dir_name} not found")
    
    # Create ZIP file
    zip_path = "inventory-management-system.zip"
    print(f"\n📦 Creating ZIP file: {zip_path}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(deploy_dir):
            for file in files:
                file_path = Path(root) / file
                arc_path = file_path.relative_to(deploy_dir)
                zipf.write(file_path, arc_path)
                print(f"   Added: {arc_path}")
    
    # Clean up temporary directory
    shutil.rmtree(deploy_dir)
    
    print(f"\n🎉 Deployment package created: {zip_path}")
    print(f"📊 File size: {Path(zip_path).stat().st_size / 1024:.1f} KB")
    
    print("\n🚀 Next Steps:")
    print("1. Go to https://github.com/new")
    print("2. Create repository: 'inventory-management-system'")
    print("3. Make it PUBLIC (required for free Streamlit)")
    print("4. Upload the ZIP file or extract and upload individual files")
    print("5. Deploy on Streamlit Cloud using DEPLOYMENT.md instructions")
    
    return zip_path

if __name__ == "__main__":
    create_deployment_package()