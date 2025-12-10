import mysql.connector
import csv
import os
import uuid
import random
from datetime import datetime

# --- Database Config ---
db_config = {
    'user': 'root',
    # I updated this to the password you used in your GUI snippet. 
    # Change it back to 'password' if that is incorrect.
    'password': 'password', 
    'host': 'localhost',
    'database': 'grocery_app'
}

def get_db_connection():
    try:
        # Connect to MySQL Server (to create DB if needed)
        conn = mysql.connector.connect(
            user=db_config['user'], 
            password=db_config['password'], 
            host=db_config['host']
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['database']}")
        conn.close()

        # Connect to the specific database
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting: {err}")
        return None

def create_tables(cursor):
    """Creates all necessary tables if they do not exist."""
    print("Checking/Creating database tables...")
    
    tables = [
        """CREATE TABLE IF NOT EXISTS user (
            user_id VARCHAR(36) NOT NULL PRIMARY KEY,
            email VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(100) NOT NULL,
            created_at DATETIME NOT NULL,
            stat VARCHAR(20) NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS user_profile (
            user_id VARCHAR(36) NOT NULL PRIMARY KEY,
            display_name VARCHAR(100),
            home_store VARCHAR(100),
            privacy_flags BOOLEAN,
            FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
        )""",
        """CREATE TABLE IF NOT EXISTS food (
            Food_Item_ID VARCHAR(36) NOT NULL PRIMARY KEY, 
            foodname VARCHAR(255) NOT NULL,               
            Category_Name VARCHAR(100),                  
            type VARCHAR(100),
            Cost_per_unit DECIMAL(10,4),                
            cur_demand INT,
            cur_supply INT
        )""",
        """CREATE TABLE IF NOT EXISTS nutrition (
            Food_Item_ID VARCHAR(36) NOT NULL PRIMARY KEY, 
            health_scale VARCHAR(50),
            Energy_kcal DECIMAL(10,2),    
            Protein_g DECIMAL(10,2),      
            Total_Fat_g DECIMAL(10,2),    
            Sugars_g DECIMAL(10,2),       
            Carbohydrate_g DECIMAL(10,2), 
            Alcohol_g DECIMAL(10,2),      
            Water_g DECIMAL(10,2),        
            Caffeine_mg DECIMAL(10,2),    
            FOREIGN KEY (Food_Item_ID) REFERENCES food(Food_Item_ID) ON DELETE CASCADE
        )""",
        """CREATE TABLE IF NOT EXISTS grocery_location (
            OBJECTID VARCHAR(36) NOT NULL PRIMARY KEY, 
            STORENAME VARCHAR(255),         
            STORE_ADDRESS VARCHAR(255),
            zipcode VARCHAR(10),
            branch_name VARCHAR(100)
        )""",
        """CREATE TABLE IF NOT EXISTS user_review (
            review_id VARCHAR(36) NOT NULL PRIMARY KEY,
            user_id VARCHAR(36) NOT NULL,
            store_id VARCHAR(36) NOT NULL,
            rating INT,
            comment TEXT,
            created_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
            FOREIGN KEY (store_id) REFERENCES grocery_location(OBJECTID) ON DELETE CASCADE
        )""",
        """CREATE TABLE IF NOT EXISTS market_price (
            price_id VARCHAR(36) NOT NULL PRIMARY KEY,
            Food_Item_ID VARCHAR(36) NOT NULL,
            form VARCHAR(50),
            retail_price DECIMAL(10,4),
            retail_unit VARCHAR(50),
            yield_factor DECIMAL(5,4),
            cup_equivalent_price DECIMAL(10,4),
            FOREIGN KEY (Food_Item_ID) REFERENCES food(Food_Item_ID) ON DELETE CASCADE
        )"""
    ]

    for sql in tables:
        cursor.execute(sql)
    print("  -> Tables ready.")

# --- Helper to map USDA Food Codes to Category Names ---
def get_category_from_code(foodcode):
    try:
        code_str = str(foodcode).strip()
        if not code_str: return "Unknown"
        first_digit = int(code_str[0])
        categories = {
            1: "Dairy", 2: "Meat, Poultry, Fish", 3: "Eggs",
            4: "Dry Beans, Nuts, Seeds", 5: "Grain Products",
            6: "Fruits", 7: "Vegetables", 8: "Fats, Oils, Dressings",
            9: "Sweets & Sugars"
        }
        return categories.get(first_digit, "Other")
    except: return "Other"

def populate_supertracker_data(cursor):
    """Reads SuperTracker Nutrients.csv to populate Food and Nutrition tables."""
    # We look for the exact filename provided in your upload list
    filename = 'supertrackerfooddatabase.xlsx - Nutrients.csv'
    csv_path = os.path.join(os.path.dirname(__file__), 'data', filename)
    
    if not os.path.exists(csv_path):
        # Fallback: try short name if you renamed it
        csv_path = os.path.join(os.path.dirname(__file__), 'data', 'Nutrients.csv')
        if not os.path.exists(csv_path):
            print(f"Skipping SuperTracker: {filename} not found.")
            return

    print("Populating Food & Nutrition from SuperTracker Data...")
    
    with open(csv_path, mode='r', encoding='utf-8-sig', errors='replace') as f:
        reader = csv.DictReader(f)
        count = 0
        
        for row in reader:
            if count >= 500: break # Limit for speed
            
            try:
                food_id = str(uuid.uuid4())
                name = row.get('foodname', 'Unknown')[:255]
                code = row.get('foodcode', '0')
                category = get_category_from_code(code)
                
                # Check duplicates based on name to prevent massive bloating
                cursor.execute("SELECT Food_Item_ID FROM food WHERE foodname = %s LIMIT 1", (name,))
                if cursor.fetchone(): continue

                # Insert FOOD
                sql_food = "INSERT INTO food (Food_Item_ID, foodname, Category_Name, type, cur_demand, cur_supply) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(sql_food, (food_id, name, category, "Generic", random.randint(10, 100), random.randint(10, 100)))

                # Helper to parse floats safely
                def get_val(key):
                    val = row.get(key, '0')
                    try: return float(val)
                    except: return 0.0

                # Insert NUTRITION
                energy = get_val('_208 Energy (kcal)')
                protein = get_val('_203 Protein (g)')
                fat = get_val('_204 Total Fat (g)')
                carbs = get_val('_205 Carbohydrate (g)')
                sugar = get_val('_269 Sugars, total (g)')
                water = get_val('_255 Water (g)')
                alcohol = get_val('_221 Alcohol (g)')
                caffeine = get_val('_262 Caffeine (mg)')

                health_score = "Moderate"
                if sugar < 5 and fat < 5: health_score = "Healthy"
                if sugar > 15 or fat > 15: health_score = "Unhealthy"

                sql_nut = """INSERT INTO nutrition 
                             (Food_Item_ID, health_scale, Energy_kcal, Protein_g, Total_Fat_g, Sugars_g, 
                              Carbohydrate_g, Alcohol_g, Water_g, Caffeine_mg)
                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql_nut, (food_id, health_score, energy, protein, fat, sugar, carbs, alcohol, water, caffeine))
                count += 1
            except mysql.connector.Error:
                continue
                
    print(f"  -> Successfully loaded {count} food items.")

def populate_locations(cursor):
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'Grocery_Store_Locations.csv')
    if not os.path.exists(csv_path): return

    print("Populating Grocery Locations...")
    with open(csv_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i > 50: break 
            
            # Check for existing
            cursor.execute("SELECT OBJECTID FROM grocery_location WHERE OBJECTID = %s", (row['OBJECTID'],))
            if cursor.fetchone(): continue

            sql = "INSERT INTO grocery_location (OBJECTID, STORENAME, STORE_ADDRESS, zipcode) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (row['OBJECTID'], row['STORENAME'], row['ADDRESS'], row['ZIPCODE']))
    print("  -> Locations populated.")

def populate_market_prices(cursor):
    files = [('Vegetable-Prices-2022.csv', 'Vegetable'), ('Fruit-Prices-2022.csv', 'Fruit')]
    print("Populating Market Prices...")
    
    for filename, cat in files:
        path = os.path.join(os.path.dirname(__file__), 'data', filename)
        if not os.path.exists(path): continue
        
        with open(path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                food_name = row.get('Vegetable') or row.get('Fruit')
                if not food_name: continue
                
                # Try to find existing food, or create new
                cursor.execute("SELECT Food_Item_ID FROM food WHERE foodname = %s LIMIT 1", (food_name,))
                res = cursor.fetchone()
                if res:
                    fid = res[0]
                else:
                    fid = str(uuid.uuid4())
                    cursor.execute("INSERT INTO food (Food_Item_ID, foodname, Category_Name) VALUES (%s, %s, %s)", (fid, food_name, cat))
                
                pid = str(uuid.uuid4())
                sql = """INSERT INTO market_price (price_id, Food_Item_ID, form, retail_price, retail_unit, yield_factor, cup_equivalent_price)
                         VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                # Handle empty strings
                def safe_float(v):
                    try: return float(v)
                    except: return 0.0

                cursor.execute(sql, (pid, fid, row['Form'], safe_float(row['RetailPrice']), row['RetailPriceUnit'], safe_float(row['Yield']), safe_float(row['CupEquivalentPrice'])))
    print("  -> Market prices populated.")

def populate_users_and_reviews(cursor):
    print("Populating Users & Reviews...")
    # Create Admin User
    admin_id = str(uuid.uuid4())
    # Check if admin exists first to avoid duplicate errors
    cursor.execute("SELECT user_id FROM user WHERE email = 'admin@test.com'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO user (user_id, email, password_hash, created_at, stat) VALUES (%s, %s, %s, %s, %s)",
                       (admin_id, "admin@test.com", "pass", datetime.now(), "active"))
    
    # Get store IDs
    cursor.execute("SELECT OBJECTID FROM grocery_location LIMIT 10")
    stores = [r[0] for r in cursor.fetchall()]
    
    if stores:
        reviews = ["Great selection!", "Prices are high.", "Fresh produce.", "Crowded parking."]
        for _ in range(10):
            rid = str(uuid.uuid4())
            sid = random.choice(stores)
            cursor.execute("INSERT INTO user_review (review_id, user_id, store_id, rating, comment, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
                           (rid, admin_id, sid, random.randint(1,5), random.choice(reviews), datetime.now()))
    print("  -> Users and Reviews populated.")

def main():
    conn = get_db_connection()
    if not conn: return
    cursor = conn.cursor()
    
    try:
        # 1. Create Tables (Fixes the "Table doesn't exist" error)
        create_tables(cursor)

        # 2. Populate Data
        populate_locations(cursor)
        populate_supertracker_data(cursor)
        populate_market_prices(cursor)
        populate_users_and_reviews(cursor)
        
        conn.commit()
        print("\n--- Database Population Complete ---")
        
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()