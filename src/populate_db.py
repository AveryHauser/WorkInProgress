import mysql.connector
import csv
import os
import uuid
import random
from datetime import datetime

# --- Database Config ---
db_config = {
    'user': 'root',
    'password': 'password',  # <--- UPDATE THIS
    'host': 'localhost',
    'database': 'grocery_app'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting: {err}")
        return None

# --- Helper to map USDA Food Codes to Category Names ---
def get_category_from_code(foodcode):
    try:
        code_str = str(foodcode).strip()
        if not code_str: return "Unknown"
        first_digit = int(code_str[0])
        
        categories = {
            1: "Dairy",
            2: "Meat, Poultry, Fish",
            3: "Eggs",
            4: "Dry Beans, Nuts, Seeds",
            5: "Grain Products",
            6: "Fruits",
            7: "Vegetables",
            8: "Fats, Oils, Dressings",
            9: "Sweets & Sugars"
        }
        return categories.get(first_digit, "Other")
    except:
        return "Other"

def populate_supertracker_data(cursor):
    """Reads SuperTracker Nutrients.csv to populate Food and Nutrition tables."""
    # Note: Using the Nutrients file because it has both names and values
    filename = 'supertrackerfooddatabase.xlsx - Nutrients.csv'
    csv_path = os.path.join(os.path.dirname(__file__), 'data', filename)
    
    if not os.path.exists(csv_path):
        print(f"Skipping SuperTracker: {filename} not found.")
        return

    print("Populating Food & Nutrition from SuperTracker Data...")
    
    with open(csv_path, mode='r', encoding='utf-8-sig', errors='replace') as f:
        reader = csv.DictReader(f)
        count = 0
        
        for row in reader:
            # Limit to first 500 items to keep it fast, remove break to load all
            if count >= 500: break
            
            try:
                # 1. Prepare Data
                food_id = str(uuid.uuid4())
                name = row.get('foodname', 'Unknown')
                code = row.get('foodcode', '0')
                category = get_category_from_code(code)
                
                # 2. Insert into FOOD table
                sql_food = """INSERT INTO food (Food_Item_ID, foodname, Category_Name, type, cur_demand, cur_supply) 
                              VALUES (%s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql_food, (food_id, name, category, "Generic", random.randint(10, 100), random.randint(10, 100)))

                # 3. Insert into NUTRITION table
                # Mapping CSV columns to DB columns
                # _203 Protein, _204 Total Fat, _205 Carb, _208 Energy, _269 Sugar, _255 Water, _221 Alcohol, _262 Caffeine
                
                def get_val(key):
                    val = row.get(key, '0')
                    return float(val) if val and val.strip() != '' else 0.0

                energy = get_val('_208 Energy (kcal)')
                protein = get_val('_203 Protein (g)')
                fat = get_val('_204 Total Fat (g)')
                carbs = get_val('_205 Carbohydrate (g)')
                sugar = get_val('_269 Sugars, total (g)')
                water = get_val('_255 Water (g)')
                alcohol = get_val('_221 Alcohol (g)')
                caffeine = get_val('_262 Caffeine (mg)')

                # Simple health scale logic
                health_score = "Moderate"
                if sugar < 5 and fat < 5: health_score = "Healthy"
                if sugar > 15 or fat > 15: health_score = "Unhealthy"

                sql_nut = """INSERT INTO nutrition 
                             (Food_Item_ID, health_scale, Energy_kcal, Protein_g, Total_Fat_g, Sugars_g, 
                              Carbohydrate_g, Alcohol_g, Water_g, Caffeine_mg)
                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                
                cursor.execute(sql_nut, (food_id, health_score, energy, protein, fat, sugar, carbs, alcohol, water, caffeine))
                count += 1
                
            except mysql.connector.Error as err:
                print(f"Skipping row: {err}")
                continue
                
    print(f"  -> Successfully loaded {count} food items.")

def populate_locations(cursor):
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'Grocery_Store_Locations.csv')
    if not os.path.exists(csv_path): return

    print("Populating Grocery Locations...")
    with open(csv_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i > 50: break # Limit for speed
            sql = """INSERT INTO grocery_location (OBJECTID, STORENAME, STORE_ADDRESS, zipcode)
                     VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE STORENAME=VALUES(STORENAME)"""
            cursor.execute(sql, (row['OBJECTID'], row['STORENAME'], row['ADDRESS'], row['ZIPCODE']))
    print("  -> Locations populated.")

def populate_market_prices(cursor):
    """Uses Vegetable/Fruit CSVs for Market Price table"""
    files = [('Vegetable-Prices-2022.csv', 'Vegetable'), ('Fruit-Prices-2022.csv', 'Fruit')]
    print("Populating Market Prices...")
    
    for filename, cat in files:
        path = os.path.join(os.path.dirname(__file__), 'data', filename)
        if not os.path.exists(path): continue
        
        with open(path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # We need a food ID. For simplicity, we create a new food entry if it doesn't exist
                # or just link it blindly. Here we will create a placeholder food entry for the price.
                food_name = row.get('Vegetable') or row.get('Fruit')
                if not food_name: continue
                
                fid = str(uuid.uuid4())
                pid = str(uuid.uuid4())
                
                # Insert minimal food record so FK works
                cursor.execute("INSERT INTO food (Food_Item_ID, foodname, Category_Name) VALUES (%s, %s, %s)", 
                               (fid, food_name, cat))
                
                # Insert Price
                sql = """INSERT INTO market_price (price_id, Food_Item_ID, form, retail_price, retail_unit, yield_factor, cup_equivalent_price)
                         VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (pid, fid, row['Form'], row['RetailPrice'], row['RetailPriceUnit'], row['Yield'], row['CupEquivalentPrice']))
    print("  -> Market prices populated.")

def populate_users_and_reviews(cursor):
    print("Populating Users & Reviews...")
    # Create Admin User
    admin_id = str(uuid.uuid4())
    cursor.execute("INSERT INTO user (user_id, email, password_hash, created_at, stat) VALUES (%s, %s, %s, %s, %s)",
                   (admin_id, "admin@test.com", "pass", datetime.now(), "active"))
    
    # Get some stores
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
    
    # 1. Locations
    populate_locations(cursor)
    
    # 2. SuperTracker Food & Nutrition
    populate_supertracker_data(cursor)
    
    # 3. Market Prices (Fruits/Veg)
    populate_market_prices(cursor)
    
    # 4. Users & Reviews
    populate_users_and_reviews(cursor)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("\n--- Database Population Complete ---")

if __name__ == "__main__":
    main()