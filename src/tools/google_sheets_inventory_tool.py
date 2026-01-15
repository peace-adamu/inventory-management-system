"""
Google Sheets-powered inventory tool - demonstrates real-time cloud data integration.
"""

import os
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from src.tools.base_tool import BaseTool, ToolInput, ToolOutput

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False


class GoogleSheetsInventoryInput(ToolInput):
    """Input schema for Google Sheets inventory operations."""
    action: str = Field(description="Action: 'check', 'update', 'add', 'list_all', 'search'")
    product_id: Optional[str] = Field(default=None, description="Product ID (required for check/update)")
    product_name: Optional[str] = Field(default=None, description="Product name (for add/search)")
    quantity: Optional[int] = Field(default=None, description="Quantity (for add/update)")
    price: Optional[float] = Field(default=None, description="Price (for add/update)")
    category: Optional[str] = Field(default=None, description="Category (for add/search)")
    search_term: Optional[str] = Field(default=None, description="Search term (for search)")


class GoogleSheetsInventoryTool(BaseTool):
    """
    A Google Sheets-powered inventory tool.
    
    This demonstrates how to integrate Google Sheets as a real-time database
    for agent tools. Perfect for collaborative inventory management!
    """
    
    def __init__(self, 
                 spreadsheet_id: Optional[str] = None,
                 worksheet_name: str = "Inventory",
                 credentials_file: Optional[str] = None):
        super().__init__(
            name="google_sheets_inventory",
            description="Real-time Google Sheets inventory management system"
        )
        
        self.spreadsheet_id = spreadsheet_id or os.getenv("GOOGLE_SHEETS_INVENTORY_ID")
        self.worksheet_name = worksheet_name
        self.credentials_file = credentials_file or os.getenv("GOOGLE_CREDENTIALS_FILE")
        
        # Headers for the Google Sheet
        self.headers = [
            "Product ID", "Product Name", "Quantity", "Price", 
            "Category", "Status", "Last Updated"
        ]
        
        self._client = None
        self._worksheet = None
        self._public_data = None
        self._is_public_sheet = False
        
        if not GSPREAD_AVAILABLE:
            print("⚠️  gspread not installed. Install with: pip install gspread google-auth")
    
    def _get_client(self):
        """Initialize Google Sheets client."""
        if not GSPREAD_AVAILABLE:
            raise ImportError("gspread library not available. Install with: pip install gspread google-auth")
        
        if self._client is None:
            try:
                # First try service account credentials if available
                if self.credentials_file and os.path.exists(self.credentials_file):
                    scope = [
                        "https://spreadsheets.google.com/feeds",
                        "https://www.googleapis.com/auth/drive"
                    ]
                    creds = Credentials.from_service_account_file(self.credentials_file, scopes=scope)
                    self._client = gspread.authorize(creds)
                else:
                    # Try to use default credentials or OAuth
                    try:
                        self._client = gspread.service_account()
                    except Exception:
                        # Fallback to OAuth flow
                        try:
                            self._client = gspread.oauth()
                        except Exception:
                            # For public sheets, try anonymous access
                            import requests
                            # This will be handled in _get_worksheet with direct API calls
                            self._client = None
                            
            except Exception as e:
                # For public sheets, we'll handle this in _get_worksheet
                self._client = None
        
        return self._client
    
    def _get_worksheet(self):
        """Get the worksheet, creating it if necessary."""
        if self._worksheet is None:
            if not self.spreadsheet_id:
                raise ValueError("Google Sheets ID not provided. Set GOOGLE_SHEETS_INVENTORY_ID environment variable or pass spreadsheet_id")
            
            try:
                client = self._get_client()
                
                if client is None:
                    # Try to access public sheet directly via API
                    return self._access_public_sheet()
                
                spreadsheet = client.open_by_key(self.spreadsheet_id)
                
                try:
                    self._worksheet = spreadsheet.worksheet(self.worksheet_name)
                except gspread.WorksheetNotFound:
                    # Create the worksheet if it doesn't exist
                    self._worksheet = spreadsheet.add_worksheet(
                        title=self.worksheet_name, 
                        rows=1000, 
                        cols=len(self.headers)
                    )
                    # Add headers
                    self._worksheet.append_row(self.headers)
                    
            except Exception as e:
                # Try public sheet access as fallback
                try:
                    return self._access_public_sheet()
                except Exception:
                    raise ValueError(f"Cannot access spreadsheet {self.spreadsheet_id}. Check permissions and ID. Error: {e}")
        
        return self._worksheet
    
    def _access_public_sheet(self):
        """Access public Google Sheet via CSV export."""
        import requests
        import csv
        from io import StringIO
        
        # Google Sheets CSV export URL for public sheets (without gid parameter)
        csv_url = f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}/export?format=csv"
        
        try:
            response = requests.get(csv_url, timeout=15)
            response.raise_for_status()
            
            # Parse CSV data
            csv_data = StringIO(response.text)
            reader = csv.DictReader(csv_data)
            
            # Store data for later use
            self._public_data = list(reader)
            self._is_public_sheet = True
            
            return "public_sheet_access"
            
        except Exception as e:
            raise ValueError(f"Cannot access public sheet {self.spreadsheet_id}: {e}")
    
    def execute(self, input_data: GoogleSheetsInventoryInput) -> ToolOutput:
        """Execute the inventory operation."""
        try:
            if not GSPREAD_AVAILABLE:
                return ToolOutput(
                    success=False, 
                    result=None, 
                    error="Google Sheets integration not available. Install with: pip install gspread google-auth"
                )
            
            if input_data.action == "check":
                result = self._check_product(input_data.product_id)
            elif input_data.action == "update":
                result = self._update_product(input_data.product_id, input_data.quantity, input_data.price)
            elif input_data.action == "add":
                result = self._add_product(
                    input_data.product_id,
                    input_data.product_name,
                    input_data.quantity,
                    input_data.price,
                    input_data.category
                )
            elif input_data.action == "list_all":
                result = self._list_all_products()
            elif input_data.action == "search":
                result = self._search_products(input_data.search_term, input_data.category)
            else:
                return ToolOutput(success=False, result=None, error=f"Unknown action: {input_data.action}")
            
            return ToolOutput(success=True, result=result)
            
        except Exception as e:
            return ToolOutput(success=False, result=None, error=str(e))
    
    def _check_product(self, product_id: str) -> Dict[str, Any]:
        """Check a specific product in the Google Sheet."""
        if not product_id:
            raise ValueError("Product ID is required for check operation")
        
        # Handle public sheet access
        if self._is_public_sheet and self._public_data:
            for i, record in enumerate(self._public_data):
                if record.get("Product ID") == product_id:
                    quantity = int(record.get("Quantity", 0)) if record.get("Quantity") else 0
                    return {
                        "product_id": record.get("Product ID", ""),
                        "product_name": record.get("Product Name", ""),
                        "quantity": quantity,
                        "price": float(record.get("Price", 0)) if record.get("Price") else 0.0,
                        "category": record.get("Category", ""),
                        "status": record.get("Status", self._calculate_status(quantity)),
                        "last_updated": record.get("Last Updated", ""),
                        "row_number": i + 2  # +2 for header row and 0-based index
                    }
            raise ValueError(f"Product {product_id} not found in inventory")
        
        # Original gspread method
        worksheet = self._get_worksheet()
        
        # Find the product row
        try:
            cell = worksheet.find(product_id)
            row_data = worksheet.row_values(cell.row)
            
            if len(row_data) >= len(self.headers):
                quantity = int(row_data[2]) if row_data[2] else 0
                return {
                    "product_id": row_data[0],
                    "product_name": row_data[1],
                    "quantity": quantity,
                    "price": float(row_data[3]) if row_data[3] else 0.0,
                    "category": row_data[4] if len(row_data) > 4 else "",
                    "status": row_data[5] if len(row_data) > 5 else self._calculate_status(quantity),
                    "last_updated": row_data[6] if len(row_data) > 6 else "",
                    "row_number": cell.row
                }
            else:
                raise ValueError(f"Incomplete data for product {product_id}")
                
        except Exception:  # Catch all exceptions instead of specific gspread.CellNotFound
            raise ValueError(f"Product {product_id} not found in inventory")
    
    def _update_product(self, product_id: str, quantity: Optional[int], price: Optional[float]) -> Dict[str, Any]:
        """Update product quantity and/or price in Google Sheets."""
        if not product_id:
            raise ValueError("Product ID is required for update operation")
        
        # First, get current product data
        current_data = self._check_product(product_id)
        row_number = current_data["row_number"]
        
        # Get worksheet and check if it's a public sheet
        worksheet = self._get_worksheet()
        
        # Handle public sheet access (read-only)
        if self._is_public_sheet or worksheet == "public_sheet_access":
            raise ValueError("Cannot update products in public sheet. Sheet is read-only. Please use a private Google Sheet with proper API credentials for write access.")
        
        # Update fields
        updates = []
        if quantity is not None:
            worksheet.update_cell(row_number, 3, quantity)  # Quantity column
            worksheet.update_cell(row_number, 6, self._calculate_status(quantity))  # Status column
            updates.append(f"quantity: {quantity}")
        
        if price is not None:
            worksheet.update_cell(row_number, 4, price)  # Price column
            updates.append(f"price: {price}")
        
        # Update timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        worksheet.update_cell(row_number, 7, timestamp)  # Last Updated column
        
        # Return updated data
        updated_data = self._check_product(product_id)
        updated_data["updates_made"] = updates
        return updated_data
    
    def _add_product(self, product_id: str, product_name: str, quantity: int, price: float, category: str) -> Dict[str, Any]:
        """Add a new product to the Google Sheet."""
        if not all([product_id, product_name, quantity is not None, price is not None, category]):
            raise ValueError("All fields required: product_id, product_name, quantity, price, category")
        
        # Get worksheet first to check if it's a public sheet
        worksheet = self._get_worksheet()
        
        # Handle public sheet access (read-only)
        if self._is_public_sheet or worksheet == "public_sheet_access":
            raise ValueError("Cannot add products to public sheet. Sheet is read-only. Please use a private Google Sheet with proper API credentials for write access.")
        
        # Check if product already exists
        try:
            worksheet.find(product_id)
            raise ValueError(f"Product {product_id} already exists")
        except Exception:
            pass  # Good, product doesn't exist (catch all exceptions instead of specific gspread.CellNotFound)
        
        # Add new row
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = self._calculate_status(quantity)
        
        new_row = [product_id, product_name, quantity, price, category, status, timestamp]
        worksheet.append_row(new_row)
        
        return {
            "product_id": product_id,
            "product_name": product_name,
            "quantity": quantity,
            "price": price,
            "category": category,
            "status": status,
            "last_updated": timestamp,
            "message": "Product added successfully"
        }
    
    def _list_all_products(self) -> List[Dict[str, Any]]:
        """List all products from the Google Sheet."""
        worksheet = self._get_worksheet()
        
        # Handle public sheet access
        if self._is_public_sheet and self._public_data:
            products = []
            for record in self._public_data:
                if record.get("Product ID"):  # Skip empty rows
                    products.append({
                        "product_id": record.get("Product ID", ""),
                        "product_name": record.get("Product Name", ""),
                        "quantity": int(record.get("Quantity", 0)) if record.get("Quantity") else 0,
                        "price": float(record.get("Price", 0)) if record.get("Price") else 0.0,
                        "category": record.get("Category", ""),
                        "status": record.get("Status", ""),
                        "last_updated": record.get("Last Updated", "")
                    })
            return products
        
        # Original gspread method
        records = worksheet.get_all_records()
        
        products = []
        for record in records:
            if record.get("Product ID"):  # Skip empty rows
                products.append({
                    "product_id": record.get("Product ID", ""),
                    "product_name": record.get("Product Name", ""),
                    "quantity": int(record.get("Quantity", 0)) if record.get("Quantity") else 0,
                    "price": float(record.get("Price", 0)) if record.get("Price") else 0.0,
                    "category": record.get("Category", ""),
                    "status": record.get("Status", ""),
                    "last_updated": record.get("Last Updated", "")
                })
        
        return products
    
    def _search_products(self, search_term: Optional[str], category: Optional[str]) -> List[Dict[str, Any]]:
        """Search products by name or category."""
        all_products = self._list_all_products()
        
        if not search_term and not category:
            return all_products
        
        filtered_products = []
        for product in all_products:
            match = True
            
            if search_term:
                search_lower = search_term.lower()
                if not (search_lower in product["product_name"].lower() or 
                       search_lower in product["product_id"].lower()):
                    match = False
            
            if category and match:
                if category.lower() not in product["category"].lower():
                    match = False
            
            if match:
                filtered_products.append(product)
        
        return filtered_products
    
    def _calculate_status(self, quantity: int) -> str:
        """Calculate stock status based on quantity."""
        if quantity == 0:
            return "out_of_stock"
        elif quantity <= 10:
            return "low_stock"
        else:
            return "in_stock"
    
    def get_sheet_info(self) -> Dict[str, Any]:
        """Get information about the Google Sheet."""
        try:
            worksheet = self._get_worksheet()
            
            # Get basic info
            row_count = len(worksheet.get_all_values())
            products = self._list_all_products()
            
            # Calculate statistics
            total_products = len(products)
            total_value = sum(p["quantity"] * p["price"] for p in products)
            
            status_counts = {}
            category_counts = {}
            
            for product in products:
                status = product["status"]
                category = product["category"]
                
                status_counts[status] = status_counts.get(status, 0) + 1
                category_counts[category] = category_counts.get(category, 0) + 1
            
            return {
                "spreadsheet_id": self.spreadsheet_id,
                "worksheet_name": self.worksheet_name,
                "total_rows": row_count,
                "total_products": total_products,
                "total_inventory_value": round(total_value, 2),
                "status_distribution": status_counts,
                "category_distribution": category_counts,
                "last_sync": "Real-time (Google Sheets)"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _get_input_schema(self) -> Dict[str, Any]:
        """Get the input schema for this tool."""
        return GoogleSheetsInventoryInput.model_json_schema()


# Mock version for when Google Sheets isn't available
class MockGoogleSheetsInventoryTool(BaseTool):
    """Mock version of Google Sheets inventory tool for demonstration."""
    
    def __init__(self):
        super().__init__(
            name="mock_google_sheets_inventory",
            description="Mock Google Sheets inventory (for demo when credentials not available)"
        )
        
        # Mock data based on your sample inventory
        self.mock_data = [
            {"product_id": "LAPTOP001", "product_name": "Gaming Laptop", "quantity": 15, "price": 1299.99, "category": "Electronics", "status": "in_stock"},
            {"product_id": "PHONE001", "product_name": "Smartphone Pro", "quantity": 45, "price": 899.99, "category": "Electronics", "status": "in_stock"},
            {"product_id": "TABLET001", "product_name": "Tablet Air", "quantity": 8, "price": 599.99, "category": "Electronics", "status": "low_stock"},
            {"product_id": "HEADPHONE001", "product_name": "Wireless Headphones", "quantity": 0, "price": 199.99, "category": "Audio", "status": "out_of_stock"},
            {"product_id": "MOUSE001", "product_name": "Gaming Mouse", "quantity": 120, "price": 79.99, "category": "Accessories", "status": "in_stock"},
            {"product_id": "KEYBOARD001", "product_name": "Mechanical Keyboard", "quantity": 35, "price": 149.99, "category": "Accessories", "status": "in_stock"},
            {"product_id": "MONITOR001", "product_name": "4K Monitor", "quantity": 12, "price": 399.99, "category": "Electronics", "status": "in_stock"},
            {"product_id": "SPEAKER001", "product_name": "Bluetooth Speaker", "quantity": 25, "price": 129.99, "category": "Audio", "status": "in_stock"},
            {"product_id": "WEBCAM001", "product_name": "HD Webcam", "quantity": 18, "price": 89.99, "category": "Accessories", "status": "in_stock"},
            {"product_id": "CHARGER001", "product_name": "USB-C Charger", "quantity": 50, "price": 29.99, "category": "Accessories", "status": "in_stock"},
        ]
    
    def execute(self, input_data: GoogleSheetsInventoryInput) -> ToolOutput:
        """Execute mock operations."""
        try:
            if input_data.action == "check":
                product = next((p for p in self.mock_data if p["product_id"] == input_data.product_id), None)
                if product:
                    result = dict(product)
                    result["message"] = "📊 Data from Google Sheets (Mock)"
                    return ToolOutput(success=True, result=result)
                else:
                    return ToolOutput(success=False, result=None, error=f"Product {input_data.product_id} not found")
            
            elif input_data.action == "list_all":
                result = [dict(p) for p in self.mock_data]
                return ToolOutput(success=True, result=result)
            
            else:
                return ToolOutput(success=True, result={"message": f"Mock: {input_data.action} operation simulated"})
                
        except Exception as e:
            return ToolOutput(success=False, result=None, error=str(e))
    
    def _get_input_schema(self) -> Dict[str, Any]:
        return GoogleSheetsInventoryInput.model_json_schema()


# Example usage
if __name__ == "__main__":
    print("📊 Google Sheets Inventory Tool Test")
    print("=" * 50)
    
    # Try real Google Sheets first, fall back to mock
    try:
        tool = GoogleSheetsInventoryTool()
        print("✅ Using real Google Sheets integration")
    except Exception as e:
        print(f"⚠️  Using mock version: {e}")
        tool = MockGoogleSheetsInventoryTool()
    
    # Test operations
    print("\n1. Listing all products:")
    result = tool.execute(GoogleSheetsInventoryInput(action="list_all"))
    if result.success:
        print(f"Found {len(result.result)} products")
        for product in result.result[:3]:  # Show first 3
            print(f"  - {product['product_name']}: {product['quantity']} units")
    else:
        print(f"Error: {result.error}")
    
    print("\n2. Checking specific product:")
    result = tool.execute(GoogleSheetsInventoryInput(action="check", product_id="LAPTOP001"))
    if result.success:
        print(f"Product: {result.result}")
    else:
        print(f"Error: {result.error}")