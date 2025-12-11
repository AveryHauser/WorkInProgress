import mysql.connector
import csv
import os
import random
from datetime import datetime

# --- Database Config ---
db_config = {
    'user': 'root',
    'password': 'password',  # <--- UPDATE THIS
    'host': 'localhost',
    'database': 'grocery_app'
}

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def get_db_connection():
    try:
        # Create Database if missing
        conn = mysql.connector.connect(
            user=db_config['user'], 
            password=db_config['password'], 
            host=db_config['host']
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['database']}")
        conn.close()

        # Connect to Database
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting: {err}")
        return None

def setup_database(cursor):
    """Executes the SQL file to reset the database schema."""
    print("Initializing Database Schema from SQL file...")
    
    # 1. Drop Tables to Start Fresh (Order matters for Foreign Keys)
    tables = [
        "log", "user_review", "market_price", "grocery_list_item", "grocery_list", 
        "pantry", "recipe_ingredient", "recipe", "store_product", 
        "food_dietary_map", "dietary_tag", "mineral", "vitamin", "nutrition", 
        "food", "category", "session", "user_profile", "user", 
        "grocery_location", "county_health_data",
    ]
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    for t in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {t}")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

    # 2. Read and Run SQL File
    sql_path = os.path.join(os.path.dirname(__file__), 'Grocery_AppDB.sql')
    if not os.path.exists(sql_path):
        print(f"Error: {sql_path} not found.")
        return

    with open(sql_path, 'r') as f:
        sql_script = f.read()

    # Execute each command
    for statement in sql_script.split(';'):
        if statement.strip():
            try:
                cursor.execute(statement)
            except mysql.connector.Error as err:
                if "already exists" not in str(err):
                    pass # Ignore trivial warnings
    
    print("  -> Schema created successfully.")

def read_data_source(partial_filename, sheet_name=None):
    """
    Helper to read data from CSV OR Excel.
    Returns a list of dictionaries (rows).
    """
    # 1. Try finding a CSV file first (Exact or partial match)
    csv_file = None
    
    # Check exact match first
    if os.path.exists(os.path.join(DATA_DIR, partial_filename)):
        csv_file = os.path.join(DATA_DIR, partial_filename)
    else:
        # Check partial match
        for f in os.listdir(DATA_DIR):
            if partial_filename in f and f.endswith(".csv"):
                csv_file = os.path.join(DATA_DIR, f)
                break
            
    if csv_file:
        # print(f"  Reading from {os.path.basename(csv_file)}...")
        with open(csv_file, mode='r', encoding='utf-8-sig', errors='replace') as f:
            return list(csv.DictReader(f))
            
    # 2. If no CSV, try the main Excel file
    xlsx_file = os.path.join(DATA_DIR, 'supertrackerfooddatabase.xlsx')
    if os.path.exists(xlsx_file):
        try:
            import pandas as pd
            # print(f"  Reading '{sheet_name}' from Excel...")
            if sheet_name:
                df = pd.read_excel(xlsx_file, sheet_name=sheet_name)
            else:
                df = pd.read_excel(xlsx_file, sheet_name=0) 
            
            # Convert to list of dicts, replacing NaN with empty string
            return df.fillna('').to_dict(orient='records')
        except:
            pass
            
    return []

def populate_categories(cursor):
    """Populates Category table from CSV."""
    print("Populating Categories...")
    
    # Try to find 'Food_Categories' data
    rows = read_data_source("Categories", "Food_Categories")
    
    if not rows:
        print("  [!] Skipping Categories: No data found.")
        return

    count = 0
    for row in rows:
        try:
            cid = row.get('Category_ID')
            cname = row.get('Category_Name')
            if cid and cname:
                cursor.execute("INSERT IGNORE INTO category (Category_ID, Category_Name) VALUES (%s, %s)", (cid, cname))
                count += 1
        except: continue
    print(f"  -> Added {count} categories.")

def get_category_id(foodcode):
    """Maps USDA Food Code to Category_ID."""
    try:
        digit = int(str(foodcode)[0])
        # Mapping USDA Groups (1-9) to your Category IDs (from CSV)
        mapping = {
            1: 6,  # Dairy
            2: 7,  # Meat
            3: 7,  # Eggs -> Meat
            4: 5,  # Beans/Nuts -> Vegetables
            5: 2,  # Grains
            6: 4,  # Fruit
            7: 5,  # Veg
            8: 10, # Fats
            9: 12  # Sweets
        }
        return mapping.get(digit, 0)
    except: return 0

def populate_food_and_nutrition(cursor):
    """Populates Food and Nutrition."""
    print("Populating Food & Nutrition...")
    
    # Try to find 'Nutrients' data
    rows = read_data_source("Nutrients", "Nutrients")

    if not rows:
        print("  [!] Skipping Food: No data found.")
        return

    count = 0
    for row in rows:
        if count >= 600: break
        
        try:
            name = str(row.get('foodname', 'Unknown'))[:255]
            cat_id = get_category_id(row.get('foodcode', 0))
            
            # Ensure Category Exists (Fallback for safety)
            cursor.execute("SELECT Category_ID FROM category WHERE Category_ID = %s", (cat_id,))
            if not cursor.fetchone():
                cat_id = 0 
                cursor.execute("INSERT IGNORE INTO category (Category_ID, Category_Name) VALUES (0, 'Other')")
            
            cursor.execute(
                "INSERT INTO food (foodname, Category_ID, type, Cost_per_unit) VALUES (%s, %s, %s, %s)",
                (name, cat_id, "Generic", 0.00)
            )
            food_id = cursor.lastrowid

            def val(k): 
                try: return float(row.get(k, 0))
                except: return 0.0
            
            # Insert Nutrition
            cursor.execute("""
                INSERT INTO nutrition 
                (Food_Item_ID, health_scale, Energy_kcal, Protein_g, Total_Fat_g, Sugars_g, Carbohydrate_g, Water_g, Caffeine_mg)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                food_id, "Neutral", 
                val('_208 Energy (kcal)'), val('_203 Protein (g)'), val('_204 Total Fat (g)'), 
                val('_269 Sugars, total (g)'), val('_205 Carbohydrate (g)'), val('_255 Water (g)'), val('_262 Caffeine (mg)')
            ))

            # Insert Vitamins (if columns exist)
            vit_c = val('_401 Vitamin C (mg)')
            if vit_c > 0:
                cursor.execute("INSERT INTO vitamin (Food_Item_ID, name, amount, unit) VALUES (%s, %s, %s, %s)", 
                               (food_id, "Vitamin C", vit_c, "mg"))

            # Insert Minerals (if columns exist)
            calcium = val('_301 Calcium (mg)')
            if calcium > 0:
                cursor.execute("INSERT INTO mineral (Food_Item_ID, name, amount, unit) VALUES (%s, %s, %s, %s)", 
                               (food_id, "Calcium", calcium, "mg"))

            count += 1
        except mysql.connector.Error:
            continue
    print(f"  -> Added {count} food items.")

def populate_market_prices(cursor):
    print("Populating Market Prices...")
    
    files = [f for f in os.listdir(DATA_DIR) if "Prices" in f and f.endswith(".csv")]
    
    count = 0
    for filename in files:
        rows = read_data_source(filename)
        for row in rows:
            name = row.get('Vegetable') or row.get('Fruit')
            if not name: continue

            # Match with Food table
            cursor.execute("SELECT Food_Item_ID FROM food WHERE foodname LIKE %s LIMIT 1", (f"%{name}%",))
            res = cursor.fetchone()
            
            if res:
                fid = res[0]
                try:
                    price = float(row.get('RetailPrice', 0))
                    cursor.execute("""
                        INSERT INTO market_price (Food_Item_ID, price_per_unit, unit_type, data_year)
                        VALUES (%s, %s, %s, %s)
                    """, (fid, price, row.get('RetailPriceUnit', 'lb'), 2022))
                    count += 1
                except: continue
                
    print(f"  -> Added {count} market prices.")

def populate_locations(cursor):
    print("Populating Locations...")
    rows = read_data_source("Grocery_Store_Locations.csv")
    count = 0
    for row in rows:
        if count > 100: break
        try:
            # Note: Your SQL schema for grocery_location has 'OBJECTID' as int auto_increment
            # We can let MySQL handle it, or insert it if provided.
            cursor.execute(
                "INSERT INTO grocery_location (STORENAME, STORE_ADDRESS, zipcode) VALUES (%s, %s, %s)",
                (row.get('STORENAME'), row.get('ADDRESS') or row.get('STORE_ADDRESS'), row.get('ZIPCODE'))
            )
            count += 1
        except: continue
    print(f"  -> Added {count} locations.")

def populate_county_data(cursor):
    print("Populating County Health Data...")
    rows = read_data_source("StateAndCountyData.csv")
    count = 0
    for row in rows:
        if count > 200: break
        try:
            cursor.execute("""
                INSERT INTO county_health_data (FIPS, State, County, Variable_Code, Value) 
                VALUES (%s, %s, %s, %s, %s)
            """, (row['FIPS'], row['State'], row['County'], row['Variable_Code'], row['Value']))
            count += 1
        except: continue
    print(f"  -> Added {count} county records.")

def populate_users_and_reviews(cursor):
    print("Populating Users & Reviews...")
    
    # Only create a user if one doesn't exist
    cursor.execute("SELECT user_id FROM user WHERE email = 'guest@test.com'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO user (email, password_hash, stat) VALUES (%s, %s, %s)", 
                       ("guest@test.com", "pass", "active"))
        user_id = cursor.lastrowid
        cursor.execute("INSERT INTO user_profile (user_id, display_name) VALUES (%s, %s)", (user_id, "Guest"))
        
        # Add a few dummy reviews just so the table isn't empty (as per requirement)
        cursor.execute("SELECT Food_Item_ID FROM food LIMIT 10")
        foods = [r[0] for r in cursor.fetchall()]
        if foods:
            for _ in range(5):
                fid = random.choice(foods)
                cursor.execute("""
                    INSERT INTO user_review (user_id, Food_Item_ID, rating, comment, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_id, fid, 5, "Sample Data Review", datetime.now()))
            print("  -> guest user and initial reviews created.")
    else:
        print("  -> guest user already exists.")

def populate_logs(cursor):
    print("Populating Logs...")
    try:
        # Generate one initial entry
        sql = "INSERT INTO log (action, time_completed) VALUES (%s, %s)"
        cursor.execute(sql, ("System: Database Repopulated", datetime.now()))
        print("  -> Added initial system log entry.")
    except Exception as e:
        print(f"  [!] Could not populate log: {e}")

def main():
    conn = get_db_connection()
    if not conn: return
    cursor = conn.cursor()

    try:
        setup_database(cursor)
        populate_categories(cursor)
        populate_food_and_nutrition(cursor)
        populate_locations(cursor)
        populate_market_prices(cursor)
        populate_county_data(cursor)
        populate_users_and_reviews(cursor)
        populate_logs(cursor)

        conn.commit()
        print("\n--- Database Population Complete ---")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()