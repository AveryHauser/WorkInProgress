import mysql.connector
import csv
import os

# --- Database Config ---
db_config = {
    'user': 'root',
    'password': 'CHANGE PASSWORD TO MYSQL PASSWORD',  # UPDATE THIS if your password is distinct
    'host': 'localhost',
    'database': 'grocery_app'
}

def populate():
    # 1. Connect to Database
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        print("Connected to database...")
    except mysql.connector.Error as err:
        print(f"Error connecting: {err}")
        return

    # 2. Add 'zipcode' column if it doesn't exist
    # We use a try/except block to safely handle the "Duplicate column" error if you run this twice.
    try:
        print("Checking table structure...")
        cursor.execute("ALTER TABLE grocery_location ADD COLUMN zipcode VARCHAR(10);")
        print("Added 'zipcode' column.")
    except mysql.connector.Error as err:
        if err.errno == 1060: # Duplicate column name error code
            print("'zipcode' column already exists. Skipping.")
        else:
            print(f"Schema Warning: {err}")

    # 3. Read CSV and Insert Data
    # This looks for src/data/Grocery_Store_Locations.csv
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'Grocery_Store_Locations.csv')
    
    if not os.path.exists(csv_path):
        print(f"ERROR: Could not find file at {csv_path}")
        return

    print(f"Reading data from {csv_path}...")
    
    count = 0
    try:
        with open(csv_path, mode='r', encoding='utf-8-sig') as csv_file:
            # DictReader automatically maps headers (OBJECTID, STORENAME, etc.)
            reader = csv.DictReader(csv_file)
            
            for row in reader:
                # Map CSV columns to Table columns
                # CSV Header: OBJECTID, STORENAME, ADDRESS, ZIPCODE
                # DB Columns: OBJECTID, STORENAME, STORE_ADDRESS, zipcode
                
                sql = """
                INSERT INTO grocery_location (OBJECTID, STORENAME, STORE_ADDRESS, zipcode)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    STORENAME=VALUES(STORENAME), 
                    STORE_ADDRESS=VALUES(STORE_ADDRESS), 
                    zipcode=VALUES(zipcode);
                """
                val = (
                    row['OBJECTID'], 
                    row['STORENAME'], 
                    row['ADDRESS'], 
                    row['ZIPCODE']
                )
                
                cursor.execute(sql, val)
                count += 1
                
        conn.commit()
        print(f"Success! Inserted/Updated {count} stores.")
        
    except FileNotFoundError:
        print("File not found. Check your 'data' folder.")
    except KeyError as e:
        print(f"CSV Error: Column {e} not found in CSV. Check your CSV headers.")
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    populate()