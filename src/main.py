import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector
import uuid
from datetime import datetime

# --- Database Configuration ---
db_config = {
    'user': 'root',
    'password': 'CHANGE PASSWORD TO MYSQL PASSWORD',  # <--- UPDATE THIS
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
        window_width = 1150
        window_height = 900
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int(screen_width / 2 - window_width / 2)
        y = int(screen_height / 2 - window_height / 2)
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')

        # --- Section 1: Login ---
        login_frame = tk.LabelFrame(root, text="Existing User Login", padx=20, pady=20)
        login_frame.pack(pady=20, padx=20, fill="x")

        tk.Label(login_frame, text="Email:").pack(anchor="w")
        self.login_email = tk.Entry(login_frame, width=30)
        self.login_email.pack(pady=5)

        tk.Label(login_frame, text="Password:").pack(anchor="w")
        self.login_pass = tk.Entry(login_frame, show="*", width=30)
        self.login_pass.pack(pady=5)

        tk.Button(login_frame, text="Login", command=self.check_login, bg="#dddddd", width=15).pack(pady=15)


    def check_login(self):
        email = self.login_email.get().strip()
        password = self.login_pass.get().strip()

        if not email or not password:
            messagebox.showwarning("Input Error", "Please enter email and password.")
            return

        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Check credentials in DB
            query = "SELECT user_id FROM user WHERE email = %s AND password_hash = %s"
            cursor.execute(query, (email, password))
            result = cursor.fetchone()
            
            conn.close()

            if result:
                self.root.destroy()
                self.on_success()
            else:
                messagebox.showerror("Login Failed", "Invalid Email or Password")
                
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error connecting:\n{err}")

    def add_user(self):
        email = self.new_email.get().strip()
        password = self.new_pass.get().strip()
        
        if not email or not password:
            messagebox.showwarning("Input Error", "Please enter an email and password.")
            return

        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()

            # Check if email exists
            cursor.execute("SELECT user_id FROM user WHERE email = %s", (email,))
            if cursor.fetchone():
                messagebox.showerror("Error", "User already exists.")
                conn.close()
                return

            # Insert new user
            uid = str(uuid.uuid4())
            sql = "INSERT INTO user (user_id, email, password_hash, created_at, stat) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (uid, email, password, datetime.now(), "Active"))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Account created! Please log in above.")
            self.new_email.delete(0, tk.END)
            self.new_pass.delete(0, tk.END)

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error creating user:\n{err}")

class GroceryApp:
    def __init__(self, root, db_config):
        self.root = root
        self.db_config = db_config
        self.root.title("Grocery Store Manager & Analytics")
        
        window_width = 1150
        window_height = 900
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int(screen_width / 2 - window_width / 2)
        y = int(screen_height / 2 - window_height / 2)
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')

        self.conn = self.connect_db()
        self.cursor = self.conn.cursor() if self.conn else None

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="Manage Data")
        self.setup_data_tab()

        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="Food Database")
        self.setup_food_tab()

        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text="Analytics Dashboard")
        self.setup_analytics_tab()

    def connect_db(self):
        try:
            return mysql.connector.connect(**self.db_config)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not connect:\n{err}")
            return None
    
    def log_action(self, action_text):
        if not self.cursor: return
        try:
            sql = "INSERT INTO log (action, time_completed) VALUES (%s, %s)"
            
            self.cursor.execute(sql, (action_text, datetime.now()))
            self.conn.commit()
            print(f"Logged action: {action_text}") 
        except mysql.connector.Error as err:
            print(f"Failed to log action: {err}")

    # --- TAB 1: DATA MANAGEMENT ---
    def setup_data_tab(self):
        # Search
        search_frame = tk.LabelFrame(self.tab1, text="Search Stores", padx=10, pady=10)
        search_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(search_frame, text="Zip Code:").pack(side=tk.LEFT)
        self.zip_entry = tk.Entry(search_frame, width=10)
        self.zip_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Search", command=self.search_stores).pack(side=tk.LEFT)

        columns = ("store_name", "address", "zip")
        self.tree = ttk.Treeview(search_frame, columns=columns, show="headings", height=5)
        self.tree.heading("store_name", text="Store Name")
        self.tree.heading("address", text="Address")
        self.tree.heading("zip", text="Zip")
        self.tree.column("store_name", width=200)
        self.tree.column("address", width=300)
        self.tree.column("zip", width=80)
        self.tree.pack(fill="x", pady=5)

        # Add Store
        add_frame = tk.LabelFrame(self.tab1, text="Add New Store (Write Data)", padx=10, pady=10)
        add_frame.pack(fill="x", padx=10, pady=10)
        
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

        # Manage Users
        user_frame = tk.LabelFrame(self.tab1, text="Manage Users", padx=10, pady=10)
        user_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(user_frame, text="Email:").grid(row=0, column=0, sticky="e")
        self.email_entry = tk.Entry(user_frame, width=30)
        self.email_entry.grid(row=0, column=1, padx=5, pady=2)
        tk.Label(user_frame, text="Password:").grid(row=1, column=0, sticky="e")
        self.password_entry = tk.Entry(user_frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=2)
        
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
            for row in self.cursor.fetchall():
                self.tree.insert("", tk.END, values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", str(err))

    def add_store(self):
        if not self.cursor: return
        try:
            sql = "INSERT INTO grocery_location (STORENAME, STORE_ADDRESS, zipcode) VALUES (%s, %s, %s)"
            self.cursor.execute(sql, (self.new_name.get(), self.new_addr.get(), self.new_zip.get()))           
            self.conn.commit()          
            self.log_action(f"Added new store: {self.new_name.get()}")
            messagebox.showinfo("Success", "Store added!")
            self.refresh_analytics()       
        except Exception as e: messagebox.showerror("Error", str(e))

    def add_user(self):
        # 1. Get input
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip() 
        
        if not email or not password:
            messagebox.showwarning("Input Error", "Please enter an email and password.")
            return

        if not self.cursor: return
        try:
            # 2. Check if email exists
            self.cursor.execute("SELECT user_id FROM user WHERE email = %s", (email,))
            if self.cursor.fetchone():
                messagebox.showerror("Error", "User already exists.")
                return

            sql = "INSERT INTO user (email, password_hash, created_at, stat) VALUES (%s, %s, %s, %s)"
            self.cursor.execute(sql, (email, password, datetime.now(), "Active"))
            
            self.conn.commit()
            
            # 4. Log and notify
            self.log_action(f"Added new user: {email}")
            messagebox.showinfo("Success", "User created!")
            
            # Clear inputs
            self.email_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)

        except Exception as e: 
            messagebox.showerror("Error", str(e))

    def del_user(self):
        if not self.cursor: return
        try:
            self.cursor.execute("DELETE FROM user WHERE email = %s AND password_hash = %s", 
                                (self.email_entry.get(), self.password_entry.get()))
            if self.cursor.rowcount > 0:
                self.conn.commit()
                self.log_action(f" delete user: {self.email_entry.get()}")
                messagebox.showinfo("Success", "User deleted.")
            else:
                messagebox.showwarning("Failed", "Incorrect credentials.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def change_email(self):
        if not self.cursor: return
        
        # 1. Get the CURRENT credentials from the main window text boxes
        current_email = self.email_entry.get().strip()
        current_password = self.password_entry.get().strip()

        if not current_email or not current_password:
            messagebox.showwarning("Error", "Enter your CURRENT email and password in the boxes first.")
            return

        # 2. Ask for the NEW email via Popup
        new_email = simpledialog.askstring("Update", "New Email:")
        if not new_email: return # User cancelled
        
        try:

            sql = "UPDATE user SET email = %s WHERE email = %s AND password_hash = %s"
            self.cursor.execute(sql, (new_email, current_email, current_password))
            
            if self.cursor.rowcount > 0:
                self.conn.commit()
                self.log_action(f"Changed email from {current_email} to {new_email}")
                messagebox.showinfo("Success", "Email updated successfully.")
                
                # Update the text box to show the new email automatically
                self.email_entry.delete(0, tk.END)
                self.email_entry.insert(0, new_email)
            else:
                messagebox.showwarning("Failed", "User not found. Did you click 'Create' first?")
                
        except Exception as e: messagebox.showerror("Error", str(e))
    # --- TAB 2: FOOD DATABASE ---
    def setup_food_tab(self):
        top_frame = tk.Frame(self.tab2)
        top_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(top_frame, text="Find Food:").pack(side=tk.LEFT)
        self.food_search_entry = tk.Entry(top_frame, width=20)
        self.food_search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Search", command=self.search_food).pack(side=tk.LEFT)
        
        tk.Button(top_frame, text="View Vitamins/Minerals", command=self.view_micros, bg="#e1f5fe").pack(side=tk.RIGHT, padx=5)
        tk.Button(top_frame, text="Edit Nutrition", command=self.edit_food, bg="#fff9c4").pack(side=tk.RIGHT, padx=5)

        cols = ("id", "name", "category", "kcal", "protein", "fat", "carbs", "sugar")
        self.food_tree = ttk.Treeview(self.tab2, columns=cols, show="headings", height=20)
        
        for c in cols: self.food_tree.heading(c, text=c.capitalize())
        self.food_tree.column("id", width=0, stretch=tk.NO)
        self.food_tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.search_food()

    def search_food(self):
        if not self.cursor: return
        for i in self.food_tree.get_children(): self.food_tree.delete(i)
        try:
            sql = """SELECT f.Food_Item_ID, f.foodname, c.Category_Name, 
                     n.Energy_kcal, n.Protein_g, n.Total_Fat_g, n.Carbohydrate_g, n.Sugars_g
                     FROM food f 
                     LEFT JOIN category c ON f.Category_ID = c.Category_ID
                     LEFT JOIN nutrition n ON f.Food_Item_ID = n.Food_Item_ID
                     WHERE f.foodname LIKE %s LIMIT 100"""
            self.cursor.execute(sql, (f"%{self.food_search_entry.get()}%",))
            for row in self.cursor.fetchall(): self.food_tree.insert("", tk.END, values=row)
        except Exception as e: messagebox.showerror("Error", str(e))
    def edit_food(self):
        sel = self.food_tree.selection()
        if not sel: return
        
        # Get the item data
        item = self.food_tree.item(sel[0])
        food_id = item['values'][0]
        food_name = item['values'][1]  
        
        new_val = simpledialog.askfloat("Edit", f"New Calories for {food_name}:")
        
        if new_val is not None:
            self.cursor.execute("UPDATE nutrition SET Energy_kcal = %s WHERE Food_Item_ID = %s", (new_val, food_id))
            self.conn.commit()
            
            self.log_action(f"Updated calories for {food_name} to {new_val}")
            
            self.search_food()
            self.refresh_analytics()

    def view_micros(self):
        sel = self.food_tree.selection()
        if not sel: return
        fid = self.food_tree.item(sel[0])['values'][0]
        
        popup = tk.Toplevel(self.root)
        popup.title("Micronutrients")
        txt = tk.Text(popup, width=40, height=15)
        txt.pack(padx=10, pady=10)
        
        self.cursor.execute("SELECT name, amount, unit FROM vitamin WHERE Food_Item_ID = %s", (fid,))
        for r in self.cursor.fetchall(): txt.insert(tk.END, f"{r[0]}: {r[1]} {r[2]}\n")
        
        self.cursor.execute("SELECT name, amount, unit FROM mineral WHERE Food_Item_ID = %s", (fid,))
        for r in self.cursor.fetchall(): txt.insert(tk.END, f"{r[0]}: {r[1]} {r[2]}\n")

    # --- TAB 3: ANALYTICS ---
    def setup_analytics_tab(self):
        control_frame = tk.Frame(self.tab3, bg="#f0f2f5")
        control_frame.pack(fill="x", side="top")
        
        # Mac-compatible button
        tk.Button(control_frame, text="Refresh Dashboard", command=self.refresh_analytics, 
                  font=("Arial", 12), highlightbackground="#f0f2f5").pack(pady=10)

        self.canvas = tk.Canvas(self.tab3, bg="#f0f2f5")
        self.canvas.pack(fill="both", expand=True)
        self.root.after(500, self.refresh_analytics)

    def draw_card(self, x, y, w, h, title):
        self.canvas.create_rectangle(x+3, y+3, x+w+3, y+h+3, fill="#d1d1d1", outline="")
        self.canvas.create_rectangle(x, y, x+w, y+h, fill="white", outline="#e1e4e8")
        self.canvas.create_text(x+15, y+20, text=title, anchor="w", font=("Segoe UI", 12, "bold"), fill="#333")
        return x+10, y+50, w-20, h-60 

    def refresh_analytics(self):
        if not self.cursor: return
        self.conn.commit()
        self.canvas.delete("all")
        
        pad = 20
        col1_x = pad
        col2_x = pad + 520
        
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
            
            self.canvas.create_text(cx + 80, cy + 30, text=str(total_stores), font=("Arial", 36, "bold"), fill="#3498db")
            self.canvas.create_text(cx + 80, cy + 70, text="Total Stores", font=("Arial", 12), fill="#7f8c8d")
            
            self.canvas.create_line(cx + 250, cy, cx + 250, cy + 100, fill="#eee")
            
            self.canvas.create_text(cx + 330, cy + 30, text=str(total_food), font=("Arial", 36, "bold"), fill="#27ae60")
            self.canvas.create_text(cx + 330, cy + 70, text="Food Items", font=("Arial", 12), fill="#7f8c8d")
        except: pass

    def draw_health_pie(self, x, y):
        cx, cy, cw, ch = self.draw_card(x, y, 500, 160, "Food Health Distribution")
        try:
            self.cursor.execute("SELECT health_scale, COUNT(*) FROM nutrition GROUP BY health_scale")
            data = self.cursor.fetchall()
            
            total = sum([d[1] for d in data])
            if total == 0: return

            start_angle = 90
            colors = {"Healthy": "#2ecc71", "Unhealthy": "#e74c3c", "Moderate": "#f1c40f"}
            pc_x, pc_y = cx + 100, cy + 50
            radius = 50
            legend_y = cy + 20
            
            for category, count in data:
                if not category: category = "Unknown"
                extent = (count / total) * 360
                color = colors.get(category, "#95a5a6")
                
                self.canvas.create_arc(pc_x-radius, pc_y-radius, pc_x+radius, pc_y+radius,
                                       start=start_angle, extent=extent, fill=color, outline="white")
                
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
                self.canvas.create_text(cx, current_y + 15, text=str(zip_code), anchor="w", font=("Arial", 10))
                self.canvas.create_rectangle(cx + 60, current_y, cx + 60 + bar_w, current_y + bar_h, fill="#3498db", outline="")
                self.canvas.create_text(cx + 60 + bar_w + 10, current_y + 15, text=str(count), anchor="w", font=("Arial", 9, "bold"), fill="#555")
                current_y += bar_h + gap
        except: pass

    def draw_cal_bar(self, x, y):
        cx, cy, cw, ch = self.draw_card(x, y, 500, 300, "Highest Calorie Categories")
        
        # 1. Ensure we are reading fresh data
        self.conn.commit()
        
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
        
        if not rows: 
            print("Debug: No data returned for chart.")
            return
        
        # 2. Print data to console to verify the DB update worked
        print("\n--- ANALYTICS DEBUG DATA ---")
        for r in rows:
            print(f"Category: {r[0]} | Avg Cal: {r[1]}")
        print("----------------------------\n")
        
        # Handle 'Decimal' types if MySQL returns them
        max_val = float(rows[0][1]) 
        
        bar_width = 40
        gap = 40
        start_x = cx + 30
        baseline_y = cy + 200
        
        for name, avg in rows:
            val = float(avg) # Ensure it is a float
            if max_val > 0:
                bar_height = (val / max_val) * 180
            else:
                bar_height = 0
                
            self.canvas.create_rectangle(start_x, baseline_y - bar_height, start_x + bar_width, baseline_y, fill="#e67e22", outline="")
            self.canvas.create_text(start_x + bar_width/2, baseline_y - bar_height - 10, text=str(int(val)), font=("Arial", 9, "bold"))
            
            label = name[:8] + ".." if len(name) > 8 else name
            self.canvas.create_text(start_x + bar_width/2, baseline_y + 15, text=label, font=("Arial", 8))
            start_x += bar_width + gap

if __name__ == "__main__":
    main_root = tk.Tk()
    
    def launch_app():
        main_root.deiconify() 
        app = GroceryApp(main_root, db_config)

    main_root.withdraw() 
    login_window = tk.Toplevel(main_root)
    login = LoginWindow(login_window, launch_app, db_config)
    
    main_root.mainloop()