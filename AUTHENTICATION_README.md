# 🎉 Store Management System - Complete Authentication System

## What's New

This update adds a complete authentication system with:

### ✨ New Features
- **Role-Based Authentication** - Separate interfaces for Shopkeeper and Customer
- **MongoDB Cloud Database** - MongoDB Atlas integration
- **JWT Authentication** - Secure token-based authentication
- **QR Code Payments** - Upload and manage payment QR codes
- **Dual Dashboards** - Dedicated interfaces for each role

### 📂 New Files Added

1. **login.html** - Authentication page with role selection
2. **shop_api_mongodb.py** - MongoDB backend with JWT auth
3. **requirements.txt** - Python dependencies

### 🚀 Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Start the MongoDB API server
python shop_api_mongodb.py

# Open login.html in your browser
```

### 📋 Features

**Shopkeeper:**
- Dashboard with statistics
- Product management
- Order tracking
- Customer management
- Sales analytics

**Customer:**
- Product browsing
- Shopping cart
- Order placement
- Order history
- Profile management

### 🔒 Security
- SHA-256 password hashing
- JWT token authentication (7-day validity)
- Role-based access control
- Protected API endpoints

### 📊 Database Schema

**MongoDB Collections:**
- `users` - User accounts (shopkeepers & customers)
- `products` - Product inventory
- `orders` - Customer orders
- `transactions` - Payment records

### 🛠️ Tech Stack
- Frontend: HTML5, CSS3, JavaScript
- Backend: Python 3, PyMongo, PyJWT
- Database: MongoDB Atlas (Cloud)
- Auth: JWT tokens

### 📱 Usage

**Register as Shopkeeper:**
1. Select "Shopkeeper" role
2. Fill personal and shop details
3. Upload QR code for payments
4. Register and access dashboard

**Register as Customer:**
1. Select "Customer" role
2. Fill personal details
3. Register and start shopping

### 🐛 Troubleshooting

- **MongoDB Connection Error:** Check internet connection
- **Module Not Found:** Run `pip install pymongo pyjwt`
- **401 Unauthorized:** Login again (token expired)

### 📞 Support

MongoDB Connection String is already configured in `shop_api_mongodb.py`

For issues, check browser console and server terminal for error messages.

---

**Happy Managing! 🛍️**
