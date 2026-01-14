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

# Visualization libraries
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Add src to path for imports
sys.path.append('src')

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# For Streamlit Cloud, also try to load from secrets
try:
    import streamlit as st
    # Set environment variables from Streamlit secrets if available
    if hasattr(st, 'secrets'):
        for key in st.secrets:
            if key not in os.environ:
                os.environ[key] = st.secrets[key]
except:
    pass

# Import our agents and tools
try:
    from agents.inventory_coordinator_agent import InventoryCoordinatorAgent
    from agents.inventory_agent import InventoryAgent
    from agents.stock_calculator_agent import StockCalculatorAgent
    from agents.transaction_agent import TransactionAgent
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
    st.markdown("**Multi-Agent System connected to Google Sheets as Database**")
    
    # Check system status
    if not AGENTS_AVAILABLE:
        st.error("❌ Agent system not available. Please check your installation.")
        return
    
    # Initialize session state
    if 'coordinator' not in st.session_state:
        # Try to get spreadsheet ID from multiple sources
        spreadsheet_id = (
            os.getenv("GOOGLE_SHEETS_INVENTORY_ID") or 
            st.secrets.get("GOOGLE_SHEETS_INVENTORY_ID", None) or
            "1CyA1nOnQ8Bzdqi60Xqk8dWcL32Zpx6ktUw_-HTeKNE8"  # Fallback to your sheet
        )
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
                "💰 Transaction Management",
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
    elif page == "💰 Transaction Management":
        show_transaction_management()
    elif page == "🤖 Multi-Agent Chat":
        show_multi_agent_chat()
    elif page == "📝 Data Management":
        show_data_management()
    elif page == "⚙️ System Settings":
        show_system_settings()

def show_dashboard():
    """Display executive dashboard with visualizations."""
    st.markdown("## 🏠 Executive Dashboard")
    
    # Get inventory data for visualizations
    try:
        from src.tools.google_sheets_inventory_tool import GoogleSheetsInventoryTool, GoogleSheetsInventoryInput
        sheets_tool = GoogleSheetsInventoryTool()
        result = sheets_tool.execute(GoogleSheetsInventoryInput(action="list_all"))
        
        if result.success and result.result:
            products_data = result.result
            df = pd.DataFrame(products_data)
            
            # Display visualizations
            show_inventory_visualizations(df)
            
        else:
            st.warning("⚠️ Could not load inventory data for visualizations")
            show_basic_dashboard()
            
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        show_basic_dashboard()

def show_inventory_visualizations(df: pd.DataFrame):
    """Display comprehensive inventory visualizations."""
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_products = len(df)
        st.metric("📦 Total Products", total_products)
    
    with col2:
        total_quantity = df['quantity'].sum()
        st.metric("📊 Total Units", f"{total_quantity:,}")
    
    with col3:
        total_value = (df['quantity'] * df['price']).sum()
        st.metric("💰 Total Value", f"${total_value:,.2f}")
    
    with col4:
        avg_price = df['price'].mean()
        st.metric("💵 Avg Price", f"${avg_price:.2f}")
    
    st.markdown("---")
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        # Stock Status Distribution (Pie Chart)
        st.markdown("### 📊 Stock Status Distribution")
        
        if PLOTLY_AVAILABLE:
            status_counts = df['status'].value_counts()
            
            colors = {
                'in_stock': '#28a745',
                'low_stock': '#ffc107', 
                'out_of_stock': '#dc3545'
            }
            
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Stock Status Breakdown",
                color=status_counts.index,
                color_discrete_map=colors
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Fallback to simple metrics
            status_counts = df['status'].value_counts()
            for status, count in status_counts.items():
                st.metric(status.replace('_', ' ').title(), count)
    
    with col2:
        # Category Value Distribution (Bar Chart)
        st.markdown("### 💰 Value by Category")
        
        if PLOTLY_AVAILABLE:
            df['total_value'] = df['quantity'] * df['price']
            category_values = df.groupby('category')['total_value'].sum().sort_values(ascending=False)
            
            fig = px.bar(
                x=category_values.index,
                y=category_values.values,
                title="Inventory Value by Category",
                labels={'x': 'Category', 'y': 'Total Value ($)'},
                color=category_values.values,
                color_continuous_scale='viridis'
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Fallback to dataframe
            df['total_value'] = df['quantity'] * df['price']
            category_summary = df.groupby('category').agg({
                'total_value': 'sum',
                'quantity': 'sum'
            }).round(2)
            st.dataframe(category_summary)
    
    # Charts Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        # Top Products by Value (Horizontal Bar)
        st.markdown("### 🏆 Top Products by Value")
        
        if PLOTLY_AVAILABLE:
            df['product_value'] = df['quantity'] * df['price']
            top_products = df.nlargest(10, 'product_value')
            
            fig = px.bar(
                top_products,
                x='product_value',
                y='product_name',
                orientation='h',
                title="Top 10 Products by Total Value",
                labels={'product_value': 'Total Value ($)', 'product_name': 'Product'},
                color='product_value',
                color_continuous_scale='blues'
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Fallback to dataframe
            df['product_value'] = df['quantity'] * df['price']
            top_products = df.nlargest(5, 'product_value')[['product_name', 'product_value']]
            st.dataframe(top_products)
    
    with col2:
        # Stock Levels (Scatter Plot)
        st.markdown("### 📈 Stock Levels vs Price")
        
        if PLOTLY_AVAILABLE:
            fig = px.scatter(
                df,
                x='price',
                y='quantity',
                size='quantity',
                color='category',
                hover_name='product_name',
                title="Stock Quantity vs Unit Price",
                labels={'price': 'Unit Price ($)', 'quantity': 'Stock Quantity'}
            )
            
            # Add threshold lines
            fig.add_hline(y=10, line_dash="dash", line_color="orange", 
                         annotation_text="Low Stock Threshold")
            fig.add_hline(y=0, line_dash="dash", line_color="red", 
                         annotation_text="Out of Stock")
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Fallback to simple scatter
            st.scatter_chart(df.set_index('product_name')[['price', 'quantity']])
    
    # Charts Row 3 - Financial Analysis
    st.markdown("---")
    st.markdown("### 💹 Financial Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Price Distribution
        st.markdown("#### 💵 Price Distribution")
        
        if PLOTLY_AVAILABLE:
            fig = px.histogram(
                df,
                x='price',
                nbins=20,
                title="Product Price Distribution",
                labels={'price': 'Unit Price ($)', 'count': 'Number of Products'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.bar_chart(df['price'].value_counts())
    
    with col2:
        # Quantity Distribution
        st.markdown("#### 📦 Quantity Distribution")
        
        if PLOTLY_AVAILABLE:
            fig = px.histogram(
                df,
                x='quantity',
                nbins=15,
                title="Stock Quantity Distribution",
                labels={'quantity': 'Stock Quantity', 'count': 'Number of Products'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.bar_chart(df['quantity'].value_counts())
    
    with col3:
        # Category Summary
        st.markdown("#### 📊 Category Summary")
        
        category_stats = df.groupby('category').agg({
            'quantity': ['sum', 'mean'],
            'price': 'mean',
            'product_name': 'count'
        }).round(2)
        
        category_stats.columns = ['Total Qty', 'Avg Qty', 'Avg Price', 'Products']
        st.dataframe(category_stats)
    
    # Stock Alerts Section
    st.markdown("---")
    st.markdown("### 🚨 Real-Time Stock Alerts")
    
    # Identify problem items with enhanced categorization
    out_of_stock = df[df['quantity'] == 0]
    critical_stock = df[(df['quantity'] > 0) & (df['quantity'] <= 5)]
    low_stock = df[(df['quantity'] > 5) & (df['quantity'] <= 10)]
    
    alert_col1, alert_col2, alert_col3 = st.columns(3)
    
    with alert_col1:
        if len(out_of_stock) > 0:
            st.error(f"🚨 **{len(out_of_stock)} OUT OF STOCK**")
            st.markdown("**Cannot sell these items:**")
            for _, item in out_of_stock.head(3).iterrows():
                st.write(f"• {item['product_name']} ({item['product_id']})")
                st.write(f"  💰 Lost revenue: ${item['price']:.2f}/unit")
            if len(out_of_stock) > 3:
                st.write(f"... and {len(out_of_stock) - 3} more")
        else:
            st.success("✅ No out of stock items")
    
    with alert_col2:
        if len(critical_stock) > 0:
            st.error(f"🔴 **{len(critical_stock)} CRITICAL STOCK**")
            st.markdown("**Limit sales to 1 per customer:**")
            for _, item in critical_stock.head(3).iterrows():
                st.write(f"• {item['product_name']}: {item['quantity']} left")
                st.write(f"  💰 At risk: ${item['quantity'] * item['price']:.2f}")
            if len(critical_stock) > 3:
                st.write(f"... and {len(critical_stock) - 3} more")
        else:
            st.success("✅ No critical stock alerts")
    
    with alert_col3:
        if len(low_stock) > 0:
            st.warning(f"⚠️ **{len(low_stock)} LOW STOCK**")
            st.markdown("**Monitor closely:**")
            for _, item in low_stock.head(3).iterrows():
                st.write(f"• {item['product_name']}: {item['quantity']} units")
                st.write(f"  💰 Value: ${item['quantity'] * item['price']:.2f}")
            if len(low_stock) > 3:
                st.write(f"... and {len(low_stock) - 3} more")
        else:
            st.success("✅ No low stock alerts")
    
    # Quick Actions for Stock Alerts
    if len(out_of_stock) > 0 or len(critical_stock) > 0 or len(low_stock) > 0:
        st.markdown("#### 🚀 Quick Actions")
        
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            if st.button("📧 Email Stock Alert", help="Send stock alert to management"):
                st.info("📧 Stock alert email functionality would be implemented here")
        
        with action_col2:
            if st.button("📋 Generate Reorder List", help="Create purchase order list"):
                reorder_items = pd.concat([out_of_stock, critical_stock, low_stock])
                if not reorder_items.empty:
                    st.markdown("**Suggested Reorder Quantities:**")
                    for _, item in reorder_items.iterrows():
                        suggested_qty = max(20, item['quantity'] * 3)  # Suggest 3x current or minimum 20
                        st.write(f"• {item['product_name']}: {suggested_qty} units")
        
        with action_col3:
            if st.button("🔄 Refresh Stock Data", help="Reload latest inventory data"):
                st.rerun()
    
    # Interactive Data Table
    st.markdown("---")
    st.markdown("### 📋 Interactive Inventory Data")
    
    # Add filters
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        category_filter = st.selectbox("Filter by Category", ["All"] + list(df['category'].unique()))
    
    with filter_col2:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    
    with filter_col3:
        min_quantity = st.number_input("Min Quantity", min_value=0, value=0)
    
    # Apply filters
    filtered_df = df.copy()
    
    if category_filter != "All":
        filtered_df = filtered_df[filtered_df['category'] == category_filter]
    
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    
    filtered_df = filtered_df[filtered_df['quantity'] >= min_quantity]
    
    # Display filtered data
    st.dataframe(
        filtered_df[['product_id', 'product_name', 'quantity', 'price', 'category', 'status']],
        use_container_width=True
    )
    
    st.markdown(f"**Showing {len(filtered_df)} of {len(df)} products**")

def show_basic_dashboard():
    """Fallback dashboard without data visualizations."""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🔄 Refresh Dashboard", type="primary"):
            with st.spinner("Generating dashboard..."):
                response = st.session_state.coordinator.process_message("generate dashboard")
                st.markdown(response)
    
    with col2:
        st.markdown("### 🚀 Quick Actions")
        
        # Quick action buttons
        if st.button("🚨 Stock Alerts", key="alerts_btn"):
            with st.spinner("Checking alerts..."):
                response = st.session_state.coordinator.process_message("generate stock alerts")
                st.markdown("### 🚨 Stock Alerts")
                st.markdown(response)
        
        if st.button("📋 Low Stock Report", key="low_stock_btn"):
            with st.spinner("Generating report..."):
                response = st.session_state.coordinator.process_message("show low stock report")
                st.markdown("### 📋 Low Stock Report")
                st.markdown(response)
        
        if st.button("💰 Financial Summary", key="financial_btn"):
            with st.spinner("Calculating..."):
                response = st.session_state.coordinator.process_message("calculate inventory values")
                st.markdown("### 💰 Financial Summary")
                st.markdown(response)
        
        if st.button("📊 Transaction Summary", key="transaction_btn"):
            with st.spinner("Loading transactions..."):
                response = st.session_state.coordinator.process_message("daily summary")
                st.markdown("### 📊 Today's Transactions")
                st.markdown(response)
    
    # Quick Sale Section
    st.markdown("---")
    st.markdown("### 💰 Quick Sale")
    
    with st.form("dashboard_quick_sale"):
        col_a, col_b, col_c = st.columns([2, 1, 1])
        
        with col_a:
            quick_product_id = st.text_input("Product ID", placeholder="e.g., LAPTOP001")
        
        with col_b:
            quick_quantity = st.number_input("Quantity", min_value=1, value=1)
        
        with col_c:
            st.write("") # Spacer
            quick_sale_btn = st.form_submit_button("💰 Quick Sale", type="primary")
        
        if quick_sale_btn and quick_product_id:
            with st.spinner("Processing quick sale..."):
                try:
                    # Initialize transaction agent if not exists
                    if 'transaction_agent' not in st.session_state:
                        spreadsheet_id = (
                            os.getenv("GOOGLE_SHEETS_INVENTORY_ID") or 
                            st.secrets.get("GOOGLE_SHEETS_INVENTORY_ID", None) or
                            "1CyA1nOnQ8Bzdqi60Xqk8dWcL32Zpx6ktUw_-HTeKNE8"
                        )
                        st.session_state.transaction_agent = TransactionAgent(spreadsheet_id=spreadsheet_id)
                    
                    # Process the sale
                    message = f"Quick sale: {quick_quantity} {quick_product_id}"
                    response = st.session_state.transaction_agent.process_message(message)
                    
                    if "✅" in response:
                        st.success("✅ Quick sale completed!")
                        st.markdown(response)
                    else:
                        st.error("❌ Quick sale failed!")
                        st.markdown(response)
                        
                except Exception as e:
                    st.error(f"❌ Error processing quick sale: {str(e)}")

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
    
    col1, col2, col3, col4 = st.columns(4)
    
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
    
    with col4:
        if st.button("💰 Transaction Analytics"):
            with st.spinner("Generating transaction analytics..."):
                response = st.session_state.coordinator.process_message("sales report and daily summary")
                st.session_state.chat_history.append(("Transaction Analytics", response))
                st.rerun()
    
    # Clear chat history
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

def show_data_management():
    """Display data management interface."""
    st.markdown("## 📝 Data Management")
    st.markdown("*Update your Google Sheets inventory data*")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 View Data", "➕ Add Products", "✏️ Update Products", "💰 Quick Sale"])
    
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
        
        # Add information about sheet access
        st.info("ℹ️ **Note**: Adding products requires write access to Google Sheets. If using a public sheet, it will be read-only.")
        
        # Quick add from template
        st.markdown("#### 🚀 Quick Add Templates")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💻 Add Electronics"):
                st.session_state.template_category = "Electronics"
                st.session_state.template_price = 500.00
        
        with col2:
            if st.button("🎧 Add Audio"):
                st.session_state.template_category = "Audio"
                st.session_state.template_price = 150.00
        
        with col3:
            if st.button("🖱️ Add Accessories"):
                st.session_state.template_category = "Accessories"
                st.session_state.template_price = 50.00
        
        st.markdown("---")
        
        with st.form("add_product_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                product_id = st.text_input("Product ID*", placeholder="e.g., LAPTOP002", help="Use format: CATEGORY + NUMBER (e.g., LAPTOP002, PHONE003)")
                product_name = st.text_input("Product Name*", placeholder="e.g., Gaming Laptop Pro")
                quantity = st.number_input("Initial Quantity*", min_value=0, value=10, help="Starting stock level")
            
            with col2:
                # Use template values if set
                default_price = st.session_state.get('template_price', 0.0)
                default_category = st.session_state.get('template_category', "Electronics")
                
                price = st.number_input("Unit Price*", min_value=0.01, value=default_price, format="%.2f")
                category = st.selectbox("Category*", ["Electronics", "Audio", "Accessories"], 
                                      index=["Electronics", "Audio", "Accessories"].index(default_category) if default_category in ["Electronics", "Audio", "Accessories"] else 0)
                
                # Additional fields
                supplier = st.text_input("Supplier", placeholder="Optional - supplier name")
            
            # Product preview
            if product_id and product_name and quantity >= 0 and price > 0:
                st.markdown("#### 👀 Product Preview")
                preview_col1, preview_col2 = st.columns(2)
                
                with preview_col1:
                    st.metric("Product ID", product_id)
                    st.metric("Initial Stock", f"{quantity} units")
                
                with preview_col2:
                    st.metric("Unit Price", f"${price:.2f}")
                    st.metric("Initial Value", f"${quantity * price:.2f}")
            
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
                                
                                # Show success details
                                success_data = result.result
                                st.markdown("#### 🎉 Product Added Successfully!")
                                
                                col_a, col_b, col_c = st.columns(3)
                                with col_a:
                                    st.metric("Product ID", success_data['product_id'])
                                with col_b:
                                    st.metric("Stock Level", f"{success_data['quantity']} units")
                                with col_c:
                                    st.metric("Total Value", f"${success_data['quantity'] * success_data['price']:.2f}")
                                
                                # Clear template values
                                if 'template_category' in st.session_state:
                                    del st.session_state.template_category
                                if 'template_price' in st.session_state:
                                    del st.session_state.template_price
                                
                                # Auto-refresh after 2 seconds
                                st.balloons()
                                st.rerun()
                            else:
                                if "read-only" in str(result.error).lower():
                                    st.warning("⚠️ **Sheet is Read-Only**: Your Google Sheet is configured as public/read-only. To add products, you need:")
                                    st.markdown("""
                                    1. **Create a private Google Sheet** with edit permissions
                                    2. **Set up Google Sheets API credentials** for write access
                                    3. **Or manually add products** to your Google Sheet
                                    
                                    For now, you can view and analyze existing data, but cannot add new products through the app.
                                    """)
                                elif "already exists" in str(result.error).lower():
                                    st.error(f"❌ Product ID '{product_id}' already exists! Please use a different ID.")
                                    
                                    # Suggest alternative IDs
                                    base_id = ''.join([c for c in product_id if c.isalpha()])
                                    number_part = ''.join([c for c in product_id if c.isdigit()])
                                    if number_part:
                                        next_num = int(number_part) + 1
                                        suggested_id = f"{base_id}{next_num:03d}"
                                        st.info(f"💡 **Suggestion**: Try using '{suggested_id}' instead")
                                else:
                                    st.error(f"❌ Error adding product: {result.error}")
                                
                        except Exception as e:
                            st.error(f"❌ Unexpected error: {str(e)}")
                            st.info("💡 **Tip**: If you're using a public Google Sheet, it's read-only. Consider setting up proper Google Sheets API credentials for write access.")
                else:
                    st.error("❌ Please fill in all required fields")
        
        # Bulk add section
        st.markdown("---")
        st.markdown("#### 📦 Bulk Add Products")
        
        with st.expander("🔧 Bulk Add from CSV"):
            st.markdown("""
            **Upload a CSV file with the following columns:**
            - Product ID, Product Name, Quantity, Price, Category
            
            **Example CSV format:**
            ```
            Product ID,Product Name,Quantity,Price,Category
            LAPTOP003,Gaming Laptop Ultra,5,1599.99,Electronics
            MOUSE002,Wireless Gaming Mouse,25,89.99,Accessories
            ```
            """)
            
            uploaded_file = st.file_uploader("Choose CSV file", type="csv")
            
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file)
                    st.dataframe(df)
                    
                    if st.button("📦 Add All Products from CSV"):
                        with st.spinner("Adding products from CSV..."):
                            success_count = 0
                            error_count = 0
                            
                            for _, row in df.iterrows():
                                try:
                                    sheets_tool = GoogleSheetsInventoryTool()
                                    result = sheets_tool.execute(GoogleSheetsInventoryInput(
                                        action="add",
                                        product_id=row['Product ID'],
                                        product_name=row['Product Name'],
                                        quantity=int(row['Quantity']),
                                        price=float(row['Price']),
                                        category=row['Category']
                                    ))
                                    
                                    if result.success:
                                        success_count += 1
                                    else:
                                        error_count += 1
                                        
                                except Exception as e:
                                    error_count += 1
                            
                            if success_count > 0:
                                st.success(f"✅ Successfully added {success_count} products!")
                            if error_count > 0:
                                st.warning(f"⚠️ {error_count} products failed to add (may already exist)")
                                
                except Exception as e:
                    st.error(f"❌ Error reading CSV file: {str(e)}")
                    st.info("💡 Make sure your CSV has the correct column names and format")
    
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
    
    with tab4:
        st.markdown("### 💰 Quick Sale")
        st.info("🚀 **Fast sales processing with automatic stock deduction and low stock alerts**")
        
        # Quick product lookup
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_product = st.text_input("🔍 Search Product:", placeholder="Type product name or ID...")
            
        with col2:
            if st.button("🔍 Search", type="secondary"):
                if search_product:
                    with st.spinner("Searching products..."):
                        try:
                            sheets_tool = GoogleSheetsInventoryTool()
                            result = sheets_tool.execute(GoogleSheetsInventoryInput(
                                action="search",
                                search_term=search_product
                            ))
                            
                            if result.success and result.result:
                                st.session_state.search_results = result.result
                            else:
                                st.warning("No products found matching your search")
                                
                        except Exception as e:
                            st.error(f"❌ Search error: {str(e)}")
        
        # Display search results for quick selection
        if 'search_results' in st.session_state and st.session_state.search_results:
            st.markdown("#### 📦 Available Products:")
            
            for product in st.session_state.search_results[:5]:  # Show top 5 results
                with st.expander(f"🏷️ {product['product_name']} ({product['product_id']}) - Stock: {product['quantity']} units"):
                    col_a, col_b, col_c = st.columns([2, 1, 1])
                    
                    with col_a:
                        st.write(f"**Category:** {product['category']}")
                        st.write(f"**Price:** ${product['price']:.2f}")
                        
                        # Stock status indicator
                        if product['quantity'] == 0:
                            st.error("🚨 OUT OF STOCK")
                        elif product['quantity'] <= 10:
                            st.warning(f"⚠️ LOW STOCK ({product['quantity']} left)")
                        else:
                            st.success(f"✅ In Stock ({product['quantity']} available)")
                    
                    with col_b:
                        sale_qty = st.number_input(
                            "Qty to Sell:", 
                            min_value=1, 
                            max_value=product['quantity'] if product['quantity'] > 0 else 0,
                            value=1,
                            key=f"qty_{product['product_id']}"
                        )
                    
                    with col_c:
                        if product['quantity'] > 0:
                            if st.button(f"💰 Sell", key=f"sell_{product['product_id']}", type="primary"):
                                # Process quick sale
                                with st.spinner("Processing sale..."):
                                    try:
                                        # Initialize transaction agent if not exists
                                        if 'transaction_agent' not in st.session_state:
                                            spreadsheet_id = (
                                                os.getenv("GOOGLE_SHEETS_INVENTORY_ID") or 
                                                st.secrets.get("GOOGLE_SHEETS_INVENTORY_ID", None) or
                                                "1CyA1nOnQ8Bzdqi60Xqk8dWcL32Zpx6ktUw_-HTeKNE8"
                                            )
                                            st.session_state.transaction_agent = TransactionAgent(spreadsheet_id=spreadsheet_id)
                                        
                                        # Process the sale
                                        message = f"Sell {sale_qty} {product['product_id']} for ${product['price']:.2f}"
                                        response = st.session_state.transaction_agent.process_message(message)
                                        
                                        if "✅" in response:
                                            st.success(f"✅ Sale completed! Sold {sale_qty} units of {product['product_name']}")
                                            
                                            # Check for low stock alert
                                            new_stock = product['quantity'] - sale_qty
                                            if new_stock <= 10 and new_stock > 0:
                                                st.warning(f"⚠️ **LOW STOCK ALERT**: {product['product_name']} now has only {new_stock} units left!")
                                            elif new_stock == 0:
                                                st.error(f"🚨 **OUT OF STOCK**: {product['product_name']} is now out of stock!")
                                            
                                            # Clear search results to refresh
                                            if 'search_results' in st.session_state:
                                                del st.session_state.search_results
                                            st.rerun()
                                        else:
                                            st.error("❌ Sale failed!")
                                            st.text(response)
                                            
                                    except Exception as e:
                                        st.error(f"❌ Error processing sale: {str(e)}")
                        else:
                            st.error("❌ Out of Stock")
        
        # Manual sale form for direct entry
        st.markdown("---")
        st.markdown("#### ✏️ Manual Sale Entry")
        
        with st.form("quick_sale_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                manual_product_id = st.text_input("Product ID*", placeholder="e.g., LAPTOP001")
                manual_quantity = st.number_input("Quantity*", min_value=1, value=1)
            
            with col2:
                manual_price = st.number_input("Unit Price*", min_value=0.01, value=0.01, format="%.2f")
                customer_name = st.text_input("Customer", placeholder="Optional")
            
            with col3:
                st.write("") # Spacer
                st.write("") # Spacer
                manual_sale_submitted = st.form_submit_button("💰 Process Sale", type="primary")
            
            if manual_sale_submitted:
                if all([manual_product_id, manual_quantity > 0, manual_price > 0]):
                    with st.spinner("Processing manual sale..."):
                        try:
                            # Initialize transaction agent if not exists
                            if 'transaction_agent' not in st.session_state:
                                spreadsheet_id = (
                                    os.getenv("GOOGLE_SHEETS_INVENTORY_ID") or 
                                    st.secrets.get("GOOGLE_SHEETS_INVENTORY_ID", None) or
                                    "1CyA1nOnQ8Bzdqi60Xqk8dWcL32Zpx6ktUw_-HTeKNE8"
                                )
                                st.session_state.transaction_agent = TransactionAgent(spreadsheet_id=spreadsheet_id)
                            
                            # Build sale message
                            message = f"Sell {manual_quantity} {manual_product_id} for ${manual_price:.2f}"
                            if customer_name:
                                message += f" to {customer_name}"
                            
                            response = st.session_state.transaction_agent.process_message(message)
                            
                            if "✅" in response:
                                st.success("✅ Manual sale completed successfully!")
                                st.markdown(response)
                                st.rerun()
                            else:
                                st.error("❌ Manual sale failed!")
                                st.markdown(response)
                                
                        except Exception as e:
                            st.error(f"❌ Error processing manual sale: {str(e)}")
                else:
                    st.error("❌ Please fill in all required fields")

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

def show_transaction_management():
    """Display transaction management interface."""
    st.markdown("## 💰 Transaction Management")
    st.markdown("*Process sales, purchases, and track transaction history*")
    
    # Initialize transaction agent if not in session state
    if 'transaction_agent' not in st.session_state:
        spreadsheet_id = (
            os.getenv("GOOGLE_SHEETS_INVENTORY_ID") or 
            st.secrets.get("GOOGLE_SHEETS_INVENTORY_ID", None) or
            "1CyA1nOnQ8Bzdqi60Xqk8dWcL32Zpx6ktUw_-HTeKNE8"
        )
        st.session_state.transaction_agent = TransactionAgent(spreadsheet_id=spreadsheet_id)
    
    tab1, tab2, tab3, tab4 = st.tabs(["💰 Process Sale", "📦 Purchase/Restock", "📊 Transaction History", "📈 Analytics"])
    
    with tab1:
        st.markdown("### 💰 Process Sale Transaction")
        st.info("💡 **Sales automatically reduce inventory levels and create transaction records**")
        
        with st.form("sale_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                sale_product_id = st.text_input("Product ID*", placeholder="e.g., LAPTOP001")
                sale_quantity = st.number_input("Quantity*", min_value=1, value=1)
                sale_price = st.number_input("Unit Price*", min_value=0.01, value=0.01, format="%.2f")
            
            with col2:
                customer_name = st.text_input("Customer Name", placeholder="e.g., John Doe")
                customer_email = st.text_input("Customer Email", placeholder="e.g., john@example.com")
                sale_notes = st.text_area("Notes", placeholder="Order details, special instructions...")
            
            sale_submitted = st.form_submit_button("💰 Process Sale", type="primary")
            
            if sale_submitted:
                if all([sale_product_id, sale_quantity > 0, sale_price > 0]):
                    customer_info = f"{customer_name} - {customer_email}".strip(" - ") if customer_name or customer_email else None
                    
                    with st.spinner("Processing sale..."):
                        try:
                            message = f"Sell {sale_quantity} {sale_product_id} for ${sale_price:.2f}"
                            if customer_info:
                                message += f" to {customer_info}"
                            if sale_notes:
                                message += f" - {sale_notes}"
                            
                            response = st.session_state.transaction_agent.process_message(message)
                            
                            if "✅" in response:
                                st.success("Sale completed successfully!")
                                st.markdown(response)
                                # Clear form by rerunning
                                st.rerun()
                            else:
                                st.error("Sale failed!")
                                st.markdown(response)
                                
                        except Exception as e:
                            st.error(f"❌ Error processing sale: {str(e)}")
                else:
                    st.error("❌ Please fill in all required fields")
    
    with tab2:
        st.markdown("### 📦 Purchase/Restock Transaction")
        st.info("💡 **Purchases automatically increase inventory levels and track costs**")
        
        with st.form("purchase_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                purchase_product_id = st.text_input("Product ID*", placeholder="e.g., LAPTOP001")
                purchase_quantity = st.number_input("Quantity*", min_value=1, value=1)
                purchase_cost = st.number_input("Unit Cost*", min_value=0.01, value=0.01, format="%.2f")
            
            with col2:
                supplier_name = st.text_input("Supplier", placeholder="e.g., Tech Supplier Inc")
                purchase_notes = st.text_area("Notes", placeholder="Purchase order details, delivery info...")
            
            purchase_submitted = st.form_submit_button("📦 Process Purchase", type="primary")
            
            if purchase_submitted:
                if all([purchase_product_id, purchase_quantity > 0, purchase_cost > 0]):
                    with st.spinner("Processing purchase..."):
                        try:
                            message = f"Purchase {purchase_quantity} {purchase_product_id} at ${purchase_cost:.2f} each"
                            if supplier_name:
                                message += f" from {supplier_name}"
                            if purchase_notes:
                                message += f" - {purchase_notes}"
                            
                            response = st.session_state.transaction_agent.process_message(message)
                            
                            if "✅" in response:
                                st.success("Purchase completed successfully!")
                                st.markdown(response)
                                # Clear form by rerunning
                                st.rerun()
                            else:
                                st.error("Purchase failed!")
                                st.markdown(response)
                                
                        except Exception as e:
                            st.error(f"❌ Error processing purchase: {str(e)}")
                else:
                    st.error("❌ Please fill in all required fields")
    
    with tab3:
        st.markdown("### 📊 Transaction History")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("📋 Show All Transactions"):
                with st.spinner("Loading transaction history..."):
                    response = st.session_state.transaction_agent.process_message("show transaction history")
                    st.markdown(response)
            
            if st.button("📅 Today's Summary"):
                with st.spinner("Generating daily summary..."):
                    response = st.session_state.transaction_agent.process_message("daily summary")
                    st.markdown(response)
        
        with col2:
            # Product-specific history
            product_id = st.text_input("Product History:", placeholder="e.g., LAPTOP001")
            if st.button("🔍 Product History") and product_id:
                with st.spinner(f"Loading history for {product_id}..."):
                    response = st.session_state.transaction_agent.process_message(f"product history for {product_id}")
                    st.markdown(response)
    
    with tab4:
        st.markdown("### 📈 Transaction Analytics")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("💰 Sales Report"):
                with st.spinner("Generating sales report..."):
                    response = st.session_state.transaction_agent.process_message("sales report")
                    st.markdown(response)
        
        with col2:
            if st.button("📊 Revenue Analysis"):
                with st.spinner("Analyzing revenue..."):
                    response = st.session_state.transaction_agent.process_message("sales analytics")
                    st.markdown(response)
        
        # Quick actions
        st.markdown("---")
        st.markdown("### 🚀 Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Stock Adjustment"):
                st.info("💡 Use format: 'Adjust LAPTOP001 by +5 units (reason)'")
                adjustment_query = st.text_input("Adjustment:", placeholder="Adjust LAPTOP001 by +5 (found extra)")
                if st.button("⚙️ Process Adjustment") and adjustment_query:
                    with st.spinner("Processing adjustment..."):
                        response = st.session_state.transaction_agent.process_message(adjustment_query)
                        st.markdown(response)
        
        with col2:
            if st.button("📊 Best Sellers"):
                with st.spinner("Finding best sellers..."):
                    response = st.session_state.transaction_agent.process_message("show best selling products")
                    st.markdown(response)
        
        with col3:
            if st.button("💹 Profit Analysis"):
                with st.spinner("Calculating profits..."):
                    response = st.session_state.transaction_agent.process_message("calculate profit margins")
                    st.markdown(response)

if __name__ == "__main__":
    main()
