import tkinter as tk
# Import the classes from the new file
from grocerygui import LoginWindow, GroceryApp

# --- Database Configuration ---
# UPDATE THESE VALUES TO MATCH YOUR LOCAL DATABASE SETUP
db_config = {
    'user': 'root',
    'password': 'password',  # <--- REPLACE WITH YOUR ACTUAL PASSWORD
    'host': 'localhost',
    'database': 'grocery_app'
}

if __name__ == "__main__":
    main_root = tk.Tk()
    
    # Callback to launch main app after login
    def launch_app():
        main_root.deiconify() # Show main window
        # Pass the database config to the GroceryApp
        app = GroceryApp(main_root, db_config)

    main_root.withdraw() # Hide main window initially
    
    # Create Login Window (TopLevel)
    login_window = tk.Toplevel(main_root)
    # Pass the launch_app callback
    login = LoginWindow(login_window, launch_app)
    
    main_root.mainloop()