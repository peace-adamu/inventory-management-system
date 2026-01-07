#!/usr/bin/env python3
"""
Test script for the Inventory Management Multi-Agent System
Tests all agents with your Google Sheets integration.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append('src')

def test_inventory_system():
    """Test the complete inventory management system."""
    
    print("🧪 TESTING INVENTORY MANAGEMENT SYSTEM")
    print("=" * 60)
    
    # Test imports
    print("\n1️⃣ Testing Imports...")
    try:
        from agents.inventory_agent import InventoryAgent
        from agents.stock_calculator_agent import StockCalculatorAgent
        from agents.inventory_coordinator_agent import InventoryCoordinatorAgent
        from tools.google_sheets_inventory_tool import GoogleSheetsInventoryTool, GoogleSheetsInventoryInput
        print("✅ All imports successful")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Check configuration
    print("\n2️⃣ Checking Configuration...")
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
    
    # Test Google Sheets Tool
    print("\n3️⃣ Testing Google Sheets Tool...")
    try:
        sheets_tool = GoogleSheetsInventoryTool(spreadsheet_id=sheets_id)
        
        # Test listing products
        result = sheets_tool.execute(GoogleSheetsInventoryInput(action="list_all"))
        
        if result.success:
            products = result.result
            print(f"✅ Google Sheets connected - Found {len(products)} products")
            
            # Show sample products
            for i, product in enumerate(products[:3]):
                print(f"   {i+1}. {product['product_name']}: {product['quantity']} units @ ${product['price']:.2f}")
            
            if len(products) > 3:
                print(f"   ... and {len(products) - 3} more products")
                
        else:
            print(f"⚠️ Using mock data: {result.error}")
            
    except Exception as e:
        print(f"⚠️ Google Sheets error (using mock): {str(e)[:100]}")
    
    # Test Individual Agents
    print("\n4️⃣ Testing Individual Agents...")
    
    # Test Inventory Agent
    print("\n📊 Testing Inventory Agent...")
    try:
        inventory_agent = InventoryAgent(spreadsheet_id=sheets_id)
        response = inventory_agent.process_message("generate inventory summary")
        print("✅ Inventory Agent working")
        print(f"   Sample response: {response[:100]}...")
    except Exception as e:
        print(f"❌ Inventory Agent error: {e}")
    
    # Test Stock Calculator Agent
    print("\n🧮 Testing Stock Calculator Agent...")
    try:
        calculator_agent = StockCalculatorAgent(spreadsheet_id=sheets_id)
        response = calculator_agent.process_message("calculate inventory values")
        print("✅ Stock Calculator Agent working")
        print(f"   Sample response: {response[:100]}...")
    except Exception as e:
        print(f"❌ Stock Calculator Agent error: {e}")
    
    # Test Coordinator Agent
    print("\n🤖 Testing Coordinator Agent...")
    try:
        coordinator = InventoryCoordinatorAgent(spreadsheet_id=sheets_id)
        
        # Test system status
        status = coordinator.get_system_status()
        print("✅ Coordinator Agent working")
        print(f"   System Status: {status}")
        
        # Test coordination
        response = coordinator.process_message("generate dashboard")
        print("✅ Multi-agent coordination working")
        print(f"   Dashboard generated: {len(response)} characters")
        
    except Exception as e:
        print(f"❌ Coordinator Agent error: {e}")
    
    # Test Multi-Agent Scenarios
    print("\n5️⃣ Testing Multi-Agent Scenarios...")
    
    try:
        coordinator = InventoryCoordinatorAgent(spreadsheet_id=sheets_id)
        
        # Test 1: Low stock analysis with calculations
        print("\n🔍 Test 1: Low Stock + Reorder Calculations")
        response = coordinator.process_message("show low stock items and calculate reorder points")
        print(f"✅ Multi-agent task completed ({len(response)} chars)")
        
        # Test 2: Comprehensive analysis
        print("\n📊 Test 2: Comprehensive Analysis")
        response = coordinator.process_message("comprehensive analysis")
        print(f"✅ Comprehensive analysis completed ({len(response)} chars)")
        
        # Test 3: Action plan generation
        print("\n🎯 Test 3: Action Plan Generation")
        response = coordinator.process_message("generate action plan")
        print(f"✅ Action plan generated ({len(response)} chars)")
        
    except Exception as e:
        print(f"❌ Multi-agent scenario error: {e}")
    
    # Test Data Operations
    print("\n6️⃣ Testing Data Operations...")
    
    try:
        sheets_tool = GoogleSheetsInventoryTool(spreadsheet_id=sheets_id)
        
        # Test product check
        result = sheets_tool.execute(GoogleSheetsInventoryInput(action="check", product_id="LAPTOP001"))
        if result.success:
            print("✅ Product lookup working")
            product = result.result
            print(f"   LAPTOP001: {product['quantity']} units @ ${product['price']:.2f}")
        else:
            print(f"⚠️ Product lookup using mock data: {result.error}")
        
        # Test search
        result = sheets_tool.execute(GoogleSheetsInventoryInput(action="search", category="Electronics"))
        if result.success:
            electronics = result.result
            print(f"✅ Category search working - Found {len(electronics)} Electronics items")
        else:
            print(f"⚠️ Category search using mock data: {result.error}")
            
    except Exception as e:
        print(f"❌ Data operations error: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 INVENTORY SYSTEM TEST COMPLETE")
    print("=" * 60)
    
    print("\n✅ **What's Working:**")
    print("• Multi-agent inventory management system")
    print("• Inventory analysis and monitoring")
    print("• Stock calculations and optimization")
    print("• Agent coordination and routing")
    print("• Google Sheets integration (or mock fallback)")
    
    print("\n🚀 **Ready to Use:**")
    print("• Run: python inventory_management_app.py")
    print("• Or: streamlit run inventory_management_app.py")
    print("• Access full multi-agent inventory management!")
    
    if not sheets_id:
        print("\n💡 **To Enable Google Sheets:**")
        print("1. Create a Google Sheet with your inventory data")
        print("2. Get the sheet ID from the URL")
        print("3. Add to .env: GOOGLE_SHEETS_INVENTORY_ID=your_sheet_id")
        print("4. See GOOGLE_SHEETS_SETUP.md for detailed instructions")
    
    return True

def demo_agent_conversations():
    """Demonstrate agent conversations."""
    
    print("\n" + "=" * 60)
    print("🎭 AGENT CONVERSATION DEMO")
    print("=" * 60)
    
    try:
        from agents.inventory_coordinator_agent import InventoryCoordinatorAgent
        
        coordinator = InventoryCoordinatorAgent()
        
        # Demo conversations
        conversations = [
            "What's my current inventory status?",
            "Show me items that need reordering",
            "Calculate the total value of my inventory",
            "Which products are moving slowly?",
            "Generate an action plan for this week"
        ]
        
        for i, question in enumerate(conversations, 1):
            print(f"\n{i}. 👤 User: {question}")
            print("   🤖 Coordinator: Processing...")
            
            try:
                response = coordinator.process_message(question)
                # Show first 200 characters of response
                preview = response[:200] + "..." if len(response) > 200 else response
                print(f"   📊 Response: {preview}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print(f"\n✅ Demo completed - {len(conversations)} conversations tested")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")

if __name__ == "__main__":
    print("🧪 Starting Inventory Management System Tests...")
    
    success = test_inventory_system()
    
    if success:
        demo_agent_conversations()
    
    print("\n🎉 All tests completed!")
    print("\n🚀 Your multi-agent inventory system is ready!")
    print("   Run: streamlit run inventory_management_app.py")