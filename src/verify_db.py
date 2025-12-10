import mysql.connector

# --- Database Config ---
db_config = {
    'user': 'root',
    'password': 'password',  # <--- UPDATE THIS
    'host': 'localhost',
    'database': 'grocery_app'
}

def verify():
    print("\n--- Verifying Database Content ---")
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # List of all tables to check
        tables = [
            "category", "food", "nutrition", "grocery_location", 
            "market_price", "user", "user_profile", "user_review", 
            "county_health_data", "vitamin", "mineral"
        ]

        print(f"{'Table Name':<25} | {'Row Count':<10}")
        print("-" * 40)

        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"{table:<25} | {count:<10}")
            except mysql.connector.Error as err:
                # Table might not exist or verify failed
                print(f"{table:<25} | Not Found / Empty")

        print("\n--- Sample Data: Top 3 Foods ---")
        cursor.execute("SELECT foodname, Category_ID FROM food LIMIT 3")
        for row in cursor.fetchall():
            print(f" - {row[0]} (Cat ID: {row[1]})")

        conn.close()
    except mysql.connector.Error as err:
        print(f"Connection Error: {err}")

if __name__ == "__main__":
    verify()