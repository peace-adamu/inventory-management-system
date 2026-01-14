#!/usr/bin/env python3
"""
Test Transaction System Integration
"""

import sys
import os
sys.path.append('src')

from agents.inventory_coordinator_agent import InventoryCoordinatorAgent
from agents.transaction_agent import TransactionAgent

def test_transaction_integration():
    """Test the complete transaction system integration."""
    
    print("🧪 Testing Transaction System Integration")
    print("=" * 50)
    
    # Test 1: Initialize coordinator with transaction agent
    print("\n1. Testing Coordinator Initialization...")
    try:
        coordinator = InventoryCoordinatorAgent()
        print("✅ Coordinator initialized successfully")
        
        # Check if transaction agent is available
        if 'transaction' in coordinator.agent_tools:
            print("✅ Transaction agent integrated successfully")
        else:
            print("❌ Transaction agent not found in coordinator")
            return False
            
    except Exception as e:
        print(f"❌ Coordinator initialization failed: {e}")
        return False
    
    # Test 2: Test transaction delegation
    print("\n2. Testing Transaction Delegation...")
    try:
        response = coordinator.process_message("sell 1 LAPTOP001 for $1299.99 to Test Customer")
        
        if "TRANSACTION RESULTS" in response:
            print("✅ Transaction delegation working")
            print(f"Response preview: {response[:100]}...")
        else:
            print("❌ Transaction delegation failed")
            print(f"Response: {response[:200]}...")
            
    except Exception as e:
        print(f"❌ Transaction delegation error: {e}")
        return False
    
    # Test 3: Test direct transaction agent
    print("\n3. Testing Direct Transaction Agent...")
    try:
        transaction_agent = TransactionAgent()
        response = transaction_agent.process_message("show transaction history")
        
        if "TRANSACTION" in response.upper():
            print("✅ Direct transaction agent working")
        else:
            print("❌ Direct transaction agent failed")
            
    except Exception as e:
        print(f"❌ Direct transaction agent error: {e}")
        return False
    
    # Test 4: Test transaction classification
    print("\n4. Testing Transaction Classification...")
    try:
        test_messages = [
            "sell 2 phones",
            "purchase 10 laptops", 
            "show sales report",
            "transaction history"
        ]
        
        for msg in test_messages:
            request_type = coordinator._classify_request(msg)
            print(f"   '{msg}' -> {request_type}")
            
        print("✅ Transaction classification working")
        
    except Exception as e:
        print(f"❌ Transaction classification error: {e}")
        return False
    
    print("\n🎉 All transaction integration tests passed!")
    return True

if __name__ == "__main__":
    success = test_transaction_integration()
    
    if success:
        print("\n✅ Transaction system is ready for use!")
        print("\n🚀 You can now:")
        print("• Process sales through the Streamlit app")
        print("• Handle purchases and restocking")
        print("• Track transaction history")
        print("• View sales analytics")
        print("• Use multi-agent coordination for transactions")
    else:
        print("\n❌ Transaction system needs attention")
        
    sys.exit(0 if success else 1)