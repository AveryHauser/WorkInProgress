import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector
import uuid
from datetime import datetime

# --- Database Configuration ---
db_config = {
    'user': 'root',          # Replace with your database username
    'password': 'password',  # Replace with your database password
    'host': 'localhost',
    'database': 'grocery_app'
}

class LoginWindow:
    def __init__(self, root, on_success_callback, db_config):
        self.root = root
        self.on_success = on_success_callback
        self.db_config = db_config
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

        conn = mysql.connector.connect(**self.db_config)
        self.cursor = conn.cursor()
        username = self.user_entry.get()
        password = self.pass_entry.get()

      #  self.cursor.execute("SELECT user_id FROM user WHERE username = '"+username+"' AND password = '"+password+"'")
       # id = self.cursor.fetchone()

        query = "SELECT user_id FROM user WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))

        result = cursor.fecthone()

        if result:
            self.root.destroy()
            self.on_success()
        else:
            messagebox.showerror("Login Failed", "Invalid Username or Password")

     #   if self.user_entry.get() == "admin" and self.pass_entry.get() == "1234":
      #      self.root.destroy()
       #     self.on_success()
        #else:
         #   messagebox.showerror("Login Failed", "Invalid Username or Password")

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

        # Tab 2: Food Database (NEW)
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="Food Database")
        self.setup_food_tab()

        # Tab 3: Analytics
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text="Analytics Dashboard")
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

        # --- Section 2: Manage Users ---
        user_frame = tk.LabelFrame(self.tab1, text="Manage Users", padx=10, pady=10)
        user_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(user_frame, text="Email:").grid(row=0, column=0, sticky="e")
        self.email_entry = tk.Entry(user_frame, width=30)
        self.email_entry.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(user_frame, text="Password:").grid(row=1, column=0, sticky="e")
        self.password_entry = tk.Entry(user_frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=2)
        
        # Buttons for your User functions
        btn_frame = tk.Frame(user_frame)
        btn_frame.grid(row=2, column=1, sticky="e", pady=10)
        
        tk.Button(btn_frame, text="Create", command=self.add_user, bg="#d9fdd3").pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Update Email", command=self.change_email, bg="#fff9c4").pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Delete", command=self.del_user, bg="#ffcccb").pack(side=tk.LEFT, padx=2)

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
            messagebox.showerror("Database Error", f"Error adding user:\n{err}")

    # TAB 2: 
    def setup_food_tab(self):
        # Top Bar: Search & Actions
        top_frame = tk.Frame(self.tab2)
        top_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(top_frame, text="Find Food:").pack(side=tk.LEFT)
        self.food_search_entry = tk.Entry(top_frame, width=20)
        self.food_search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Search", command=self.search_food).pack(side=tk.LEFT)
        
        tk.Button(top_frame, text="View Vitamins/Minerals", command=self.view_micros, bg="#e1f5fe").pack(side=tk.RIGHT, padx=5)
        tk.Button(top_frame, text="Edit Nutrition", command=self.edit_food, bg="#fff9c4").pack(side=tk.RIGHT, padx=5)

        # Main Table (Food + Nutrition Join)
        columns = ("id", "name", "category", "kcal", "protein", "fat", "carbs", "sugar")
        self.food_tree = ttk.Treeview(self.tab2, columns=columns, show="headings", height=20)
        
        self.food_tree.heading("id", text="ID")
        self.food_tree.heading("name", text="Food Name")
        self.food_tree.heading("category", text="Category")
        self.food_tree.heading("kcal", text="Energy (kcal)")
        self.food_tree.heading("protein", text="Protein (g)")
        self.food_tree.heading("fat", text="Fat (g)")
        self.food_tree.heading("carbs", text="Carbs (g)")
        self.food_tree.heading("sugar", text="Sugar (g)")

        self.food_tree.column("id", width=0, stretch=tk.NO) # Hidden ID column
        self.food_tree.column("name", width=250)
        self.food_tree.column("category", width=150)
        self.food_tree.column("kcal", width=80)
        self.food_tree.column("protein", width=80)
        self.food_tree.column("fat", width=80)
        self.food_tree.column("carbs", width=80)
        self.food_tree.column("sugar", width=80)
        
        self.food_tree.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Load initial data
        self.search_food()

    def search_food(self):
        if not self.cursor: return
        query = self.food_search_entry.get().strip()
        
        for i in self.food_tree.get_children(): self.food_tree.delete(i)
        
        try:
            # Join Food, Category, and Nutrition tables
            sql = """
                SELECT f.Food_Item_ID, f.foodname, c.Category_Name, 
                       n.Energy_kcal, n.Protein_g, n.Total_Fat_g, n.Carbohydrate_g, n.Sugars_g
                FROM food f
                LEFT JOIN category c ON f.Category_ID = c.Category_ID
                LEFT JOIN nutrition n ON f.Food_Item_ID = n.Food_Item_ID
                WHERE f.foodname LIKE %s
                LIMIT 100
            """
            self.cursor.execute(sql, (f"%{query}%",))
            for row in self.cursor.fetchall():
                self.food_tree.insert("", tk.END, values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", str(err))

    def edit_food(self):
        selected = self.food_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a food to edit.")
            return

        item = self.food_tree.item(selected[0])
        food_id = item['values'][0]
        current_name = item['values'][1]
        
        new_kcal = simpledialog.askfloat("Edit Nutrition", f"Enter new Energy (kcal) for {current_name}:")
        
        if new_kcal is not None:
            try:
                self.cursor.execute("UPDATE nutrition SET Energy_kcal = %s WHERE Food_Item_ID = %s", (new_kcal, food_id))
                self.conn.commit()
                messagebox.showinfo("Success", "Nutrition updated!")
                self.search_food() # Refresh
                self.refresh_analytics() # Update charts
            except mysql.connector.Error as err:
                messagebox.showerror("Error", str(err))

    def view_micros(self, event=None):
        """Shows Vitamins and Minerals in a popup."""
        selected = self.food_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a food to view details.")
            return

        item = self.food_tree.item(selected[0])
        food_id = item['values'][0]
        food_name = item['values'][1]

        popup = tk.Toplevel(self.root)
        popup.title(f"Micronutrients: {food_name}")
        popup.geometry("400x400")

        txt = tk.Text(popup, width=50, height=20)
        txt.pack(padx=10, pady=10)
        
        try:
            txt.insert(tk.END, "--- VITAMINS ---\n")
            self.cursor.execute("SELECT name, amount, unit FROM vitamin WHERE Food_Item_ID = %s", (food_id,))
            vits = self.cursor.fetchall()
            if vits:
                for v in vits: txt.insert(tk.END, f"{v[0]}: {v[1]} {v[2]}\n")
            else:
                txt.insert(tk.END, "No Vitamin data available.\n")

            txt.insert(tk.END, "\n--- MINERALS ---\n")
            self.cursor.execute("SELECT name, amount, unit FROM mineral WHERE Food_Item_ID = %s", (food_id,))
            mins = self.cursor.fetchall()
            if mins:
                for m in mins: txt.insert(tk.END, f"{m[0]}: {m[1]} {m[2]}\n")
            else:
                txt.insert(tk.END, "No Mineral data available.\n")
                
            txt.config(state=tk.DISABLED)
        except mysql.connector.Error as err:
            txt.insert(tk.END, f"Error: {err}")

    # ------------------------------------------------------------------
    # TAB 3: ANALYTICS
    # ------------------------------------------------------------------
    def setup_analytics_tab(self):
        tk.Button(self.tab3, text="Refresh Analytics", command=self.refresh_analytics).pack(pady=5)
        self.charts_frame = tk.Frame(self.tab3)
        self.charts_frame.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(self.charts_frame, bg="white")
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        self.root.after(500, self.refresh_analytics)

    def refresh_analytics(self):
        if not self.cursor: return
        self.canvas.delete("all")
        self.draw_summary_stats(50, 50)
        self.draw_top_zips_chart(50, 200)
        self.draw_health_chart(350, 200)   # NEW
        self.draw_cal_chart(650, 200)     # NEW

    def draw_summary_stats(self, x, y):
        try:
            self.cursor.execute("SELECT COUNT(*) FROM grocery_location")
            total_stores = self.cursor.fetchone()[0]
            self.cursor.execute("SELECT COUNT(*) FROM food")
            total_food = self.cursor.fetchone()[0]

            self.canvas.create_text(x, y, text="View 1: Database Summary", font=("Arial", 12, "bold"), anchor="w")
            self.canvas.create_text(x, y+30, text=f"Total Stores Tracked: {total_stores}", anchor="w", fill="blue")
            self.canvas.create_text(x, y+50, text=f"Total Food Items: {total_food}", anchor="w", fill="green")
        except: pass

    def draw_top_zips_chart(self, x, y):
        self.canvas.create_text(x, y, text="View 2: Top Zips", font=("Arial", 11, "bold"), anchor="w")
        try:
            sql = "SELECT zipcode, COUNT(*) as cnt FROM grocery_location GROUP BY zipcode ORDER BY cnt DESC LIMIT 3"
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
            start_y = y + 30
            max_width = 150
            if rows:
                max_val = rows[0][1]
                for i, (zip_c, count) in enumerate(rows):
                    bar_w = (count / max_val) * max_width if max_val > 0 else 0
                    self.canvas.create_rectangle(x, start_y, x + bar_w, start_y + 20, fill="#69b3a2", outline="white")
                    self.canvas.create_text(x + bar_w + 5, start_y + 10, text=f"{zip_c} ({count})", anchor="w")
                    start_y += 30
        except: pass

    def draw_health_chart(self, x, y):
        """Shows Count of Healthy vs Unhealthy foods."""
        self.canvas.create_text(x, y, text="View 3: Food Health Scale", font=("Arial", 11, "bold"), anchor="w")
        try:
            sql = "SELECT health_scale, COUNT(*) FROM nutrition GROUP BY health_scale"
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
            
            start_y = y + 30
            max_width = 150
            
            total = sum([r[1] for r in rows]) if rows else 1
            
            for scale, count in rows:
                if not scale: scale = "Unknown"
                bar_w = (count / total) * max_width
                color = "#69b3a2" if scale == "Healthy" else "#ff9f43"
                
                self.canvas.create_rectangle(x, start_y, x + bar_w, start_y + 20, fill=color, outline="white")
                self.canvas.create_text(x + bar_w + 5, start_y + 10, text=f"{scale} ({count})", anchor="w")
                start_y += 30
        except: pass

    def draw_cal_chart(self, x, y):
        """Shows Avg Calories by Category."""
        self.canvas.create_text(x, y, text="View 4: Avg Calories", font=("Arial", 11, "bold"), anchor="w")
        try:
            sql = """
                SELECT c.Category_Name, AVG(n.Energy_kcal) as avg_cal
                FROM food f
                JOIN nutrition n ON f.Food_Item_ID = n.Food_Item_ID
                JOIN category c ON f.Category_ID = c.Category_ID
                GROUP BY c.Category_Name
                ORDER BY avg_cal DESC
                LIMIT 5
            """
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
            
            start_y = y + 30
            max_width = 150
            max_val = rows[0][1] if rows else 1
            
            for name, avg in rows:
                bar_w = (avg / max_val) * max_width
                self.canvas.create_rectangle(x, start_y, x + bar_w, start_y + 20, fill="#74b9ff", outline="white")
                self.canvas.create_text(x + bar_w + 5, start_y + 10, text=f"{name[:10]}.. ({int(avg)})", anchor="w")
                start_y += 30
        except: pass

if __name__ == "__main__":
    main_root = tk.Tk()
    
    def launch_app():
        main_root.deiconify() 
        app = GroceryApp(main_root, db_config)

    main_root.withdraw() 
    login_window = tk.Toplevel(main_root)
    login = LoginWindow(login_window, launch_app, db_config)
    
    main_root.mainloop()
