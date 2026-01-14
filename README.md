# 📊 Multi-Agent Inventory Management System

A sophisticated inventory management system powered by specialized AI agents that connect to Google Sheets for real-time inventory tracking, analysis, and optimization.

## ✨ Enhanced Features (Latest Update)

### 🆕 **Direct Product Management**
- ➕ **Add Products Directly**: Add new inventory items through the web interface
- 🚀 **Quick Add Templates**: Pre-configured templates for Electronics, Audio, and Accessories
- 📦 **Bulk Import**: Upload CSV files to add multiple products at once
- ✅ **Smart Validation**: Automatic duplicate detection and ID suggestions
- 💡 **Real-time Preview**: See product details before adding

### 💰 **Advanced Sales Processing**
- 🛒 **Quick Sale Interface**: Process sales with automatic stock deduction
- 🔍 **Stock Availability Check**: Real-time inventory validation before sales
- 🚨 **Instant Alerts**: Immediate low stock warnings after each sale
- 👤 **Customer Tracking**: Record customer information with each transaction
- 📊 **Sales Analytics**: Performance metrics and revenue tracking

### 🚨 **Real-Time Stock Alerts**
- **🚨 Critical Alerts**: Out of stock items (cannot sell)
- **🔴 High Priority**: Critical stock (≤5 units, limit sales to 1 per customer)
- **🟡 Medium Priority**: Low stock (6-10 units, monitor closely)
- **💰 Financial Impact**: Calculate lost revenue and at-risk inventory value
- **📧 Action Items**: Automated reorder suggestions and management notifications

### 📈 **Enhanced Dashboard**
- **Interactive Visualizations**: Plotly charts for stock distribution and trends
- **Real-time Metrics**: Live inventory value and stock status indicators
- **Quick Actions**: One-click access to sales, alerts, and reports
- **Stock Status Grid**: Visual indicators for all inventory levels
- **Financial Overview**: Revenue, costs, and profit analysis

## 🤖 Multi-Agent Architecture

### 🏢 **Inventory Coordinator Agent**
The master orchestrator that manages the entire system:
- Routes requests to appropriate specialist agents
- Combines insights from multiple agents
- Generates comprehensive reports and dashboards
- Handles data updates and system coordination

### 📊 **Inventory Agent** 
Specializes in stock monitoring and analysis:
- **Stock Level Analysis**: Complete inventory health checks
- **Low Stock Reports**: Items needing immediate attention
- **Stock Alerts**: Critical and urgent notifications
- **Product Status**: Individual item monitoring
- **Category Analysis**: Performance by product category

### 🧮 **Stock Calculator Agent**
Handles all financial calculations and optimization:
- **Reorder Point Calculations**: When to reorder each product
- **Economic Order Quantity (EOQ)**: Optimal order sizes
- **Financial Analysis**: Inventory values and carrying costs
- **Turnover Analysis**: How fast products move
- **ABC Analysis**: Strategic product classification
- **Optimal Stock Levels**: Min/max recommendations

### 💰 **Sales Agent** *(New)*
Specialized in sales operations with automatic inventory management:
- **Quick Sales Processing**: Fast transaction processing with stock validation
- **Automatic Stock Deduction**: Real-time inventory updates after each sale
- **Stock Availability Checking**: Pre-sale inventory validation
- **Sales Analytics**: Revenue tracking and performance metrics
- **Customer Management**: Transaction history and customer information
- **Real-time Alerts**: Instant low stock notifications after sales

### 🔄 **Transaction Agent**
Manages all inventory movements and transaction history:
- **Sales Transactions**: Process customer purchases with stock updates
- **Purchase/Restock**: Handle supplier orders and inventory additions
- **Stock Adjustments**: Corrections and manual inventory changes
- **Transaction History**: Complete audit trail of all movements
- **Financial Tracking**: Revenue, costs, and profit calculations

## 🚀 Key Features

### 📈 **Real-Time Analysis**
- Live connection to your Google Sheets
- Instant stock level monitoring
- Automated alert generation
- Real-time financial calculations

### 🎯 **Intelligent Recommendations**
- Automated reorder point calculations
- Optimal stock level suggestions
- Financial optimization advice
- Strategic product classification

### 💰 **Financial Intelligence**
- Total inventory valuation
- Carrying cost analysis
- Turnover rate calculations
- ROI and profitability metrics

### 🔄 **Multi-Agent Coordination**
- Seamless agent collaboration
- Comprehensive analysis combining multiple perspectives
- Intelligent request routing
- Coordinated action plans

## 🛠️ Installation & Setup

### 1. **Install Dependencies**
```bash
pip install streamlit pandas python-dotenv pydantic
```

### 2. **Configure Environment**
Create a `.env` file:
```env
# Your Google API Key
GOOGLE_API_KEY=AIzaSyBjBqEmFZqswUus4GYyZS1S0zAgm2rIZKs

# Your Google Sheets ID (optional - will use mock data if not provided)
GOOGLE_SHEETS_INVENTORY_ID=your_google_sheet_id_here
```

### 3. **Google Sheets Setup** (Optional)
For full functionality with your own data:

1. **Create Google Sheet** with this structure:
   ```
   Product ID | Product Name | Quantity | Price | Category | Status | Last Updated
   LAPTOP001  | Gaming Laptop| 15       | 1299.99| Electronics| in_stock| 2024-01-06 10:00:00
   ```

2. **Get Sheet ID** from the URL:
   ```
   https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit
   ```

3. **Add to .env file**:
   ```env
   GOOGLE_SHEETS_INVENTORY_ID=your_sheet_id_here
   ```

### 4. **Launch the System**
```bash
# Easy launcher (recommended)
python run_inventory_app.py

# Or directly with Streamlit
streamlit run inventory_management_app.py

# Or test the system first
python test_inventory_agents.py
```

## 📱 User Interface

### 🏠 **Dashboard**
Executive overview with:
- Key performance metrics
- Urgent alerts and notifications
- Quick action buttons
- Real-time system status

### 📊 **Inventory Analysis**
Powered by the Inventory Agent:
- Complete stock level analysis
- Low stock reports
- Product and category breakdowns
- Custom analysis queries

### 🧮 **Stock Calculations**
Powered by the Stock Calculator Agent:
- Reorder point calculations
- Financial analysis and reports
- Turnover and ABC analysis
- Optimization recommendations

### 🤖 **Multi-Agent Chat**
Interactive interface for:
- Natural language queries
- Multi-agent coordination
- Comprehensive analysis requests
- Real-time agent collaboration

### 📝 **Data Management**
Direct Google Sheets integration:
- View current inventory
- Add new products
- Update existing items
- Search and filter data

## 💬 Example Commands

### 📊 **Inventory Analysis**
```
"Analyze stock levels"
"Show low stock report"
"Check LAPTOP001 status"
"Analyze Electronics category"
"Generate stock alerts"
```

### 🧮 **Calculations**
```
"Calculate reorder points"
"Generate financial report"
"Perform ABC analysis"
"Calculate optimal stock levels"
"Analyze inventory turnover"
```

### 🤝 **Multi-Agent Tasks**
```
"Comprehensive analysis"
"Low stock and calculate reorders"
"ABC analysis and stock levels"
"Generate action plan"
"Show dashboard"
```

### 📝 **Data Updates**
```
"Add new product LAPTOP002"
"Update LAPTOP001 quantity to 50"
"List all products"
"Search Electronics category"
```

## 🎯 Use Cases

### 📈 **Daily Operations**
- Monitor stock levels and alerts
- Check product availability
- Review urgent reorder needs
- Track inventory changes

### 💰 **Financial Management**
- Calculate total inventory value
- Analyze carrying costs
- Optimize stock investments
- Track profitability metrics

### 🔄 **Strategic Planning**
- ABC analysis for prioritization
- Turnover analysis for efficiency
- Optimal stock level planning
- Supplier negotiation support

### 📊 **Reporting**
- Executive dashboards
- Comprehensive analysis reports
- Action plans and recommendations
- Performance tracking

## 🔧 Technical Architecture

### 🏗️ **Agent Framework**
- **Base Agent Class**: Common functionality for all agents
- **Specialized Agents**: Domain-specific expertise
- **Tool Integration**: Google Sheets and calculation tools
- **Coordinator Pattern**: Intelligent request routing

### 🔗 **Google Sheets Integration**
- **Real-time Data**: Live connection to your sheets
- **CRUD Operations**: Create, read, update, delete
- **Mock Fallback**: Works without Google Sheets setup
- **Error Handling**: Graceful degradation

### 🖥️ **Streamlit Interface**
- **Multi-page Application**: Organized by functionality
- **Interactive Components**: Forms, buttons, charts
- **Real-time Updates**: Live data refresh
- **Responsive Design**: Works on desktop and mobile

## 🚨 Troubleshooting

### ❌ **Common Issues**

**"Agent system not available"**
- Check that all files are in the correct directories
- Ensure Python path includes the `src` folder
- Verify all dependencies are installed

**"Google Sheets connection failed"**
- Check your Google Sheets ID in `.env`
- Verify sheet permissions (public or shared)
- The system works with mock data if sheets unavailable

**"Import errors"**
- Install missing packages: `pip install streamlit pandas python-dotenv`
- Check Python version (3.7+ recommended)
- Ensure all project files are present

### 🔧 **Testing**
```bash
# Test the complete system
python test_inventory_agents.py

# Test individual components
python -c "from src.agents.inventory_coordinator_agent import InventoryCoordinatorAgent; print('✅ Agents working')"
```

## 📚 Project Structure

```
📁 Multi-Agent Inventory System/
├── 📄 inventory_management_app.py     # Main Streamlit application
├── 📄 run_inventory_app.py           # Easy launcher script
├── 📄 test_inventory_agents.py       # System testing script
├── 📄 .env                          # Environment configuration
├── 📁 src/
│   ├── 📁 agents/
│   │   ├── 📄 inventory_coordinator_agent.py    # Master coordinator
│   │   ├── 📄 inventory_agent.py               # Stock analysis specialist
│   │   ├── 📄 stock_calculator_agent.py        # Financial calculations
│   │   └── 📄 base_agent.py                    # Base agent framework
│   └── 📁 tools/
│       ├── 📄 google_sheets_inventory_tool.py  # Google Sheets integration
│       ├── 📄 calculator_tool.py               # Mathematical operations
│       └── 📄 base_tool.py                     # Base tool framework
└── 📄 INVENTORY_SYSTEM_README.md     # This documentation
```

## 🎉 Success Stories

### 📊 **What You Get**
- **Automated Monitoring**: Never miss low stock situations
- **Optimized Ordering**: Calculate exactly when and how much to order
- **Financial Insights**: Understand your inventory investment
- **Strategic Intelligence**: ABC analysis for better decision making
- **Time Savings**: Automated analysis instead of manual spreadsheet work

### 🚀 **Next Steps**
1. **Test the system** with the provided sample data
2. **Connect your Google Sheets** for real inventory data
3. **Explore the multi-agent capabilities** with natural language queries
4. **Set up regular monitoring** using the dashboard and alerts
5. **Optimize your inventory** using the calculation recommendations

## 🤝 Support

### 📖 **Documentation**
- See `GOOGLE_SHEETS_SETUP.md` for detailed Google Sheets configuration
- Check `test_inventory_agents.py` for system validation
- Review agent code in `src/agents/` for customization

### 🔧 **Customization**
- Modify thresholds in agent configuration
- Add new product categories
- Customize calculation parameters
- Extend with additional tools

---

**🎯 Ready to revolutionize your inventory management with AI agents!**

Launch with: `python run_inventory_app.py`