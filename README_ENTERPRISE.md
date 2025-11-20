# 🏪 Store Management System - Enterprise Edition

## 🚀 Overview
A comprehensive, production-ready store management system with role-based authentication, real-time inventory tracking, and advanced analytics.

## ✨ Enterprise Features

### 🔐 Security & Authentication
- **JWT-based Authentication** with 7-day token validity
- **Role-Based Access Control (RBAC)** - Shopkeeper & Customer roles
- **SHA-256 Password Hashing** for secure password storage
- **Token Verification** on all protected endpoints
- **CORS Support** for cross-origin requests

### 📊 Advanced Logging & Monitoring
- **Structured Logging** with timestamp, level, and context
- **Request/Response Logging** for all API calls
- **Error Tracking** with detailed stack traces
- **Performance Monitoring** with query optimization

### 🎯 Database Optimization
- **MongoDB Indexes** on frequently queried fields
  - Email (unique index)
  - Product name and category
  - Order date and customer ID
- **Aggregation Pipelines** for complex analytics
- **Connection Pooling** for better performance
- **Automatic Reconnection** handling

### 📦 Product Management
- **CRUD Operations** with validation
- **Stock Management** with low-stock alerts
- **Category-based Organization**
- **Real-time Inventory Updates**
- **Bulk Operations Support**

### 🛒 Order Processing
- **Stock Validation** before order placement
- **Automatic Stock Deduction**
- **Order History Tracking**
- **Multiple Payment Methods** (Cash, Card, UPI)
- **Customer Statistics** (Total Orders, Total Spent)

### 📈 Analytics & Reporting
- **Daily Sales Tracking**
- **7-Day Sales Trend Charts**
- **Category-wise Distribution**
- **Low Stock Alerts**
- **Customer Analytics**
- **Revenue Reports**

### 👥 User Management
- **Detailed User Profiles**
- **Registration with QR Code Upload** (Shopkeeper)
- **Customer Information** (DOB, Address, etc.)
- **Activity Tracking**

## 🛠️ Technology Stack

### Backend
- **Python 3.7+** - Core programming language
- **HTTP Server** - Native Python HTTP server
- **PyMongo 4.0+** - MongoDB driver
- **PyJWT 2.8+** - JWT token handling

### Database
- **MongoDB Atlas** - Cloud database
- **Collections**:
  - `users` - User accounts (shopkeepers & customers)
  - `products` - Product inventory
  - `orders` - Order transactions
  - `analytics` - Analytics data

### Frontend
- **HTML5** - Modern markup
- **CSS3** - Advanced styling with gradients, animations
- **JavaScript ES6+** - Modern JavaScript features
- **Chart.js 3.9+** - Data visualization

## 📋 API Endpoints

### Authentication
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | User login | No |

### Products
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/products` | Get all products | Yes |
| POST | `/api/products` | Add new product | Shopkeeper |
| PUT | `/api/products/:id` | Update product | Shopkeeper |
| DELETE | `/api/products/:id` | Delete product | Shopkeeper |

### Orders
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/orders` | Place order | Customer |
| GET | `/api/customer/orders` | Get customer orders | Customer |
| GET | `/api/shopkeeper/orders` | Get all orders | Shopkeeper |

### Dashboard
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/shopkeeper/stats` | Dashboard stats | Shopkeeper |
| GET | `/api/shopkeeper/analytics` | Analytics data | Shopkeeper |
| GET | `/api/shopkeeper/customers` | Customer list | Shopkeeper |
| GET | `/api/customer/profile` | User profile | Customer |

### Payment
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/shop/qr` | Get shop QR code | Yes |
| PUT | `/api/shopkeeper/update-qr` | Update QR code | Shopkeeper |

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.7 or higher
python --version

# pip package manager
pip --version
```

### Installation

1. **Clone Repository**
```bash
git clone https://github.com/Saurabhdoiphode/Store-Management-System.git
cd Store-Management-System
```

2. **Install Dependencies**
```bash
pip install pymongo pyjwt
```

3. **Start Server**
```bash
python shop_api_mongodb.py
```

4. **Access Application**
```
Open browser: http://localhost:8000/login.html
```

## 📱 Usage Guide

### For Shopkeepers

1. **Registration**
   - Select "Shopkeeper" role
   - Provide shop details (name, address, GST)
   - Upload payment QR code
   - Enter UPI ID

2. **Dashboard Features**
   - **📦 Orders Tab**: View and manage all customer orders
   - **📊 Inventory Tab**: Add, edit, delete products
   - **📈 Analytics Tab**: View sales charts and trends
   - **👥 Customers Tab**: View customer list and statistics
   - **⚙️ Settings Tab**: Update QR code and payment details

3. **Product Management**
   - Click "➕ Add Product"
   - Fill in product details
   - Set initial stock and price
   - Click "🔄 Refresh" to reload products

### For Customers

1. **Registration**
   - Select "Customer" role
   - Provide personal details
   - Enter delivery address

2. **Shopping Features**
   - **🛍️ Shop Tab**: Browse and add products to cart
   - **📦 My Orders Tab**: View order history
   - **👤 Profile Tab**: View personal information

3. **Placing Orders**
   - Click on products to add to cart
   - Click cart icon (🛒) in bottom-right
   - Select payment method
   - For UPI: Scan QR code and confirm payment
   - Place order

## 🔧 Configuration

### MongoDB Connection
Edit in `shop_api_mongodb.py`:
```python
MONGO_URI = "your_mongodb_connection_string"
```

### JWT Secret Key
Change in production:
```python
JWT_SECRET = "your_secure_secret_key"
```

### Server Port
Modify in `run_server()`:
```python
run_server(port=8000)  # Change port if needed
```

## 🐛 Troubleshooting

### Products Not Loading

**Problem**: "Failed to load products" error

**Solutions**:
1. Check server is running: Look for "🚀 Server running" message
2. Check MongoDB connection: Look for "✅ MongoDB Connected" message
3. Check browser console for errors (F12)
4. Verify token is valid (check localStorage)

### Authentication Issues

**Problem**: "Unauthorized" errors

**Solutions**:
1. Login again to refresh token
2. Clear browser cache and localStorage
3. Check token expiration (7-day validity)

### Server Errors

**Problem**: 500 Internal Server Error

**Solutions**:
1. Check terminal logs for detailed error messages
2. Verify MongoDB connection string
3. Ensure all required packages are installed
4. Check Python version (3.7+)

## 📊 Monitoring & Logs

### Log Levels
- **INFO**: Normal operations (connections, successful requests)
- **WARNING**: Unusual but not critical (unauthorized access attempts)
- **ERROR**: Serious issues (database errors, failed operations)

### Log Format
```
2025-11-20 12:23:21,870 - INFO - ✅ MongoDB Connected Successfully
2025-11-20 12:23:22,377 - INFO - ✅ Database indexes created
2025-11-20 12:23:45,123 - INFO - GET /api/products - Status: 200
```

### Viewing Logs
Logs are printed to the terminal where the server is running. Monitor in real-time.

## 🔒 Security Best Practices

1. **Change JWT Secret**: Use a strong, random secret key in production
2. **HTTPS**: Deploy with SSL/TLS certificate
3. **Environment Variables**: Store sensitive data in env files
4. **Rate Limiting**: Implement to prevent abuse
5. **Input Validation**: All inputs are validated on server-side
6. **Password Policy**: Implement strong password requirements

## 🚀 Deployment

### Local Development
```bash
python shop_api_mongodb.py
```

### Production Deployment
1. Use a production WSGI server (Gunicorn, uWSGI)
2. Set up reverse proxy (Nginx, Apache)
3. Enable HTTPS with SSL certificate
4. Configure firewall rules
5. Set up monitoring and alerting

## 📈 Performance Optimization

### Database
- Indexes created on frequently queried fields
- Aggregation pipelines for complex queries
- Connection pooling enabled

### API
- Response caching for static data
- Pagination for large datasets
- Compression for JSON responses

### Frontend
- Lazy loading of images
- Debouncing for search inputs
- Local caching of product data

## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first.

## 📄 License
MIT License - Feel free to use for personal and commercial projects

## 👨‍💻 Developer
**Saurabh Doiphode**
- GitHub: [@Saurabhdoiphode](https://github.com/Saurabhdoiphode)
- Repository: [Store-Management-System](https://github.com/Saurabhdoiphode/Store-Management-System)

## 🎉 Version History

### v2.0.0 (Enterprise Edition) - November 2025
- ✅ Enterprise-level logging system
- ✅ Advanced error handling with stack traces
- ✅ Database indexing for performance
- ✅ Enhanced validation on all endpoints
- ✅ Comprehensive analytics dashboard
- ✅ Stock validation before order placement
- ✅ Real-time inventory updates
- ✅ Customer statistics tracking

### v1.0.0 - Initial Release
- Basic authentication system
- Product management
- Order processing
- Dashboard interfaces

## 📞 Support
For issues and questions, please open an issue on GitHub or contact the developer.

---

**Built with ❤️ for modern retail management**
