import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# --- Database Configuration ---
# UPDATE THESE VALUES TO MATCH YOUR LOCAL DATABASE SETUP
db_config = {
    'user': 'root',          # Replace with your database username
    'password': '',  # Replace with your database password
    'host': 'localhost',
    'database': 'grocery_app'
}

class GroceryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Grocery Store Finder")
        # Window dimensions
        window_width = 600
        window_height = 500

        # Get the screen dimension
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Find the center point
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)

        # Set the position of the window to the center of the screen
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        # Connect to DB
        self.conn = self.connect_db()
        self.cursor = self.conn.cursor() if self.conn else None

        # Title Label
        title_label = tk.Label(root, text="Search Stores by Zip Code", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # Available Zip Codes Frame
        zip_frame = tk.LabelFrame(root, text="Available Zip Codes (Sample)", padx=10, pady=10)
        zip_frame.pack(pady=5, padx=10, fill="x")

        self.zip_display = tk.Label(zip_frame, text="Loading...", font=("Arial", 10), fg="green")
        self.zip_display.pack()

        # Input Area
        input_frame = tk.Frame(root)
        input_frame.pack(pady=15)

        tk.Label(input_frame, text="Enter Zip Code:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        self.zip_entry = tk.Entry(input_frame, font=("Arial", 12), width=10)
        self.zip_entry.pack(side=tk.LEFT, padx=5)
        
        search_btn = tk.Button(input_frame, text="Search", command=self.search_stores, font=("Arial", 10, "bold"))
        search_btn.pack(side=tk.LEFT, padx=10)

        # Results Area
        results_frame = tk.LabelFrame(root, text="Stores Found", padx=10, pady=10)
        results_frame.pack(pady=5, padx=10, fill="both", expand=True)

        # Treeview for creating a table-like display
        columns = ("store_name", "address")
        self.tree = ttk.Treeview(results_frame, columns=columns, show="headings")
        self.tree.heading("store_name", text="Store Name")
        self.tree.heading("address", text="Address")
        self.tree.column("store_name", width=200)
        self.tree.column("address", width=300)
        self.tree.pack(fill="both", expand=True)

        # Load initial sample zip codes
        self.load_sample_zips()

    def connect_db(self):
        try:
            conn = mysql.connector.connect(**db_config)
            return conn
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not connect to database:\n{err}")
            return None

    def load_sample_zips(self):
        if not self.cursor: return
        
        try:
            # Query to fetch 6 distinct zip codes
            query = "SELECT DISTINCT zipcode FROM grocery_location WHERE zipcode IS NOT NULL LIMIT 6"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            
            if rows:
                # FIX: Convert numeric zip codes to strings using str()
                zips = [str(row[0]) for row in rows]  # <--- The change is here
                zip_string = "  |  ".join(zips)
                self.zip_display.config(text=zip_string)
            else:
                self.zip_display.config(text="No data found in grocery_location table.")
        except mysql.connector.Error as err:
            self.zip_display.config(text="Error fetching zip codes.")
            print(f"Error: {err}")

    def search_stores(self):
        if not self.cursor: return

        zip_input = self.zip_entry.get().strip()
        
        if not zip_input:
            messagebox.showwarning("Input Error", "Please enter a zip code.")
            return

        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            # Query for stores matching the zip
            query = "SELECT STORENAME, STORE_ADDRESS FROM grocery_location WHERE zipcode = %s"
            self.cursor.execute(query, (zip_input,))
            rows = self.cursor.fetchall()

            if rows:
                for row in rows:
                    self.tree.insert("", tk.END, values=row)
            else:
                messagebox.showinfo("No Results", f"No stores found for zip code: {zip_input}")

        except mysql.connector.Error as err:
            messagebox.showerror("Query Error", f"Error searching database:\n{err}")

    def add_user(self):
        if not self.cursor: return

        email_input = self.email_entry.get().strip()        # CHECK EMAIL ENTRY
        
        if not email_input:
            messagebox.showwarning("Input Error", "Please enter an email.")
            return

        password_input = self.password_entry.get().strip()        # CHECK PASSWORD ENTRY
        
        if not password_input:
            messagebox.showwarning("Input Error", "Please enter a password.")
            return

        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            self.cursor.execute("INSERT INTO user (email, password_hash, created_at, stat) VALUES (%s, %s, %s, %s)", (email_input, password_input, datetime.datetime.now(), "Active"))
        except mysql.connector.Error as err:
            messagebox.showerror("Query Error", f"Error searching database:\n{err}")

    def del_user(self):
        if not self.cursor: return

        email_input = self.email_entry.get().strip()        # CHECK EMAIL ENTRY
        
        if not email_input:
            messagebox.showwarning("Input Error", "Please enter an email.")
            return

        password_input = self.password_entry.get().strip()        # CHECK PASSWORD ENTRY
        
        if not password_input:
            messagebox.showwarning("Input Error", "Please enter a password.")
            return

        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            self.cursor.execute("DELETE FROM user WHERE email = '"+email_input+"' AND password_hash = '"+password_input+"'")
        except mysql.connector.Error as err:
            messagebox.showerror("Query Error", f"Error searching database:\n{err}")

    def change_email(self):
        if not self.cursor: return

        old_email_input = self.email_entry.get().strip()        # CHECK EMAIL ENTRY
        
        if not old_email_input:
            messagebox.showwarning("Input Error", "Please enter an email.")
            return

        password_input = self.password_entry.get().strip()        # CHECK PASSWORD ENTRY
        
        if not password_input:
            messagebox.showwarning("Input Error", "Please enter a password.")
            return

        new_email_input = self.email_entry.get().strip()        # CHECK EMAIL ENTRY
        
        if not new_email_input:
            messagebox.showwarning("Input Error", "Please enter an email.")
            return

        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            self.cursor.execute("UPDATE user SET email = '"+new_email_input+"' WHERE email = '"+old_email_input+"' AND password_hash = '"+password_input+"'")
        except mysql.connector.Error as err:
            messagebox.showerror("Query Error", f"Error searching database:\n{err}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GroceryApp(root)
    root.mainloop()