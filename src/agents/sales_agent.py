"""
Sales Agent - Specialized agent for sales operations with automatic stock management.
"""

from typing import Dict, Any, List, Optional
from src.agents.base_agent import BaseAgent
from src.tools.transaction_tool import TransactionTool, TransactionInput
from src.tools.google_sheets_inventory_tool import GoogleSheetsInventoryTool, GoogleSheetsInventoryInput


class SalesAgent(BaseAgent):
    """
    Specialized agent for sales operations.
    
    This agent can:
    - Process sales with automatic stock deduction
    - Check stock availability before sales
    - Generate low stock alerts
    - Track sales performance
    - Handle customer information
    - Process returns and refunds
    """
    
    def __init__(self, spreadsheet_id: str = None):
        # Initialize tools
        self.transaction_tool = TransactionTool(spreadsheet_id=spreadsheet_id)
        self.inventory_tool = GoogleSheetsInventoryTool(spreadsheet_id=spreadsheet_id)
        
        super().__init__(
            name="sales_agent",
            description="Specialized agent for sales processing with automatic inventory management",
            tools=[self.transaction_tool, self.inventory_tool]
        )
        
        # Sales thresholds
        self.low_stock_threshold = 10
        self.critical_stock_threshold = 5
    
    def process_message(self, message: str) -> str:
        """Process sales-related messages."""
        self.conversation_history.append({"role": "user", "content": message})
        
        try:
            # Determine what sales operation to perform
            operation = self._classify_sales_request(message)
            
            if operation == "quick_sale":
                response = self._handle_quick_sale(message)
            elif operation == "check_availability":
                response = self._check_stock_availability(message)
            elif operation == "sales_report":
                response = self._generate_sales_report()
            elif operation == "low_stock_alert":
                response = self._generate_low_stock_alerts()
            elif operation == "return_refund":
                response = self._handle_return_refund(message)
            elif operation == "customer_history":
                response = self._show_customer_history(message)
            else:
                response = self._handle_general_sales_query(message)
                
        except Exception as e:
            response = f"❌ I encountered an error processing the sales request: {str(e)}"
        
        self.conversation_history.append({"role": "assistant", "content": response})
        return response
    
    def _classify_sales_request(self, message: str) -> str:
        """Classify the type of sales request."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['sell', 'sale', 'quick sale', 'process sale']):
            return "quick_sale"
        elif any(word in message_lower for word in ['check stock', 'availability', 'in stock', 'available']):
            return "check_availability"
        elif any(word in message_lower for word in ['sales report', 'sales performance', 'revenue']):
            return "sales_report"
        elif any(word in message_lower for word in ['low stock', 'stock alert', 'running low']):
            return "low_stock_alert"
        elif any(word in message_lower for word in ['return', 'refund', 'cancel sale']):
            return "return_refund"
        elif any(word in message_lower for word in ['customer history', 'customer purchases']):
            return "customer_history"
        else:
            return "general"
    
    def _handle_quick_sale(self, message: str) -> str:
        """Handle quick sale requests with stock validation."""
        try:
            # Extract sale details from message
            import re
            
            # Extract product ID
            product_match = re.search(r'\b([A-Z]+\d+)\b', message.upper())
            product_id = product_match.group(1) if product_match else None
            
            # Extract quantity
            quantity_match = re.search(r'\b(\d+)\s*(?:units?|pieces?|items?)?\b', message)
            quantity = int(quantity_match.group(1)) if quantity_match else 1
            
            # Extract price
            price_match = re.search(r'\$?(\d+(?:\.\d{2})?)', message)
            unit_price = float(price_match.group(1)) if price_match else None
            
            # Extract customer info
            customer_match = re.search(r'(?:to|customer|buyer)\s+([A-Za-z\s\-@.]+)', message, re.IGNORECASE)
            customer_info = customer_match.group(1).strip() if customer_match else None
            
            if not product_id:
                return """💰 **QUICK SALE PROCESSING**

Please provide the product ID for the sale.

**Example formats:**
• "Quick sale: 2 LAPTOP001 for $1299.99"
• "Sell 1 PHONE001 to John Doe"
• "Process sale MOUSE001 quantity 3"

**What product would you like to sell?**"""
            
            # First, check stock availability
            stock_check = self.inventory_tool.execute(GoogleSheetsInventoryInput(action="check", product_id=product_id))
            
            if not stock_check.success:
                return f"❌ **Product Not Found**: {product_id} is not in the inventory system."
            
            product = stock_check.result
            current_stock = product["quantity"]
            
            # Validate stock availability
            if current_stock < quantity:
                return f"""⚠️ **INSUFFICIENT STOCK**

**Product:** {product['product_name']} ({product_id})
**Requested:** {quantity} units
**Available:** {current_stock} units
**Shortage:** {quantity - current_stock} units

**Options:**
1. Reduce quantity to {current_stock} units
2. Restock the product first
3. Check alternative products

**Current Status:** {product['status'].replace('_', ' ').title()}"""
            
            # Use product price if not specified
            if not unit_price:
                unit_price = product["price"]
            
            # Process the sale
            result = self.transaction_tool.execute(TransactionInput(
                action="sale",
                product_id=product_id,
                quantity=quantity,
                unit_price=unit_price,
                customer_info=customer_info,
                notes=f"Quick sale processed: {message[:100]}"
            ))
            
            if result.success:
                sale_data = result.result
                new_stock = sale_data['new_stock']
                
                # Build response with stock alerts
                response = f"""✅ **SALE COMPLETED SUCCESSFULLY**

**📦 Product:** {sale_data['product_name']} ({sale_data['product_id']})
**💰 Sale Details:**
• Quantity Sold: {sale_data['quantity_sold']} units
• Unit Price: ${sale_data['unit_price']:.2f}
• **Total Amount: ${sale_data['total_amount']:.2f}**

**📊 Stock Update:**
• Previous Stock: {sale_data['previous_stock']} units
• **New Stock: {new_stock} units**
• Stock Reduced: -{sale_data['quantity_sold']} units

**👤 Customer:** {sale_data['customer_info'] or 'Walk-in customer'}
**🆔 Transaction ID:** {sale_data['transaction_id']}"""

                # Add stock alerts
                if new_stock == 0:
                    response += f"\n\n🚨 **CRITICAL ALERT**: {product['product_name']} is now OUT OF STOCK!"
                    response += "\n• Immediate reorder required"
                    response += "\n• Consider removing from sales displays"
                elif new_stock <= self.critical_stock_threshold:
                    response += f"\n\n🔴 **CRITICAL STOCK**: Only {new_stock} units left!"
                    response += "\n• Urgent reorder needed"
                elif new_stock <= self.low_stock_threshold:
                    response += f"\n\n🟡 **LOW STOCK WARNING**: {new_stock} units remaining"
                    response += "\n• Plan reorder within 1-2 weeks"
                
                return response
            else:
                return f"❌ **Sale Failed:** {result.error}"
                
        except Exception as e:
            return f"❌ Error processing quick sale: {str(e)}"
    
    def _check_stock_availability(self, message: str) -> str:
        """Check stock availability for products."""
        try:
            import re
            
            # Extract product ID
            product_match = re.search(r'\b([A-Z]+\d+)\b', message.upper())
            product_id = product_match.group(1) if product_match else None
            
            if not product_id:
                return """📦 **STOCK AVAILABILITY CHECK**

Please specify a product ID to check availability.

**Example:**
• "Check stock for LAPTOP001"
• "Is PHONE001 available?"
• "MOUSE001 availability"

**Which product would you like to check?**"""
            
            # Check stock
            result = self.inventory_tool.execute(GoogleSheetsInventoryInput(action="check", product_id=product_id))
            
            if not result.success:
                # If direct check fails, try searching in the full inventory
                list_result = self.inventory_tool.execute(GoogleSheetsInventoryInput(action="list_all"))
                if list_result.success:
                    products = list_result.result
                    product = next((p for p in products if p["product_id"] == product_id), None)
                    if product:
                        result.success = True
                        result.result = product
                    else:
                        return f"❌ **Product Not Found**: {product_id} is not in the inventory system."
                else:
                    return f"❌ **Product Not Found**: {product_id} is not in the inventory system."
            
            product = result.result
            quantity = product["quantity"]
            
            # Determine availability status
            if quantity == 0:
                status_emoji = "🚨"
                status_text = "OUT OF STOCK"
                availability = "Not Available"
                recommendation = "Immediate reorder required"
            elif quantity <= self.critical_stock_threshold:
                status_emoji = "🔴"
                status_text = "CRITICAL STOCK"
                availability = f"Limited ({quantity} units)"
                recommendation = "Urgent reorder needed"
            elif quantity <= self.low_stock_threshold:
                status_emoji = "🟡"
                status_text = "LOW STOCK"
                availability = f"Available ({quantity} units)"
                recommendation = "Consider reordering soon"
            else:
                status_emoji = "✅"
                status_text = "IN STOCK"
                availability = f"Available ({quantity} units)"
                recommendation = "Stock levels are healthy"
            
            return f"""{status_emoji} **STOCK AVAILABILITY: {product['product_name']}**

**📦 Product Details:**
• Product ID: {product['product_id']}
• Category: {product['category']}
• Unit Price: ${product['price']:.2f}

**📊 Availability:**
• Current Stock: {quantity} units
• Status: {status_text}
• Availability: {availability}
• Total Value: ${quantity * product['price']:.2f}

**💡 Recommendation:** {recommendation}

**🛒 Sales Info:**
• Can fulfill orders up to {quantity} units
• Estimated value per unit: ${product['price']:.2f}"""
            
        except Exception as e:
            return f"❌ Error checking stock availability: {str(e)}"
    
    def _generate_sales_report(self) -> str:
        """Generate comprehensive sales report."""
        try:
            # Get transaction data
            result = self.transaction_tool.execute(TransactionInput(action="list_transactions"))
            
            if not result.success:
                return f"❌ Error retrieving sales data: {result.error}"
            
            transactions = result.result
            sales = [t for t in transactions if t["transaction_type"] == "sale"]
            
            if not sales:
                return "📊 **No sales transactions found.**"
            
            # Calculate metrics
            total_revenue = sum(t["total_amount"] for t in sales)
            total_units = sum(abs(t["quantity"]) for t in sales)
            avg_sale_value = total_revenue / len(sales) if sales else 0
            
            # Product performance
            product_performance = {}
            for sale in sales:
                pid = sale["product_id"]
                if pid not in product_performance:
                    product_performance[pid] = {
                        "name": sale["product_name"],
                        "units_sold": 0,
                        "revenue": 0,
                        "transactions": 0
                    }
                product_performance[pid]["units_sold"] += abs(sale["quantity"])
                product_performance[pid]["revenue"] += sale["total_amount"]
                product_performance[pid]["transactions"] += 1
            
            # Sort by revenue
            top_products = sorted(product_performance.items(), key=lambda x: x[1]["revenue"], reverse=True)
            
            # Recent sales
            recent_sales = sorted(sales, key=lambda x: f"{x['date']} {x['time']}", reverse=True)[:5]
            
            report = f"""📊 **COMPREHENSIVE SALES REPORT**
═══════════════════════════════════════

💰 **Overall Performance:**
• Total Sales Transactions: {len(sales)}
• **Total Revenue: ${total_revenue:.2f}**
• Total Units Sold: {total_units:,}
• Average Sale Value: ${avg_sale_value:.2f}

🏆 **Top Performing Products:**"""

            for i, (pid, data) in enumerate(top_products[:5], 1):
                avg_price = data["revenue"] / data["units_sold"] if data["units_sold"] > 0 else 0
                report += f"\n{i}. **{data['name']}** ({pid})"
                report += f"\n   Revenue: ${data['revenue']:.2f} | Units: {data['units_sold']} | Avg Price: ${avg_price:.2f}"
            
            report += f"\n\n📅 **Recent Sales:**"
            for sale in recent_sales:
                report += f"\n• {sale['date']} - {sale['product_name']}: {abs(sale['quantity'])} units @ ${sale['unit_price']:.2f}"
                if sale['customer_info']:
                    report += f" (Customer: {sale['customer_info']})"
            
            return report
            
        except Exception as e:
            return f"❌ Error generating sales report: {str(e)}"
    
    def _generate_low_stock_alerts(self) -> str:
        """Generate low stock alerts for sales team."""
        try:
            # Get all products
            result = self.inventory_tool.execute(GoogleSheetsInventoryInput(action="list_all"))
            
            if not result.success:
                return f"❌ Could not retrieve inventory data: {result.error}"
            
            products = result.result
            
            # Filter products by stock levels
            out_of_stock = [p for p in products if p["quantity"] == 0]
            critical_stock = [p for p in products if 0 < p["quantity"] <= self.critical_stock_threshold]
            low_stock = [p for p in products if self.critical_stock_threshold < p["quantity"] <= self.low_stock_threshold]
            
            report = "🚨 **SALES TEAM STOCK ALERTS**\n"
            report += "═══════════════════════════════════════\n\n"
            
            if out_of_stock:
                report += f"🚨 **OUT OF STOCK - CANNOT SELL ({len(out_of_stock)} items):**\n"
                for item in out_of_stock:
                    report += f"• {item['product_name']} ({item['product_id']}) - ${item['price']:.2f}\n"
                    report += f"  ⚠️ Remove from sales displays immediately\n"
                report += "\n"
            
            if critical_stock:
                report += f"🔴 **CRITICAL STOCK - LIMIT SALES ({len(critical_stock)} items):**\n"
                for item in critical_stock:
                    report += f"• {item['product_name']}: {item['quantity']} left - ${item['price']:.2f}\n"
                    report += f"  ⚠️ Limit to 1 per customer\n"
                report += "\n"
            
            if low_stock:
                report += f"🟡 **LOW STOCK - MONITOR CLOSELY ({len(low_stock)} items):**\n"
                for item in low_stock:
                    report += f"• {item['product_name']}: {item['quantity']} units - ${item['price']:.2f}\n"
                report += "\n"
            
            if not (out_of_stock or critical_stock or low_stock):
                report += "✅ **All products have healthy stock levels!**\n"
                report += "No immediate stock concerns for sales operations.\n"
            else:
                report += "📋 **SALES TEAM ACTIONS:**\n"
                if out_of_stock:
                    report += "• Update displays and remove out-of-stock items\n"
                if critical_stock:
                    report += "• Implement purchase limits for critical stock items\n"
                if low_stock:
                    report += "• Monitor low stock items closely during sales\n"
                report += "• Notify management for urgent restocking\n"
            
            return report
            
        except Exception as e:
            return f"❌ Error generating stock alerts: {str(e)}"
    
    def _handle_return_refund(self, message: str) -> str:
        """Handle return and refund requests."""
        # This is a placeholder for return/refund functionality
        return """🔄 **RETURNS & REFUNDS**

Return and refund processing is not yet implemented.

**For now, please:**
1. Process manual stock adjustment to add returned items back
2. Record refund amount separately
3. Update customer records manually

**Future features will include:**
• Automated return processing
• Refund calculations
• Customer credit management
• Return reason tracking

**Need help with a manual adjustment?**
Ask me to "adjust [PRODUCT_ID] by +[quantity] (returned item)"
"""
    
    def _show_customer_history(self, message: str) -> str:
        """Show customer purchase history."""
        # This is a placeholder for customer history functionality
        return """👤 **CUSTOMER HISTORY**

Customer purchase history tracking is not yet fully implemented.

**Current capabilities:**
• Transaction records include customer information
• Sales reports show recent customer purchases

**Future features will include:**
• Customer purchase history lookup
• Customer loyalty tracking
• Purchase pattern analysis
• Personalized recommendations

**For now, check recent sales in the sales report for customer information.**
"""
    
    def _handle_general_sales_query(self, message: str) -> str:
        """Handle general sales queries."""
        return f"""💰 **Sales Agent Ready!**

I specialize in sales operations with automatic inventory management:

🛒 **Sales Processing:**
• "Quick sale: 2 LAPTOP001 for $1299.99"
• "Sell 1 PHONE001 to John Doe"
• Automatic stock deduction and alerts

📦 **Stock Availability:**
• "Check stock for LAPTOP001"
• "Is PHONE001 available?"
• Real-time availability checking

📊 **Sales Analytics:**
• "Generate sales report"
• "Show sales performance"
• Revenue and product analysis

🚨 **Stock Alerts:**
• "Show low stock alerts"
• "Stock alerts for sales team"
• Critical stock notifications

🎯 **What sales operation can I help you with?**

Your message: "{message}"
"""