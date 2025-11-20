"""
Store Management System API with MongoDB and JWT Authentication
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import json
import jwt
import datetime
import hashlib
import os

try:
    from pymongo import MongoClient
    from bson.objectid import ObjectId
except ImportError:
    print("Installing required packages...")
    os.system('pip install pymongo pyjwt')
    from pymongo import MongoClient
    from bson.objectid import ObjectId

# MongoDB Connection
MONGO_URI = "mongodb+srv://saurabhdoiphode1711_db_user:k4y74dzGWx24XgSv@cluster0.bengi2a.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client['store_management']

# Collections
users_collection = db['users']
products_collection = db['products']
orders_collection = db['orders']

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
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        for key, value in CORS_HEADERS.items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
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
        """Get all products"""
        try:
            products = list(products_collection.find())
            for product in products:
                product['id'] = str(product['_id'])
                del product['_id']
            
            self.send_json_response(products)
        except Exception as e:
            print(f"Error getting products: {e}")
            self.send_json_response({'error': 'Failed to get products'}, 500)
    
    def add_product(self, data):
        """Add new product"""
        user = self.verify_token()
        if not user or user['role'] != 'shopkeeper':
            self.send_json_response({'error': 'Unauthorized'}, 401)
            return
        
        try:
            product = {
                'name': data['name'],
                'category': data['category'],
                'price': float(data['price']),
                'stock': float(data['stock']),
                'shopkeeperId': user['user_id'],
                'createdAt': datetime.datetime.utcnow()
            }
            
            result = products_collection.insert_one(product)
            product['id'] = str(result.inserted_id)
            del product['_id']
            
            self.send_json_response(product, 201)
        except Exception as e:
            print(f"Error adding product: {e}")
            self.send_json_response({'error': 'Failed to add product'}, 500)
    
    def update_product(self, product_id, data):
        """Update product"""
        user = self.verify_token()
        if not user or user['role'] != 'shopkeeper':
            self.send_json_response({'error': 'Unauthorized'}, 401)
            return
        
        try:
            update_data = {}
            if 'price' in data:
                update_data['price'] = float(data['price'])
            if 'stock' in data:
                update_data['stock'] = float(data['stock'])
            
            result = products_collection.update_one(
                {'_id': ObjectId(product_id)},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                self.send_json_response({'message': 'Product updated successfully'})
            else:
                self.send_json_response({'error': 'Product not found'}, 404)
        except Exception as e:
            print(f"Error updating product: {e}")
            self.send_json_response({'error': 'Failed to update product'}, 500)
    
    def delete_product(self, product_id):
        """Delete product"""
        user = self.verify_token()
        if not user or user['role'] != 'shopkeeper':
            self.send_json_response({'error': 'Unauthorized'}, 401)
            return
        
        try:
            result = products_collection.delete_one({'_id': ObjectId(product_id)})
            
            if result.deleted_count > 0:
                self.send_json_response({'message': 'Product deleted successfully'})
            else:
                self.send_json_response({'error': 'Product not found'}, 404)
        except Exception as e:
            print(f"Error deleting product: {e}")
            self.send_json_response({'error': 'Failed to delete product'}, 500)
    
    # Order endpoints
    def place_order(self, data):
        """Place an order"""
        user = self.verify_token()
        if not user or user['role'] != 'customer':
            self.send_json_response({'error': 'Unauthorized'}, 401)
            return
        
        try:
            order = {
                'customerId': user['user_id'],
                'items': data['items'],
                'total': float(data['total']),
                'paymentMethod': data['paymentMethod'],
                'status': 'completed',
                'date': datetime.datetime.utcnow()
            }
            
            for item in data['items']:
                products_collection.update_one(
                    {'_id': ObjectId(item['id'])},
                    {'$inc': {'stock': -item['quantity']}}
                )
            
            users_collection.update_one(
                {'_id': ObjectId(user['user_id'])},
                {'$inc': {'totalOrders': 1, 'totalSpent': order['total']}}
            )
            
            result = orders_collection.insert_one(order)
            
            self.send_json_response({
                'message': 'Order placed successfully',
                'orderId': str(result.inserted_id)
            }, 201)
            
        except Exception as e:
            print(f"Error placing order: {e}")
            self.send_json_response({'error': 'Failed to place order'}, 500)
    
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
        """Get shopkeeper dashboard statistics"""
        user = self.verify_token()
        if not user or user['role'] != 'shopkeeper':
            self.send_json_response({'error': 'Unauthorized'}, 401)
            return
        
        try:
            today_start = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_sales = orders_collection.aggregate([
                {'$match': {'date': {'$gte': today_start}}},
                {'$group': {'_id': None, 'total': {'$sum': '$total'}}}
            ])
            today_sales = list(today_sales)
            today_sales_amount = today_sales[0]['total'] if today_sales else 0
            
            total_products = products_collection.count_documents({})
            low_stock_count = products_collection.count_documents({'stock': {'$lte': 10}})
            total_customers = users_collection.count_documents({'role': 'customer'})
            
            self.send_json_response({
                'todaySales': today_sales_amount,
                'totalProducts': total_products,
                'lowStockCount': low_stock_count,
                'totalCustomers': total_customers
            })
            
        except Exception as e:
            print(f"Error getting stats: {e}")
            self.send_json_response({'error': 'Failed to get stats'}, 500)
    
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
