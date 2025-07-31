from decimal import Decimal
import mysql.connector
from mysql.connector import Error
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import parse_qs, urlparse
import datetime

# Database connection configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'ar12ya34',
    'database': 'shop_management'
}

def create_connection():
    """Create a database connection"""
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def initialize_database():
    """Initialize the database with product data"""
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Insert products if they don't exist
            products = [
                (1, "Sugar", "GROCERY", 40.00, 100, "kg"),
                (2, "Rice", "GROCERY", 120.00, 200, "kg"),
                (3, "Eggs", "GROCERY", 10.00, 500, "units"),
                (4, "Wheat", "GROCERY", 200.00, 150, "kg"),
                (5, "Salt", "GROCERY", 60.00, 300, "kg"),
                (6, "Peanuts", "GROCERY", 100.00, 100, "kg"),
                (7, "Pasta", "GROCERY", 30.00, 200, "kg"),
                (8, "Bread", "GROCERY", 20.00, 300, "units"),
                (9, "Jaggery", "GROCERY", 50.00, 100, "kg"),
                (10, "Hail Oil", "OIL", 20.00, 200, "liters"),
                (11, "Vegetable Oil", "OIL", 50.00, 150, "liters"),
                (12, "Peanut Oil", "OIL", 70.00, 100, "liters"),
                (13, "Sunflower Oil", "OIL", 180.00, 80, "liters"),
                (14, "Coconut Oil", "OIL", 80.00, 120, "liters"),
                (15, "Corn Oil", "OIL", 30.00, 200, "liters"),
                (16, "Avocado Oil", "OIL", 550.00, 50, "liters"),
                (17, "Potato Chips", "SNACK", 10.00, 300, "units"),
                (18, "Tomato Chips", "SNACK", 10.00, 250, "units"),
                (19, "Popcorn", "SNACK", 10.00, 200, "units"),
                (20, "Chocolate Bars", "SNACK", 20.00, 150, "units"),
                (21, "Cream Biscuits", "SNACK", 15.00, 200, "units"),
                (22, "Cold Drinks", "SNACK", 25.00, 300, "units"),
                (23, "Cookies", "SNACK", 30.00, 250, "units"),
                (24, "Rice Cakes", "SNACK", 40.00, 150, "units"),
                (25, "Cheese Puffs", "SNACK", 35.00, 200, "units"),
                (26, "Protein Bars", "SNACK", 50.00, 100, "units"),
                (27, "Cow Milk", "DAIRY", 25.00, 300, "liters"),
                (28, "Cow Cheese", "DAIRY", 200.00, 100, "kg"),
                (29, "Buffalo Milk", "DAIRY", 30.00, 250, "liters"),
                (30, "Buffalo Cheese", "DAIRY", 250.00, 80, "kg"),
                (31, "Ice-Cream", "DAIRY", 100.00, 150, "units"),
                (32, "Yogurt", "DAIRY", 40.00, 200, "units"),
                (33, "Paneer", "DAIRY", 150.00, 100, "kg")
            ]
            
            insert_query = """
            INSERT IGNORE INTO products (product_id, name, category, price, stock_quantity, unit)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            cursor.executemany(insert_query, products)
            connection.commit()
            print("Database initialized with product data.")
            
        except Error as e:
            print(f"Error initializing database: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

# Initialize the database when the script starts
initialize_database()

class RequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type='application/json'):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers()
    
    def do_GET(self):
        try:
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            
            if path == '/api/daily-sales':
                self.handle_daily_sales()
            elif path == '/api/users':
                self.handle_all_users()
            elif path == '/api/transactions':
                self.handle_recent_transactions()
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({'error': 'Not found'}).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            
            if path == '/api/register':
                self.handle_register(data)
            elif path == '/api/products':
                self.handle_products(data)
            elif path == '/api/product':
                self.handle_product(data)
            elif path == '/api/checkout':
                self.handle_checkout(data)
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({'error': 'Not found'}).encode())
        except json.JSONDecodeError:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': 'Invalid JSON data'}).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def handle_register(self, data):
        name = data.get('name')
        phone = data.get('phone')
        
        if not name or not phone:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': 'Name and phone are required'}).encode())
            return
        
        connection = create_connection()
        if not connection:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': 'Database connection failed'}).encode())
            return
        
        try:
            cursor = connection.cursor()
            insert_user = "INSERT INTO users (name, phone) VALUES (%s, %s)"
            cursor.execute(insert_user, (name, phone))
            user_id = cursor.lastrowid
            
            cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            if cursor.fetchone():
                connection.commit()
                self._set_headers(201)
                self.wfile.write(json.dumps({'user_id': user_id}).encode())
            else:
                connection.rollback()
                self._set_headers(500)
                self.wfile.write(json.dumps({'error': 'User creation failed'}).encode())
        except Error as e:
            connection.rollback()
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': str(e)}).encode())
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def handle_products(self, data):
        category = data.get('category')
        
        if not category:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': 'Category is required'}).encode())
            return
        
        connection = create_connection()
        if not connection:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': 'Database connection failed'}).encode())
            return
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT product_id, name, price, stock_quantity, unit 
                FROM products 
                WHERE category = %s AND stock_quantity > 0
                ORDER BY product_id
            """
            cursor.execute(query, (category,))
            products = cursor.fetchall()
            
            # Convert Decimal to float for JSON serialization
            for product in products:
                product['price'] = float(product['price'])
                product['stock_quantity'] = float(product['stock_quantity'])
            
            self._set_headers(200)
            self.wfile.write(json.dumps({'products': products}).encode())
        except Error as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': str(e)}).encode())
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def handle_product(self, data):
        product_id = data.get('product_id')
        
        if not product_id:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': 'Product ID is required'}).encode())
            return
        
        connection = create_connection()
        if not connection:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': 'Database connection failed'}).encode())
            return
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT product_id, name, price, stock_quantity, unit 
                FROM products 
                WHERE product_id = %s
            """
            cursor.execute(query, (product_id,))
            product = cursor.fetchone()
            
            if product:
                product['price'] = float(product['price'])
                product['stock_quantity'] = float(product['stock_quantity'])
                self._set_headers(200)
                self.wfile.write(json.dumps({'product': product}).encode())
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({'error': 'Product not found'}).encode())
        except Error as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': str(e)}).encode())
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def handle_checkout(self, data):
        transactions = data.get('transactions')
        
        if not transactions or not isinstance(transactions, list):
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': 'Invalid transactions data'}).encode())
            return
        
        connection = create_connection()
        if not connection:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': 'Database connection failed'}).encode())
            return
        
        try:
            cursor = connection.cursor()
            
            # Process each transaction
            for trans in transactions:
                # Update stock
                update_stock = "UPDATE products SET stock_quantity = stock_quantity - %s WHERE product_id = %s"
                cursor.execute(update_stock, (float(trans['quantity']), trans['product_id']))
                
                # Record transaction
                insert_transaction = """
                    INSERT INTO transactions (user_id, product_id, quantity, unit_price, total_price, discount, payment_method)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_transaction, (
                    trans['user_id'], 
                    trans['product_id'], 
                    float(trans['quantity']), 
                    float(trans['unit_price']), 
                    float(trans['total_price']), 
                    float(trans.get('discount', 0)), 
                    trans.get('payment_method', 'Cash')
                ))
            
            connection.commit()
            self._set_headers(201)
            self.wfile.write(json.dumps({'success': True}).encode())
        except Error as e:
            connection.rollback()
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': str(e)}).encode())
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def handle_daily_sales(self):
        connection = create_connection()
        if not connection:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': 'Database connection failed'}).encode())
            return
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Get sales data
            sales_query = """
                SELECT 
                    p.name AS product,
                    SUM(t.quantity) AS quantity_purchased,
                    p.stock_quantity AS available_stock,
                    SUM(t.total_price) AS total_sales
                FROM 
                    transactions t
                JOIN 
                    products p ON t.product_id = p.product_id
                WHERE 
                    DATE(t.transaction_date) = CURDATE()
                GROUP BY 
                    t.product_id
            """
            cursor.execute(sales_query)
            sales_data = cursor.fetchall()
            
            # Get total bill
            total_query = "SELECT SUM(total_price) AS total FROM transactions WHERE DATE(transaction_date) = CURDATE()"
            cursor.execute(total_query)
            total_result = cursor.fetchone()
            total_bill = float(total_result['total']) if total_result['total'] else 0.0
            
            # Convert Decimal to float
            for item in sales_data:
                item['quantity_purchased'] = float(item['quantity_purchased'])
                item['available_stock'] = float(item['available_stock'])
                item['total_sales'] = float(item['total_sales'])
            
            self._set_headers(200)
            self.wfile.write(json.dumps({
                'sales': sales_data,
                'total_bill': total_bill
            }).encode())
        except Error as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': str(e)}).encode())
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def handle_all_users(self):
        connection = create_connection()
        if not connection:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': 'Database connection failed'}).encode())
            return
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users ORDER BY user_id DESC")
            users = cursor.fetchall()
            
            self._set_headers(200)
            self.wfile.write(json.dumps({'users': users}).encode())
        except Error as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': str(e)}).encode())
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def handle_recent_transactions(self):
        connection = create_connection()
        if not connection:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': 'Database connection failed'}).encode())
            return
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT t.transaction_id, u.name AS customer, p.name AS product, 
                       t.quantity, t.unit_price, t.total_price, t.payment_method, 
                       t.transaction_date
                FROM transactions t
                JOIN users u ON t.user_id = u.user_id
                JOIN products p ON t.product_id = p.product_id
                ORDER BY t.transaction_date DESC 
                LIMIT 5
            """)
            transactions = cursor.fetchall()
            
            # Convert Decimal to float
            for trans in transactions:
                trans['quantity'] = float(trans['quantity'])
                trans['unit_price'] = float(trans['unit_price'])
                trans['total_price'] = float(trans['total_price'])
            
            self._set_headers(200)
            self.wfile.write(json.dumps({'transactions': transactions}).encode())
        except Error as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': str(e)}).encode())
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()