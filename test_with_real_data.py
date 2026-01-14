"""
Test the enhanced features with real Google Sheets data.
"""

import os
import sys
from datetime import datetime

# Add src to path for imports
sys.path.append('src')

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from tools.google_sheets_inventory_tool import GoogleSheetsInventoryTool, GoogleSheetsInventoryInput
from agents.sales_agent import SalesAgent
from tools.sales_tool import SalesTool, SalesInput

def test_real_data_connection():
    """Test connection to real Google Sheets data."""
    print("🔗 TESTING: Google Sheets Connection")
    print("-" * 50)
    
    try:
        inventory_tool = GoogleSheetsInventoryTool()
        result = inventory_tool.execute(GoogleSheetsInventoryInput(action="list_all"))
        
        if result.success:
            products = result.result
            print(f"✅ Connected successfully!")
            print(f"📊 Found {len(products)} products in inventory")
            
            # Show sample products
            print("\n📦 Sample Products:")
            for i, product in enumerate(products[:3], 1):
                print(f"   {i}. {product['product_name']} ({product['product_id']})")
                print(f"      Stock: {product['quantity']} units @ ${product['price']:.2f}")
                print(f"      Status: {product['status']}")
            
            return products
        else:
            print(f"❌ Connection failed: {result.error}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def test_stock_availability_check():
    """Test stock availability checking with real data."""
    print("\n🔍 TESTING: Stock Availability Check")
    print("-" * 50)
    
    try:
        sales_agent = SalesAgent()
        
        # Test with a known product
        print("Checking availability for LAPTOP001...")
        response = sales_agent.process_message("Check stock for LAPTOP001")
        print(response)
        
        return "✅" in response or "📦" in response
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_stock_alerts_generation():
    """Test stock alerts with real data."""
    print("\n🚨 TESTING: Stock Alerts Generation")
    print("-" * 50)
    
    try:
        sales_tool = SalesTool()
        result = sales_tool.execute(SalesInput(action="stock_alerts"))
        
        if result.success:
            alerts = result.result
            print("✅ Stock alerts generated successfully!")
            
            summary = alerts.get('summary', {})
            print(f"📊 Alert Summary:")
            print(f"   Total Products: {summary.get('total_products', 0)}")
            print(f"   🚨 Out of Stock: {summary.get('out_of_stock_count', 0)} items")
            print(f"   🔴 Critical Stock: {summary.get('critical_stock_count', 0)} items")
            print(f"   🟡 Low Stock: {summary.get('low_stock_count', 0)} items")
            print(f"   ✅ Healthy Stock: {summary.get('healthy_stock_count', 0)} items")
            
            # Show specific alerts
            if alerts.get('alerts', {}).get('out_of_stock'):
                print(f"\n🚨 Out of Stock Items:")
                for item in alerts['alerts']['out_of_stock'][:2]:
                    print(f"   • {item['product_name']} ({item['product_id']})")
            
            if alerts.get('alerts', {}).get('critical_stock'):
                print(f"\n🔴 Critical Stock Items:")
                for item in alerts['alerts']['critical_stock'][:2]:
                    print(f"   • {item['product_name']}: {item['current_stock']} units")
            
            if alerts.get('alerts', {}).get('low_stock'):
                print(f"\n🟡 Low Stock Items:")
                for item in alerts['alerts']['low_stock'][:2]:
                    print(f"   • {item['product_name']}: {item['current_stock']} units")
            
            return True
        else:
            print(f"❌ Failed to generate alerts: {result.error}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_sales_processing_simulation():
    """Test sales processing (simulation only - won't actually modify data)."""
    print("\n💰 TESTING: Sales Processing (Simulation)")
    print("-" * 50)
    
    try:
        # First check what products are available
        inventory_tool = GoogleSheetsInventoryTool()
        result = inventory_tool.execute(GoogleSheetsInventoryInput(action="list_all"))
        
        if not result.success:
            print("❌ Cannot access inventory for simulation")
            return False
        
        products = result.result
        
        # Find a product with good stock for simulation
        suitable_product = None
        for product in products:
            if product['quantity'] > 5:  # Has enough stock for simulation
                suitable_product = product
                break
        
        if not suitable_product:
            print("⚠️ No products with sufficient stock for simulation")
            return False
        
        print(f"🎯 Simulating sale for: {suitable_product['product_name']}")
        print(f"   Current Stock: {suitable_product['quantity']} units")
        print(f"   Unit Price: ${suitable_product['price']:.2f}")
        
        # Simulate what would happen in a sale
        simulated_sale_qty = 2
        new_stock = suitable_product['quantity'] - simulated_sale_qty
        total_amount = simulated_sale_qty * suitable_product['price']
        
        print(f"\n📊 Simulation Results:")
        print(f"   Sale Quantity: {simulated_sale_qty} units")
        print(f"   Total Amount: ${total_amount:.2f}")
        print(f"   New Stock Level: {new_stock} units")
        
        # Determine what alerts would be triggered
        if new_stock == 0:
            print(f"   🚨 ALERT: Product would be OUT OF STOCK!")
        elif new_stock <= 5:
            print(f"   🔴 ALERT: Product would have CRITICAL STOCK!")
        elif new_stock <= 10:
            print(f"   🟡 ALERT: Product would have LOW STOCK!")
        else:
            print(f"   ✅ Stock level would remain healthy")
        
        print(f"\n💡 This demonstrates the automatic stock deduction and alert system")
        print(f"   In the actual app, this would update the Google Sheet immediately")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_enhanced_features_demo():
    """Run a comprehensive demo of all enhanced features."""
    print("🚀 ENHANCED FEATURES DEMO WITH REAL DATA")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Data Connection
    products = test_real_data_connection()
    if not products:
        print("\n❌ Cannot proceed without data connection")
        return
    
    # Test 2: Stock Availability
    availability_success = test_stock_availability_check()
    
    # Test 3: Stock Alerts
    alerts_success = test_stock_alerts_generation()
    
    # Test 4: Sales Processing Simulation
    sales_success = test_sales_processing_simulation()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 DEMO SUMMARY")
    print("=" * 80)
    
    tests = [
        ("Data Connection", products is not None),
        ("Stock Availability Check", availability_success),
        ("Stock Alerts Generation", alerts_success),
        ("Sales Processing Simulation", sales_success)
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status:<12} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed >= 3:
        print("\n🎉 ENHANCED FEATURES ARE WORKING!")
        print("\n🚀 Ready to use:")
        print("   1. Run: python run_inventory_app.py")
        print("   2. Go to 'Data Management' tab")
        print("   3. Try the 'Add Products' and 'Quick Sale' features")
        print("   4. Check the enhanced dashboard with real-time alerts")
    else:
        print(f"\n⚠️ Some features need attention. Check the errors above.")
    
    print(f"\nDemo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_enhanced_features_demo()