"""
Inventory Coordinator Agent - Multi-agent system for comprehensive inventory management.
"""

from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent
from src.agents.inventory_agent import InventoryAgent
from src.agents.stock_calculator_agent import StockCalculatorAgent
from src.agents.transaction_agent import TransactionAgent
from src.tools.google_sheets_inventory_tool import GoogleSheetsInventoryTool, GoogleSheetsInventoryInput


class AgentTool:
    """Wrapper to use an agent as a tool."""
    
    def __init__(self, agent: BaseAgent):
        self.agent = agent
        self.name = f"{agent.name}_tool"
        self.description = f"Delegate to {agent.name}: {agent.description}"
    
    def execute(self, input_data):
        """Execute the agent with the given message."""
        message = input_data.get('message', '')
        result = self.agent.process_message(message)
        return {
            'success': True,
            'result': result,
            'error': None
        }
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the tool schema for this agent."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The message to send to the agent"
                    }
                },
                "required": ["message"]
            }
        }


class InventoryCoordinatorAgent(BaseAgent):
    """
    Inventory Coordinator Agent - Orchestrates multiple specialized inventory agents.
    
    This coordinator manages a multi-agent system for comprehensive inventory management:
    - Inventory Agent: Stock analysis, alerts, and monitoring
    - Stock Calculator Agent: Financial calculations, reorder points, optimization
    - Direct Google Sheets access for data updates
    
    The coordinator intelligently routes requests to the most appropriate specialist
    and can combine insights from multiple agents for comprehensive analysis.
    """
    
    def __init__(self, spreadsheet_id: str = None):
        # Initialize specialist agents
        self.inventory_agent = InventoryAgent(spreadsheet_id=spreadsheet_id)
        self.calculator_agent = StockCalculatorAgent(spreadsheet_id=spreadsheet_id)
        self.transaction_agent = TransactionAgent(spreadsheet_id=spreadsheet_id)
        
        # Initialize direct Google Sheets tool for updates
        self.sheets_tool = GoogleSheetsInventoryTool(spreadsheet_id=spreadsheet_id)
        
        # Wrap agents as tools
        inventory_tool = AgentTool(self.inventory_agent)
        calculator_tool = AgentTool(self.calculator_agent)
        transaction_tool = AgentTool(self.transaction_agent)
        
        super().__init__(
            name="inventory_coordinator",
            description="Multi-agent coordinator for comprehensive inventory management and analysis",
            tools=[self.sheets_tool]  # Direct sheets access for updates
        )
        
        # Store agent tools
        self.agent_tools = {
            'inventory': inventory_tool,
            'calculator': calculator_tool,
            'transaction': transaction_tool
        }
        
        # Track conversation context for intelligent routing
        self.context = {
            "last_analysis_type": None,
            "current_focus": None,
            "pending_actions": []
        }
    
    def process_message(self, message: str) -> str:
        """
        Process inventory management requests by routing to appropriate agents.
        """
        self.conversation_history.append({"role": "user", "content": message})
        
        try:
            # Determine the type of request and routing strategy
            request_type = self._classify_request(message)
            
            if request_type == "comprehensive_analysis":
                response = self._perform_comprehensive_analysis(message)
            elif request_type == "multi_agent_task":
                response = self._handle_multi_agent_task(message)
            elif request_type == "data_update":
                response = self._handle_data_update(message)
            elif request_type == "dashboard":
                response = self._generate_dashboard()
            elif request_type == "inventory_focus":
                response = self._delegate_to_inventory_agent(message)
            elif request_type == "calculation_focus":
                response = self._delegate_to_calculator_agent(message)
            elif request_type == "action_plan":
                response = self._generate_action_plan(message)
            elif request_type == "transaction_focus":
                response = self._delegate_to_transaction_agent(message)
            else:
                response = self._handle_general_coordination(message)
                
        except Exception as e:
            response = f"❌ Coordination error: {str(e)}"
        
        self.conversation_history.append({"role": "assistant", "content": response})
        return response
    
    def _classify_request(self, message: str) -> str:
        """Classify the type of inventory management request."""
        message_lower = message.lower()
        
        # Multi-agent or comprehensive requests
        if any(word in message_lower for word in ['complete analysis', 'full report', 'comprehensive', 'everything']):
            return "comprehensive_analysis"
        elif any(word in message_lower for word in ['dashboard', 'overview', 'summary']):
            return "dashboard"
        elif any(word in message_lower for word in ['action plan', 'what should i do', 'recommendations']):
            return "action_plan"
        
        # Data update requests
        elif any(word in message_lower for word in ['update', 'add', 'change', 'modify', 'set']):
            return "data_update"
        
        # Transaction requests
        elif any(word in message_lower for word in ['sell', 'sale', 'sold', 'buy', 'purchase', 'transaction']):
            return "transaction_focus"
        
        # Calculation-focused requests
        elif any(word in message_lower for word in ['calculate', 'reorder', 'eoq', 'financial', 'turnover', 'abc', 'optimal']):
            return "calculation_focus"
        
        # Inventory analysis requests
        elif any(word in message_lower for word in ['analyze', 'stock levels', 'low stock', 'alerts', 'status']):
            return "inventory_focus"
        
        # Multi-agent coordination needed
        elif any(word in message_lower for word in ['both', 'combine', 'together', 'and also']):
            return "multi_agent_task"
        
        else:
            return "general"
    
    def _perform_comprehensive_analysis(self, message: str) -> str:
        """Perform comprehensive analysis using both agents."""
        try:
            # Get inventory analysis
            inventory_result = self.agent_tools['inventory'].execute({'message': 'analyze stock levels'})
            
            # Get financial calculations
            calculator_result = self.agent_tools['calculator'].execute({'message': 'generate financial report'})
            
            # Get reorder calculations
            reorder_result = self.agent_tools['calculator'].execute({'message': 'calculate reorder points'})
            
            # Combine results into comprehensive report
            report = f"""🏢 **COMPREHENSIVE INVENTORY ANALYSIS**
═══════════════════════════════════════

{inventory_result['result']}

═══════════════════════════════════════

{calculator_result['result']}

═══════════════════════════════════════

{reorder_result['result']}

═══════════════════════════════════════

🎯 **COORDINATOR SUMMARY:**

This comprehensive analysis combines insights from both inventory monitoring and financial calculations. 
Key areas requiring attention have been identified across stock levels, financial performance, and reorder requirements.

💡 **Next Steps:**
1. Review urgent reorder recommendations
2. Address critical stock alerts
3. Implement optimization suggestions
4. Monitor financial KPIs regularly

Use specific commands like "show low stock report" or "calculate optimal levels" for focused analysis."""
            
            return report
            
        except Exception as e:
            return f"❌ Error during comprehensive analysis: {str(e)}"
    
    def _handle_multi_agent_task(self, message: str) -> str:
        """Handle tasks requiring coordination between multiple agents."""
        try:
            # Extract specific requirements from message
            if "low stock" in message.lower() and "calculate" in message.lower():
                # Get low stock items and calculate reorder requirements
                inventory_result = self.agent_tools['inventory'].execute({'message': 'generate low stock report'})
                calculator_result = self.agent_tools['calculator'].execute({'message': 'calculate reorder points'})
                
                return f"""🤝 **MULTI-AGENT COORDINATION: Low Stock Analysis & Calculations**
═══════════════════════════════════════

📊 **INVENTORY ANALYSIS:**
{inventory_result['result']}

═══════════════════════════════════════

🧮 **REORDER CALCULATIONS:**
{calculator_result['result']}

═══════════════════════════════════════

🎯 **COORDINATED RECOMMENDATIONS:**
The inventory agent has identified items needing attention, and the calculator agent has determined optimal reorder quantities and timing. Cross-reference these reports to prioritize actions."""
            
            elif "abc" in message.lower() and "stock" in message.lower():
                # Combine ABC analysis with stock level analysis
                abc_result = self.agent_tools['calculator'].execute({'message': 'perform abc analysis'})
                stock_result = self.agent_tools['inventory'].execute({'message': 'analyze stock levels'})
                
                return f"""🤝 **MULTI-AGENT COORDINATION: ABC Analysis & Stock Monitoring**
═══════════════════════════════════════

📊 **ABC CLASSIFICATION:**
{abc_result['result']}

═══════════════════════════════════════

📈 **STOCK LEVEL ANALYSIS:**
{stock_result['result']}

═══════════════════════════════════════

🎯 **STRATEGIC INSIGHTS:**
Combine ABC classification with current stock levels to prioritize management attention and resources effectively."""
            
            else:
                return self._handle_general_coordination(message)
                
        except Exception as e:
            return f"❌ Error in multi-agent coordination: {str(e)}"
    
    def _handle_data_update(self, message: str) -> str:
        """Handle inventory data updates through Google Sheets."""
        try:
            # Parse update request
            if "add" in message.lower():
                return """📝 **ADD NEW PRODUCT:**

To add a new product, I need:
• Product ID (e.g., LAPTOP002)
• Product Name
• Quantity
• Price
• Category

Example: "Add product LAPTOP002, Gaming Laptop Pro, 25 units, $1599.99, Electronics"

Or use the format: add LAPTOP002 "Gaming Laptop Pro" 25 1599.99 Electronics"""
            
            elif "update" in message.lower():
                # Try to extract product ID and new values
                product_id = self._extract_product_id(message)
                
                if product_id:
                    # Check current status first
                    result = self.sheets_tool.execute(GoogleSheetsInventoryInput(action="check", product_id=product_id))
                    
                    if result.success:
                        current = result.result
                        return f"""📝 **UPDATE PRODUCT: {product_id}**

Current Status:
• Product: {current['product_name']}
• Quantity: {current['quantity']} units
• Price: ${current['price']:.2f}
• Category: {current['category']}

To update, specify what to change:
• "Update {product_id} quantity to 50"
• "Update {product_id} price to 1299.99"
• "Set {product_id} stock to 30 units"

What would you like to update?"""
                    else:
                        return f"❌ Product {product_id} not found. Available products can be seen with 'list all products'"
                else:
                    return "❌ Please specify a product ID to update (e.g., LAPTOP001)"
            
            else:
                return """📝 **INVENTORY DATA UPDATES:**

I can help you update your Google Sheets inventory:

🆕 **Add Products:**
• "Add new product" - I'll guide you through the process
• "Add LAPTOP002 'Gaming Laptop' 25 1599.99 Electronics" - Direct add

🔄 **Update Existing:**
• "Update LAPTOP001 quantity to 50"
• "Update PHONE001 price to 899.99"
• "Check TABLET001" - See current status first

📋 **View Data:**
• "List all products" - See everything
• "Search Electronics" - Filter by category

What would you like to update?"""
                
        except Exception as e:
            return f"❌ Error handling data update: {str(e)}"
    
    def _generate_dashboard(self) -> str:
        """Generate an executive dashboard combining key metrics."""
        try:
            # Get key metrics from both agents
            inventory_summary = self.agent_tools['inventory'].execute({'message': 'generate inventory summary'})
            financial_metrics = self.agent_tools['calculator'].execute({'message': 'calculate inventory values'})
            alerts = self.agent_tools['inventory'].execute({'message': 'generate stock alerts'})
            
            # Get sheet info for real-time status
            sheet_info = self.sheets_tool.get_sheet_info()
            
            dashboard = f"""📊 **INVENTORY MANAGEMENT DASHBOARD**
═══════════════════════════════════════

🔄 **REAL-TIME STATUS:**
• Last Updated: {sheet_info.get('last_sync', 'Unknown')}
• Data Source: Google Sheets
• Total Products: {sheet_info.get('total_products', 'N/A')}
• Total Value: ${sheet_info.get('total_inventory_value', 0):,.2f}

🚨 **URGENT ALERTS:**
{alerts['result']}

═══════════════════════════════════════

📈 **KEY METRICS:**
{inventory_summary['result']}

═══════════════════════════════════════

💰 **FINANCIAL OVERVIEW:**
{financial_metrics['result']}

═══════════════════════════════════════

🎯 **QUICK ACTIONS:**
• "Show low stock report" - Items needing reorder
• "Calculate reorder points" - Optimization recommendations  
• "Perform ABC analysis" - Strategic classification
• "Generate action plan" - Prioritized next steps

Dashboard refreshed from live Google Sheets data! 🔄"""
            
            return dashboard
            
        except Exception as e:
            return f"❌ Error generating dashboard: {str(e)}"
    
    def _delegate_to_inventory_agent(self, message: str) -> str:
        """Delegate to inventory analysis agent."""
        try:
            result = self.agent_tools['inventory'].execute({'message': message})
            
            # Add coordinator context
            response = f"""📊 **INVENTORY ANALYSIS RESULTS:**
═══════════════════════════════════════

{result['result']}

═══════════════════════════════════════

🤖 **Coordinator Note:** This analysis was performed by the Inventory Agent. 
For financial calculations or reorder optimization, try commands like:
• "Calculate reorder points"
• "Generate financial report"
• "Perform ABC analysis"
"""
            
            return response
            
        except Exception as e:
            return f"❌ Error delegating to inventory agent: {str(e)}"
    
    def _delegate_to_calculator_agent(self, message: str) -> str:
        """Delegate to stock calculator agent."""
        try:
            result = self.agent_tools['calculator'].execute({'message': message})
            
            # Add coordinator context
            response = f"""🧮 **CALCULATION RESULTS:**
═══════════════════════════════════════

{result['result']}

═══════════════════════════════════════

🤖 **Coordinator Note:** These calculations were performed by the Stock Calculator Agent.
For stock level analysis or alerts, try commands like:
• "Analyze stock levels"
• "Show low stock report"
• "Generate stock alerts"
"""
            
            return response
            
        except Exception as e:
            return f"❌ Error delegating to calculator agent: {str(e)}"
    
    def _delegate_to_transaction_agent(self, message: str) -> str:
        """Delegate to transaction agent."""
        try:
            result = self.agent_tools['transaction'].execute({'message': message})
            
            # Add coordinator context
            response = f"""💰 **TRANSACTION RESULTS:**
═══════════════════════════════════════

{result['result']}

═══════════════════════════════════════

🤖 **Coordinator Note:** This transaction was processed by the Transaction Agent.
Inventory levels have been automatically updated in Google Sheets.
For inventory analysis or calculations, try commands like:
• "Analyze stock levels"
• "Calculate reorder points"
• "Show transaction history"
"""
            
            return response
            
        except Exception as e:
            return f"❌ Error delegating to transaction agent: {str(e)}"
    
    def _generate_action_plan(self, message: str) -> str:
        """Generate prioritized action plan based on current inventory status."""
        try:
            # Get critical information from both agents
            alerts = self.agent_tools['inventory'].execute({'message': 'generate stock alerts'})
            reorders = self.agent_tools['calculator'].execute({'message': 'calculate reorder points'})
            
            # Analyze the results to create prioritized actions
            action_plan = f"""🎯 **INVENTORY ACTION PLAN**
═══════════════════════════════════════

📋 **IMMEDIATE ACTIONS (Today):**

{self._extract_urgent_actions(alerts['result'])}

📅 **SHORT-TERM ACTIONS (This Week):**

{self._extract_short_term_actions(reorders['result'])}

📈 **STRATEGIC ACTIONS (This Month):**

• Review and optimize inventory policies
• Implement ABC classification management
• Analyze supplier performance and terms
• Consider automation for reorder processes

💰 **FINANCIAL PRIORITIES:**

• Calculate total investment needed for reorders
• Review carrying costs and optimize stock levels
• Negotiate better terms with key suppliers
• Implement inventory KPI tracking

🔄 **MONITORING SETUP:**

• Daily: Check critical stock alerts
• Weekly: Review reorder recommendations
• Monthly: Analyze turnover and financial metrics
• Quarterly: Perform comprehensive ABC analysis

═══════════════════════════════════════

🤖 **Next Steps:** Use specific commands to dive deeper into any area:
• "Show low stock report" - Detailed reorder list
• "Calculate optimal stock levels" - Optimization recommendations
• "Generate financial report" - Investment analysis"""
            
            return action_plan
            
        except Exception as e:
            return f"❌ Error generating action plan: {str(e)}"
    
    def _extract_urgent_actions(self, alerts_text: str) -> str:
        """Extract urgent actions from alerts."""
        if "NO URGENT STOCK ALERTS" in alerts_text:
            return "✅ No urgent actions required - all stock levels are adequate"
        
        actions = []
        if "OUT OF STOCK" in alerts_text:
            actions.append("🚨 Place emergency orders for out-of-stock items")
        if "CRITICAL" in alerts_text:
            actions.append("⚠️ Review and approve urgent purchase orders")
        if "Immediate reorder" in alerts_text:
            actions.append("📞 Contact suppliers for expedited delivery")
        
        return "\n".join(f"• {action}" for action in actions) if actions else "✅ No immediate actions required"
    
    def _extract_short_term_actions(self, reorders_text: str) -> str:
        """Extract short-term actions from reorder calculations."""
        actions = [
            "📊 Review reorder point calculations and adjust if needed",
            "💰 Prepare purchase orders for items below reorder points",
            "🤝 Negotiate bulk pricing with suppliers for large orders",
            "📈 Update demand forecasts based on recent sales trends"
        ]
        
        return "\n".join(f"• {action}" for action in actions)
    
    def _handle_general_coordination(self, message: str) -> str:
        """Handle general coordination requests."""
        return f"""🤖 **INVENTORY COORDINATOR READY!**

I orchestrate multiple specialized agents for comprehensive inventory management:

🏢 **MULTI-AGENT CAPABILITIES:**

📊 **Inventory Agent** - Stock Analysis & Monitoring:
• "Analyze stock levels" - Complete inventory analysis
• "Show low stock report" - Items needing reorder
• "Generate stock alerts" - Urgent attention items
• "Check LAPTOP001" - Specific product status

🧮 **Stock Calculator Agent** - Financial & Optimization:
• "Calculate reorder points" - When to reorder
• "Generate financial report" - Investment analysis
• "Perform ABC analysis" - Strategic classification
• "Calculate optimal stock levels" - Min/max recommendations

💰 **Transaction Agent** - Sales & Purchase Management:
• "Sell 2 LAPTOP001 for $1299.99 to John Doe" - Process sales
• "Purchase 10 LAPTOP001 at $1200 each" - Handle restocking
• "Show transaction history" - View recent transactions
• "Daily summary" - Transaction analytics

🤝 **COORDINATED ANALYSIS:**
• "Generate dashboard" - Executive overview
• "Comprehensive analysis" - Full multi-agent report
• "Generate action plan" - Prioritized next steps
• "Low stock and calculate reorders" - Combined analysis

📝 **DATA MANAGEMENT:**
• "Add new product" - Add to Google Sheets
• "Update LAPTOP001 quantity to 50" - Modify inventory
• "List all products" - View current data

🎯 **What would you like me to coordinate?**

Your message: "{message}"
"""
    
    def _extract_product_id(self, message: str) -> str:
        """Extract product ID from message."""
        import re
        pattern = r'\b[A-Z]+\d+\b'
        matches = re.findall(pattern, message.upper())
        return matches[0] if matches else ""
    
    def get_available_agents(self) -> Dict[str, Dict[str, Any]]:
        """Get information about available specialist agents."""
        return {
            name: tool.get_schema() 
            for name, tool in self.agent_tools.items()
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        try:
            sheet_info = self.sheets_tool.get_sheet_info()
            
            return {
                "coordinator_status": "Active",
                "inventory_agent": "Ready",
                "calculator_agent": "Ready", 
                "google_sheets": "Connected" if not sheet_info.get('error') else "Error",
                "total_products": sheet_info.get('total_products', 0),
                "total_value": sheet_info.get('total_inventory_value', 0),
                "last_sync": sheet_info.get('last_sync', 'Unknown')
            }
            
        except Exception as e:
            return {
                "coordinator_status": "Active",
                "error": str(e)
            }