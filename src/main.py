import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector
import uuid
from datetime import datetime

# --- Database Configuration ---
db_config = {
    'user': 'root',
    'password': 'password',  # <--- UPDATE THIS
    'host': 'localhost',
    'database': 'grocery_app'
}

class LoginWindow:
    def __init__(self, root, on_success_callback):
        self.root = root
        self.on_success = on_success_callback
        self.root.title("System Login")
        
        # Center the window
        window_width = 1200
        window_height = 900
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int(screen_width / 2 - window_width / 2)
        y = int(screen_height / 2 - window_height / 2)
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')

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
        self.pass_entry.insert(0, "1234") 
        self.pass_entry.pack()

        tk.Button(root, text="Login", command=self.check_login, bg="#dddddd").pack(pady=15)

    def check_login(self):
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
        
        # Window dimensions - made wider for food table
        window_width = 1200
        window_height = 900
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
            self.new_name.delete(0, tk.END)
            self.new_addr.delete(0, tk.END)
            self.new_zip.delete(0, tk.END)
            self.refresh_analytics()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))

    def add_user(self):
        if not self.cursor: return
        email_input = self.email_entry.get().strip()
        password_input = self.password_entry.get().strip()
        if not email_input or not password_input:
            messagebox.showwarning("Input Error", "Please enter email and password.")
            return

        try:
            uid = str(uuid.uuid4())
            # FIX: datetime.now() instead of datetime.datetime.now()
            self.cursor.execute("INSERT INTO user (user_id, email, password_hash, created_at, stat) VALUES (%s, %s, %s, %s, %s)", 
                                (uid, email_input, password_input, datetime.now(), "Active"))
            self.conn.commit()
            messagebox.showinfo("Success", "User created.")
        except mysql.connector.Error as err:
            messagebox.showerror("Query Error", f"Error adding user:\n{err}")

    def del_user(self):
        if not self.cursor: return
        email_input = self.email_entry.get().strip()
        password_input = self.password_entry.get().strip()
        
        if not email_input or not password_input:
            messagebox.showwarning("Input Error", "Please enter email and password to delete.")
            return

        try:
            # FIX: Use parameterized query to prevent SQL Injection
            sql = "DELETE FROM user WHERE email = %s AND password_hash = %s"
            self.cursor.execute(sql, (email_input, password_input))
            if self.cursor.rowcount > 0:
                self.conn.commit()
                messagebox.showinfo("Success", "User deleted.")
            else:
                messagebox.showwarning("Failed", "No user found with that email/password.")
        except mysql.connector.Error as err:
            messagebox.showerror("Query Error", f"Error deleting user:\n{err}")

    def change_email(self):
        if not self.cursor: return
        old_email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not old_email or not password:
            messagebox.showwarning("Input Error", "Enter current email and password.")
            return
            
        new_email = simpledialog.askstring("Update Email", "Enter new email address:")
        if not new_email: return

        try:
            # FIX: Use parameterized query
            sql = "UPDATE user SET email = %s WHERE email = %s AND password_hash = %s"
            self.cursor.execute(sql, (new_email, old_email, password))
            if self.cursor.rowcount > 0:
                self.conn.commit()
                messagebox.showinfo("Success", "Email updated.")
            else:
                messagebox.showwarning("Failed", "Invalid credentials or user not found.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error updating user:\n{err}")

    # ------------------------------------------------------------------
    # TAB 2: FOOD DATABASE (NEW)
    # ------------------------------------------------------------------
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
        # 1. Header with Refresh
        control_frame = tk.Frame(self.tab3, bg="#f0f2f5")
        control_frame.pack(fill="x", side="top")
        
        tk.Button(control_frame, text="Refresh Dashboard", command=self.refresh_analytics, 
                  bg="#4a90e2", fg="black", font=("Arial", 10, "bold"), padx=10, pady=5).pack(pady=10)

        # 2. Main Canvas for Dashboard
        self.canvas = tk.Canvas(self.tab3, bg="#f0f2f5")
        self.canvas.pack(fill="both", expand=True)
        
        self.root.after(500, self.refresh_analytics)

    def draw_card(self, x, y, w, h, title):
        """Draws a white card background with shadow and title."""
        # Shadow
        self.canvas.create_rectangle(x+3, y+3, x+w+3, y+h+3, fill="#d1d1d1", outline="")
        # Box
        self.canvas.create_rectangle(x, y, x+w, y+h, fill="white", outline="#e1e4e8")
        # Header Line
        self.canvas.create_line(x, y+40, x+w, y+40, fill="#f0f0f0")
        # Title
        self.canvas.create_text(x+15, y+20, text=title, anchor="w", font=("Segoe UI", 12, "bold"), fill="#333")
        
        return x+10, y+50, w-20, h-60 # Returns the inner content area

    def refresh_analytics(self):
        if not self.cursor: return
        self.canvas.delete("all")
        
        # Grid Layout Config
        pad = 20
        col1_x = pad
        col2_x = pad + 520
        
        # Draw Cards
        self.draw_summary_kpi(col1_x, pad)
        self.draw_health_pie(col2_x, pad)
        self.draw_top_zips_bar(col1_x, pad + 180)
        self.draw_cal_bar(col2_x, pad + 180)

    def draw_summary_kpi(self, x, y):
        cx, cy, cw, ch = self.draw_card(x, y, 500, 160, "Key Metrics")
        
        try:
            self.cursor.execute("SELECT COUNT(*) FROM grocery_location")
            total_stores = self.cursor.fetchone()[0]
            self.cursor.execute("SELECT COUNT(*) FROM food")
            total_food = self.cursor.fetchone()[0]
            
            # Draw KPI 1 (Stores)
            self.canvas.create_text(cx + 80, cy + 30, text=str(total_stores), font=("Arial", 36, "bold"), fill="#3498db")
            self.canvas.create_text(cx + 80, cy + 70, text="Total Stores", font=("Arial", 12), fill="#7f8c8d")
            
            # Separator
            self.canvas.create_line(cx + 250, cy, cx + 250, cy + 100, fill="#eee")
            
            # Draw KPI 2 (Foods)
            self.canvas.create_text(cx + 330, cy + 30, text=str(total_food), font=("Arial", 36, "bold"), fill="#27ae60")
            self.canvas.create_text(cx + 330, cy + 70, text="Food Items", font=("Arial", 12), fill="#7f8c8d")
        except: pass

    def draw_health_pie(self, x, y):
        cx, cy, cw, ch = self.draw_card(x, y, 500, 160, "Food Health Distribution")
        
        try:
            self.cursor.execute("SELECT health_scale, COUNT(*) FROM nutrition GROUP BY health_scale")
            data = self.cursor.fetchall() # [(Healthy, 10), (Unhealthy, 5)]
            
            total = sum([d[1] for d in data])
            if total == 0: return

            start_angle = 90
            colors = {"Healthy": "#2ecc71", "Unhealthy": "#e74c3c", "Moderate": "#f1c40f"}
            
            # Center of Pie
            pc_x, pc_y = cx + 100, cy + 50
            radius = 50
            
            legend_y = cy + 20
            
            for category, count in data:
                extent = (count / total) * 360
                color = colors.get(category, "#95a5a6")
                
                # Draw Slice
                self.canvas.create_arc(pc_x-radius, pc_y-radius, pc_x+radius, pc_y+radius,
                                       start=start_angle, extent=extent, fill=color, outline="white")
                
                # Draw Legend
                self.canvas.create_rectangle(cx + 200, legend_y, cx + 215, legend_y + 15, fill=color, outline="")
                self.canvas.create_text(cx + 225, legend_y + 8, text=f"{category}: {count} ({int(extent/3.6)}%)", anchor="w", font=("Arial", 10))
                legend_y += 25
                
                start_angle += extent
        except: pass

    def draw_top_zips_bar(self, x, y):
        cx, cy, cw, ch = self.draw_card(x, y, 500, 300, "Top 5 Zip Codes (Store Density)")
        
        try:
            self.cursor.execute("SELECT zipcode, COUNT(*) as cnt FROM grocery_location GROUP BY zipcode ORDER BY cnt DESC LIMIT 5")
            rows = self.cursor.fetchall()
            if not rows: return
            
            max_val = rows[0][1]
            bar_h = 30
            gap = 15
            current_y = cy + 10
            
            for zip_code, count in rows:
                bar_w = (count / max_val) * (cw - 100)
                
                # Label
                self.canvas.create_text(cx, current_y + 15, text=str(zip_code), anchor="w", font=("Arial", 10))
                
                # Bar
                self.canvas.create_rectangle(cx + 60, current_y, cx + 60 + bar_w, current_y + bar_h, fill="#3498db", outline="")
                
                # Value Label
                self.canvas.create_text(cx + 60 + bar_w + 10, current_y + 15, text=str(count), anchor="w", font=("Arial", 9, "bold"), fill="#555")
                
                current_y += bar_h + gap
        except: pass

    def draw_cal_bar(self, x, y):
        cx, cy, cw, ch = self.draw_card(x, y, 500, 300, "Highest Calorie Categories")
        
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
            if not rows: return
            
            max_val = rows[0][1]
            bar_width = 40
            gap = 40
            start_x = cx + 30
            baseline_y = cy + 200
            
            for name, avg in rows:
                bar_height = (avg / max_val) * 180
                
                # Bar
                self.canvas.create_rectangle(start_x, baseline_y - bar_height, start_x + bar_width, baseline_y, fill="#e67e22", outline="")
                
                # Value on top
                self.canvas.create_text(start_x + bar_width/2, baseline_y - bar_height - 10, text=str(int(avg)), font=("Arial", 9, "bold"))
                
                # Label below (truncated)
                label = name[:8] + ".." if len(name) > 8 else name
                self.canvas.create_text(start_x + bar_width/2, baseline_y + 15, text=label, font=("Arial", 8))
                
                start_x += bar_width + gap
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