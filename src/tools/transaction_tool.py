"""
Transaction Management Tool - Handles sales, purchases, and stock movements.
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from src.tools.base_tool import BaseTool, ToolInput, ToolOutput
from src.tools.google_sheets_inventory_tool import GoogleSheetsInventoryTool, GoogleSheetsInventoryInput


class TransactionInput(ToolInput):
    """Input schema for transaction operations."""
    action: str = Field(description="Action: 'sale', 'purchase', 'adjustment', 'list_transactions', 'get_product_history'")
    product_id: Optional[str] = Field(default=None, description="Product ID for the transaction")
    quantity: Optional[int] = Field(default=None, description="Quantity (positive for purchase/adjustment in, negative for sale/adjustment out)")
    unit_price: Optional[float] = Field(default=None, description="Unit price for the transaction")
    transaction_type: Optional[str] = Field(default=None, description="Type: 'sale', 'purchase', 'adjustment'")
    notes: Optional[str] = Field(default=None, description="Additional notes for the transaction")
    customer_info: Optional[str] = Field(default=None, description="Customer information for sales")


class TransactionTool(BaseTool):
    """
    Transaction management tool for inventory operations.
    
    Handles:
    - Sales transactions (reduces stock)
    - Purchase transactions (increases stock)
    - Stock adjustments (corrections)
    - Transaction history tracking
    - Automatic inventory updates
    """
    
    def __init__(self, spreadsheet_id: Optional[str] = None):
        super().__init__(
            name="transaction_tool",
            description="Manage sales, purchases, and stock movements with automatic inventory updates"
        )
        
        self.spreadsheet_id = spreadsheet_id or os.getenv("GOOGLE_SHEETS_INVENTORY_ID")
        self.inventory_tool = GoogleSheetsInventoryTool(spreadsheet_id=self.spreadsheet_id)
        
        # Transaction headers for Google Sheets
        self.transaction_headers = [
            "Transaction ID", "Date", "Time", "Product ID", "Product Name", 
            "Transaction Type", "Quantity", "Unit Price", "Total Amount", 
            "Previous Stock", "New Stock", "Customer Info", "Notes", "Status"
        ]
        
        # In-memory transaction storage (for demo - in production use database)
        self.transactions = []
        self._transaction_counter = 1000
    
    def execute(self, input_data: TransactionInput) -> ToolOutput:
        """Execute transaction operations."""
        try:
            if input_data.action == "sale":
                result = self._process_sale(
                    input_data.product_id,
                    input_data.quantity,
                    input_data.unit_price,
                    input_data.customer_info,
                    input_data.notes
                )
            elif input_data.action == "purchase":
                result = self._process_purchase(
                    input_data.product_id,
                    input_data.quantity,
                    input_data.unit_price,
                    input_data.notes
                )
            elif input_data.action == "adjustment":
                result = self._process_adjustment(
                    input_data.product_id,
                    input_data.quantity,
                    input_data.notes
                )
            elif input_data.action == "list_transactions":
                result = self._list_transactions()
            elif input_data.action == "get_product_history":
                result = self._get_product_history(input_data.product_id)
            else:
                return ToolOutput(success=False, result=None, error=f"Unknown action: {input_data.action}")
            
            return ToolOutput(success=True, result=result)
            
        except Exception as e:
            return ToolOutput(success=False, result=None, error=str(e))
    
    def _process_sale(self, product_id: str, quantity: int, unit_price: float, customer_info: str = None, notes: str = None) -> Dict[str, Any]:
        """Process a sale transaction."""
        if not all([product_id, quantity, unit_price]):
            raise ValueError("Product ID, quantity, and unit price are required for sales")
        
        if quantity <= 0:
            raise ValueError("Sale quantity must be positive")
        
        # Get current product info
        product_result = self.inventory_tool.execute(GoogleSheetsInventoryInput(action="check", product_id=product_id))
        
        if not product_result.success:
            raise ValueError(f"Product {product_id} not found: {product_result.error}")
        
        product = product_result.result
        current_stock = product["quantity"]
        
        # Check if enough stock available
        if current_stock < quantity:
            raise ValueError(f"Insufficient stock. Available: {current_stock}, Requested: {quantity}")
        
        # Calculate new stock level
        new_stock = current_stock - quantity
        
        # Update inventory
        update_result = self.inventory_tool.execute(GoogleSheetsInventoryInput(
            action="update",
            product_id=product_id,
            quantity=new_stock
        ))
        
        if not update_result.success:
            raise ValueError(f"Failed to update inventory: {update_result.error}")
        
        # Create transaction record
        transaction = self._create_transaction_record(
            product_id=product_id,
            product_name=product["product_name"],
            transaction_type="sale",
            quantity=-quantity,  # Negative for sales
            unit_price=unit_price,
            previous_stock=current_stock,
            new_stock=new_stock,
            customer_info=customer_info,
            notes=notes
        )
        
        return {
            "transaction_id": transaction["transaction_id"],
            "product_id": product_id,
            "product_name": product["product_name"],
            "quantity_sold": quantity,
            "unit_price": unit_price,
            "total_amount": quantity * unit_price,
            "previous_stock": current_stock,
            "new_stock": new_stock,
            "customer_info": customer_info,
            "status": "completed",
            "message": f"Sale completed: {quantity} units of {product['product_name']} sold for ${quantity * unit_price:.2f}"
        }
    
    def _process_purchase(self, product_id: str, quantity: int, unit_price: float, notes: str = None) -> Dict[str, Any]:
        """Process a purchase/restock transaction."""
        if not all([product_id, quantity, unit_price]):
            raise ValueError("Product ID, quantity, and unit price are required for purchases")
        
        if quantity <= 0:
            raise ValueError("Purchase quantity must be positive")
        
        # Get current product info
        product_result = self.inventory_tool.execute(GoogleSheetsInventoryInput(action="check", product_id=product_id))
        
        if not product_result.success:
            raise ValueError(f"Product {product_id} not found: {product_result.error}")
        
        product = product_result.result
        current_stock = product["quantity"]
        
        # Calculate new stock level
        new_stock = current_stock + quantity
        
        # Update inventory
        update_result = self.inventory_tool.execute(GoogleSheetsInventoryInput(
            action="update",
            product_id=product_id,
            quantity=new_stock
        ))
        
        if not update_result.success:
            raise ValueError(f"Failed to update inventory: {update_result.error}")
        
        # Create transaction record
        transaction = self._create_transaction_record(
            product_id=product_id,
            product_name=product["product_name"],
            transaction_type="purchase",
            quantity=quantity,  # Positive for purchases
            unit_price=unit_price,
            previous_stock=current_stock,
            new_stock=new_stock,
            notes=notes
        )
        
        return {
            "transaction_id": transaction["transaction_id"],
            "product_id": product_id,
            "product_name": product["product_name"],
            "quantity_purchased": quantity,
            "unit_price": unit_price,
            "total_cost": quantity * unit_price,
            "previous_stock": current_stock,
            "new_stock": new_stock,
            "status": "completed",
            "message": f"Purchase completed: {quantity} units of {product['product_name']} added for ${quantity * unit_price:.2f}"
        }
    
    def _process_adjustment(self, product_id: str, quantity_change: int, notes: str = None) -> Dict[str, Any]:
        """Process a stock adjustment (correction)."""
        if not all([product_id, quantity_change is not None]):
            raise ValueError("Product ID and quantity change are required for adjustments")
        
        # Get current product info
        product_result = self.inventory_tool.execute(GoogleSheetsInventoryInput(action="check", product_id=product_id))
        
        if not product_result.success:
            raise ValueError(f"Product {product_id} not found: {product_result.error}")
        
        product = product_result.result
        current_stock = product["quantity"]
        
        # Calculate new stock level
        new_stock = max(0, current_stock + quantity_change)  # Ensure stock doesn't go negative
        
        # Update inventory
        update_result = self.inventory_tool.execute(GoogleSheetsInventoryInput(
            action="update",
            product_id=product_id,
            quantity=new_stock
        ))
        
        if not update_result.success:
            raise ValueError(f"Failed to update inventory: {update_result.error}")
        
        # Create transaction record
        transaction = self._create_transaction_record(
            product_id=product_id,
            product_name=product["product_name"],
            transaction_type="adjustment",
            quantity=quantity_change,
            unit_price=0,  # No price for adjustments
            previous_stock=current_stock,
            new_stock=new_stock,
            notes=notes or "Stock adjustment"
        )
        
        adjustment_type = "increase" if quantity_change > 0 else "decrease"
        
        return {
            "transaction_id": transaction["transaction_id"],
            "product_id": product_id,
            "product_name": product["product_name"],
            "adjustment_type": adjustment_type,
            "quantity_change": quantity_change,
            "previous_stock": current_stock,
            "new_stock": new_stock,
            "status": "completed",
            "message": f"Stock adjustment: {product['product_name']} {adjustment_type} by {abs(quantity_change)} units"
        }
    
    def _create_transaction_record(self, product_id: str, product_name: str, transaction_type: str, 
                                 quantity: int, unit_price: float, previous_stock: int, new_stock: int,
                                 customer_info: str = None, notes: str = None) -> Dict[str, Any]:
        """Create a transaction record."""
        now = datetime.now()
        transaction_id = f"TXN{self._transaction_counter:06d}"
        self._transaction_counter += 1
        
        transaction = {
            "transaction_id": transaction_id,
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "product_id": product_id,
            "product_name": product_name,
            "transaction_type": transaction_type,
            "quantity": quantity,
            "unit_price": unit_price,
            "total_amount": abs(quantity) * unit_price,
            "previous_stock": previous_stock,
            "new_stock": new_stock,
            "customer_info": customer_info or "",
            "notes": notes or "",
            "status": "completed"
        }
        
        # Store transaction (in production, save to database or Google Sheets)
        self.transactions.append(transaction)
        
        return transaction
    
    def _list_transactions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent transactions."""
        # Sort by date/time descending (most recent first)
        sorted_transactions = sorted(
            self.transactions, 
            key=lambda x: f"{x['date']} {x['time']}", 
            reverse=True
        )
        
        return sorted_transactions[:limit]
    
    def _get_product_history(self, product_id: str) -> Dict[str, Any]:
        """Get transaction history for a specific product."""
        if not product_id:
            raise ValueError("Product ID is required")
        
        # Filter transactions for this product
        product_transactions = [
            t for t in self.transactions 
            if t["product_id"] == product_id
        ]
        
        # Sort by date/time descending
        product_transactions.sort(
            key=lambda x: f"{x['date']} {x['time']}", 
            reverse=True
        )
        
        # Calculate summary statistics
        total_sales = sum(abs(t["quantity"]) for t in product_transactions if t["transaction_type"] == "sale")
        total_purchases = sum(t["quantity"] for t in product_transactions if t["transaction_type"] == "purchase")
        total_adjustments = sum(t["quantity"] for t in product_transactions if t["transaction_type"] == "adjustment")
        
        sales_revenue = sum(t["total_amount"] for t in product_transactions if t["transaction_type"] == "sale")
        purchase_cost = sum(t["total_amount"] for t in product_transactions if t["transaction_type"] == "purchase")
        
        return {
            "product_id": product_id,
            "total_transactions": len(product_transactions),
            "summary": {
                "total_sales": total_sales,
                "total_purchases": total_purchases,
                "total_adjustments": total_adjustments,
                "sales_revenue": sales_revenue,
                "purchase_cost": purchase_cost,
                "net_profit": sales_revenue - purchase_cost
            },
            "transactions": product_transactions
        }
    
    def get_daily_summary(self, date: str = None) -> Dict[str, Any]:
        """Get daily transaction summary."""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        daily_transactions = [t for t in self.transactions if t["date"] == date]
        
        sales = [t for t in daily_transactions if t["transaction_type"] == "sale"]
        purchases = [t for t in daily_transactions if t["transaction_type"] == "purchase"]
        adjustments = [t for t in daily_transactions if t["transaction_type"] == "adjustment"]
        
        return {
            "date": date,
            "total_transactions": len(daily_transactions),
            "sales": {
                "count": len(sales),
                "total_revenue": sum(t["total_amount"] for t in sales),
                "units_sold": sum(abs(t["quantity"]) for t in sales)
            },
            "purchases": {
                "count": len(purchases),
                "total_cost": sum(t["total_amount"] for t in purchases),
                "units_purchased": sum(t["quantity"] for t in purchases)
            },
            "adjustments": {
                "count": len(adjustments),
                "net_adjustment": sum(t["quantity"] for t in adjustments)
            }
        }
    
    def _get_input_schema(self) -> Dict[str, Any]:
        """Get the input schema for this tool."""
        return TransactionInput.model_json_schema()


# Example usage and testing
if __name__ == "__main__":
    print("📊 Transaction Tool Test")
    print("=" * 50)
    
    # Initialize transaction tool
    transaction_tool = TransactionTool()
    
    # Test sale transaction
    print("\n1. Testing Sale Transaction:")
    sale_result = transaction_tool.execute(TransactionInput(
        action="sale",
        product_id="LAPTOP001",
        quantity=2,
        unit_price=1299.99,
        customer_info="John Doe - john@example.com",
        notes="Online order #12345"
    ))
    
    if sale_result.success:
        print("✅ Sale completed:")
        print(f"   {sale_result.result}")
    else:
        print(f"❌ Sale failed: {sale_result.error}")
    
    # Test purchase transaction
    print("\n2. Testing Purchase Transaction:")
    purchase_result = transaction_tool.execute(TransactionInput(
        action="purchase",
        product_id="LAPTOP001",
        quantity=10,
        unit_price=1200.00,
        notes="Restock from supplier ABC"
    ))
    
    if purchase_result.success:
        print("✅ Purchase completed:")
        print(f"   {purchase_result.result}")
    else:
        print(f"❌ Purchase failed: {purchase_result.error}")
    
    # List transactions
    print("\n3. Recent Transactions:")
    transactions_result = transaction_tool.execute(TransactionInput(action="list_transactions"))
    
    if transactions_result.success:
        transactions = transactions_result.result
        print(f"✅ Found {len(transactions)} transactions")
        for txn in transactions[:3]:  # Show first 3
            print(f"   {txn['transaction_id']}: {txn['transaction_type']} - {txn['product_name']} ({txn['quantity']} units)")
    else:
        print(f"❌ Failed to list transactions: {transactions_result.error}")