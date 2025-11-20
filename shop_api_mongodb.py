"""
Store Management System - Enterprise Level API
MongoDB + JWT Authentication + Advanced Features
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import json
import jwt
import datetime
import hashlib
import os
import traceback
import logging
from typing import Optional, Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from pymongo import MongoClient, ASCENDING, DESCENDING
    from bson.objectid import ObjectId
    from bson.json_util import dumps
except ImportError:
    logger.info("Installing required packages...")
    os.system('pip install pymongo pyjwt')
    from pymongo import MongoClient, ASCENDING, DESCENDING
    from bson.objectid import ObjectId
    from bson.json_util import dumps

# MongoDB Connection
MONGO_URI = "mongodb+srv://saurabhdoiphode1711_db_user:k4y74dzGWx24XgSv@cluster0.bengi2a.mongodb.net/?appName=Cluster0"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()  # Test connection
    db = client['store_management']
    logger.info("✅ MongoDB Connected Successfully")
except Exception as e:
    logger.error(f"❌ MongoDB Connection Failed: {e}")
    raise

# Collections
users_collection = db['users']
products_collection = db['products']
orders_collection = db['orders']
analytics_collection = db['analytics']

# Create indexes for better performance
try:
    users_collection.create_index([('email', ASCENDING)], unique=True)
    products_collection.create_index([('name', ASCENDING)])
    products_collection.create_index([('category', ASCENDING)])
    orders_collection.create_index([('customerId', ASCENDING)])
    orders_collection.create_index([('date', DESCENDING)])
    logger.info("✅ Database indexes created")
except Exception as e:
    logger.warning(f"⚠️ Index creation warning: {e}")

# JWT Secret Key
JWT_SECRET = "your_super_secret_key_change_in_production_2024"
JWT_ALGORITHM = "HS256"

# CORS headers
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
}

class StoreAPIHandler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        for key, value in CORS_HEADERS.items():
            self.send_header(key, value)
        self.end_headers()
    
    def send_json_response(self, data, status=200):
        """Send JSON response with CORS headers"""
        try:
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            for key, value in CORS_HEADERS.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
            
            # Log request
            if status >= 400:
                logger.warning(f"{self.command} {self.path} - Status: {status}")
            else:
                logger.info(f"{self.command} {self.path} - Status: {status}")
        except Exception as e:
            logger.error(f"Error sending response: {e}")
    
    def get_auth_token(self):
        """Extract JWT token from Authorization header"""
        auth_header = self.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header[7:]
        return None
    
    def verify_token(self):
        """Verify JWT token and return user data"""
        token = self.get_auth_token()
        if not token:
            return None
        
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except:
            return None
    
    def hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_token(self, user_id, email, role):
        """Generate JWT token"""
        payload = {
            'user_id': str(user_id),
            'email': email,
            'role': role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/api/products':
            self.get_products()
        elif path == '/api/shopkeeper/stats':
            self.get_shopkeeper_stats()
        elif path == '/api/shopkeeper/orders':
            self.get_shopkeeper_orders()
        elif path == '/api/shopkeeper/customers':
            self.get_shopkeeper_customers()
        elif path == '/api/shopkeeper/analytics':
            self.get_shopkeeper_analytics()
        elif path == '/api/customer/orders':
            self.get_customer_orders()
        elif path == '/api/customer/profile':
            self.get_customer_profile()
        elif path == '/api/shop/qr':
            self.get_shop_qr()
        else:
            self.send_json_response({'error': 'Not found'}, 404)
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
        
        try:
            data = json.loads(body)
        except:
            data = {}
        
        if path == '/api/auth/register':
            self.register_user(data)
        elif path == '/api/auth/login':
            self.login_user(data)
        elif path == '/api/products':
            self.add_product(data)
        elif path == '/api/orders':
            self.place_order(data)
        else:
            self.send_json_response({'error': 'Not found'}, 404)
    
    def do_PUT(self):
        """Handle PUT requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
        
        try:
            data = json.loads(body)
        except:
            data = {}
        
        if path.startswith('/api/products/'):
            product_id = path.split('/')[-1]
            self.update_product(product_id, data)
        elif path == '/api/shopkeeper/update-qr':
            self.update_shop_qr(data)
        else:
            self.send_json_response({'error': 'Not found'}, 404)
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path.startswith('/api/products/'):
            product_id = path.split('/')[-1]
            self.delete_product(product_id)
        else:
            self.send_json_response({'error': 'Not found'}, 404)
    
    # Authentication endpoints
    def register_user(self, data):
        """Register a new user"""
        try:
            required_fields = ['email', 'password', 'firstName', 'lastName', 'phone', 'role']
            for field in required_fields:
                if field not in data:
                    self.send_json_response({'error': f'Missing field: {field}'}, 400)
                    return
            
            if users_collection.find_one({'email': data['email']}):
                self.send_json_response({'error': 'User already exists'}, 400)
                return
            
            user = {
                'email': data['email'],
                'password': self.hash_password(data['password']),
                'firstName': data['firstName'],
                'lastName': data['lastName'],
                'phone': data['phone'],
                'role': data['role'],
                'address': data.get('address', ''),
                'city': data.get('city', ''),
                'pincode': data.get('pincode', ''),
                'createdAt': datetime.datetime.utcnow()
            }
            
            if data['role'] == 'shopkeeper':
                user['shopName'] = data.get('shopName', '')
                user['shopAddress'] = data.get('shopAddress', '')
                user['gstNumber'] = data.get('gstNumber', '')
                user['upiId'] = data.get('upiId', '')
                user['qrCodeUrl'] = data.get('qrCodeUrl', '')
            elif data['role'] == 'customer':
                user['dateOfBirth'] = data.get('dateOfBirth', '')
                user['totalOrders'] = 0
                user['totalSpent'] = 0
            
            result = users_collection.insert_one(user)
            user_id = result.inserted_id
            
            token = self.generate_token(user_id, user['email'], user['role'])
            
            self.send_json_response({
                'message': 'User registered successfully',
                'token': token,
                'userId': str(user_id),
                'userName': f"{user['firstName']} {user['lastName']}",
                'userRole': user['role']
            }, 201)
            
        except Exception as e:
            print(f"Error registering user: {e}")
            self.send_json_response({'error': 'Registration failed'}, 500)
    
    def login_user(self, data):
        """Login user"""
        try:
            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                self.send_json_response({'error': 'Email and password required'}, 400)
                return
            
            user = users_collection.find_one({'email': email})
            
            if not user or user['password'] != self.hash_password(password):
                self.send_json_response({'error': 'Invalid credentials'}, 401)
                return
            
            token = self.generate_token(user['_id'], user['email'], user['role'])
            
            self.send_json_response({
                'message': 'Login successful',
                'token': token,
                'userId': str(user['_id']),
                'userName': f"{user['firstName']} {user['lastName']}",
                'userRole': user['role']
            })
            
        except Exception as e:
            print(f"Error logging in: {e}")
            self.send_json_response({'error': 'Login failed'}, 500)
    
    # Product endpoints
    def get_products(self):
        """Get all products with enhanced error handling"""
        try:
            logger.info("Fetching all products...")
            
            # Verify token (optional for products, but good for tracking)
            user = self.verify_token()
            
            products = list(products_collection.find().sort('createdAt', DESCENDING))
            
            logger.info(f"Found {len(products)} products")
            
            result = []
            for product in products:
                result.append({
                    'id': str(product['_id']),
                    'name': product.get('name', ''),
                    'category': product.get('category', ''),
                    'price': float(product.get('price', 0)),
                    'stock': float(product.get('stock', 0)),
                    'shopkeeperId': product.get('shopkeeperId', ''),
                    'createdAt': product.get('createdAt').isoformat() if product.get('createdAt') else None
                })
            
            self.send_json_response(result)
            
        except Exception as e:
            logger.error(f"Error getting products: {e}")
            logger.error(traceback.format_exc())
            self.send_json_response({
                'error': 'Failed to get products',
                'details': str(e)
            }, 500)
    
    def add_product(self, data):
        """Add new product with validation"""
        user = self.verify_token()
        if not user or user['role'] != 'shopkeeper':
            logger.warning("Unauthorized product addition attempt")
            self.send_json_response({'error': 'Unauthorized'}, 401)
            return
        
        try:
            # Validate required fields
            required_fields = ['name', 'category', 'price', 'stock']
            for field in required_fields:
                if field not in data or not data[field]:
                    self.send_json_response({
                        'error': f'Missing required field: {field}'
                    }, 400)
                    return
            
            # Validate price and stock
            try:
                price = float(data['price'])
                stock = float(data['stock'])
                if price < 0 or stock < 0:
                    raise ValueError("Negative values not allowed")
            except ValueError as e:
                self.send_json_response({
                    'error': f'Invalid number format: {str(e)}'
                }, 400)
                return
            
            product = {
                'name': data['name'].strip(),
                'category': data['category'].strip(),
                'price': price,
                'stock': stock,
                'shopkeeperId': user['user_id'],
                'createdAt': datetime.datetime.utcnow(),
                'updatedAt': datetime.datetime.utcnow()
            }
            
            logger.info(f"Adding product: {product['name']} by user {user['user_id']}")
            
            result = products_collection.insert_one(product)
            
            logger.info(f"✅ Product added successfully: {result.inserted_id}")
            
            # Return complete product info
            response_product = {
                'id': str(result.inserted_id),
                'name': product['name'],
                'category': product['category'],
                'price': product['price'],
                'stock': product['stock'],
                'shopkeeperId': product['shopkeeperId'],
                'createdAt': product['createdAt'].isoformat()
            }
            
            self.send_json_response(response_product, 201)
            
        except Exception as e:
            logger.error(f"Error adding product: {e}")
            logger.error(traceback.format_exc())
            self.send_json_response({
                'error': 'Failed to add product',
                'details': str(e)
            }, 500)
    
    def update_product(self, product_id, data):
        """Update product with validation"""
        user = self.verify_token()
        if not user or user['role'] != 'shopkeeper':
            self.send_json_response({'error': 'Unauthorized'}, 401)
            return
        
        try:
            if not product_id or len(product_id) != 24:
                self.send_json_response({'error': 'Invalid product ID'}, 400)
                return
            
            update_data = {'updatedAt': datetime.datetime.utcnow()}
            
            if 'price' in data:
                try:
                    price = float(data['price'])
                    if price < 0:
                        raise ValueError("Price cannot be negative")
                    update_data['price'] = price
                except ValueError as e:
                    self.send_json_response({'error': str(e)}, 400)
                    return
            
            if 'stock' in data:
                try:
                    stock = float(data['stock'])
                    if stock < 0:
                        raise ValueError("Stock cannot be negative")
                    update_data['stock'] = stock
                except ValueError as e:
                    self.send_json_response({'error': str(e)}, 400)
                    return
            
            if 'name' in data:
                update_data['name'] = data['name'].strip()
            
            if 'category' in data:
                update_data['category'] = data['category'].strip()
            
            logger.info(f"Updating product {product_id} with data: {update_data}")
            
            result = products_collection.update_one(
                {'_id': ObjectId(product_id)},
                {'$set': update_data}
            )
            
            if result.matched_count > 0:
                logger.info(f"✅ Product {product_id} updated successfully")
                self.send_json_response({
                    'message': 'Product updated successfully',
                    'modified': result.modified_count > 0
                })
            else:
                logger.warning(f"Product {product_id} not found")
                self.send_json_response({'error': 'Product not found'}, 404)
                
        except Exception as e:
            logger.error(f"Error updating product: {e}")
            logger.error(traceback.format_exc())
            self.send_json_response({
                'error': 'Failed to update product',
                'details': str(e)
            }, 500)
    
    def delete_product(self, product_id):
        """Delete product with validation"""
        user = self.verify_token()
        if not user or user['role'] != 'shopkeeper':
            self.send_json_response({'error': 'Unauthorized'}, 401)
            return
        
        try:
            if not product_id or len(product_id) != 24:
                self.send_json_response({'error': 'Invalid product ID'}, 400)
                return
            
            logger.info(f"Deleting product {product_id}")
            
            # Check if product exists first
            product = products_collection.find_one({'_id': ObjectId(product_id)})
            if not product:
                logger.warning(f"Product {product_id} not found")
                self.send_json_response({'error': 'Product not found'}, 404)
                return
            
            result = products_collection.delete_one({'_id': ObjectId(product_id)})
            
            if result.deleted_count > 0:
                logger.info(f"✅ Product {product_id} deleted successfully")
                self.send_json_response({
                    'message': 'Product deleted successfully',
                    'deletedProduct': product.get('name', 'Unknown')
                })
            else:
                self.send_json_response({'error': 'Failed to delete product'}, 500)
                
        except Exception as e:
            logger.error(f"Error deleting product: {e}")
            logger.error(traceback.format_exc())
            self.send_json_response({
                'error': 'Failed to delete product',
                'details': str(e)
            }, 500)
    
    # Order endpoints
    def place_order(self, data):
        """Place an order with validation and stock management"""
        user = self.verify_token()
        if not user or user['role'] != 'customer':
            self.send_json_response({'error': 'Unauthorized'}, 401)
            return
        
        try:
            # Validate order data
            if 'items' not in data or not data['items']:
                self.send_json_response({'error': 'Order must contain items'}, 400)
                return
            
            if 'paymentMethod' not in data:
                self.send_json_response({'error': 'Payment method required'}, 400)
                return
            
            logger.info(f"Processing order for customer {user['user_id']}")
            
            # Validate stock availability
            for item in data['items']:
                product = products_collection.find_one({'_id': ObjectId(item['id'])})
                if not product:
                    self.send_json_response({
                        'error': f"Product {item['name']} not found"
                    }, 400)
                    return
                
                if product['stock'] < item['quantity']:
                    self.send_json_response({
                        'error': f"Insufficient stock for {item['name']}. Available: {product['stock']}"
                    }, 400)
                    return
            
            # Calculate total
            calculated_total = sum(item['price'] * item['quantity'] for item in data['items'])
            
            order = {
                'customerId': user['user_id'],
                'items': data['items'],
                'total': calculated_total,
                'paymentMethod': data['paymentMethod'],
                'status': 'completed',
                'date': datetime.datetime.utcnow()
            }
            
            # Update stock for each item
            for item in data['items']:
                result = products_collection.update_one(
                    {'_id': ObjectId(item['id'])},
                    {
                        '$inc': {'stock': -item['quantity']},
                        '$set': {'updatedAt': datetime.datetime.utcnow()}
                    }
                )
                logger.info(f"Updated stock for product {item['id']}: -{item['quantity']}")
            
            # Update customer stats
            users_collection.update_one(
                {'_id': ObjectId(user['user_id'])},
                {
                    '$inc': {
                        'totalOrders': 1,
                        'totalSpent': order['total']
                    },
                    '$set': {'updatedAt': datetime.datetime.utcnow()}
                }
            )
            
            # Insert order
            result = orders_collection.insert_one(order)
            
            logger.info(f"✅ Order {result.inserted_id} placed successfully")
            
            self.send_json_response({
                'message': 'Order placed successfully',
                'orderId': str(result.inserted_id),
                'total': order['total'],
                'itemCount': len(order['items'])
            }, 201)
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            logger.error(traceback.format_exc())
            self.send_json_response({
                'error': 'Failed to place order',
                'details': str(e)
            }, 500)
    
    def get_customer_orders(self):
        """Get customer's orders"""
        user = self.verify_token()
        if not user or user['role'] != 'customer':
            self.send_json_response({'error': 'Unauthorized'}, 401)
            return
        
        try:
            orders = list(orders_collection.find({'customerId': user['user_id']}))
            
            for order in orders:
                order['id'] = str(order['_id'])
                order['itemCount'] = len(order['items'])
                del order['_id']
                del order['customerId']
            
            self.send_json_response(orders)
        except Exception as e:
            print(f"Error getting orders: {e}")
            self.send_json_response({'error': 'Failed to get orders'}, 500)
    
    def get_shopkeeper_orders(self):
        """Get all orders"""
        user = self.verify_token()
        if not user or user['role'] != 'shopkeeper':
            self.send_json_response({'error': 'Unauthorized'}, 401)
            return
        
        try:
            orders = list(orders_collection.find())
            
            for order in orders:
                order['id'] = str(order['_id'])
                order['itemCount'] = len(order['items'])
                
                customer = users_collection.find_one({'_id': ObjectId(order['customerId'])})
                order['customerName'] = f"{customer['firstName']} {customer['lastName']}" if customer else 'Unknown'
                
                del order['_id']
                del order['customerId']
            
            self.send_json_response(orders)
        except Exception as e:
            print(f"Error getting orders: {e}")
            self.send_json_response({'error': 'Failed to get orders'}, 500)
    
    # Shopkeeper dashboard endpoints
    def get_shopkeeper_stats(self):
        """Get comprehensive shopkeeper dashboard statistics"""
        user = self.verify_token()
        if not user or user['role'] != 'shopkeeper':
            self.send_json_response({'error': 'Unauthorized'}, 401)
            return
        
        try:
            logger.info("Fetching shopkeeper stats...")
            
            today_start = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Today's sales
            today_sales_pipeline = [
                {'$match': {'date': {'$gte': today_start}}},
                {'$group': {'_id': None, 'total': {'$sum': '$total'}, 'count': {'$sum': 1}}}
            ]
            today_sales = list(orders_collection.aggregate(today_sales_pipeline))
            today_sales_amount = float(today_sales[0]['total']) if today_sales else 0.0
            today_orders_count = today_sales[0]['count'] if today_sales else 0
            
            # Total products
            total_products = products_collection.count_documents({})
            
            # Low stock count
            low_stock_count = products_collection.count_documents({'stock': {'$lte': 10}})
            
            # Out of stock count
            out_of_stock = products_collection.count_documents({'stock': 0})
            
            # Total customers
            total_customers = users_collection.count_documents({'role': 'customer'})
            
            # Total orders
            total_orders = orders_collection.count_documents({})
            
            # Total revenue
            total_revenue_pipeline = [
                {'$group': {'_id': None, 'total': {'$sum': '$total'}}}
            ]
            total_revenue = list(orders_collection.aggregate(total_revenue_pipeline))
            total_revenue_amount = float(total_revenue[0]['total']) if total_revenue else 0.0
            
            logger.info(f"Stats fetched: Products={total_products}, Customers={total_customers}")
            
            self.send_json_response({
                'todaySales': round(today_sales_amount, 2),
                'todayOrders': today_orders_count,
                'totalProducts': total_products,
                'lowStockCount': low_stock_count,
                'outOfStock': out_of_stock,
                'totalCustomers': total_customers,
                'totalOrders': total_orders,
                'totalRevenue': round(total_revenue_amount, 2)
            })
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            logger.error(traceback.format_exc())
            self.send_json_response({
                'error': 'Failed to get stats',
                'details': str(e)
            }, 500)
    
    def get_shopkeeper_customers(self):
        """Get all customers"""
        user = self.verify_token()
        if not user or user['role'] != 'shopkeeper':
            self.send_json_response({'error': 'Unauthorized'}, 401)
            return
        
        try:
            customers = list(users_collection.find({'role': 'customer'}))
            
            for customer in customers:
                customer['id'] = str(customer['_id'])
                del customer['_id']
                del customer['password']
            
            self.send_json_response(customers)
        except Exception as e:
            print(f"Error getting customers: {e}")
            self.send_json_response({'error': 'Failed to get customers'}, 500)
    
    def get_shopkeeper_analytics(self):
        """Get analytics data"""
        user = self.verify_token()
        if not user or user['role'] != 'shopkeeper':
            self.send_json_response({'error': 'Unauthorized'}, 401)
            return
        
        try:
            days = []
            sales_data = []
            
            for i in range(6, -1, -1):
                day_start = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=i)
                day_end = day_start + datetime.timedelta(days=1)
                
                day_sales = orders_collection.aggregate([
                    {'$match': {'date': {'$gte': day_start, '$lt': day_end}}},
                    {'$group': {'_id': None, 'total': {'$sum': '$total'}}}
                ])
                day_sales = list(day_sales)
                
                days.append(day_start.strftime('%a'))
                sales_data.append(day_sales[0]['total'] if day_sales else 0)
            
            category_data = products_collection.aggregate([
                {'$group': {'_id': '$category', 'count': {'$sum': 1}}}
            ])
            category_data = list(category_data)
            
            category_labels = [item['_id'] for item in category_data]
            category_counts = [item['count'] for item in category_data]
            
            self.send_json_response({
                'salesLabels': days,
                'salesData': sales_data,
                'categoryLabels': category_labels,
                'categoryData': category_counts
            })
            
        except Exception as e:
            print(f"Error getting analytics: {e}")
            self.send_json_response({'error': 'Failed to get analytics'}, 500)
    
    # Customer endpoints
    def get_customer_profile(self):
        """Get customer profile"""
        user = self.verify_token()
        if not user or user['role'] != 'customer':
            self.send_json_response({'error': 'Unauthorized'}, 401)
            return
        
        try:
            customer = users_collection.find_one({'_id': ObjectId(user['user_id'])})
            
            if customer:
                customer['id'] = str(customer['_id'])
                del customer['_id']
                del customer['password']
                
                self.send_json_response(customer)
            else:
                self.send_json_response({'error': 'Profile not found'}, 404)
                
        except Exception as e:
            print(f"Error getting profile: {e}")
            self.send_json_response({'error': 'Failed to get profile'}, 500)
    
    def get_shop_qr(self):
        """Get shop QR code and UPI ID"""
        user = self.verify_token()
        if not user:
            self.send_json_response({'error': 'Unauthorized'}, 401)
            return
        
        try:
            shopkeeper = users_collection.find_one({'role': 'shopkeeper'})
            
            if shopkeeper:
                self.send_json_response({
                    'qrCodeUrl': shopkeeper.get('qrCodeUrl', ''),
                    'upiId': shopkeeper.get('upiId', '')
                })
            else:
                self.send_json_response({'error': 'Shop info not found'}, 404)
                
        except Exception as e:
            print(f"Error getting QR: {e}")
            self.send_json_response({'error': 'Failed to get QR code'}, 500)
    
    def update_shop_qr(self, data):
        """Update shop QR code"""
        user = self.verify_token()
        if not user or user['role'] != 'shopkeeper':
            self.send_json_response({'error': 'Unauthorized'}, 401)
            return
        
        try:
            update_data = {}
            if 'upiId' in data:
                update_data['upiId'] = data['upiId']
            if 'qrCodeUrl' in data:
                update_data['qrCodeUrl'] = data['qrCodeUrl']
            
            users_collection.update_one(
                {'_id': ObjectId(user['user_id'])},
                {'$set': update_data}
            )
            
            self.send_json_response({'message': 'QR code updated successfully'})
            
        except Exception as e:
            print(f"Error updating QR: {e}")
            self.send_json_response({'error': 'Failed to update QR code'}, 500)


def run_server(port=8000):
    """Run the HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, StoreAPIHandler)
    print(f'🚀 Server running on http://localhost:{port}')
    print(f'📊 MongoDB Connected')
    print(f'🔐 JWT Authentication enabled')
    print('\nPress Ctrl+C to stop the server\n')
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n\n👋 Server stopped')
        httpd.server_close()


if __name__ == '__main__':
    run_server()
