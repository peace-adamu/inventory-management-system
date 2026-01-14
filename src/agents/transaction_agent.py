"""
Transaction Agent - Specialized agent for sales, purchases, and inventory transactions.
"""

from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent
from src.tools.transaction_tool import TransactionTool, TransactionInput


class TransactionAgent(BaseAgent):
    """
    Specialized agent for transaction management.
    
    This agent can:
    - Process sales transactions
    - Handle purchase/restock operations
    - Manage stock adjustments
    - Generate transaction reports
    - Track product movement history
    - Provide sales analytics
    """
    
    def __init__(self, spreadsheet_id: str = None):
        # Initialize the transaction tool
        self.transaction_tool = TransactionTool(spreadsheet_id=spreadsheet_id)
        
        super().__init__(
            name="transaction_agent",
            description="Specialized agent for sales, purchases, and inventory transaction management",
            tools=[self.transaction_tool]
        )
    
    def process_message(self, message: str) -> str:
        """Process transaction-related messages."""
        self.conversation_history.append({"role": "user", "content": message})
        
        try:
            # Determine what transaction operation to perform
            operation = self._classify_transaction_request(message)
            
            if operation == "sale":
                response = self._handle_sale_request(message)
            elif operation == "purchase":
                response = self._handle_purchase_request(message)
            elif operation == "adjustment":
                response = self._handle_adjustment_request(message)
            elif operation == "transaction_history":
                response = self._show_transaction_history(message)
            elif operation == "product_history":
                response = self._show_product_history(message)
            elif operation == "daily_summary":
                response = self._generate_daily_summary()
            elif operation == "sales_report":
                response = self._generate_sales_report()
            else:
                response = self._handle_general_transaction_query(message)
                
        except Exception as e:
            response = f"❌ I encountered an error processing the transaction: {str(e)}"
        
        self.conversation_history.append({"role": "assistant", "content": response})
        return response
    
    def _classify_transaction_request(self, message: str) -> str:
        """Classify the type of transaction request."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['sell', 'sale', 'sold', 'customer bought']):
            return "sale"
        elif any(word in message_lower for word in ['buy', 'purchase', 'restock', 'order', 'supplier']):
            return "purchase"
        elif any(word in message_lower for word in ['adjust', 'correction', 'fix stock', 'inventory adjustment']):
            return "adjustment"
        elif any(word in message_lower for word in ['transaction history', 'recent transactions', 'transaction list']):
            return "transaction_history"
        elif any(word in message_lower for word in ['product history', 'movement history', 'track product']):
            return "product_history"
        elif any(word in message_lower for word in ['daily summary', 'today sales', 'daily report']):
            return "daily_summary"
        elif any(word in message_lower for word in ['sales report', 'sales analytics', 'revenue']):
            return "sales_report"
        else:
            return "general"
    
    def _handle_sale_request(self, message: str) -> str:
        """Handle sale transaction requests."""
        # Try to extract sale details from message
        # This is a simplified parser - in production, use more sophisticated NLP
        
        try:
            # Look for patterns like "sell 2 LAPTOP001 for $1299.99 to John Doe"
            import re
            
            # Extract product ID
            product_match = re.search(r'\b([A-Z]+\d+)\b', message.upper())
            product_id = product_match.group(1) if product_match else None
            
            # Extract quantity
            quantity_match = re.search(r'\b(\d+)\s*(?:units?|pieces?|items?)?\b', message)
            quantity = int(quantity_match.group(1)) if quantity_match else None
            
            # Extract price
            price_match = re.search(r'\$?(\d+(?:\.\d{2})?)', message)
            unit_price = float(price_match.group(1)) if price_match else None
            
            # Extract customer info
            customer_match = re.search(r'(?:to|customer|buyer)\s+([A-Za-z\s]+)', message, re.IGNORECASE)
            customer_info = customer_match.group(1).strip() if customer_match else None
            
            if not all([product_id, quantity, unit_price]):
                return """💰 **PROCESS SALE**

To process a sale, I need:
• **Product ID** (e.g., LAPTOP001)
• **Quantity** (number of units)
• **Unit Price** (price per unit)
• **Customer Info** (optional)

**Example formats:**
• "Sell 2 LAPTOP001 for $1299.99 to John Doe"
• "Sale: 1 PHONE001 at $899.99"
• "Customer bought 3 MOUSE001 for $79.99 each"

**What information can you provide?**"""
            
            # Process the sale
            result = self.transaction_tool.execute(TransactionInput(
                action="sale",
                product_id=product_id,
                quantity=quantity,
                unit_price=unit_price,
                customer_info=customer_info,
                notes=f"Sale processed via agent: {message[:100]}"
            ))
            
            if result.success:
                sale_data = result.result
                return f"""✅ **SALE COMPLETED**

**Transaction Details:**
• Transaction ID: {sale_data['transaction_id']}
• Product: {sale_data['product_name']} ({sale_data['product_id']})
• Quantity Sold: {sale_data['quantity_sold']} units
• Unit Price: ${sale_data['unit_price']:.2f}
• **Total Amount: ${sale_data['total_amount']:.2f}**

**Stock Update:**
• Previous Stock: {sale_data['previous_stock']} units
• **New Stock: {sale_data['new_stock']} units**
• Stock Reduced: -{sale_data['quantity_sold']} units

**Customer:** {sale_data['customer_info'] or 'Not specified'}

{sale_data['message']}"""
            else:
                return f"❌ **Sale Failed:** {result.error}"
                
        except Exception as e:
            return f"❌ Error processing sale: {str(e)}"
    
    def _handle_purchase_request(self, message: str) -> str:
        """Handle purchase/restock requests."""
        try:
            import re
            
            # Extract details from message
            product_match = re.search(r'\b([A-Z]+\d+)\b', message.upper())
            product_id = product_match.group(1) if product_match else None
            
            quantity_match = re.search(r'\b(\d+)\s*(?:units?|pieces?|items?)?\b', message)
            quantity = int(quantity_match.group(1)) if quantity_match else None
            
            price_match = re.search(r'\$?(\d+(?:\.\d{2})?)', message)
            unit_price = float(price_match.group(1)) if price_match else None
            
            if not all([product_id, quantity, unit_price]):
                return """📦 **PROCESS PURCHASE/RESTOCK**

To process a purchase, I need:
• **Product ID** (e.g., LAPTOP001)
• **Quantity** (number of units to add)
• **Unit Cost** (cost per unit)

**Example formats:**
• "Purchase 10 LAPTOP001 at $1200 each"
• "Restock 50 MOUSE001 for $60 per unit"
• "Order 25 PHONE001 at $800 each from supplier"

**What are the purchase details?**"""
            
            # Process the purchase
            result = self.transaction_tool.execute(TransactionInput(
                action="purchase",
                product_id=product_id,
                quantity=quantity,
                unit_price=unit_price,
                notes=f"Purchase processed via agent: {message[:100]}"
            ))
            
            if result.success:
                purchase_data = result.result
                return f"""✅ **PURCHASE COMPLETED**

**Transaction Details:**
• Transaction ID: {purchase_data['transaction_id']}
• Product: {purchase_data['product_name']} ({purchase_data['product_id']})
• Quantity Purchased: {purchase_data['quantity_purchased']} units
• Unit Cost: ${purchase_data['unit_price']:.2f}
• **Total Cost: ${purchase_data['total_cost']:.2f}**

**Stock Update:**
• Previous Stock: {purchase_data['previous_stock']} units
• **New Stock: {purchase_data['new_stock']} units**
• Stock Added: +{purchase_data['quantity_purchased']} units

{purchase_data['message']}"""
            else:
                return f"❌ **Purchase Failed:** {result.error}"
                
        except Exception as e:
            return f"❌ Error processing purchase: {str(e)}"
    
    def _handle_adjustment_request(self, message: str) -> str:
        """Handle stock adjustment requests."""
        try:
            import re
            
            # Extract details from message
            product_match = re.search(r'\b([A-Z]+\d+)\b', message.upper())
            product_id = product_match.group(1) if product_match else None
            
            # Look for adjustment amount (can be positive or negative)
            adjustment_match = re.search(r'([+-]?\d+)', message)
            quantity_change = int(adjustment_match.group(1)) if adjustment_match else None
            
            if not all([product_id, quantity_change is not None]):
                return """⚙️ **STOCK ADJUSTMENT**

To process a stock adjustment, I need:
• **Product ID** (e.g., LAPTOP001)
• **Quantity Change** (positive to add, negative to remove)
• **Reason** (optional)

**Example formats:**
• "Adjust LAPTOP001 by +5 units (found extra inventory)"
• "Correct PHONE001 by -2 (damaged items)"
• "Fix MOUSE001 stock: -10 units"

**What adjustment do you need?**"""
            
            # Process the adjustment
            result = self.transaction_tool.execute(TransactionInput(
                action="adjustment",
                product_id=product_id,
                quantity=quantity_change,
                notes=f"Adjustment processed via agent: {message[:100]}"
            ))
            
            if result.success:
                adj_data = result.result
                change_type = "increased" if quantity_change > 0 else "decreased"
                return f"""✅ **STOCK ADJUSTMENT COMPLETED**

**Adjustment Details:**
• Transaction ID: {adj_data['transaction_id']}
• Product: {adj_data['product_name']} ({adj_data['product_id']})
• Adjustment Type: {adj_data['adjustment_type'].title()}
• Quantity Change: {adj_data['quantity_change']:+d} units

**Stock Update:**
• Previous Stock: {adj_data['previous_stock']} units
• **New Stock: {adj_data['new_stock']} units**

{adj_data['message']}"""
            else:
                return f"❌ **Adjustment Failed:** {result.error}"
                
        except Exception as e:
            return f"❌ Error processing adjustment: {str(e)}"
    
    def _show_transaction_history(self, message: str) -> str:
        """Show recent transaction history."""
        try:
            result = self.transaction_tool.execute(TransactionInput(action="list_transactions"))
            
            if result.success:
                transactions = result.result
                
                if not transactions:
                    return "📋 **No transactions found.**"
                
                report = f"📋 **RECENT TRANSACTIONS ({len(transactions)} total)**\n"
                report += "═══════════════════════════════════════\n\n"
                
                for txn in transactions[:10]:  # Show last 10
                    txn_type_emoji = {
                        "sale": "💰",
                        "purchase": "📦", 
                        "adjustment": "⚙️"
                    }.get(txn["transaction_type"], "📄")
                    
                    report += f"{txn_type_emoji} **{txn['transaction_id']}** - {txn['date']} {txn['time']}\n"
                    report += f"   {txn['transaction_type'].title()}: {txn['product_name']} ({txn['product_id']})\n"
                    report += f"   Quantity: {txn['quantity']:+d} units"
                    
                    if txn['transaction_type'] != 'adjustment':
                        report += f" @ ${txn['unit_price']:.2f} = ${txn['total_amount']:.2f}"
                    
                    report += f"\n   Stock: {txn['previous_stock']} → {txn['new_stock']}\n"
                    
                    if txn['customer_info']:
                        report += f"   Customer: {txn['customer_info']}\n"
                    
                    if txn['notes']:
                        report += f"   Notes: {txn['notes']}\n"
                    
                    report += "\n"
                
                if len(transactions) > 10:
                    report += f"... and {len(transactions) - 10} more transactions\n"
                
                return report
            else:
                return f"❌ Error retrieving transactions: {result.error}"
                
        except Exception as e:
            return f"❌ Error showing transaction history: {str(e)}"
    
    def _show_product_history(self, message: str) -> str:
        """Show transaction history for a specific product."""
        try:
            import re
            
            # Extract product ID
            product_match = re.search(r'\b([A-Z]+\d+)\b', message.upper())
            product_id = product_match.group(1) if product_match else None
            
            if not product_id:
                return """📊 **PRODUCT TRANSACTION HISTORY**

Please specify a product ID to view its transaction history.

**Example:**
• "Show history for LAPTOP001"
• "Track PHONE001 movements"
• "MOUSE001 transaction history"

**Which product would you like to track?**"""
            
            result = self.transaction_tool.execute(TransactionInput(
                action="get_product_history",
                product_id=product_id
            ))
            
            if result.success:
                history = result.result
                summary = history["summary"]
                transactions = history["transactions"]
                
                report = f"📊 **PRODUCT HISTORY: {product_id}**\n"
                report += "═══════════════════════════════════════\n\n"
                
                report += f"📈 **Summary Statistics:**\n"
                report += f"• Total Transactions: {history['total_transactions']}\n"
                report += f"• Units Sold: {summary['total_sales']}\n"
                report += f"• Units Purchased: {summary['total_purchases']}\n"
                report += f"• Net Adjustments: {summary['total_adjustments']:+d}\n"
                report += f"• Sales Revenue: ${summary['sales_revenue']:.2f}\n"
                report += f"• Purchase Cost: ${summary['purchase_cost']:.2f}\n"
                report += f"• **Net Profit: ${summary['net_profit']:.2f}**\n\n"
                
                if transactions:
                    report += f"📋 **Recent Transactions:**\n"
                    for txn in transactions[:5]:  # Show last 5
                        txn_type_emoji = {
                            "sale": "💰",
                            "purchase": "📦", 
                            "adjustment": "⚙️"
                        }.get(txn["transaction_type"], "📄")
                        
                        report += f"{txn_type_emoji} {txn['date']} - {txn['transaction_type'].title()}\n"
                        report += f"   Quantity: {txn['quantity']:+d} units"
                        
                        if txn['transaction_type'] != 'adjustment':
                            report += f" @ ${txn['unit_price']:.2f}"
                        
                        report += f"\n   Stock: {txn['previous_stock']} → {txn['new_stock']}\n\n"
                    
                    if len(transactions) > 5:
                        report += f"... and {len(transactions) - 5} more transactions\n"
                
                return report
            else:
                return f"❌ Error retrieving product history: {result.error}"
                
        except Exception as e:
            return f"❌ Error showing product history: {str(e)}"
    
    def _generate_daily_summary(self) -> str:
        """Generate daily transaction summary."""
        try:
            summary = self.transaction_tool.get_daily_summary()
            
            report = f"📅 **DAILY SUMMARY - {summary['date']}**\n"
            report += "═══════════════════════════════════════\n\n"
            
            report += f"📊 **Overview:**\n"
            report += f"• Total Transactions: {summary['total_transactions']}\n\n"
            
            # Sales summary
            sales = summary['sales']
            report += f"💰 **Sales:**\n"
            report += f"• Transactions: {sales['count']}\n"
            report += f"• Units Sold: {sales['units_sold']}\n"
            report += f"• **Revenue: ${sales['total_revenue']:.2f}**\n\n"
            
            # Purchases summary
            purchases = summary['purchases']
            report += f"📦 **Purchases:**\n"
            report += f"• Transactions: {purchases['count']}\n"
            report += f"• Units Purchased: {purchases['units_purchased']}\n"
            report += f"• **Cost: ${purchases['total_cost']:.2f}**\n\n"
            
            # Adjustments summary
            adjustments = summary['adjustments']
            report += f"⚙️ **Adjustments:**\n"
            report += f"• Transactions: {adjustments['count']}\n"
            report += f"• Net Change: {adjustments['net_adjustment']:+d} units\n\n"
            
            # Net summary
            net_profit = sales['total_revenue'] - purchases['total_cost']
            report += f"📈 **Net Results:**\n"
            report += f"• **Gross Profit: ${net_profit:.2f}**\n"
            report += f"• Net Unit Change: {sales['units_sold'] * -1 + purchases['units_purchased'] + adjustments['net_adjustment']:+d}\n"
            
            return report
            
        except Exception as e:
            return f"❌ Error generating daily summary: {str(e)}"
    
    def _generate_sales_report(self) -> str:
        """Generate sales analytics report."""
        try:
            result = self.transaction_tool.execute(TransactionInput(action="list_transactions"))
            
            if not result.success:
                return f"❌ Error retrieving transactions: {result.error}"
            
            transactions = result.result
            sales = [t for t in transactions if t["transaction_type"] == "sale"]
            
            if not sales:
                return "📊 **No sales transactions found.**"
            
            # Calculate analytics
            total_revenue = sum(t["total_amount"] for t in sales)
            total_units = sum(abs(t["quantity"]) for t in sales)
            avg_sale_value = total_revenue / len(sales) if sales else 0
            
            # Product performance
            product_sales = {}
            for sale in sales:
                pid = sale["product_id"]
                if pid not in product_sales:
                    product_sales[pid] = {"units": 0, "revenue": 0, "name": sale["product_name"]}
                product_sales[pid]["units"] += abs(sale["quantity"])
                product_sales[pid]["revenue"] += sale["total_amount"]
            
            # Sort by revenue
            top_products = sorted(product_sales.items(), key=lambda x: x[1]["revenue"], reverse=True)
            
            report = f"📊 **SALES ANALYTICS REPORT**\n"
            report += "═══════════════════════════════════════\n\n"
            
            report += f"💰 **Overall Performance:**\n"
            report += f"• Total Sales: {len(sales)} transactions\n"
            report += f"• **Total Revenue: ${total_revenue:.2f}**\n"
            report += f"• Units Sold: {total_units}\n"
            report += f"• Average Sale Value: ${avg_sale_value:.2f}\n\n"
            
            report += f"🏆 **Top Performing Products:**\n"
            for i, (pid, data) in enumerate(top_products[:5], 1):
                report += f"{i}. **{data['name']}** ({pid})\n"
                report += f"   Revenue: ${data['revenue']:.2f} | Units: {data['units']}\n"
            
            return report
            
        except Exception as e:
            return f"❌ Error generating sales report: {str(e)}"
    
    def _handle_general_transaction_query(self, message: str) -> str:
        """Handle general transaction queries."""
        return f"""💼 **Transaction Agent Ready!**

I can help you with:

💰 **Sales Transactions:**
• "Sell 2 LAPTOP001 for $1299.99 to John Doe"
• "Customer bought 1 PHONE001 at $899.99"
• Process sales and automatically update inventory

📦 **Purchase/Restock:**
• "Purchase 10 LAPTOP001 at $1200 each"
• "Restock 50 MOUSE001 for $60 per unit"
• Add inventory and track costs

⚙️ **Stock Adjustments:**
• "Adjust LAPTOP001 by +5 units (found extra)"
• "Correct PHONE001 by -2 (damaged items)"
• Fix inventory discrepancies

📊 **Reports & Analytics:**
• "Show transaction history"
• "Product history for LAPTOP001"
• "Daily summary"
• "Sales report"

🎯 **What transaction would you like to process?**

Your message: "{message}"
"""