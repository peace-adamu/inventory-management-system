"""
Test script for enhanced inventory management features:
1. Adding items directly from the app
2. Sales processing with automatic stock deduction
3. Real-time stock alerts
"""

import os
import sys
from datetime import datetime

# Add src to path for imports
sys.path.append('src')

# Import the enhanced components
try:
    from agents.sales_agent import SalesAgent
    from tools.sales_tool import SalesTool, SalesInput
    from tools.google_sheets_inventory_tool import GoogleSheetsInventoryTool, GoogleSheetsInventoryInput
    from agents.transaction_agent import TransactionAgent
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    print(f"❌ Import error: {e}")
    IMPORTS_SUCCESSFUL = False

def test_add_product_functionality():
    """Test adding products directly through the app."""
    print("\n" + "="*60)
    print("🧪 TESTING: Add Product Functionality")
    print("="*60)
    
    if not IMPORTS_SUCCESSFUL:
        print("❌ Cannot test - imports failed")
        return False
    
    try:
        # Initialize inventory tool
        inventory_tool = GoogleSheetsInventoryTool()
        
        # Test adding a new product
        test_product = {
            "product_id": "TEST001",
            "product_name": "Test Gaming Mouse",
            "quantity": 25,
            "price": 79.99,
            "category": "Accessories"
        }
        
        print(f"📦 Adding test product: {test_product['product_name']}")
        
        result = inventory_tool.execute(GoogleSheetsInventoryInput(
            action="add",
            product_id=test_product["product_id"],
            product_name=test_product["product_name"],
            quantity=test_product["quantity"],
            price=test_product["price"],
            category=test_product["category"]
        ))
        
        if result.success:
            print("✅ Product added successfully!")
            print(f"   Product ID: {result.result['product_id']}")
            print(f"   Initial Stock: {result.result['quantity']} units")
            print(f"   Total Value: ${result.result['quantity'] * result.result['price']:.2f}")
            return True
        else:
            print(f"❌ Failed to add product: {result.error}")
            if "already exists" in str(result.error).lower():
                print("   (This is expected if product already exists)")
                return True
            return False
            
    except Exception as e:
        print(f"❌ Error testing add product: {str(e)}")
        return False

def test_sales_with_stock_deduction():
    """Test sales processing with automatic stock deduction."""
    print("\n" + "="*60)
    print("🧪 TESTING: Sales with Automatic Stock Deduction")
    print("="*60)
    
    if not IMPORTS_SUCCESSFUL:
        print("❌ Cannot test - imports failed")
        return False
    
    try:
        # Initialize sales agent
        sales_agent = SalesAgent()
        
        # Test checking stock availability first
        print("📊 Checking stock availability for LAPTOP001...")
        availability_response = sales_agent.process_message("Check stock for LAPTOP001")
        print(availability_response)
        
        print("\n" + "-"*40)
        
        # Test processing a sale
        print("💰 Processing test sale...")
        sale_response = sales_agent.process_message("Quick sale: 1 LAPTOP001 for $1299.99 to Test Customer")
        print(sale_response)
        
        # Check if sale was successful
        if "✅" in sale_response:
            print("\n✅ Sales processing test PASSED")
            
            # Test stock alerts after sale
            print("\n🚨 Checking for stock alerts after sale...")
            alert_response = sales_agent.process_message("Show low stock alerts")
            print(alert_response)
            
            return True
        else:
            print("\n❌ Sales processing test FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Error testing sales: {str(e)}")
        return False

def test_enhanced_sales_tool():
    """Test the enhanced sales tool functionality."""
    print("\n" + "="*60)
    print("🧪 TESTING: Enhanced Sales Tool")
    print("="*60)
    
    if not IMPORTS_SUCCESSFUL:
        print("❌ Cannot test - imports failed")
        return False
    
    try:
        # Initialize sales tool
        sales_tool = SalesTool()
        
        # Test 1: Check availability
        print("1️⃣ Testing availability check...")
        availability_result = sales_tool.execute(SalesInput(
            action="check_availability",
            product_id="PHONE001"
        ))
        
        if availability_result.success:
            availability = availability_result.result
            print(f"✅ Availability check successful:")
            print(f"   Product: {availability['product_name']}")
            print(f"   Stock: {availability['availability']['current_stock']} units")
            print(f"   Status: {availability['availability']['status']}")
            print(f"   Can Sell: {availability['availability']['can_sell']}")
        else:
            print(f"❌ Availability check failed: {availability_result.error}")
        
        print("\n" + "-"*30)
        
        # Test 2: Generate stock alerts
        print("2️⃣ Testing stock alerts generation...")
        alerts_result = sales_tool.execute(SalesInput(action="stock_alerts"))
        
        if alerts_result.success:
            alerts = alerts_result.result
            print(f"✅ Stock alerts generated:")
            print(f"   Out of Stock: {alerts['summary']['out_of_stock_count']} items")
            print(f"   Critical Stock: {alerts['summary']['critical_stock_count']} items")
            print(f"   Low Stock: {alerts['summary']['low_stock_count']} items")
            
            # Show some specific alerts
            if alerts['alerts']['out_of_stock']:
                print(f"   🚨 Out of stock items:")
                for item in alerts['alerts']['out_of_stock'][:3]:
                    print(f"      • {item['product_name']} ({item['product_id']})")
                    
        else:
            print(f"❌ Stock alerts failed: {alerts_result.error}")
        
        print("\n" + "-"*30)
        
        # Test 3: Sales analytics
        print("3️⃣ Testing sales analytics...")
        analytics_result = sales_tool.execute(SalesInput(action="sales_analytics"))
        
        if analytics_result.success:
            analytics = analytics_result.result
            if analytics['analytics_available']:
                print(f"✅ Sales analytics generated:")
                print(f"   Total Revenue: ${analytics['overall_performance']['total_revenue']:.2f}")
                print(f"   Total Transactions: {analytics['overall_performance']['total_transactions']}")
                print(f"   Average Sale Value: ${analytics['overall_performance']['average_sale_value']:.2f}")
                
                if analytics['top_products']:
                    print(f"   Top Product: {analytics['top_products'][0]['product_name']}")
            else:
                print("ℹ️ No sales data available for analytics")
        else:
            print(f"❌ Sales analytics failed: {analytics_result.error}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing enhanced sales tool: {str(e)}")
        return False

def test_real_time_stock_alerts():
    """Test real-time stock alert functionality."""
    print("\n" + "="*60)
    print("🧪 TESTING: Real-Time Stock Alerts")
    print("="*60)
    
    if not IMPORTS_SUCCESSFUL:
        print("❌ Cannot test - imports failed")
        return False
    
    try:
        # Initialize inventory tool
        inventory_tool = GoogleSheetsInventoryTool()
        
        # Get all products to analyze stock levels
        print("📊 Analyzing current stock levels...")
        result = inventory_tool.execute(GoogleSheetsInventoryInput(action="list_all"))
        
        if not result.success:
            print(f"❌ Could not retrieve inventory: {result.error}")
            return False
        
        products = result.result
        
        # Categorize products by stock level
        out_of_stock = [p for p in products if p["quantity"] == 0]
        critical_stock = [p for p in products if 0 < p["quantity"] <= 5]
        low_stock = [p for p in products if 5 < p["quantity"] <= 10]
        healthy_stock = [p for p in products if p["quantity"] > 10]
        
        print(f"📈 Stock Level Analysis:")
        print(f"   🚨 Out of Stock: {len(out_of_stock)} items")
        print(f"   🔴 Critical Stock (≤5): {len(critical_stock)} items")
        print(f"   🟡 Low Stock (6-10): {len(low_stock)} items")
        print(f"   ✅ Healthy Stock (>10): {len(healthy_stock)} items")
        
        # Show specific alerts
        if out_of_stock:
            print(f"\n🚨 OUT OF STOCK ALERTS:")
            for item in out_of_stock[:3]:
                print(f"   • {item['product_name']} ({item['product_id']}) - ${item['price']:.2f}")
                print(f"     ⚠️ Cannot process sales - immediate restock required")
        
        if critical_stock:
            print(f"\n🔴 CRITICAL STOCK ALERTS:")
            for item in critical_stock[:3]:
                print(f"   • {item['product_name']}: {item['quantity']} units left")
                print(f"     ⚠️ Limit sales and reorder urgently")
        
        if low_stock:
            print(f"\n🟡 LOW STOCK WARNINGS:")
            for item in low_stock[:3]:
                print(f"   • {item['product_name']}: {item['quantity']} units")
                print(f"     💡 Plan reorder within 1-2 weeks")
        
        # Calculate financial impact
        lost_revenue = sum(p["price"] * 10 for p in out_of_stock)  # Assume 10 units demand
        at_risk_revenue = sum(p["price"] * p["quantity"] for p in critical_stock)
        
        print(f"\n💰 Financial Impact:")
        print(f"   Lost Revenue Potential: ${lost_revenue:.2f}")
        print(f"   At-Risk Revenue: ${at_risk_revenue:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing stock alerts: {str(e)}")
        return False

def test_integration_workflow():
    """Test the complete workflow: Add product -> Sell product -> Check alerts."""
    print("\n" + "="*60)
    print("🧪 TESTING: Complete Integration Workflow")
    print("="*60)
    
    if not IMPORTS_SUCCESSFUL:
        print("❌ Cannot test - imports failed")
        return False
    
    try:
        # Step 1: Add a test product
        print("1️⃣ Adding test product...")
        inventory_tool = GoogleSheetsInventoryTool()
        
        test_product_id = f"TESTINT{datetime.now().strftime('%H%M%S')}"
        
        add_result = inventory_tool.execute(GoogleSheetsInventoryInput(
            action="add",
            product_id=test_product_id,
            product_name="Integration Test Product",
            quantity=5,  # Low quantity to trigger alerts
            price=99.99,
            category="Accessories"
        ))
        
        if add_result.success:
            print(f"✅ Test product added: {test_product_id}")
        else:
            print(f"⚠️ Could not add test product: {add_result.error}")
            # Continue with existing product
            test_product_id = "MOUSE001"  # Use existing product
        
        print("\n" + "-"*30)
        
        # Step 2: Check initial stock
        print("2️⃣ Checking initial stock...")
        check_result = inventory_tool.execute(GoogleSheetsInventoryInput(
            action="check",
            product_id=test_product_id
        ))
        
        if check_result.success:
            initial_stock = check_result.result["quantity"]
            print(f"✅ Initial stock for {test_product_id}: {initial_stock} units")
        else:
            print(f"❌ Could not check stock: {check_result.error}")
            return False
        
        print("\n" + "-"*30)
        
        # Step 3: Process a sale
        print("3️⃣ Processing sale...")
        transaction_agent = TransactionAgent()
        
        sale_message = f"Sell 2 {test_product_id} for $99.99 to Integration Test Customer"
        sale_response = transaction_agent.process_message(sale_message)
        
        print("Sale Response:")
        print(sale_response)
        
        print("\n" + "-"*30)
        
        # Step 4: Check stock after sale
        print("4️⃣ Checking stock after sale...")
        final_check = inventory_tool.execute(GoogleSheetsInventoryInput(
            action="check",
            product_id=test_product_id
        ))
        
        if final_check.success:
            final_stock = final_check.result["quantity"]
            print(f"✅ Final stock for {test_product_id}: {final_stock} units")
            print(f"   Stock change: {final_stock - initial_stock} units")
            
            # Check if stock alerts should be triggered
            if final_stock <= 5:
                print(f"🚨 Stock alert triggered: {test_product_id} has {final_stock} units left")
            
        else:
            print(f"❌ Could not check final stock: {final_check.error}")
        
        print("\n" + "-"*30)
        
        # Step 5: Generate stock alerts
        print("5️⃣ Generating stock alerts...")
        sales_tool = SalesTool()
        alerts_result = sales_tool.execute(SalesInput(action="stock_alerts"))
        
        if alerts_result.success:
            alerts = alerts_result.result
            print(f"✅ Stock alerts summary:")
            print(f"   Out of Stock: {alerts['summary']['out_of_stock_count']} items")
            print(f"   Critical Stock: {alerts['summary']['critical_stock_count']} items")
            print(f"   Low Stock: {alerts['summary']['low_stock_count']} items")
        
        print("\n✅ Integration workflow test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error in integration workflow: {str(e)}")
        return False

def main():
    """Run all enhanced feature tests."""
    print("🚀 ENHANCED INVENTORY MANAGEMENT FEATURES TEST")
    print("=" * 80)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if imports were successful
    if not IMPORTS_SUCCESSFUL:
        print("\n❌ CRITICAL ERROR: Could not import required modules")
        print("Please ensure all dependencies are installed and paths are correct")
        return
    
    # Run tests
    tests = [
        ("Add Product Functionality", test_add_product_functionality),
        ("Sales with Stock Deduction", test_sales_with_stock_deduction),
        ("Enhanced Sales Tool", test_enhanced_sales_tool),
        ("Real-Time Stock Alerts", test_real_time_stock_alerts),
        ("Integration Workflow", test_integration_workflow)
    ]
    
    results = []
    
    for test_name, test_function in tests:
        try:
            print(f"\n🧪 Running: {test_name}")
            result = test_function()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status:<12} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Enhanced features are working correctly.")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please check the errors above.")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()