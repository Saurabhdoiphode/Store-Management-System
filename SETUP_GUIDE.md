# Store Management System - Setup Guide

## Quick Setup (3 Steps)

### Step 1: Install Python Dependencies

```bash
pip install pymongo pyjwt
```

Or use requirements.txt:
```bash
pip install -r requirements.txt
```

### Step 2: Start the API Server

```bash
python shop_api_mongodb.py
```

You should see:
```
🚀 Server running on http://localhost:8000
📊 MongoDB Connected
🔐 JWT Authentication enabled
```

### Step 3: Open the Application

- Open `login.html` in your web browser
- Register as Shopkeeper or Customer
- Start using the system!

## File Structure

```
Store Management/
├── login.html                 # ✅ Authentication page (NEW)
├── shop_api_mongodb.py       # ✅ MongoDB API with JWT (NEW)
├── requirements.txt          # ✅ Dependencies (NEW)
├── index.html                # Original store interface
├── app.js                    # Original JavaScript
├── shop_api.py              # Original API (MySQL)
└── qr code.jpg              # Sample QR code
```

## Usage

### For Shopkeepers:
1. Register with shopkeeper role
2. Upload QR code for payments
3. Add products to inventory
4. Manage orders and customers
5. View analytics

### For Customers:
1. Register with customer role
2. Browse products
3. Add to cart and checkout
4. View order history

## API Endpoints

- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login user
- `GET /api/products` - Get products
- `POST /api/products` - Add product (shopkeeper only)
- `POST /api/orders` - Place order (customer only)

## Database

MongoDB Atlas (Cloud)
- Connection configured in `shop_api_mongodb.py`
- Collections: users, products, orders

## Troubleshooting

**Python packages not found?**
```bash
pip install pymongo pyjwt
```

**Server won't start?**
- Check if port 8000 is available
- Verify Python is installed: `python --version`

**Can't connect to MongoDB?**
- Check internet connection
- MongoDB Atlas requires internet

---

**Need more features?** Check the original files:
- `index.html` - Original enhanced interface
- `shop_api.py` - Original MySQL API
