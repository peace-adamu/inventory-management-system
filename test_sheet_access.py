#!/usr/bin/env python3
"""
Simple test to verify Google Sheets public access.
"""

import requests
import csv
from io import StringIO

def test_sheet_access():
    """Test direct access to your Google Sheet."""
    
    sheet_id = "1CyA1nOnQ8Bzdqi60Xqk8dWcL32Zpx6ktUw_-HTeKNE8"
    
    print("🧪 Testing Google Sheets Access")
    print("=" * 50)
    print(f"Sheet ID: {sheet_id}")
    
    # Try different export formats
    formats_to_try = [
        ("CSV", f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"),
        ("CSV Alt", f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"),
        ("TSV", f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=tsv&gid=0"),
    ]
    
    for format_name, url in formats_to_try:
        print(f"\n🔍 Testing {format_name} format...")
        print(f"URL: {url}")
        
        try:
            response = requests.get(url, timeout=15)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCCESS! Sheet is accessible")
                
                # Try to parse the data
                if format_name.startswith("CSV"):
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    rows = list(reader)
                    
                    print(f"📊 Found {len(rows)} data rows")
                    
                    if rows:
                        print("📋 Sample data:")
                        for i, row in enumerate(rows[:3]):
                            print(f"  Row {i+1}: {dict(row)}")
                        
                        if len(rows) > 3:
                            print(f"  ... and {len(rows) - 3} more rows")
                    
                    return True
                else:
                    print(f"📄 Content preview: {response.text[:200]}...")
                    return True
                    
            elif response.status_code == 403:
                print("❌ FORBIDDEN - Sheet is not publicly accessible")
                print("   Please make sure the sheet is shared with 'Anyone with the link'")
                
            elif response.status_code == 404:
                print("❌ NOT FOUND - Sheet ID might be incorrect")
                
            else:
                print(f"❌ ERROR {response.status_code}: {response.text[:100]}")
                
        except requests.exceptions.Timeout:
            print("⏰ TIMEOUT - Connection took too long")
            
        except requests.exceptions.ConnectionError:
            print("🌐 CONNECTION ERROR - Check internet connection")
            
        except Exception as e:
            print(f"❌ UNEXPECTED ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("🔧 TROUBLESHOOTING STEPS:")
    print("1. Open your Google Sheet")
    print("2. Click 'Share' button (top right)")
    print("3. Change from 'Restricted' to 'Anyone with the link'")
    print("4. Set permission to 'Viewer'")
    print("5. Click 'Done'")
    print("6. Run this test again")
    
    return False

if __name__ == "__main__":
    success = test_sheet_access()
    
    if success:
        print("\n🎉 Your Google Sheet is properly configured!")
        print("   The inventory system should now work with your real data.")
        print("   Run: python run_inventory_app.py")
    else:
        print("\n⚠️ Sheet access needs to be configured.")
        print("   The system will use mock data until this is fixed.")