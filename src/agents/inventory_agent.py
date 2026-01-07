"""
Inventory Analysis Agent - Specialized agent for inventory management and analysis.
"""

from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent
from src.tools.google_sheets_inventory_tool import GoogleSheetsInventoryTool, GoogleSheetsInventoryInput


class InventoryAgent(BaseAgent):
    """
    Specialized agent for inventory analysis and management.
    
    This agent can:
    - Analyze stock levels and identify issues
    - Generate inventory reports
    - Recommend actions for low/high stock
    - Monitor inventory health
    """
    
    def __init__(self, spreadsheet_id: str = None):
        # Initialize the Google Sheets inventory tool
        self.inventory_tool = GoogleSheetsInventoryTool(spreadsheet_id=spreadsheet_id)
        
        super().__init__(
            name="inventory_agent",
            description="Specialized agent for inventory analysis, stock monitoring, and management recommendations",
            tools=[self.inventory_tool]
        )
        
        # Inventory thresholds
        self.low_stock_threshold = 10
        self.high_stock_threshold = 100
        self.critical_stock_threshold = 5
    
    def process_message(self, message: str) -> str:
        """Process inventory-related messages."""
        self.conversation_history.append({"role": "user", "content": message})
        
        try:
            # Determine what inventory operation to perform
            operation = self._classify_inventory_request(message)
            
            if operation == "stock_analysis":
                response = self._analyze_stock_levels()
            elif operation == "low_stock_report":
                response = self._generate_low_stock_report()
            elif operation == "inventory_summary":
                response = self._generate_inventory_summary()
            elif operation == "product_check":
                product_id = self._extract_product_id(message)
                response = self._check_specific_product(product_id)
            elif operation == "category_analysis":
                category = self._extract_category(message)
                response = self._analyze_category(category)
            elif operation == "stock_alerts":
                response = self._generate_stock_alerts()
            else:
                response = self._handle_general_inventory_query(message)
                
        except Exception as e:
            response = f"❌ I encountered an error analyzing inventory: {str(e)}"
        
        self.conversation_history.append({"role": "assistant", "content": response})
        return response
    
    def _classify_inventory_request(self, message: str) -> str:
        """Classify the type of inventory request."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['low stock', 'running low', 'reorder']):
            return "low_stock_report"
        elif any(word in message_lower for word in ['summary', 'overview', 'total']):
            return "inventory_summary"
        elif any(word in message_lower for word in ['analyze', 'analysis', 'stock levels']):
            return "stock_analysis"
        elif any(word in message_lower for word in ['check', 'status of', 'how many']):
            return "product_check"
        elif any(word in message_lower for word in ['category', 'electronics', 'audio', 'accessories']):
            return "category_analysis"
        elif any(word in message_lower for word in ['alert', 'warning', 'critical']):
            return "stock_alerts"
        else:
            return "general"
    
    def _analyze_stock_levels(self) -> str:
        """Perform comprehensive stock level analysis."""
        try:
            # Get all products
            result = self.inventory_tool.execute(GoogleSheetsInventoryInput(action="list_all"))
            
            if not result.success:
                return f"❌ Could not retrieve inventory data: {result.error}"
            
            products = result.result
            
            # Analyze stock levels
            analysis = {
                "total_products": len(products),
                "in_stock": 0,
                "low_stock": 0,
                "out_of_stock": 0,
                "critical_stock": 0,
                "high_stock": 0,
                "total_value": 0,
                "categories": {}
            }
            
            low_stock_items = []
            critical_items = []
            high_stock_items = []
            
            for product in products:
                quantity = product["quantity"]
                value = quantity * product["price"]
                analysis["total_value"] += value
                
                # Category tracking
                category = product["category"]
                if category not in analysis["categories"]:
                    analysis["categories"][category] = {"count": 0, "total_quantity": 0, "total_value": 0}
                
                analysis["categories"][category]["count"] += 1
                analysis["categories"][category]["total_quantity"] += quantity
                analysis["categories"][category]["total_value"] += value
                
                # Stock level classification
                if quantity == 0:
                    analysis["out_of_stock"] += 1
                elif quantity <= self.critical_stock_threshold:
                    analysis["critical_stock"] += 1
                    critical_items.append(product)
                elif quantity <= self.low_stock_threshold:
                    analysis["low_stock"] += 1
                    low_stock_items.append(product)
                elif quantity >= self.high_stock_threshold:
                    analysis["high_stock"] += 1
                    high_stock_items.append(product)
                else:
                    analysis["in_stock"] += 1
            
            # Generate report
            report = f"""📊 **INVENTORY STOCK ANALYSIS**
═══════════════════════════════════════

📈 **Overall Statistics:**
• Total Products: {analysis['total_products']}
• Total Inventory Value: ${analysis['total_value']:,.2f}

📊 **Stock Level Distribution:**
• ✅ In Stock (Normal): {analysis['in_stock']} products
• ⚠️ Low Stock (≤{self.low_stock_threshold}): {analysis['low_stock']} products
• 🚨 Critical Stock (≤{self.critical_stock_threshold}): {analysis['critical_stock']} products
• ❌ Out of Stock: {analysis['out_of_stock']} products
• 📦 High Stock (≥{self.high_stock_threshold}): {analysis['high_stock']} products

📂 **Category Breakdown:**"""

            for category, data in analysis["categories"].items():
                report += f"\n• {category}: {data['count']} products, {data['total_quantity']} units, ${data['total_value']:,.2f}"
            
            # Add critical alerts
            if critical_items:
                report += f"\n\n🚨 **CRITICAL STOCK ALERTS:**"
                for item in critical_items:
                    report += f"\n• {item['product_name']} ({item['product_id']}): Only {item['quantity']} left!"
            
            # Add low stock warnings
            if low_stock_items:
                report += f"\n\n⚠️ **LOW STOCK WARNINGS:**"
                for item in low_stock_items[:5]:  # Show top 5
                    report += f"\n• {item['product_name']}: {item['quantity']} units remaining"
                if len(low_stock_items) > 5:
                    report += f"\n• ... and {len(low_stock_items) - 5} more items"
            
            return report
            
        except Exception as e:
            return f"❌ Error during stock analysis: {str(e)}"
    
    def _generate_low_stock_report(self) -> str:
        """Generate a focused low stock report."""
        try:
            result = self.inventory_tool.execute(GoogleSheetsInventoryInput(action="list_all"))
            
            if not result.success:
                return f"❌ Could not retrieve inventory data: {result.error}"
            
            products = result.result
            
            # Filter low stock items
            low_stock_items = []
            critical_items = []
            out_of_stock_items = []
            
            for product in products:
                quantity = product["quantity"]
                if quantity == 0:
                    out_of_stock_items.append(product)
                elif quantity <= self.critical_stock_threshold:
                    critical_items.append(product)
                elif quantity <= self.low_stock_threshold:
                    low_stock_items.append(product)
            
            report = "⚠️ **LOW STOCK REPORT**\n═══════════════════════════\n"
            
            if out_of_stock_items:
                report += f"\n🚨 **OUT OF STOCK ({len(out_of_stock_items)} items):**\n"
                for item in out_of_stock_items:
                    report += f"• {item['product_name']} ({item['product_id']}) - ${item['price']:.2f}\n"
            
            if critical_items:
                report += f"\n🔴 **CRITICAL STOCK ({len(critical_items)} items):**\n"
                for item in critical_items:
                    report += f"• {item['product_name']}: {item['quantity']} left (${item['price']:.2f} each)\n"
            
            if low_stock_items:
                report += f"\n🟡 **LOW STOCK ({len(low_stock_items)} items):**\n"
                for item in low_stock_items:
                    report += f"• {item['product_name']}: {item['quantity']} units (${item['price']:.2f} each)\n"
            
            if not (out_of_stock_items or critical_items or low_stock_items):
                report += "\n✅ **Great news! No low stock issues detected.**\n"
                report += "All products are adequately stocked."
            else:
                # Add recommendations
                report += f"\n💡 **RECOMMENDATIONS:**\n"
                if out_of_stock_items:
                    report += "• Immediately reorder out-of-stock items\n"
                if critical_items:
                    report += "• Urgent reorder needed for critical stock items\n"
                if low_stock_items:
                    report += "• Plan reorders for low stock items within 1-2 weeks\n"
            
            return report
            
        except Exception as e:
            return f"❌ Error generating low stock report: {str(e)}"
    
    def _generate_inventory_summary(self) -> str:
        """Generate a high-level inventory summary."""
        try:
            result = self.inventory_tool.execute(GoogleSheetsInventoryInput(action="list_all"))
            
            if not result.success:
                return f"❌ Could not retrieve inventory data: {result.error}"
            
            products = result.result
            
            # Calculate summary statistics
            total_products = len(products)
            total_quantity = sum(p["quantity"] for p in products)
            total_value = sum(p["quantity"] * p["price"] for p in products)
            avg_price = sum(p["price"] for p in products) / total_products if total_products > 0 else 0
            
            # Category breakdown
            categories = {}
            for product in products:
                cat = product["category"]
                if cat not in categories:
                    categories[cat] = {"count": 0, "quantity": 0, "value": 0}
                categories[cat]["count"] += 1
                categories[cat]["quantity"] += product["quantity"]
                categories[cat]["value"] += product["quantity"] * product["price"]
            
            # Top products by value
            products_by_value = sorted(products, key=lambda x: x["quantity"] * x["price"], reverse=True)
            
            summary = f"""📋 **INVENTORY SUMMARY**
═══════════════════════════════

📊 **Key Metrics:**
• Total Products: {total_products}
• Total Units in Stock: {total_quantity:,}
• Total Inventory Value: ${total_value:,.2f}
• Average Product Price: ${avg_price:.2f}

📂 **By Category:**"""

            for category, data in categories.items():
                percentage = (data["value"] / total_value * 100) if total_value > 0 else 0
                summary += f"\n• {category}: {data['count']} products, ${data['value']:,.2f} ({percentage:.1f}%)"
            
            summary += f"\n\n💰 **Top 5 Products by Value:**"
            for i, product in enumerate(products_by_value[:5], 1):
                value = product["quantity"] * product["price"]
                summary += f"\n{i}. {product['product_name']}: ${value:,.2f} ({product['quantity']} × ${product['price']:.2f})"
            
            return summary
            
        except Exception as e:
            return f"❌ Error generating inventory summary: {str(e)}"
    
    def _check_specific_product(self, product_id: str) -> str:
        """Check status of a specific product."""
        if not product_id:
            return "❌ Please specify a product ID to check."
        
        try:
            result = self.inventory_tool.execute(GoogleSheetsInventoryInput(action="check", product_id=product_id))
            
            if not result.success:
                return f"❌ Product '{product_id}' not found in inventory."
            
            product = result.result
            quantity = product["quantity"]
            total_value = quantity * product["price"]
            
            # Determine status and recommendations
            if quantity == 0:
                status_emoji = "🚨"
                status_text = "OUT OF STOCK"
                recommendation = "Immediate reorder required!"
            elif quantity <= self.critical_stock_threshold:
                status_emoji = "🔴"
                status_text = "CRITICAL STOCK"
                recommendation = "Urgent reorder needed!"
            elif quantity <= self.low_stock_threshold:
                status_emoji = "🟡"
                status_text = "LOW STOCK"
                recommendation = "Consider reordering soon."
            else:
                status_emoji = "✅"
                status_text = "IN STOCK"
                recommendation = "Stock levels are healthy."
            
            report = f"""{status_emoji} **PRODUCT STATUS: {product['product_name']}**
═══════════════════════════════════════

📦 **Product Details:**
• Product ID: {product['product_id']}
• Category: {product['category']}
• Unit Price: ${product['price']:.2f}

📊 **Stock Information:**
• Current Quantity: {quantity} units
• Total Value: ${total_value:.2f}
• Status: {status_text}
• Last Updated: {product.get('last_updated', 'Unknown')}

💡 **Recommendation:** {recommendation}"""

            return report
            
        except Exception as e:
            return f"❌ Error checking product: {str(e)}"
    
    def _analyze_category(self, category: str) -> str:
        """Analyze inventory for a specific category."""
        try:
            result = self.inventory_tool.execute(GoogleSheetsInventoryInput(action="search", category=category))
            
            if not result.success:
                return f"❌ Could not search category: {result.error}"
            
            products = result.result
            
            if not products:
                return f"❌ No products found in category '{category}'"
            
            # Analyze category
            total_products = len(products)
            total_quantity = sum(p["quantity"] for p in products)
            total_value = sum(p["quantity"] * p["price"] for p in products)
            avg_price = sum(p["price"] for p in products) / total_products
            
            # Stock status breakdown
            in_stock = sum(1 for p in products if p["quantity"] > self.low_stock_threshold)
            low_stock = sum(1 for p in products if 0 < p["quantity"] <= self.low_stock_threshold)
            out_of_stock = sum(1 for p in products if p["quantity"] == 0)
            
            report = f"""📂 **CATEGORY ANALYSIS: {category.upper()}**
═══════════════════════════════════════

📊 **Category Overview:**
• Total Products: {total_products}
• Total Units: {total_quantity:,}
• Total Value: ${total_value:,.2f}
• Average Price: ${avg_price:.2f}

📈 **Stock Status:**
• ✅ In Stock: {in_stock} products
• ⚠️ Low Stock: {low_stock} products
• ❌ Out of Stock: {out_of_stock} products

📋 **Product List:**"""

            for product in products:
                status = "✅" if product["quantity"] > self.low_stock_threshold else "⚠️" if product["quantity"] > 0 else "❌"
                report += f"\n{status} {product['product_name']}: {product['quantity']} units @ ${product['price']:.2f}"
            
            return report
            
        except Exception as e:
            return f"❌ Error analyzing category: {str(e)}"
    
    def _generate_stock_alerts(self) -> str:
        """Generate urgent stock alerts."""
        try:
            result = self.inventory_tool.execute(GoogleSheetsInventoryInput(action="list_all"))
            
            if not result.success:
                return f"❌ Could not retrieve inventory data: {result.error}"
            
            products = result.result
            
            # Find urgent items
            urgent_items = []
            for product in products:
                if product["quantity"] <= self.critical_stock_threshold:
                    urgency = "CRITICAL" if product["quantity"] == 0 else "HIGH"
                    urgent_items.append({
                        "product": product,
                        "urgency": urgency,
                        "days_until_stockout": self._estimate_stockout_days(product)
                    })
            
            if not urgent_items:
                return "✅ **NO URGENT STOCK ALERTS**\nAll products have adequate stock levels."
            
            # Sort by urgency
            urgent_items.sort(key=lambda x: (x["urgency"] == "CRITICAL", -x["product"]["quantity"]))
            
            alert = f"🚨 **URGENT STOCK ALERTS ({len(urgent_items)} items)**\n"
            alert += "═══════════════════════════════════════\n"
            
            for item in urgent_items:
                product = item["product"]
                urgency_emoji = "🚨" if item["urgency"] == "CRITICAL" else "⚠️"
                
                alert += f"\n{urgency_emoji} **{product['product_name']}** ({product['product_id']})\n"
                alert += f"   • Current Stock: {product['quantity']} units\n"
                alert += f"   • Unit Price: ${product['price']:.2f}\n"
                alert += f"   • Category: {product['category']}\n"
                alert += f"   • Urgency: {item['urgency']}\n"
            
            alert += f"\n💡 **IMMEDIATE ACTIONS REQUIRED:**\n"
            alert += "• Review and approve emergency purchase orders\n"
            alert += "• Contact suppliers for expedited delivery\n"
            alert += "• Consider alternative products if available\n"
            
            return alert
            
        except Exception as e:
            return f"❌ Error generating stock alerts: {str(e)}"
    
    def _estimate_stockout_days(self, product: Dict[str, Any]) -> int:
        """Estimate days until stockout (simplified calculation)."""
        # This is a simplified estimation - in practice you'd use historical sales data
        quantity = product["quantity"]
        if quantity == 0:
            return 0
        
        # Assume average daily usage based on price (higher price = lower usage)
        price = product["price"]
        if price > 500:
            daily_usage = 0.5  # Expensive items move slowly
        elif price > 100:
            daily_usage = 1.0  # Medium price items
        else:
            daily_usage = 2.0  # Cheaper items move faster
        
        return int(quantity / daily_usage) if daily_usage > 0 else 999
    
    def _extract_product_id(self, message: str) -> str:
        """Extract product ID from message."""
        # Simple extraction - look for patterns like LAPTOP001, PHONE001, etc.
        import re
        pattern = r'\b[A-Z]+\d+\b'
        matches = re.findall(pattern, message.upper())
        return matches[0] if matches else ""
    
    def _extract_category(self, message: str) -> str:
        """Extract category from message."""
        message_lower = message.lower()
        categories = ["electronics", "audio", "accessories"]
        
        for category in categories:
            if category in message_lower:
                return category.title()
        
        return ""
    
    def _handle_general_inventory_query(self, message: str) -> str:
        """Handle general inventory queries."""
        return f"""🤖 **Inventory Agent Ready!**

I can help you with:

📊 **Analysis Commands:**
• "Analyze stock levels" - Complete inventory analysis
• "Show low stock report" - Items needing reorder
• "Generate inventory summary" - High-level overview
• "Show stock alerts" - Urgent items needing attention

🔍 **Product Commands:**
• "Check LAPTOP001" - Status of specific product
• "Analyze Electronics category" - Category breakdown

📈 **What would you like me to analyze?**

Your message: "{message}"
"""