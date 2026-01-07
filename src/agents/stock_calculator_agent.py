"""
Stock Calculator Agent - Specialized agent for inventory calculations and analytics.
"""

from typing import Dict, Any, List, Tuple
from src.agents.base_agent import BaseAgent
from src.tools.google_sheets_inventory_tool import GoogleSheetsInventoryTool, GoogleSheetsInventoryInput
from src.tools.calculator_tool import CalculatorTool, CalculatorInput
import math


class StockCalculatorAgent(BaseAgent):
    """
    Specialized agent for inventory calculations and financial analytics.
    
    This agent can:
    - Calculate reorder points and quantities
    - Analyze inventory turnover rates
    - Calculate total inventory values
    - Determine optimal stock levels
    - Generate financial reports
    """
    
    def __init__(self, spreadsheet_id: str = None):
        # Initialize tools
        self.inventory_tool = GoogleSheetsInventoryTool(spreadsheet_id=spreadsheet_id)
        self.calculator_tool = CalculatorTool()
        
        super().__init__(
            name="stock_calculator_agent",
            description="Specialized agent for inventory calculations, reorder points, and financial analytics",
            tools=[self.inventory_tool, self.calculator_tool]
        )
        
        # Default business parameters (can be customized)
        self.lead_time_days = 7  # Days to receive new stock
        self.safety_stock_days = 3  # Extra days of stock for safety
        self.target_service_level = 0.95  # 95% service level
        self.carrying_cost_rate = 0.20  # 20% annual carrying cost
    
    def process_message(self, message: str) -> str:
        """Process stock calculation requests."""
        self.conversation_history.append({"role": "user", "content": message})
        
        try:
            # Determine what calculation to perform
            calculation_type = self._classify_calculation_request(message)
            
            if calculation_type == "reorder_points":
                response = self._calculate_reorder_points()
            elif calculation_type == "inventory_value":
                response = self._calculate_inventory_values()
            elif calculation_type == "turnover_analysis":
                response = self._analyze_inventory_turnover()
            elif calculation_type == "optimal_stock":
                response = self._calculate_optimal_stock_levels()
            elif calculation_type == "financial_report":
                response = self._generate_financial_report()
            elif calculation_type == "product_calculation":
                product_id = self._extract_product_id(message)
                response = self._calculate_product_metrics(product_id)
            elif calculation_type == "category_calculation":
                category = self._extract_category(message)
                response = self._calculate_category_metrics(category)
            elif calculation_type == "abc_analysis":
                response = self._perform_abc_analysis()
            else:
                response = self._handle_general_calculation_query(message)
                
        except Exception as e:
            response = f"❌ I encountered an error during calculations: {str(e)}"
        
        self.conversation_history.append({"role": "assistant", "content": response})
        return response
    
    def _classify_calculation_request(self, message: str) -> str:
        """Classify the type of calculation request."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['reorder', 'reorder point', 'when to order']):
            return "reorder_points"
        elif any(word in message_lower for word in ['inventory value', 'total value', 'worth']):
            return "inventory_value"
        elif any(word in message_lower for word in ['turnover', 'rotation', 'velocity']):
            return "turnover_analysis"
        elif any(word in message_lower for word in ['optimal', 'best stock', 'recommended']):
            return "optimal_stock"
        elif any(word in message_lower for word in ['financial report', 'financial', 'profit']):
            return "financial_report"
        elif any(word in message_lower for word in ['calculate', 'metrics']) and any(word in message_lower for word in ['product', 'item']):
            return "product_calculation"
        elif any(word in message_lower for word in ['category', 'electronics', 'audio', 'accessories']):
            return "category_calculation"
        elif any(word in message_lower for word in ['abc', 'abc analysis', 'pareto']):
            return "abc_analysis"
        else:
            return "general"
    
    def _calculate_reorder_points(self) -> str:
        """Calculate reorder points for all products."""
        try:
            result = self.inventory_tool.execute(GoogleSheetsInventoryInput(action="list_all"))
            
            if not result.success:
                return f"❌ Could not retrieve inventory data: {result.error}"
            
            products = result.result
            reorder_calculations = []
            
            for product in products:
                # Estimate daily demand (simplified - in practice use historical data)
                daily_demand = self._estimate_daily_demand(product)
                
                # Calculate reorder point: (Lead time × Daily demand) + Safety stock
                lead_time_demand = daily_demand * self.lead_time_days
                safety_stock = daily_demand * self.safety_stock_days
                reorder_point = lead_time_demand + safety_stock
                
                # Calculate economic order quantity (EOQ)
                eoq = self._calculate_eoq(product, daily_demand * 365)  # Annual demand
                
                # Determine if reorder is needed
                current_stock = product["quantity"]
                needs_reorder = current_stock <= reorder_point
                
                reorder_calculations.append({
                    "product": product,
                    "daily_demand": daily_demand,
                    "reorder_point": reorder_point,
                    "eoq": eoq,
                    "current_stock": current_stock,
                    "needs_reorder": needs_reorder,
                    "shortage": max(0, reorder_point - current_stock) if needs_reorder else 0
                })
            
            # Sort by urgency (most urgent first)
            reorder_calculations.sort(key=lambda x: (-x["shortage"], x["needs_reorder"]))
            
            # Generate report
            report = f"""📊 **REORDER POINT CALCULATIONS**
═══════════════════════════════════════

⚙️ **Parameters Used:**
• Lead Time: {self.lead_time_days} days
• Safety Stock: {self.safety_stock_days} days
• Service Level: {self.target_service_level*100:.0f}%

🔄 **Reorder Recommendations:**
"""
            
            urgent_reorders = [calc for calc in reorder_calculations if calc["needs_reorder"]]
            
            if urgent_reorders:
                report += f"\n🚨 **URGENT REORDERS NEEDED ({len(urgent_reorders)} items):**\n"
                for calc in urgent_reorders:
                    product = calc["product"]
                    shortage = calc["shortage"]
                    eoq = calc["eoq"]
                    
                    report += f"\n• **{product['product_name']}** ({product['product_id']})\n"
                    report += f"  Current Stock: {calc['current_stock']} units\n"
                    report += f"  Reorder Point: {calc['reorder_point']:.0f} units\n"
                    report += f"  Shortage: {shortage:.0f} units\n"
                    report += f"  Recommended Order: {eoq:.0f} units\n"
                    report += f"  Order Cost: ${eoq * product['price']:,.2f}\n"
            
            # Show products with healthy stock
            healthy_stock = [calc for calc in reorder_calculations if not calc["needs_reorder"]]
            if healthy_stock:
                report += f"\n✅ **HEALTHY STOCK LEVELS ({len(healthy_stock)} items):**\n"
                for calc in healthy_stock[:5]:  # Show first 5
                    product = calc["product"]
                    days_until_reorder = (calc["current_stock"] - calc["reorder_point"]) / calc["daily_demand"]
                    report += f"• {product['product_name']}: {days_until_reorder:.0f} days until reorder\n"
                
                if len(healthy_stock) > 5:
                    report += f"• ... and {len(healthy_stock) - 5} more items with healthy stock\n"
            
            # Summary calculations
            total_reorder_cost = sum(calc["eoq"] * calc["product"]["price"] for calc in urgent_reorders)
            report += f"\n💰 **FINANCIAL SUMMARY:**\n"
            report += f"• Total Reorder Investment: ${total_reorder_cost:,.2f}\n"
            report += f"• Items Needing Reorder: {len(urgent_reorders)}\n"
            report += f"• Items with Healthy Stock: {len(healthy_stock)}\n"
            
            return report
            
        except Exception as e:
            return f"❌ Error calculating reorder points: {str(e)}"
    
    def _calculate_inventory_values(self) -> str:
        """Calculate comprehensive inventory values."""
        try:
            result = self.inventory_tool.execute(GoogleSheetsInventoryInput(action="list_all"))
            
            if not result.success:
                return f"❌ Could not retrieve inventory data: {result.error}"
            
            products = result.result
            
            # Calculate various inventory values
            total_units = sum(p["quantity"] for p in products)
            total_value = sum(p["quantity"] * p["price"] for p in products)
            
            # Category breakdown
            category_values = {}
            for product in products:
                category = product["category"]
                if category not in category_values:
                    category_values[category] = {"units": 0, "value": 0, "products": 0}
                
                category_values[category]["units"] += product["quantity"]
                category_values[category]["value"] += product["quantity"] * product["price"]
                category_values[category]["products"] += 1
            
            # Calculate carrying costs
            annual_carrying_cost = total_value * self.carrying_cost_rate
            monthly_carrying_cost = annual_carrying_cost / 12
            
            # Find most/least valuable items
            products_by_value = sorted(products, key=lambda x: x["quantity"] * x["price"], reverse=True)
            
            report = f"""💰 **INVENTORY VALUE ANALYSIS**
═══════════════════════════════════════

📊 **Total Inventory Metrics:**
• Total Products: {len(products):,}
• Total Units: {total_units:,}
• Total Inventory Value: ${total_value:,.2f}
• Average Value per Product: ${total_value/len(products):,.2f}
• Average Value per Unit: ${total_value/total_units:.2f}

💸 **Carrying Cost Analysis:**
• Annual Carrying Cost ({self.carrying_cost_rate*100:.0f}%): ${annual_carrying_cost:,.2f}
• Monthly Carrying Cost: ${monthly_carrying_cost:,.2f}
• Daily Carrying Cost: ${annual_carrying_cost/365:.2f}

📂 **Value by Category:**"""

            for category, data in sorted(category_values.items(), key=lambda x: x[1]["value"], reverse=True):
                percentage = (data["value"] / total_value * 100) if total_value > 0 else 0
                avg_value = data["value"] / data["products"] if data["products"] > 0 else 0
                
                report += f"\n• **{category}**: ${data['value']:,.2f} ({percentage:.1f}%)"
                report += f"\n  └─ {data['products']} products, {data['units']:,} units, avg ${avg_value:,.2f}/product"
            
            report += f"\n\n🏆 **Top 5 Most Valuable Items:**"
            for i, product in enumerate(products_by_value[:5], 1):
                item_value = product["quantity"] * product["price"]
                percentage = (item_value / total_value * 100) if total_value > 0 else 0
                report += f"\n{i}. {product['product_name']}: ${item_value:,.2f} ({percentage:.1f}%)"
                report += f"\n   └─ {product['quantity']} units × ${product['price']:.2f}"
            
            # Calculate inventory concentration
            top_10_value = sum(p["quantity"] * p["price"] for p in products_by_value[:10])
            concentration = (top_10_value / total_value * 100) if total_value > 0 else 0
            
            report += f"\n\n📈 **Inventory Concentration:**"
            report += f"\n• Top 10 items represent {concentration:.1f}% of total value"
            report += f"\n• Inventory diversity: {len(products)} different products"
            
            return report
            
        except Exception as e:
            return f"❌ Error calculating inventory values: {str(e)}"
    
    def _analyze_inventory_turnover(self) -> str:
        """Analyze inventory turnover rates (simplified calculation)."""
        try:
            result = self.inventory_tool.execute(GoogleSheetsInventoryInput(action="list_all"))
            
            if not result.success:
                return f"❌ Could not retrieve inventory data: {result.error}"
            
            products = result.result
            
            # Estimate turnover rates (in practice, use historical sales data)
            turnover_analysis = []
            
            for product in products:
                # Estimate annual demand based on price and category
                estimated_annual_demand = self._estimate_annual_demand(product)
                current_stock = product["quantity"]
                
                # Calculate turnover ratio
                if current_stock > 0:
                    turnover_ratio = estimated_annual_demand / current_stock
                    days_of_supply = 365 / turnover_ratio if turnover_ratio > 0 else 999
                else:
                    turnover_ratio = float('inf')
                    days_of_supply = 0
                
                # Classify turnover speed
                if turnover_ratio >= 12:  # Monthly turnover
                    speed = "Fast"
                elif turnover_ratio >= 4:   # Quarterly turnover
                    speed = "Medium"
                elif turnover_ratio >= 1:   # Annual turnover
                    speed = "Slow"
                else:
                    speed = "Very Slow"
                
                turnover_analysis.append({
                    "product": product,
                    "turnover_ratio": turnover_ratio,
                    "days_of_supply": days_of_supply,
                    "speed": speed,
                    "estimated_annual_demand": estimated_annual_demand
                })
            
            # Sort by turnover ratio
            turnover_analysis.sort(key=lambda x: x["turnover_ratio"], reverse=True)
            
            # Generate report
            report = f"""🔄 **INVENTORY TURNOVER ANALYSIS**
═══════════════════════════════════════

📊 **Turnover Speed Distribution:**"""
            
            speed_counts = {}
            for analysis in turnover_analysis:
                speed = analysis["speed"]
                speed_counts[speed] = speed_counts.get(speed, 0) + 1
            
            for speed in ["Fast", "Medium", "Slow", "Very Slow"]:
                count = speed_counts.get(speed, 0)
                percentage = (count / len(products) * 100) if products else 0
                report += f"\n• {speed} Movers: {count} products ({percentage:.1f}%)"
            
            report += f"\n\n🚀 **FAST MOVERS (High Turnover):**"
            fast_movers = [a for a in turnover_analysis if a["speed"] == "Fast"]
            
            if fast_movers:
                for analysis in fast_movers[:5]:  # Top 5
                    product = analysis["product"]
                    report += f"\n• **{product['product_name']}**"
                    report += f"\n  └─ Turnover: {analysis['turnover_ratio']:.1f}x/year, {analysis['days_of_supply']:.0f} days supply"
            else:
                report += "\n• No fast-moving items identified"
            
            report += f"\n\n🐌 **SLOW MOVERS (Low Turnover):**"
            slow_movers = [a for a in turnover_analysis if a["speed"] in ["Slow", "Very Slow"]]
            
            if slow_movers:
                # Show slowest movers
                slowest = sorted(slow_movers, key=lambda x: x["turnover_ratio"])[:5]
                for analysis in slowest:
                    product = analysis["product"]
                    tied_up_capital = product["quantity"] * product["price"]
                    report += f"\n• **{product['product_name']}**"
                    report += f"\n  └─ {analysis['days_of_supply']:.0f} days supply, ${tied_up_capital:,.2f} tied up"
            else:
                report += "\n• No slow-moving items identified"
            
            # Calculate overall metrics
            total_value = sum(p["quantity"] * p["price"] for p in products)
            weighted_turnover = sum(
                (a["product"]["quantity"] * a["product"]["price"] * a["turnover_ratio"]) / total_value
                for a in turnover_analysis if a["turnover_ratio"] != float('inf')
            ) if total_value > 0 else 0
            
            report += f"\n\n📈 **OVERALL TURNOVER METRICS:**"
            report += f"\n• Weighted Average Turnover: {weighted_turnover:.2f}x per year"
            report += f"\n• Average Days of Supply: {365/weighted_turnover:.0f} days"
            report += f"\n• Fast Movers: {len(fast_movers)} items"
            report += f"\n• Slow Movers: {len(slow_movers)} items"
            
            return report
            
        except Exception as e:
            return f"❌ Error analyzing inventory turnover: {str(e)}"
    
    def _calculate_optimal_stock_levels(self) -> str:
        """Calculate optimal stock levels for all products."""
        try:
            result = self.inventory_tool.execute(GoogleSheetsInventoryInput(action="list_all"))
            
            if not result.success:
                return f"❌ Could not retrieve inventory data: {result.error}"
            
            products = result.result
            optimization_results = []
            
            for product in products:
                # Calculate optimal parameters
                daily_demand = self._estimate_daily_demand(product)
                annual_demand = daily_demand * 365
                
                # Economic Order Quantity (EOQ)
                eoq = self._calculate_eoq(product, annual_demand)
                
                # Reorder point
                reorder_point = (daily_demand * self.lead_time_days) + (daily_demand * self.safety_stock_days)
                
                # Maximum stock level
                max_stock = reorder_point + eoq
                
                # Minimum stock level (safety stock)
                min_stock = daily_demand * self.safety_stock_days
                
                # Current vs optimal analysis
                current_stock = product["quantity"]
                
                if current_stock < min_stock:
                    status = "CRITICAL - Below minimum"
                    action = f"Order {eoq:.0f} units immediately"
                elif current_stock < reorder_point:
                    status = "LOW - Below reorder point"
                    action = f"Order {eoq:.0f} units soon"
                elif current_stock > max_stock:
                    status = "HIGH - Above maximum"
                    action = "Consider reducing orders"
                else:
                    status = "OPTIMAL - Within range"
                    action = "No action needed"
                
                optimization_results.append({
                    "product": product,
                    "current_stock": current_stock,
                    "min_stock": min_stock,
                    "reorder_point": reorder_point,
                    "max_stock": max_stock,
                    "eoq": eoq,
                    "status": status,
                    "action": action,
                    "daily_demand": daily_demand
                })
            
            # Sort by priority (critical items first)
            optimization_results.sort(key=lambda x: (
                "CRITICAL" not in x["status"],
                "LOW" not in x["status"],
                x["product"]["product_name"]
            ))
            
            # Generate report
            report = f"""⚙️ **OPTIMAL STOCK LEVEL ANALYSIS**
═══════════════════════════════════════

📋 **Optimization Parameters:**
• Lead Time: {self.lead_time_days} days
• Safety Stock: {self.safety_stock_days} days
• Service Level: {self.target_service_level*100:.0f}%
• Carrying Cost Rate: {self.carrying_cost_rate*100:.0f}%

🎯 **STOCK LEVEL RECOMMENDATIONS:**
"""
            
            # Group by status
            critical_items = [r for r in optimization_results if "CRITICAL" in r["status"]]
            low_items = [r for r in optimization_results if "LOW" in r["status"]]
            high_items = [r for r in optimization_results if "HIGH" in r["status"]]
            optimal_items = [r for r in optimization_results if "OPTIMAL" in r["status"]]
            
            if critical_items:
                report += f"\n🚨 **CRITICAL ITEMS ({len(critical_items)}):**\n"
                for result in critical_items:
                    product = result["product"]
                    report += f"\n• **{product['product_name']}** ({product['product_id']})\n"
                    report += f"  Current: {result['current_stock']} | Min: {result['min_stock']:.0f} | Reorder: {result['reorder_point']:.0f} | Max: {result['max_stock']:.0f}\n"
                    report += f"  Action: {result['action']}\n"
            
            if low_items:
                report += f"\n⚠️ **LOW STOCK ITEMS ({len(low_items)}):**\n"
                for result in low_items[:5]:  # Show top 5
                    product = result["product"]
                    report += f"• {product['product_name']}: {result['current_stock']} → Order {result['eoq']:.0f} units\n"
                if len(low_items) > 5:
                    report += f"• ... and {len(low_items) - 5} more items\n"
            
            if high_items:
                report += f"\n📦 **OVERSTOCKED ITEMS ({len(high_items)}):**\n"
                excess_value = 0
                for result in high_items[:5]:  # Show top 5
                    product = result["product"]
                    excess = result["current_stock"] - result["max_stock"]
                    excess_value += excess * product["price"]
                    report += f"• {product['product_name']}: {excess:.0f} units excess (${excess * product['price']:,.2f})\n"
                if len(high_items) > 5:
                    report += f"• ... and {len(high_items) - 5} more items\n"
                report += f"  Total Excess Value: ${excess_value:,.2f}\n"
            
            report += f"\n✅ **OPTIMALLY STOCKED ({len(optimal_items)} items)**\n"
            
            # Summary calculations
            total_reorder_investment = sum(r["eoq"] * r["product"]["price"] for r in critical_items + low_items)
            
            report += f"\n💰 **FINANCIAL IMPACT:**\n"
            report += f"• Required Investment: ${total_reorder_investment:,.2f}\n"
            report += f"• Items Needing Orders: {len(critical_items) + len(low_items)}\n"
            report += f"• Overstocked Items: {len(high_items)}\n"
            report += f"• Optimally Stocked: {len(optimal_items)}\n"
            
            return report
            
        except Exception as e:
            return f"❌ Error calculating optimal stock levels: {str(e)}"
    
    def _generate_financial_report(self) -> str:
        """Generate comprehensive financial report."""
        try:
            result = self.inventory_tool.execute(GoogleSheetsInventoryInput(action="list_all"))
            
            if not result.success:
                return f"❌ Could not retrieve inventory data: {result.error}"
            
            products = result.result
            
            # Calculate financial metrics
            total_inventory_value = sum(p["quantity"] * p["price"] for p in products)
            total_units = sum(p["quantity"] for p in products)
            
            # Carrying costs
            annual_carrying_cost = total_inventory_value * self.carrying_cost_rate
            monthly_carrying_cost = annual_carrying_cost / 12
            
            # Estimate annual sales and profit (simplified)
            estimated_annual_sales = 0
            estimated_cogs = 0
            
            for product in products:
                annual_demand = self._estimate_annual_demand(product)
                sales_value = annual_demand * product["price"]
                # Assume 60% gross margin
                cogs = sales_value * 0.4
                
                estimated_annual_sales += sales_value
                estimated_cogs += cogs
            
            gross_profit = estimated_annual_sales - estimated_cogs
            net_profit = gross_profit - annual_carrying_cost
            
            # Inventory turnover
            inventory_turnover = estimated_cogs / total_inventory_value if total_inventory_value > 0 else 0
            
            # Category financial breakdown
            category_financials = {}
            for product in products:
                category = product["category"]
                if category not in category_financials:
                    category_financials[category] = {
                        "inventory_value": 0,
                        "estimated_sales": 0,
                        "units": 0,
                        "products": 0
                    }
                
                annual_demand = self._estimate_annual_demand(product)
                category_financials[category]["inventory_value"] += product["quantity"] * product["price"]
                category_financials[category]["estimated_sales"] += annual_demand * product["price"]
                category_financials[category]["units"] += product["quantity"]
                category_financials[category]["products"] += 1
            
            # Generate report
            report = f"""💰 **FINANCIAL INVENTORY REPORT**
═══════════════════════════════════════

📊 **INVENTORY INVESTMENT:**
• Total Inventory Value: ${total_inventory_value:,.2f}
• Total Units in Stock: {total_units:,}
• Average Value per Unit: ${total_inventory_value/total_units:.2f}
• Number of SKUs: {len(products)}

💸 **CARRYING COSTS:**
• Annual Carrying Cost ({self.carrying_cost_rate*100:.0f}%): ${annual_carrying_cost:,.2f}
• Monthly Carrying Cost: ${monthly_carrying_cost:,.2f}
• Daily Carrying Cost: ${annual_carrying_cost/365:.2f}

📈 **PROJECTED PERFORMANCE:**
• Estimated Annual Sales: ${estimated_annual_sales:,.2f}
• Estimated COGS: ${estimated_cogs:,.2f}
• Gross Profit: ${gross_profit:,.2f}
• Net Profit (after carrying costs): ${net_profit:,.2f}
• Inventory Turnover Ratio: {inventory_turnover:.2f}x per year

📂 **FINANCIAL BREAKDOWN BY CATEGORY:**"""

            for category, data in sorted(category_financials.items(), key=lambda x: x[1]["inventory_value"], reverse=True):
                inv_percentage = (data["inventory_value"] / total_inventory_value * 100) if total_inventory_value > 0 else 0
                sales_percentage = (data["estimated_sales"] / estimated_annual_sales * 100) if estimated_annual_sales > 0 else 0
                roi = (data["estimated_sales"] / data["inventory_value"] * 100) if data["inventory_value"] > 0 else 0
                
                report += f"\n\n• **{category}**:"
                report += f"\n  └─ Inventory Value: ${data['inventory_value']:,.2f} ({inv_percentage:.1f}%)"
                report += f"\n  └─ Projected Sales: ${data['estimated_sales']:,.2f} ({sales_percentage:.1f}%)"
                report += f"\n  └─ ROI: {roi:.1f}%"
                report += f"\n  └─ {data['products']} products, {data['units']:,} units"
            
            # Key performance indicators
            report += f"\n\n📊 **KEY PERFORMANCE INDICATORS:**"
            report += f"\n• Inventory-to-Sales Ratio: {(total_inventory_value/estimated_annual_sales)*100:.1f}%"
            report += f"\n• Days Sales in Inventory: {365/inventory_turnover:.0f} days"
            report += f"\n• Gross Margin: {(gross_profit/estimated_annual_sales)*100:.1f}%"
            report += f"\n• Net Margin: {(net_profit/estimated_annual_sales)*100:.1f}%"
            
            # Recommendations
            report += f"\n\n💡 **FINANCIAL RECOMMENDATIONS:**"
            
            if inventory_turnover < 4:
                report += f"\n• ⚠️ Low inventory turnover - consider reducing slow-moving stock"
            else:
                report += f"\n• ✅ Healthy inventory turnover rate"
            
            if (total_inventory_value/estimated_annual_sales) > 0.25:
                report += f"\n• ⚠️ High inventory-to-sales ratio - optimize stock levels"
            else:
                report += f"\n• ✅ Reasonable inventory-to-sales ratio"
            
            report += f"\n• 💰 Potential annual savings from optimization: ${annual_carrying_cost*0.2:,.2f}"
            
            return report
            
        except Exception as e:
            return f"❌ Error generating financial report: {str(e)}"
    
    def _calculate_product_metrics(self, product_id: str) -> str:
        """Calculate detailed metrics for a specific product."""
        if not product_id:
            return "❌ Please specify a product ID for calculations."
        
        try:
            result = self.inventory_tool.execute(GoogleSheetsInventoryInput(action="check", product_id=product_id))
            
            if not result.success:
                return f"❌ Product '{product_id}' not found."
            
            product = result.result
            
            # Calculate various metrics
            daily_demand = self._estimate_daily_demand(product)
            annual_demand = daily_demand * 365
            
            # Financial metrics
            current_value = product["quantity"] * product["price"]
            annual_sales_value = annual_demand * product["price"]
            
            # Inventory metrics
            eoq = self._calculate_eoq(product, annual_demand)
            reorder_point = (daily_demand * self.lead_time_days) + (daily_demand * self.safety_stock_days)
            
            # Turnover metrics
            turnover_ratio = annual_demand / product["quantity"] if product["quantity"] > 0 else float('inf')
            days_of_supply = product["quantity"] / daily_demand if daily_demand > 0 else 999
            
            # Carrying cost
            annual_carrying_cost = current_value * self.carrying_cost_rate
            
            report = f"""🔢 **PRODUCT CALCULATIONS: {product['product_name']}**
═══════════════════════════════════════

📦 **BASIC INFORMATION:**
• Product ID: {product['product_id']}
• Category: {product['category']}
• Unit Price: ${product['price']:.2f}
• Current Stock: {product['quantity']} units

💰 **FINANCIAL METRICS:**
• Current Inventory Value: ${current_value:,.2f}
• Estimated Annual Sales: ${annual_sales_value:,.2f}
• Annual Carrying Cost: ${annual_carrying_cost:.2f}
• Value per Unit: ${product['price']:.2f}

📊 **DEMAND & TURNOVER:**
• Estimated Daily Demand: {daily_demand:.2f} units
• Estimated Annual Demand: {annual_demand:.0f} units
• Inventory Turnover: {turnover_ratio:.2f}x per year
• Days of Supply: {days_of_supply:.0f} days

⚙️ **OPTIMIZATION METRICS:**
• Economic Order Quantity (EOQ): {eoq:.0f} units
• Reorder Point: {reorder_point:.0f} units
• Safety Stock: {daily_demand * self.safety_stock_days:.0f} units
• Lead Time Demand: {daily_demand * self.lead_time_days:.0f} units

🎯 **RECOMMENDATIONS:**"""

            # Generate recommendations
            if product["quantity"] == 0:
                report += f"\n• 🚨 URGENT: Product is out of stock - order {eoq:.0f} units immediately"
            elif product["quantity"] < reorder_point:
                shortage = reorder_point - product["quantity"]
                report += f"\n• ⚠️ Below reorder point by {shortage:.0f} units - order {eoq:.0f} units"
            elif turnover_ratio < 2:
                report += f"\n• 🐌 Slow-moving item - consider reducing stock or promotional pricing"
            elif turnover_ratio > 12:
                report += f"\n• 🚀 Fast-moving item - consider increasing stock levels"
            else:
                report += f"\n• ✅ Stock levels appear optimal for current demand"
            
            # Cost analysis
            if annual_carrying_cost > annual_sales_value * 0.1:
                report += f"\n• 💸 High carrying cost relative to sales - optimize stock levels"
            
            return report
            
        except Exception as e:
            return f"❌ Error calculating product metrics: {str(e)}"
    
    def _calculate_category_metrics(self, category: str) -> str:
        """Calculate metrics for a specific category."""
        try:
            result = self.inventory_tool.execute(GoogleSheetsInventoryInput(action="search", category=category))
            
            if not result.success:
                return f"❌ Could not search category: {result.error}"
            
            products = result.result
            
            if not products:
                return f"❌ No products found in category '{category}'"
            
            # Calculate category totals
            total_products = len(products)
            total_units = sum(p["quantity"] for p in products)
            total_value = sum(p["quantity"] * p["price"] for p in products)
            avg_price = sum(p["price"] for p in products) / total_products
            
            # Calculate aggregate metrics
            total_annual_demand = 0
            total_eoq_investment = 0
            
            for product in products:
                daily_demand = self._estimate_daily_demand(product)
                annual_demand = daily_demand * 365
                eoq = self._calculate_eoq(product, annual_demand)
                
                total_annual_demand += annual_demand
                total_eoq_investment += eoq * product["price"]
            
            # Turnover analysis
            category_turnover = total_annual_demand / total_units if total_units > 0 else 0
            
            # Carrying costs
            annual_carrying_cost = total_value * self.carrying_cost_rate
            
            report = f"""📂 **CATEGORY CALCULATIONS: {category.upper()}**
═══════════════════════════════════════

📊 **CATEGORY OVERVIEW:**
• Total Products: {total_products}
• Total Units: {total_units:,}
• Total Value: ${total_value:,.2f}
• Average Price: ${avg_price:.2f}

💰 **FINANCIAL METRICS:**
• Annual Carrying Cost: ${annual_carrying_cost:,.2f}
• Estimated Annual Demand: {total_annual_demand:.0f} units
• Category Turnover: {category_turnover:.2f}x per year
• Optimal Reorder Investment: ${total_eoq_investment:,.2f}

📈 **PERFORMANCE ANALYSIS:**"""

            # Performance classification
            if category_turnover >= 6:
                performance = "High Performance"
                emoji = "🚀"
            elif category_turnover >= 3:
                performance = "Good Performance"
                emoji = "✅"
            elif category_turnover >= 1:
                performance = "Average Performance"
                emoji = "⚠️"
            else:
                performance = "Poor Performance"
                emoji = "🐌"
            
            report += f"\n• {emoji} **{performance}** (Turnover: {category_turnover:.2f}x)"
            
            # Top performers in category
            products_by_value = sorted(products, key=lambda x: x["quantity"] * x["price"], reverse=True)
            
            report += f"\n\n🏆 **TOP PRODUCTS BY VALUE:**"
            for i, product in enumerate(products_by_value[:3], 1):
                value = product["quantity"] * product["price"]
                percentage = (value / total_value * 100) if total_value > 0 else 0
                report += f"\n{i}. {product['product_name']}: ${value:,.2f} ({percentage:.1f}%)"
            
            # Recommendations
            report += f"\n\n💡 **CATEGORY RECOMMENDATIONS:**"
            
            if category_turnover < 2:
                report += f"\n• Consider reducing inventory levels for slow-moving items"
                report += f"\n• Implement promotional strategies to increase sales velocity"
            elif category_turnover > 8:
                report += f"\n• Consider increasing stock levels to avoid stockouts"
                report += f"\n• Monitor for supply chain constraints"
            
            report += f"\n• Potential annual savings: ${annual_carrying_cost * 0.15:,.2f}"
            
            return report
            
        except Exception as e:
            return f"❌ Error calculating category metrics: {str(e)}"
    
    def _perform_abc_analysis(self) -> str:
        """Perform ABC analysis on inventory."""
        try:
            result = self.inventory_tool.execute(GoogleSheetsInventoryInput(action="list_all"))
            
            if not result.success:
                return f"❌ Could not retrieve inventory data: {result.error}"
            
            products = result.result
            
            # Calculate annual value for each product
            product_values = []
            for product in products:
                annual_demand = self._estimate_annual_demand(product)
                annual_value = annual_demand * product["price"]
                product_values.append({
                    "product": product,
                    "annual_value": annual_value,
                    "current_value": product["quantity"] * product["price"]
                })
            
            # Sort by annual value (descending)
            product_values.sort(key=lambda x: x["annual_value"], reverse=True)
            
            # Calculate cumulative percentages
            total_annual_value = sum(pv["annual_value"] for pv in product_values)
            cumulative_value = 0
            
            for pv in product_values:
                cumulative_value += pv["annual_value"]
                pv["cumulative_percentage"] = (cumulative_value / total_annual_value * 100) if total_annual_value > 0 else 0
            
            # Classify into ABC categories
            a_items = []
            b_items = []
            c_items = []
            
            for pv in product_values:
                if pv["cumulative_percentage"] <= 80:
                    pv["category"] = "A"
                    a_items.append(pv)
                elif pv["cumulative_percentage"] <= 95:
                    pv["category"] = "B"
                    b_items.append(pv)
                else:
                    pv["category"] = "C"
                    c_items.append(pv)
            
            # Calculate category statistics
            def calc_category_stats(items):
                if not items:
                    return {"count": 0, "annual_value": 0, "current_value": 0, "percentage": 0}
                
                return {
                    "count": len(items),
                    "annual_value": sum(item["annual_value"] for item in items),
                    "current_value": sum(item["current_value"] for item in items),
                    "percentage": len(items) / len(products) * 100 if products else 0
                }
            
            a_stats = calc_category_stats(a_items)
            b_stats = calc_category_stats(b_items)
            c_stats = calc_category_stats(c_items)
            
            # Generate report
            report = f"""📊 **ABC INVENTORY ANALYSIS**
═══════════════════════════════════════

🎯 **ABC CLASSIFICATION RESULTS:**

🅰️ **CLASS A - HIGH VALUE (Top 80% of value)**
• Products: {a_stats['count']} ({a_stats['percentage']:.1f}% of items)
• Annual Value: ${a_stats['annual_value']:,.2f}
• Current Inventory: ${a_stats['current_value']:,.2f}
• Management Focus: Tight control, frequent review

🅱️ **CLASS B - MEDIUM VALUE (Next 15% of value)**
• Products: {b_stats['count']} ({b_stats['percentage']:.1f}% of items)
• Annual Value: ${b_stats['annual_value']:,.2f}
• Current Inventory: ${b_stats['current_value']:,.2f}
• Management Focus: Moderate control, periodic review

🅲️ **CLASS C - LOW VALUE (Remaining 5% of value)**
• Products: {c_stats['count']} ({c_stats['percentage']:.1f}% of items)
• Annual Value: ${c_stats['annual_value']:,.2f}
• Current Inventory: ${c_stats['current_value']:,.2f}
• Management Focus: Simple controls, annual review

📋 **TOP CLASS A ITEMS:**"""

            for i, item in enumerate(a_items[:5], 1):
                product = item["product"]
                report += f"\n{i}. **{product['product_name']}** ({product['product_id']})"
                report += f"\n   └─ Annual Value: ${item['annual_value']:,.2f} | Current Stock: ${item['current_value']:,.2f}"
            
            if len(a_items) > 5:
                report += f"\n   ... and {len(a_items) - 5} more Class A items"
            
            report += f"\n\n💡 **MANAGEMENT RECOMMENDATIONS:**"
            report += f"\n\n🅰️ **Class A Items ({a_stats['count']} products):**"
            report += f"\n• Implement daily monitoring and tight inventory controls"
            report += f"\n• Use sophisticated forecasting methods"
            report += f"\n• Negotiate better supplier terms due to high volume"
            report += f"\n• Consider vendor-managed inventory for top items"
            
            report += f"\n\n🅱️ **Class B Items ({b_stats['count']} products):**"
            report += f"\n• Weekly monitoring and moderate controls"
            report += f"\n• Standard forecasting and reorder procedures"
            report += f"\n• Quarterly supplier reviews"
            
            report += f"\n\n🅲️ **Class C Items ({c_stats['count']} products):**"
            report += f"\n• Monthly monitoring with simple controls"
            report += f"\n• Consider bulk purchasing to reduce ordering costs"
            report += f"\n• Annual supplier reviews"
            report += f"\n• Evaluate discontinuation of very slow movers"
            
            # Investment analysis
            total_current_value = sum(pv["current_value"] for pv in product_values)
            
            report += f"\n\n💰 **INVESTMENT DISTRIBUTION:**"
            report += f"\n• Total Current Inventory: ${total_current_value:,.2f}"
            report += f"\n• Class A Investment: ${a_stats['current_value']:,.2f} ({a_stats['current_value']/total_current_value*100:.1f}%)"
            report += f"\n• Class B Investment: ${b_stats['current_value']:,.2f} ({b_stats['current_value']/total_current_value*100:.1f}%)"
            report += f"\n• Class C Investment: ${c_stats['current_value']:,.2f} ({c_stats['current_value']/total_current_value*100:.1f}%)"
            
            return report
            
        except Exception as e:
            return f"❌ Error performing ABC analysis: {str(e)}"
    
    def _estimate_daily_demand(self, product: Dict[str, Any]) -> float:
        """Estimate daily demand based on product characteristics."""
        # Simplified demand estimation - in practice, use historical sales data
        price = product["price"]
        category = product["category"].lower()
        
        # Base demand by category
        if "electronics" in category:
            base_demand = 2.0
        elif "audio" in category:
            base_demand = 1.5
        elif "accessories" in category:
            base_demand = 3.0
        else:
            base_demand = 1.0
        
        # Adjust by price (higher price = lower demand)
        if price > 1000:
            price_factor = 0.3
        elif price > 500:
            price_factor = 0.5
        elif price > 100:
            price_factor = 0.8
        else:
            price_factor = 1.2
        
        return base_demand * price_factor
    
    def _estimate_annual_demand(self, product: Dict[str, Any]) -> float:
        """Estimate annual demand."""
        return self._estimate_daily_demand(product) * 365
    
    def _calculate_eoq(self, product: Dict[str, Any], annual_demand: float) -> float:
        """Calculate Economic Order Quantity."""
        # Simplified EOQ calculation
        # EOQ = sqrt((2 * D * S) / H)
        # Where: D = annual demand, S = ordering cost, H = holding cost per unit
        
        ordering_cost = 50  # Assume $50 per order
        holding_cost_per_unit = product["price"] * self.carrying_cost_rate
        
        if holding_cost_per_unit <= 0:
            return annual_demand / 12  # Monthly supply as fallback
        
        eoq = math.sqrt((2 * annual_demand * ordering_cost) / holding_cost_per_unit)
        
        # Ensure reasonable bounds
        min_order = max(1, annual_demand / 52)  # At least weekly supply
        max_order = annual_demand / 4  # At most quarterly supply
        
        return max(min_order, min(eoq, max_order))
    
    def _extract_product_id(self, message: str) -> str:
        """Extract product ID from message."""
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
    
    def _handle_general_calculation_query(self, message: str) -> str:
        """Handle general calculation queries."""
        return f"""🧮 **Stock Calculator Agent Ready!**

I can perform these calculations:

📊 **Inventory Calculations:**
• "Calculate reorder points" - When to reorder each product
• "Calculate inventory values" - Total values and breakdowns
• "Analyze inventory turnover" - How fast products move
• "Calculate optimal stock levels" - Min/max recommendations

💰 **Financial Analysis:**
• "Generate financial report" - Comprehensive financial metrics
• "Perform ABC analysis" - Classify products by value importance

🔍 **Product-Specific:**
• "Calculate metrics for LAPTOP001" - Detailed product analysis
• "Calculate Electronics category" - Category-wide metrics

📈 **What calculations would you like me to perform?**

Your message: "{message}"
"""