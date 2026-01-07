# 🚀 Deployment Guide

## GitHub & Streamlit Cloud Deployment

### **Step 1: Push to GitHub**

1. **Initialize Git Repository** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Multi-Agent Inventory Management System"
   ```

2. **Create GitHub Repository**:
   - Go to [GitHub](https://github.com)
   - Click "New repository"
   - Name it: `inventory-management-system`
   - Make it **Public** (required for free Streamlit deployment)
   - Don't initialize with README (we already have one)

3. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/inventory-management-system.git
   git branch -M main
   git push -u origin main
   ```

### **Step 2: Deploy on Streamlit Cloud**

1. **Go to Streamlit Cloud**: https://share.streamlit.io/

2. **Connect GitHub**: Sign in with your GitHub account

3. **Deploy App**:
   - Click "New app"
   - Select your repository: `inventory-management-system`
   - Main file path: `inventory_management_app.py`
   - Click "Deploy!"

### **Step 3: Configure Environment Variables**

In Streamlit Cloud, add these secrets:

1. **Click "Manage app"** → **"Settings"** → **"Secrets"**

2. **Add your configuration**:
   ```toml
   GOOGLE_API_KEY = "AIzaSyBjBqEmFZqswUus4GYyZS1S0zAgm2rIZKs"
   GOOGLE_SHEETS_INVENTORY_ID = "1CyA1nOnQ8Bzdqi60Xqk8dWcL32Zpx6ktUw_-HTeKNE8"
   ```

3. **Save and restart** the app

### **Step 4: Test Your Deployed App**

Your app will be available at:
```
https://YOUR_USERNAME-inventory-management-system-inventory-management-app-xyz123.streamlit.app/
```

## 🔧 Local Development

To run locally:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/inventory-management-system.git
   cd inventory-management-system
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run the app**:
   ```bash
   streamlit run inventory_management_app.py
   ```

## 🎯 Features

- **Multi-Agent System**: Inventory analysis, stock calculations, coordination
- **Real-time Google Sheets**: Live inventory data integration
- **Interactive Dashboard**: Executive overview and analytics
- **Smart Recommendations**: Reorder points, ABC analysis, optimization
- **Natural Language**: Chat with agents using plain English

## 🔐 Security Notes

- Never commit `.env` files to GitHub
- Use Streamlit Cloud secrets for production
- Keep your Google Sheets publicly readable but not editable
- Regularly rotate API keys

## 📊 Sample Data

The system includes sample inventory data in `sample_inventory_sheet.csv`. Upload this to your Google Sheets to get started quickly.

## 🆘 Troubleshooting

**Common Issues:**

1. **"Module not found"**: Check `requirements.txt` and redeploy
2. **"Google Sheets access denied"**: Verify sheet is publicly accessible
3. **"API key invalid"**: Check secrets configuration in Streamlit Cloud
4. **"App won't start"**: Check logs in Streamlit Cloud dashboard

**Support:**
- Check the app logs in Streamlit Cloud
- Verify all environment variables are set
- Test Google Sheets access with `test_sheet_access.py`