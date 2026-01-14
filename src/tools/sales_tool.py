"""
Sales Tool - Enhanced sales processing with automatic stock management and alerts.
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from src.tools.base_tool import BaseTool, ToolInput, ToolOutput
from src.tools.google_sheets_inventory_tool import GoogleSheetsInventoryTool, GoogleSheetsInventoryInput
from src.tools.transaction_tool import TransactionTool, TransactionInput


class SalesInput(ToolInput):
    """Input schema for sales operations."""
    action: str = Field(description="Action: 'quick_sale', 'check_availability', 'bulk_sale', 'sales_analytics', 'stock_alerts'")
    product_id: Optional[str] = Field(default=None, description="Product ID for the sale")
    quantity: Optional[int] = Field(default=None, description="Quantity to sell")
    unit_price: Optional[float] = Field(default=None, description="Unit price (optional, uses product price if not specified)")
    customer_info: Optional[str] = Field(default=None, description="Customer information")
    notes: Optional[str] = Field(default=None, description="Additional notes")
    products: Optional[List[Dict[str, Any]]] = Field(default=None, description="List of products for bulk sale")


class SalesTool(BaseTool):
    """
    Enhanced sales tool with automatic stock management.
    
    Features:
    - Quick sales processing with stock validation
    - Automatic stock deduction
    - Real-time stock alerts
    - Bulk sales processing
    - Sales analytics and reporting
    - Stock availability checking
    """
    
    def __init__(self, spreadsheet_id: Optional[str] = None):
        super().__init__(
            name="sales_tool",
            description="Enhanced sales processing with automatic inventory management and alerts"
        )
        
        self.spreadsheet_id = spreadsheet_id or os.getenv("GOOGLE_SHEETS_INVENTORY_ID")
        self.inventory_tool = GoogleSheetsInventoryTool(spreadsheet_id=self.spreadsheet_id)
        self.transaction_tool = TransactionTool(spreadsheet_id=self.spreadsheet_id)
        
        # Stock thresholds
        self.low_stock_threshold = 10
        self.critical_stock_threshold = 5
        self.out_of_stock_threshold = 0
    
    def execute(self, input_data: SalesInput) -> ToolOutput:
        """Execute sales operations."""
        try:
            if input_data.action == "quick_sale":
                result = self._process_quick_sale(
                    input_data.product_id,
                    input_data.quantity,
                    input_data.unit_price,
                    input_data.customer_info,
                    input_data.notes
                )
            elif input_data.action == "check_availability":
                result = self._check_availability(input_data.product_id)
            elif input_data.action == "bulk_sale":
                result = self._process_bulk_sale(input_data.products, input_data.customer_info)
            elif input_data.action == "sales_analytics":
                result = self._generate_sales_analytics()
            elif input_data.action == "stock_alerts":
                result = self._generate_stock_alerts()
            else:
                return ToolOutput(success=False, result=None, error=f"Unknown action: {input_data.action}")
            
            return ToolOutput(success=True, result=result)
            
        except Exception as e:
            return ToolOutput(success=False, result=None, error=str(e))
    
    def _process_quick_sale(self, product_id: str, quantity: int, unit_price: float = None, 
                           customer_info: str = None, notes: str = None) -> Dict[str, Any]:
        """Process a quick sale with enhanced stock management."""
        if not product_id or not quantity:
            raise ValueError("Product ID and quantity are required for sales")
        
        if quantity <= 0:
            raise ValueError("Sale quantity must be positive")
        
        # Get current product info
        product_result = self.inventory_tool.execute(GoogleSheetsInventoryInput(action="check", product_id=product_id))
        
        if not product_result.success:
            raise ValueError(f"Product {product_id} not found: {product_result.error}")
        
        product = product_result.result
        current_stock = product["quantity"]
        
        # Enhanced stock validation
        if current_stock <= 0:
            raise ValueError(f"Product {product_id} is OUT OF STOCK. Cannot process sale.")
        
        if current_stock < quantity:
            raise ValueError(f"Insufficient stock for {product_id}. Available: {current_stock}, Requested: {quantity}")
        
        # Use product price if not specified
        if not unit_price:
            unit_price = product["price"]
        
        # Calculate new stock level
        new_stock = current_stock - quantity
        
        # Process the sale using transaction tool
        sale_result = self.transaction_tool.execute(TransactionInput(
            action="sale",
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
            customer_info=customer_info,
            notes=notes or f"Quick sale processed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ))
        
        if not sale_result.success:
            raise ValueError(f"Failed to process sale: {sale_result.error}")
        
        sale_data = sale_result.result
        
        # Generate stock alerts
        stock_alerts = self._generate_stock_alert_for_product(product, new_stock)
        
        return {
            "sale_completed": True,
            "transaction_id": sale_data["transaction_id"],
            "product_info": {
                "product_id": product_id,
                "product_name": product["product_name"],
                "category": product["category"]
            },
            "sale_details": {
                "quantity_sold": quantity,
                "unit_price": unit_price,
                "total_amount": quantity * unit_price,
                "customer_info": customer_info
            },
            "stock_update": {
                "previous_stock": current_stock,
                "new_stock": new_stock,
                "stock_change": -quantity
            },
            "alerts": stock_alerts,
            "timestamp": datetime.now().isoformat()
        }
    
    def _check_availability(self, product_id: str) -> Dict[str, Any]:
        """Check detailed stock availability for a product."""
        if not product_id:
            raise ValueError("Product ID is required for availability check")
        
        # Get product info
        result = self.inventory_tool.execute(GoogleSheetsInventoryInput(action="check", product_id=product_id))
        
        if not result.success:
            raise ValueError(f"Product {product_id} not found: {result.error}")
        
        product = result.result
        quantity = product["quantity"]
        
        # Determine availability status
        if quantity <= self.out_of_stock_threshold:
            status = "out_of_stock"
            availability_level = "critical"
            can_sell = False
            max_sale_quantity = 0
            recommendation = "Immediate restock required"
        elif quantity <= self.critical_stock_threshold:
            status = "critical_stock"
            availability_level = "critical"
            can_sell = True
            max_sale_quantity = quantity
            recommendation = "Limit sales and reorder urgently"
        elif quantity <= self.low_stock_threshold:
            status = "low_stock"
            availability_level = "warning"
            can_sell = True
            max_sale_quantity = quantity
            recommendation = "Monitor closely and plan reorder"
        else:
            status = "in_stock"
            availability_level = "good"
            can_sell = True
            max_sale_quantity = quantity
            recommendation = "Stock levels are healthy"
        
        return {
            "product_id": product_id,
            "product_name": product["product_name"],
            "category": product["category"],
            "unit_price": product["price"],
            "availability": {
                "current_stock": quantity,
                "status": status,
                "level": availability_level,
                "can_sell": can_sell,
                "max_sale_quantity": max_sale_quantity
            },
            "financial": {
                "unit_price": product["price"],
                "total_value": quantity * product["price"],
                "potential_revenue": max_sale_quantity * product["price"]
            },
            "recommendation": recommendation,
            "last_updated": product.get("last_updated", "Unknown")
        }
    
    def _process_bulk_sale(self, products: List[Dict[str, Any]], customer_info: str = None) -> Dict[str, Any]:
        """Process multiple products in a single sale transaction."""
        if not products:
            raise ValueError("Product list is required for bulk sale")
        
        successful_sales = []
        failed_sales = []
        total_amount = 0
        stock_alerts = []
        
        for product_data in products:
            try:
                product_id = product_data.get("product_id")
                quantity = product_data.get("quantity", 1)
                unit_price = product_data.get("unit_price")
                
                # Process individual sale
                sale_result = self._process_quick_sale(
                    product_id=product_id,
                    quantity=quantity,
                    unit_price=unit_price,
                    customer_info=customer_info,
                    notes=f"Bulk sale item - {len(products)} products total"
                )
                
                successful_sales.append(sale_result)
                total_amount += sale_result["sale_details"]["total_amount"]
                
                # Collect stock alerts
                if sale_result["alerts"]:
                    stock_alerts.extend(sale_result["alerts"])
                
            except Exception as e:
                failed_sales.append({
                    "product_id": product_data.get("product_id", "Unknown"),
                    "error": str(e)
                })
        
        return {
            "bulk_sale_completed": True,
            "summary": {
                "total_products_attempted": len(products),
                "successful_sales": len(successful_sales),
                "failed_sales": len(failed_sales),
                "total_amount": total_amount
            },
            "successful_sales": successful_sales,
            "failed_sales": failed_sales,
            "stock_alerts": stock_alerts,
            "customer_info": customer_info,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_sales_analytics(self) -> Dict[str, Any]:
        """Generate comprehensive sales analytics."""
        try:
            # Get transaction data
            transactions_result = self.transaction_tool.execute(TransactionInput(action="list_transactions"))
            
            if not transactions_result.success:
                raise ValueError(f"Could not retrieve transaction data: {transactions_result.error}")
            
            transactions = transactions_result.result
            sales = [t for t in transactions if t["transaction_type"] == "sale"]
            
            if not sales:
                return {
                    "analytics_available": False,
                    "message": "No sales data available for analysis"
                }
            
            # Calculate basic metrics
            total_revenue = sum(t["total_amount"] for t in sales)
            total_units = sum(abs(t["quantity"]) for t in sales)
            total_transactions = len(sales)
            avg_sale_value = total_revenue / total_transactions if total_transactions > 0 else 0
            avg_units_per_sale = total_units / total_transactions if total_transactions > 0 else 0
            
            # Product performance analysis
            product_performance = {}
            for sale in sales:
                pid = sale["product_id"]
                if pid not in product_performance:
                    product_performance[pid] = {
                        "product_name": sale["product_name"],
                        "units_sold": 0,
                        "revenue": 0,
                        "transactions": 0,
                        "avg_price": 0
                    }
                
                product_performance[pid]["units_sold"] += abs(sale["quantity"])
                product_performance[pid]["revenue"] += sale["total_amount"]
                product_performance[pid]["transactions"] += 1
            
            # Calculate average prices
            for pid, data in product_performance.items():
                if data["units_sold"] > 0:
                    data["avg_price"] = data["revenue"] / data["units_sold"]
            
            # Sort products by revenue
            top_products = sorted(product_performance.items(), key=lambda x: x[1]["revenue"], reverse=True)
            
            # Time-based analysis (simplified)
            today = datetime.now().strftime("%Y-%m-%d")
            today_sales = [s for s in sales if s["date"] == today]
            today_revenue = sum(t["total_amount"] for t in today_sales)
            today_units = sum(abs(t["quantity"]) for t in today_sales)
            
            return {
                "analytics_available": True,
                "overall_performance": {
                    "total_revenue": total_revenue,
                    "total_units_sold": total_units,
                    "total_transactions": total_transactions,
                    "average_sale_value": avg_sale_value,
                    "average_units_per_sale": avg_units_per_sale
                },
                "today_performance": {
                    "revenue": today_revenue,
                    "units_sold": today_units,
                    "transactions": len(today_sales)
                },
                "top_products": [
                    {
                        "product_id": pid,
                        "product_name": data["product_name"],
                        "revenue": data["revenue"],
                        "units_sold": data["units_sold"],
                        "transactions": data["transactions"],
                        "avg_price": data["avg_price"]
                    }
                    for pid, data in top_products[:10]
                ],
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "analytics_available": False,
                "error": str(e)
            }
    
    def _generate_stock_alerts(self) -> Dict[str, Any]:
        """Generate comprehensive stock alerts for sales operations."""
        try:
            # Get all products
            result = self.inventory_tool.execute(GoogleSheetsInventoryInput(action="list_all"))
            
            if not result.success:
                raise ValueError(f"Could not retrieve inventory data: {result.error}")
            
            products = result.result
            
            # Categorize products by stock level
            out_of_stock = []
            critical_stock = []
            low_stock = []
            healthy_stock = []
            
            for product in products:
                quantity = product["quantity"]
                
                if quantity <= self.out_of_stock_threshold:
                    out_of_stock.append(product)
                elif quantity <= self.critical_stock_threshold:
                    critical_stock.append(product)
                elif quantity <= self.low_stock_threshold:
                    low_stock.append(product)
                else:
                    healthy_stock.append(product)
            
            # Calculate financial impact
            lost_revenue_potential = sum(p["price"] * 10 for p in out_of_stock)  # Assume 10 units average demand
            at_risk_revenue = sum(p["price"] * p["quantity"] for p in critical_stock)
            
            return {
                "alert_timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_products": len(products),
                    "out_of_stock_count": len(out_of_stock),
                    "critical_stock_count": len(critical_stock),
                    "low_stock_count": len(low_stock),
                    "healthy_stock_count": len(healthy_stock)
                },
                "financial_impact": {
                    "lost_revenue_potential": lost_revenue_potential,
                    "at_risk_revenue": at_risk_revenue
                },
                "alerts": {
                    "out_of_stock": [
                        {
                            "product_id": p["product_id"],
                            "product_name": p["product_name"],
                            "category": p["category"],
                            "unit_price": p["price"],
                            "status": "Cannot sell - immediate restock required"
                        }
                        for p in out_of_stock
                    ],
                    "critical_stock": [
                        {
                            "product_id": p["product_id"],
                            "product_name": p["product_name"],
                            "category": p["category"],
                            "current_stock": p["quantity"],
                            "unit_price": p["price"],
                            "status": "Limit sales - urgent reorder needed"
                        }
                        for p in critical_stock
                    ],
                    "low_stock": [
                        {
                            "product_id": p["product_id"],
                            "product_name": p["product_name"],
                            "category": p["category"],
                            "current_stock": p["quantity"],
                            "unit_price": p["price"],
                            "status": "Monitor closely - plan reorder"
                        }
                        for p in low_stock
                    ]
                },
                "recommendations": self._generate_stock_recommendations(out_of_stock, critical_stock, low_stock)
            }
            
        except Exception as e:
            return {
                "alert_timestamp": datetime.now().isoformat(),
                "error": str(e),
                "alerts_available": False
            }
    
    def _generate_stock_alert_for_product(self, product: Dict[str, Any], new_stock: int) -> List[Dict[str, Any]]:
        """Generate stock alerts for a specific product after sale."""
        alerts = []
        
        if new_stock <= self.out_of_stock_threshold:
            alerts.append({
                "level": "critical",
                "type": "out_of_stock",
                "message": f"{product['product_name']} is now OUT OF STOCK",
                "action_required": "Immediate restock required",
                "impact": "Cannot process further sales"
            })
        elif new_stock <= self.critical_stock_threshold:
            alerts.append({
                "level": "high",
                "type": "critical_stock",
                "message": f"{product['product_name']} has critical stock level: {new_stock} units",
                "action_required": "Urgent reorder needed",
                "impact": "Limited sales capacity"
            })
        elif new_stock <= self.low_stock_threshold:
            alerts.append({
                "level": "medium",
                "type": "low_stock",
                "message": f"{product['product_name']} has low stock: {new_stock} units",
                "action_required": "Plan reorder within 1-2 weeks",
                "impact": "Monitor sales closely"
            })
        
        return alerts
    
    def _generate_stock_recommendations(self, out_of_stock: List, critical_stock: List, low_stock: List) -> List[str]:
        """Generate actionable stock recommendations."""
        recommendations = []
        
        if out_of_stock:
            recommendations.append(f"URGENT: Restock {len(out_of_stock)} out-of-stock items immediately")
            recommendations.append("Remove out-of-stock items from sales displays")
            recommendations.append("Consider alternative products for customer inquiries")
        
        if critical_stock:
            recommendations.append(f"HIGH PRIORITY: Reorder {len(critical_stock)} critical stock items")
            recommendations.append("Implement purchase limits for critical stock items")
            recommendations.append("Notify customers of limited availability")
        
        if low_stock:
            recommendations.append(f"MEDIUM PRIORITY: Plan reorders for {len(low_stock)} low stock items")
            recommendations.append("Monitor sales velocity for low stock items")
            recommendations.append("Prepare purchase orders for next restock cycle")
        
        if not (out_of_stock or critical_stock or low_stock):
            recommendations.append("All products have healthy stock levels")
            recommendations.append("Continue monitoring stock levels during sales")
        
        return recommendations
    
    def _get_input_schema(self) -> Dict[str, Any]:
        """Get the input schema for this tool."""
        return SalesInput.model_json_schema()


# Example usage and testing
if __name__ == "__main__":
    print("💰 Sales Tool Test")
    print("=" * 50)
    
    # Initialize sales tool
    sales_tool = SalesTool()
    
    # Test availability check
    print("\n1. Testing Availability Check:")
    availability_result = sales_tool.execute(SalesInput(
        action="check_availability",
        product_id="LAPTOP001"
    ))
    
    if availability_result.success:
        print("✅ Availability check completed:")
        availability = availability_result.result
        print(f"   Product: {availability['product_name']}")
        print(f"   Stock: {availability['availability']['current_stock']} units")
        print(f"   Status: {availability['availability']['status']}")
        print(f"   Can Sell: {availability['availability']['can_sell']}")
    else:
        print(f"❌ Availability check failed: {availability_result.error}")
    
    # Test quick sale
    print("\n2. Testing Quick Sale:")
    sale_result = sales_tool.execute(SalesInput(
        action="quick_sale",
        product_id="LAPTOP001",
        quantity=1,
        customer_info="Test Customer",
        notes="Test sale transaction"
    ))
    
    if sale_result.success:
        print("✅ Quick sale completed:")
        sale_data = sale_result.result
        print(f"   Transaction ID: {sale_data['transaction_id']}")
        print(f"   Amount: ${sale_data['sale_details']['total_amount']:.2f}")
        print(f"   New Stock: {sale_data['stock_update']['new_stock']} units")
        if sale_data['alerts']:
            print(f"   Alerts: {len(sale_data['alerts'])} stock alerts generated")
    else:
        print(f"❌ Quick sale failed: {sale_result.error}")
    
    # Test stock alerts
    print("\n3. Testing Stock Alerts:")
    alerts_result = sales_tool.execute(SalesInput(action="stock_alerts"))
    
    if alerts_result.success:
        alerts_data = alerts_result.result
        print("✅ Stock alerts generated:")
        print(f"   Out of Stock: {alerts_data['summary']['out_of_stock_count']} items")
        print(f"   Critical Stock: {alerts_data['summary']['critical_stock_count']} items")
        print(f"   Low Stock: {alerts_data['summary']['low_stock_count']} items")
    else:
        print(f"❌ Stock alerts failed: {alerts_result.error}")