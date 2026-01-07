"""
Inventory Management System - Multi-Agent Streamlit Interface
Connected to the database Google Sheets for real-time inventory management.
"""

import streamlit as st
import os
import sys
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime

# Add src to path for imports
sys.path.append('src')

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import our agents and tools
try:
    from agents.inventory_coordinator_agent import InventoryCoordinatorAgent
    from agents.inventory_agent import InventoryAgent
    from agents.stock_calculator_agent import StockCalculatorAgent
    from tools.google_sheets_inventory_tool import GoogleSheetsInventoryTool, GoogleSheetsInventoryInput
    AGENTS_AVAILABLE = True
except ImportError as e:
    AGENTS_AVAILABLE = False
    st.error(f"❌ Could not import agents: {e}")

# Page configuration
st.set_page_config(
    page_title="📊 Inventory Management System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .agent-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .alert-critical {
        background-color: #ffebee;
        color: #c62828;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border-left: 4px solid #f44336;
    }
    .alert-warning {
        background-color: #fff3e0;
        color: #ef6c00;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border-left: 4px solid #ff9800;
    }
    .alert-success {
        background-color: #e8f5e8;
        color: #2e7d32;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border-left: 4px solid #4caf50;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function."""
    
    # Header
    st.markdown('<h1 class="main-header">📊 Inventory Management System</h1>', unsafe_allow_html=True)
    st.markdown("**Multi-Agent System connected to your Google Sheets**")
    
    # Check system status
    if not AGENTS_AVAILABLE:
        st.error("❌ Agent system not available. Please check your installation.")
        return
    
    # Initialize session state
    if 'coordinator' not in st.session_state:
        spreadsheet_id = os.getenv("GOOGLE_SHEETS_INVENTORY_ID")
        st.session_state.coordinator = InventoryCoordinatorAgent(spreadsheet_id=spreadsheet_id)
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("## 🧭 Navigation")
        
        page = st.selectbox(
            "Choose a section:",
            [
                "🏠 Dashboard",
                "📊 Inventory Analysis", 
                "🧮 Stock Calculations",
                "🤖 Multi-Agent Chat",
                "📝 Data Management",
                "⚙️ System Settings"
            ]
        )
        
        # System status in sidebar
        st.markdown("---")
        st.markdown("### 🔄 System Status")
        
        try:
            status = st.session_state.coordinator.get_system_status()
            
            if status.get('google_sheets') == 'Connected':
                st.success("✅ Google Sheets Connected")
                st.metric("Products", status.get('total_products', 0))
                st.metric("Total Value", f"${status.get('total_value', 0):,.2f}")
            else:
                st.warning("⚠️ Google Sheets: Using Mock Data")
                
        except Exception as e:
            st.error(f"❌ Status Error: {str(e)[:50]}...")
    
    # Route to different pages
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "📊 Inventory Analysis":
        show_inventory_analysis()
    elif page == "🧮 Stock Calculations":
        show_stock_calculations()
    elif page == "🤖 Multi-Agent Chat":
        show_multi_agent_chat()
    elif page == "📝 Data Management":
        show_data_management()
    elif page == "⚙️ System Settings":
        show_system_settings()

def show_dashboard():
    """Display executive dashboard."""
    st.markdown("## 🏠 Executive Dashboard")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🔄 Refresh Dashboard", type="primary"):
            with st.spinner("Generating dashboard..."):
                response = st.session_state.coordinator.process_message("generate dashboard")
                st.markdown(response)
        
        # Auto-load dashboard on first visit
        if 'dashboard_loaded' not in st.session_state:
            with st.spinner("Loading dashboard..."):
                response = st.session_state.coordinator.process_message("generate dashboard")
                st.markdown(response)
                st.session_state.dashboard_loaded = True
    
    with col2:
        st.markdown("### 🚀 Quick Actions")
        
        if st.button("🚨 Stock Alerts"):
            with st.spinner("Checking alerts..."):
                response = st.session_state.coordinator.process_message("generate stock alerts")
                st.markdown(response)
        
        if st.button("📋 Low Stock Report"):
            with st.spinner("Generating report..."):
                response = st.session_state.coordinator.process_message("show low stock report")
                st.markdown(response)
        
        if st.button("💰 Financial Summary"):
            with st.spinner("Calculating..."):
                response = st.session_state.coordinator.process_message("calculate inventory values")
                st.markdown(response)
        
        if st.button("🎯 Action Plan"):
            with st.spinner("Creating plan..."):
                response = st.session_state.coordinator.process_message("generate action plan")
                st.markdown(response)

def show_inventory_analysis():
    """Display inventory analysis interface."""
    st.markdown("## 📊 Inventory Analysis")
    st.markdown("*Powered by the Inventory Agent*")
    
    # Analysis options
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📈 Stock Level Analysis")
        
        if st.button("🔍 Complete Stock Analysis"):
            with st.spinner("Analyzing stock levels..."):
                response = st.session_state.coordinator.process_message("analyze stock levels")
                st.markdown(response)
        
        if st.button("⚠️ Low Stock Report"):
            with st.spinner("Generating low stock report..."):
                response = st.session_state.coordinator.process_message("generate low stock report")
                st.markdown(response)
        
        if st.button("📋 Inventory Summary"):
            with st.spinner("Creating summary..."):
                response = st.session_state.coordinator.process_message("generate inventory summary")
                st.markdown(response)
    
    with col2:
        st.markdown("### 🔍 Product & Category Analysis")
        
        # Product lookup
        product_id = st.text_input("Product ID:", placeholder="e.g., LAPTOP001")
        if st.button("📦 Check Product") and product_id:
            with st.spinner(f"Checking {product_id}..."):
                response = st.session_state.coordinator.process_message(f"check {product_id}")
                st.markdown(response)
        
        # Category analysis
        category = st.selectbox("Category:", ["", "Electronics", "Audio", "Accessories"])
        if st.button("📂 Analyze Category") and category:
            with st.spinner(f"Analyzing {category}..."):
                response = st.session_state.coordinator.process_message(f"analyze {category} category")
                st.markdown(response)
    
    # Custom analysis
    st.markdown("---")
    st.markdown("### 💬 Custom Analysis")
    
    custom_query = st.text_input(
        "Ask the Inventory Agent:",
        placeholder="e.g., 'Show me all critical stock items' or 'What's the status of Electronics?'"
    )
    
    if st.button("🤖 Analyze") and custom_query:
        with st.spinner("Processing analysis..."):
            response = st.session_state.coordinator._delegate_to_inventory_agent(custom_query)
            st.markdown(response)

def show_stock_calculations():
    """Display stock calculation interface."""
    st.markdown("## 🧮 Stock Calculations")
    st.markdown("*Powered by the Stock Calculator Agent*")
    
    # Calculation categories
    tab1, tab2, tab3 = st.tabs(["📊 Reorder & Optimization", "💰 Financial Analysis", "📈 Advanced Analytics"])
    
    with tab1:
        st.markdown("### 🔄 Reorder Point Calculations")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("📋 Calculate Reorder Points"):
                with st.spinner("Calculating reorder points..."):
                    response = st.session_state.coordinator.process_message("calculate reorder points")
                    st.markdown(response)
            
            if st.button("⚙️ Optimal Stock Levels"):
                with st.spinner("Calculating optimal levels..."):
                    response = st.session_state.coordinator.process_message("calculate optimal stock levels")
                    st.markdown(response)
        
        with col2:
            # Product-specific calculations
            product_id = st.text_input("Calculate for Product:", placeholder="e.g., LAPTOP001")
            if st.button("🔢 Product Calculations") and product_id:
                with st.spinner(f"Calculating metrics for {product_id}..."):
                    response = st.session_state.coordinator.process_message(f"calculate metrics for {product_id}")
                    st.markdown(response)
    
    with tab2:
        st.markdown("### 💰 Financial Analysis")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("💵 Inventory Values"):
                with st.spinner("Calculating inventory values..."):
                    response = st.session_state.coordinator.process_message("calculate inventory values")
                    st.markdown(response)
            
            if st.button("📊 Financial Report"):
                with st.spinner("Generating financial report..."):
                    response = st.session_state.coordinator.process_message("generate financial report")
                    st.markdown(response)
        
        with col2:
            # Category financial analysis
            category = st.selectbox("Financial Analysis for Category:", ["", "Electronics", "Audio", "Accessories"])
            if st.button("📂 Category Financials") and category:
                with st.spinner(f"Analyzing {category} financials..."):
                    response = st.session_state.coordinator.process_message(f"calculate {category} category")
                    st.markdown(response)
    
    with tab3:
        st.markdown("### 📈 Advanced Analytics")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🔄 Turnover Analysis"):
                with st.spinner("Analyzing inventory turnover..."):
                    response = st.session_state.coordinator.process_message("analyze inventory turnover")
                    st.markdown(response)
        
        with col2:
            if st.button("🎯 ABC Analysis"):
                with st.spinner("Performing ABC analysis..."):
                    response = st.session_state.coordinator.process_message("perform abc analysis")
                    st.markdown(response)
    
    # Custom calculations
    st.markdown("---")
    st.markdown("### 💬 Custom Calculations")
    
    calc_query = st.text_input(
        "Ask the Calculator Agent:",
        placeholder="e.g., 'Calculate EOQ for all products' or 'What's the turnover for Electronics?'"
    )
    
    if st.button("🧮 Calculate") and calc_query:
        with st.spinner("Processing calculation..."):
            response = st.session_state.coordinator._delegate_to_calculator_agent(calc_query)
            st.markdown(response)

def show_multi_agent_chat():
    """Display multi-agent chat interface."""
    st.markdown("## 🤖 Multi-Agent Chat")
    st.markdown("*Coordinate between Inventory Agent and Stock Calculator Agent*")
    
    # Chat interface
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for i, (user_msg, agent_response) in enumerate(st.session_state.chat_history):
        with st.container():
            st.markdown(f"**You:** {user_msg}")
            st.markdown(f"**Coordinator:** {agent_response}")
            st.markdown("---")
    
    # Chat input
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_input(
            "Message:",
            placeholder="e.g., 'Show me low stock items and calculate reorder quantities'",
            key="chat_input"
        )
    
    with col2:
        send_button = st.button("📤 Send", type="primary")
    
    if send_button and user_input:
        with st.spinner("Processing with multi-agent system..."):
            response = st.session_state.coordinator.process_message(user_input)
            
            # Add to chat history
            st.session_state.chat_history.append((user_input, response))
            
            # Clear input and rerun to show new message
            st.rerun()
    
    # Quick action buttons
    st.markdown("### 🚀 Quick Multi-Agent Commands")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Comprehensive Analysis"):
            with st.spinner("Running comprehensive analysis..."):
                response = st.session_state.coordinator.process_message("comprehensive analysis")
                st.session_state.chat_history.append(("Comprehensive Analysis", response))
                st.rerun()
    
    with col2:
        if st.button("⚠️ Low Stock + Calculations"):
            with st.spinner("Analyzing low stock and calculating reorders..."):
                response = st.session_state.coordinator.process_message("low stock and calculate reorders")
                st.session_state.chat_history.append(("Low Stock + Calculations", response))
                st.rerun()
    
    with col3:
        if st.button("📊 ABC + Stock Analysis"):
            with st.spinner("Combining ABC analysis with stock monitoring..."):
                response = st.session_state.coordinator.process_message("abc analysis and stock levels")
                st.session_state.chat_history.append(("ABC + Stock Analysis", response))
                st.rerun()
    
    # Clear chat history
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

def show_data_management():
    """Display data management interface."""
    st.markdown("## 📝 Data Management")
    st.markdown("*Update your Google Sheets inventory data*")
    
    tab1, tab2, tab3 = st.tabs(["📋 View Data", "➕ Add Products", "✏️ Update Products"])
    
    with tab1:
        st.markdown("### 📊 Current Inventory Data")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("📋 List All Products"):
                with st.spinner("Loading all products..."):
                    try:
                        sheets_tool = GoogleSheetsInventoryTool()
                        result = sheets_tool.execute(GoogleSheetsInventoryInput(action="list_all"))
                        
                        if result.success:
                            products = result.result
                            df = pd.DataFrame(products)
                            st.dataframe(df, use_container_width=True)
                            
                            # Summary stats
                            st.markdown("### 📊 Summary")
                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                st.metric("Total Products", len(products))
                            with col_b:
                                total_units = sum(p["quantity"] for p in products)
                                st.metric("Total Units", f"{total_units:,}")
                            with col_c:
                                total_value = sum(p["quantity"] * p["price"] for p in products)
                                st.metric("Total Value", f"${total_value:,.2f}")
                        else:
                            st.error(f"❌ Error loading data: {result.error}")
                            
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        with col2:
            # Search functionality
            search_term = st.text_input("Search Products:", placeholder="Product name or ID")
            category_filter = st.selectbox("Filter by Category:", ["", "Electronics", "Audio", "Accessories"])
            
            if st.button("🔍 Search") and (search_term or category_filter):
                with st.spinner("Searching..."):
                    try:
                        sheets_tool = GoogleSheetsInventoryTool()
                        result = sheets_tool.execute(GoogleSheetsInventoryInput(
                            action="search",
                            search_term=search_term,
                            category=category_filter
                        ))
                        
                        if result.success:
                            products = result.result
                            if products:
                                df = pd.DataFrame(products)
                                st.dataframe(df, use_container_width=True)
                            else:
                                st.warning("No products found matching your criteria")
                        else:
                            st.error(f"❌ Search error: {result.error}")
                            
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    with tab2:
        st.markdown("### ➕ Add New Product")
        
        with st.form("add_product_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                product_id = st.text_input("Product ID*", placeholder="e.g., LAPTOP002")
                product_name = st.text_input("Product Name*", placeholder="e.g., Gaming Laptop Pro")
                quantity = st.number_input("Quantity*", min_value=0, value=0)
            
            with col2:
                price = st.number_input("Price*", min_value=0.0, value=0.0, format="%.2f")
                category = st.selectbox("Category*", ["Electronics", "Audio", "Accessories"])
            
            submitted = st.form_submit_button("➕ Add Product", type="primary")
            
            if submitted:
                if all([product_id, product_name, quantity >= 0, price > 0, category]):
                    with st.spinner("Adding product..."):
                        try:
                            sheets_tool = GoogleSheetsInventoryTool()
                            result = sheets_tool.execute(GoogleSheetsInventoryInput(
                                action="add",
                                product_id=product_id,
                                product_name=product_name,
                                quantity=quantity,
                                price=price,
                                category=category
                            ))
                            
                            if result.success:
                                st.success(f"✅ Product {product_id} added successfully!")
                                st.json(result.result)
                            else:
                                st.error(f"❌ Error adding product: {result.error}")
                                
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                else:
                    st.error("❌ Please fill in all required fields")
    
    with tab3:
        st.markdown("### ✏️ Update Existing Product")
        
        # Product selection
        product_id = st.text_input("Product ID to Update:", placeholder="e.g., LAPTOP001")
        
        if st.button("🔍 Load Product") and product_id:
            with st.spinner("Loading product..."):
                try:
                    sheets_tool = GoogleSheetsInventoryTool()
                    result = sheets_tool.execute(GoogleSheetsInventoryInput(action="check", product_id=product_id))
                    
                    if result.success:
                        st.session_state.current_product = result.result
                        st.success(f"✅ Loaded product: {result.result['product_name']}")
                    else:
                        st.error(f"❌ Product not found: {result.error}")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        # Update form
        if 'current_product' in st.session_state:
            product = st.session_state.current_product
            
            st.markdown(f"**Updating: {product['product_name']} ({product['product_id']})**")
            
            with st.form("update_product_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_quantity = st.number_input(
                        "New Quantity", 
                        min_value=0, 
                        value=product['quantity'],
                        help=f"Current: {product['quantity']}"
                    )
                
                with col2:
                    new_price = st.number_input(
                        "New Price", 
                        min_value=0.0, 
                        value=float(product['price']),
                        format="%.2f",
                        help=f"Current: ${product['price']:.2f}"
                    )
                
                update_submitted = st.form_submit_button("💾 Update Product", type="primary")
                
                if update_submitted:
                    with st.spinner("Updating product..."):
                        try:
                            sheets_tool = GoogleSheetsInventoryTool()
                            result = sheets_tool.execute(GoogleSheetsInventoryInput(
                                action="update",
                                product_id=product['product_id'],
                                quantity=new_quantity,
                                price=new_price
                            ))
                            
                            if result.success:
                                st.success("✅ Product updated successfully!")
                                st.json(result.result)
                                # Clear the current product to force reload
                                del st.session_state.current_product
                            else:
                                st.error(f"❌ Error updating product: {result.error}")
                                
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")

def show_system_settings():
    """Display system settings and configuration."""
    st.markdown("## ⚙️ System Settings")
    
    tab1, tab2, tab3 = st.tabs(["🔧 Configuration", "📊 Agent Status", "🔗 Google Sheets Setup"])
    
    with tab1:
        st.markdown("### 🔧 System Configuration")
        
        # Environment variables
        st.markdown("#### 🔑 API Keys & Configuration")
        
        google_api_key = os.getenv("GOOGLE_API_KEY")
        sheets_id = os.getenv("GOOGLE_SHEETS_INVENTORY_ID")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if google_api_key:
                st.success(f"✅ Google API Key: ...{google_api_key[-4:]}")
            else:
                st.error("❌ Google API Key not configured")
            
            if sheets_id:
                st.success(f"✅ Sheets ID: ...{sheets_id[-10:]}")
            else:
                st.warning("⚠️ Google Sheets ID not configured")
        
        with col2:
            st.markdown("**Configuration Files:**")
            st.code("""
# .env file should contain:
GOOGLE_API_KEY=your_api_key_here
GOOGLE_SHEETS_INVENTORY_ID=your_sheet_id_here
            """)
    
    with tab2:
        st.markdown("### 📊 Agent System Status")
        
        try:
            status = st.session_state.coordinator.get_system_status()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Coordinator", status.get('coordinator_status', 'Unknown'))
                st.metric("Inventory Agent", status.get('inventory_agent', 'Unknown'))
            
            with col2:
                st.metric("Calculator Agent", status.get('calculator_agent', 'Unknown'))
                st.metric("Google Sheets", status.get('google_sheets', 'Unknown'))
            
            with col3:
                st.metric("Total Products", status.get('total_products', 0))
                st.metric("Total Value", f"${status.get('total_value', 0):,.2f}")
            
            # Detailed status
            st.markdown("#### 🔍 Detailed Status")
            st.json(status)
            
        except Exception as e:
            st.error(f"❌ Error getting system status: {str(e)}")
    
    with tab3:
        st.markdown("### 🔗 Google Sheets Setup")
        
        st.markdown("""
        #### 📋 Setup Instructions:
        
        1. **Create Google Sheet**: Use the sample data structure
        2. **Get Sheet ID**: From the URL of your Google Sheet
        3. **Configure API**: Enable Google Sheets API in Google Cloud Console
        4. **Set Environment**: Add sheet ID to your `.env` file
        
        #### 📊 Required Sheet Structure:
        """)
        
        # Show sample data structure
        sample_data = {
            "Product ID": ["LAPTOP001", "PHONE001", "TABLET001"],
            "Product Name": ["Gaming Laptop", "Smartphone Pro", "Tablet Air"],
            "Quantity": [15, 45, 8],
            "Price": [1299.99, 899.99, 599.99],
            "Category": ["Electronics", "Electronics", "Electronics"],
            "Status": ["in_stock", "in_stock", "low_stock"],
            "Last Updated": ["2024-01-06 10:00:00", "2024-01-06 10:00:00", "2024-01-06 10:00:00"]
        }
        
        df = pd.DataFrame(sample_data)
        st.dataframe(df, use_container_width=True)
        
        st.markdown("""
        #### 🔧 Testing Connection:
        """)
        
        if st.button("🧪 Test Google Sheets Connection"):
            with st.spinner("Testing connection..."):
                try:
                    sheets_tool = GoogleSheetsInventoryTool()
                    sheet_info = sheets_tool.get_sheet_info()
                    
                    if 'error' not in sheet_info:
                        st.success("✅ Google Sheets connection successful!")
                        st.json(sheet_info)
                    else:
                        st.error(f"❌ Connection failed: {sheet_info['error']}")
                        
                except Exception as e:
                    st.error(f"❌ Connection test failed: {str(e)}")
                    st.markdown("""
                    **Common Issues:**
                    - Google Sheets API not enabled
                    - Invalid sheet ID
                    - Missing credentials
                    - Sheet permissions
                    
                    **See GOOGLE_SHEETS_SETUP.md for detailed instructions**
                    """)

if __name__ == "__main__":
    main()
