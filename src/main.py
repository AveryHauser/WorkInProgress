import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import uuid
from datetime import datetime

# --- Database Configuration ---
db_config = {
    'user': 'root',
    'password': 'password',  # <--- UPDATE THIS TO YOUR PASSWORD
    'host': 'localhost',
    'database': 'grocery_app'
}

class LoginWindow:
    def __init__(self, root, on_success_callback):
        self.root = root
        self.on_success = on_success_callback
        self.root.title("System Login")
        
        # Center the window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int(screen_width/2 - 800/2)
        y = int(screen_height/2 - 600/2)
        self.root.geometry(f"800x600+{x}+{y}")

        tk.Label(root, text="Grocery Admin Login", font=("Arial", 14, "bold")).pack(pady=20)
        
        # Username
        tk.Frame(root).pack(pady=5)
        tk.Label(root, text="User:").pack()
        self.user_entry = tk.Entry(root)
        self.user_entry.insert(0, "admin")
        self.user_entry.pack()

        # Password
        tk.Label(root, text="Password:").pack()
        self.pass_entry = tk.Entry(root, show="*")
        self.pass_entry.insert(0, "1234") # Temp password
        self.pass_entry.pack()

        tk.Button(root, text="Login", command=self.check_login, bg="#dddddd").pack(pady=15)

    def check_login(self):
        # Temp hardcoded password logic
        if self.user_entry.get() == "admin" and self.pass_entry.get() == "1234":
            self.root.destroy()
            self.on_success()
        else:
            messagebox.showerror("Login Failed", "Invalid Username or Password")

class GroceryApp:
    def __init__(self, root, db_config):
        self.root = root
        self.db_config = db_config
        self.root.title("Grocery Store Manager & Analytics")
        
        # Window dimensions
        window_width = 800
        window_height = 700 # Increased height for new fields
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int(screen_width / 2 - window_width / 2)
        y = int(screen_height / 2 - window_height / 2)
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')

        # Connect to DB
        self.conn = self.connect_db()
        self.cursor = self.conn.cursor() if self.conn else None

        # --- Tabs Setup ---
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        # Tab 1: Data Management
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="Manage Data")
        self.setup_data_tab()

        # Tab 2: Analytics
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="Analytics Dashboard")
        self.setup_analytics_tab()

    def connect_db(self):
        try:
            conn = mysql.connector.connect(**self.db_config)
            return conn
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not connect:\n{err}")
            return None

    # ------------------------------------------------------------------
    # TAB 1: DATA MANAGEMENT
    # ------------------------------------------------------------------
    def setup_data_tab(self):
        # --- Section 1: Search Stores ---
        search_frame = tk.LabelFrame(self.tab1, text="Search Stores", padx=10, pady=10)
        search_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(search_frame, text="Zip Code:").pack(side=tk.LEFT)
        self.zip_entry = tk.Entry(search_frame, width=10)
        self.zip_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Search", command=self.search_stores).pack(side=tk.LEFT)

        # Treeview Results
        columns = ("store_name", "address", "zip")
        self.tree = ttk.Treeview(search_frame, columns=columns, show="headings", height=5)
        self.tree.heading("store_name", text="Store Name")
        self.tree.heading("address", text="Address")
        self.tree.heading("zip", text="Zip")
        self.tree.column("store_name", width=200)
        self.tree.column("address", width=300)
        self.tree.column("zip", width=80)
        self.tree.pack(fill="x", pady=5)

        add_frame = tk.LabelFrame(self.tab1, text="Add New Store (Write Data)", padx=10, pady=10)
        add_frame.pack(fill="x", padx=10, pady=10)

        # Form
        tk.Label(add_frame, text="Store Name:").grid(row=0, column=0, sticky="e")
        self.new_name = tk.Entry(add_frame, width=30)
        self.new_name.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(add_frame, text="Address:").grid(row=1, column=0, sticky="e")
        self.new_addr = tk.Entry(add_frame, width=30)
        self.new_addr.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(add_frame, text="Zip Code:").grid(row=2, column=0, sticky="e")
        self.new_zip = tk.Entry(add_frame, width=10)
        self.new_zip.grid(row=2, column=1, sticky="w", padx=5, pady=2)

        tk.Button(add_frame, text="Add to Database", command=self.add_store, bg="#d9fdd3").grid(row=3, column=1, sticky="e", pady=10)

        # --- Section 2: Add User ---
        user_frame = tk.LabelFrame(self.tab1, text="Add New User", padx=10, pady=10)
        user_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(user_frame, text="Email:").grid(row=0, column=0, sticky="e")
        self.email_entry = tk.Entry(user_frame, width=30)
        self.email_entry.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(user_frame, text="Password:").grid(row=1, column=0, sticky="e")
        self.password_entry = tk.Entry(user_frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=2)

        tk.Button(user_frame, text="Create User", command=self.add_user, bg="#d9fdd3").grid(row=2, column=1, sticky="e", pady=10)

    def search_stores(self):
        if not self.cursor: return
        zip_code = self.zip_entry.get().strip()
        
        for i in self.tree.get_children(): self.tree.delete(i)
        
        try:
            sql = "SELECT STORENAME, STORE_ADDRESS, zipcode FROM grocery_location WHERE zipcode = %s"
            self.cursor.execute(sql, (zip_code,))
            rows = self.cursor.fetchall()
            if not rows:
                messagebox.showinfo("Info", "No stores found.")
            for row in rows:
                self.tree.insert("", tk.END, values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", str(err))
    
    def add_store(self):
        if not self.cursor: return
        name = self.new_name.get()
        addr = self.new_addr.get()
        zip_c = self.new_zip.get()

        if not name or not zip_c:
            messagebox.showwarning("Missing Data", "Name and Zip Code are required.")
            return

        try:
            obj_id = str(uuid.uuid4())
            sql = "INSERT INTO grocery_location (OBJECTID, STORENAME, STORE_ADDRESS, zipcode) VALUES (%s, %s, %s, %s)"
            self.cursor.execute(sql, (obj_id, name, addr, zip_c))
            self.conn.commit()
            messagebox.showinfo("Success", "Store added successfully!")
            
            # Clear fields
            self.new_name.delete(0, tk.END)
            self.new_addr.delete(0, tk.END)
            self.new_zip.delete(0, tk.END)
            
            # Refresh Analytics
            self.refresh_analytics()
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))

    def add_user(self):
        """Adds a new user to the database with a unique ID."""
        if not self.cursor: return

        email_input = self.email_entry.get().strip()
        password_input = self.password_entry.get().strip()
        
        if not email_input:
            messagebox.showwarning("Input Error", "Please enter an email.")
            return

        if not password_input:
            messagebox.showwarning("Input Error", "Please enter a password.")
            return

        try:
            # 1. Generate unique ID (Fixes the issue of hardcoding '1')
            user_id = str(uuid.uuid4())
            current_time = datetime.now()

            # 2. Insert Query
            sql = "INSERT INTO user (user_id, email, password_hash, created_at, stat) VALUES (%s, %s, %s, %s, %s)"
            self.cursor.execute(sql, (user_id, email_input, password_input, current_time, "Active"))
            
            # 3. Commit (Required to save data)
            self.conn.commit()

            messagebox.showinfo("Success", "User added successfully!")
            
            # Clear fields
            self.email_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error adding user:\n{err}")

    # ------------------------------------------------------------------
    # TAB 2: ANALYTICS
    # ------------------------------------------------------------------
    def setup_analytics_tab(self):
        tk.Button(self.tab2, text="Refresh Analytics", command=self.refresh_analytics).pack(pady=5)
        self.charts_frame = tk.Frame(self.tab2)
        self.charts_frame.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(self.charts_frame, bg="white")
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        self.root.after(500, self.refresh_analytics)

    def refresh_analytics(self):
        if not self.cursor: return
        self.canvas.delete("all")
        self.draw_summary_stats(50, 50)
        self.draw_top_zips_chart(50, 200)
        self.draw_top_brands_chart(400, 200)

    def draw_summary_stats(self, x, y):
        try:
            self.cursor.execute("SELECT COUNT(*) FROM grocery_location")
            total_stores = self.cursor.fetchone()[0]
            self.cursor.execute("SELECT COUNT(DISTINCT zipcode) FROM grocery_location")
            total_zips = self.cursor.fetchone()[0]

            self.canvas.create_text(x, y, text="View 1: Database Summary", font=("Arial", 12, "bold"), anchor="w")
            self.canvas.create_text(x, y+30, text=f"Total Stores Tracked: {total_stores}", anchor="w", fill="blue")
            self.canvas.create_text(x, y+50, text=f"Total Zip Codes Covered: {total_zips}", anchor="w", fill="green")
        except: pass

    def draw_top_zips_chart(self, x, y):
        self.canvas.create_text(x, y, text="View 2: Top 3 Zip Codes (Density)", font=("Arial", 11, "bold"), anchor="w")
        try:
            sql = "SELECT zipcode, COUNT(*) as cnt FROM grocery_location GROUP BY zipcode ORDER BY cnt DESC LIMIT 3"
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
            start_y = y + 30
            max_width = 200
            if rows:
                max_val = rows[0][1]
                for i, (zip_c, count) in enumerate(rows):
                    bar_w = (count / max_val) * max_width if max_val > 0 else 0
                    self.canvas.create_rectangle(x, start_y, x + bar_w, start_y + 20, fill="#69b3a2", outline="white")
                    self.canvas.create_text(x + bar_w + 5, start_y + 10, text=f"{zip_c} ({count})", anchor="w")
                    start_y += 30
            else:
                self.canvas.create_text(x, start_y, text="No Data Available", anchor="w")
        except: pass

    def draw_top_brands_chart(self, x, y):
        self.canvas.create_text(x, y, text="View 3: Top 3 Store Brands", font=("Arial", 11, "bold"), anchor="w")
        try:
            sql = "SELECT STORENAME, COUNT(*) as cnt FROM grocery_location GROUP BY STORENAME ORDER BY cnt DESC LIMIT 3"
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
            start_y = y + 30
            max_width = 200
            if rows:
                max_val = rows[0][1]
                for i, (name, count) in enumerate(rows):
                    bar_w = (count / max_val) * max_width if max_val > 0 else 0
                    self.canvas.create_rectangle(x, start_y, x + bar_w, start_y + 20, fill="#ff9f43", outline="white")
                    disp_name = (name[:15] + '..') if len(name) > 15 else name
                    self.canvas.create_text(x + bar_w + 5, start_y + 10, text=f"{disp_name} ({count})", anchor="w")
                    start_y += 30
            else:
                self.canvas.create_text(x, start_y, text="No Data Available", anchor="w")
        except: pass

if __name__ == "__main__":
    main_root = tk.Tk()
    
    def launch_app():
        main_root.deiconify() 
        app = GroceryApp(main_root, db_config)

    main_root.withdraw() 
    login_window = tk.Toplevel(main_root)
    login = LoginWindow(login_window, launch_app)
    
    main_root.mainloop()