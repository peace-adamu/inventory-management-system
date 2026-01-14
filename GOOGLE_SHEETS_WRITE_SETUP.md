# 🔧 Google Sheets Write Access Setup

## Enable Adding Products Through the App

Currently, your app uses a public Google Sheet (read-only). To enable adding/editing products directly through the app, you need write access.

## 🎯 **Option 1: Service Account (Recommended for Production)**

### **Step 1: Create Service Account**

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Select your project** (or create new one)
3. **Enable Google Sheets API**:
   - Go to "APIs & Services" > "Library"
   - Search "Google Sheets API"
   - Click "Enable"

4. **Create Service Account**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Name: `inventory-management-service`
   - Click "Create and Continue"

5. **Download Credentials**:
   - Click on your service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create New Key"
   - Choose "JSON"
   - Download the file (keep it secure!)

### **Step 2: Share Sheet with Service Account**

1. **Open your Google Sheet**
2. **Click "Share"**
3. **Add the service account email** (from the JSON file)
   - Email looks like: `inventory-management-service@your-project.iam.gserviceaccount.com`
4. **Set permission to "Editor"**
5. **Click "Send"**

### **Step 3: Configure Streamlit Secrets**

In Streamlit Cloud, add this to your secrets:

```toml
GOOGLE_API_KEY = "AIzaSyBjBqEmFZqswUus4GYyZS1S0zAgm2rIZKs"
GOOGLE_SHEETS_INVENTORY_ID = "1CyA1nOnQ8Bzdqi60Xqk8dWcL32Zpx6ktUw_-HTeKNE8"

# Add your service account credentials (paste the entire JSON content)
GOOGLE_SERVICE_ACCOUNT_JSON = '''
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "inventory-management-service@your-project.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
'''
```

## 🎯 **Option 2: OAuth (Simpler Setup)**

### **Step 1: Create OAuth Credentials**

1. **Go to Google Cloud Console** > "APIs & Services" > "Credentials"
2. **Click "Create Credentials"** > "OAuth 2.0 Client IDs"
3. **Application type**: "Web application"
4. **Authorized redirect URIs**: Add your Streamlit app URL
5. **Download the credentials JSON**

### **Step 2: Configure OAuth in App**

Add to Streamlit secrets:
```toml
GOOGLE_OAUTH_CLIENT_ID = "your-client-id"
GOOGLE_OAUTH_CLIENT_SECRET = "your-client-secret"
```

## 🎯 **Option 3: Quick Test (Development Only)**

For testing, you can:

1. **Make your sheet editable by anyone with link**:
   - Open Google Sheet
   - Click "Share" > "Change to anyone with the link"
   - Set permission to "Editor" (⚠️ Not secure for production)

2. **Use Google Apps Script** (Advanced):
   - Create a Google Apps Script web app
   - Proxy requests through the script

## 🔐 **Security Best Practices**

- ✅ Use Service Account for production
- ✅ Keep credentials secure (never commit to Git)
- ✅ Use environment variables/secrets
- ✅ Limit sheet permissions to specific service account
- ❌ Never make sheets publicly editable
- ❌ Never expose credentials in code

## 🧪 **Testing Write Access**

Once configured, test by:
1. Going to "Data Management" in your app
2. Adding a test product
3. Checking if it appears in your Google Sheet

## 🆘 **Troubleshooting**

**"Permission denied"**: Service account not shared with sheet
**"Invalid credentials"**: Check JSON format in secrets
**"API not enabled"**: Enable Google Sheets API in Cloud Console
**"Quota exceeded"**: Check API usage limits

---

**Recommendation**: Start with Option 1 (Service Account) for the most reliable write access.