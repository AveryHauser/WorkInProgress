import tkinter as tk

def show_store_list():
    # Get the text from the entry widget
    zipcode = enter_zip.get()
    
    # Simple check: only show "STORE LIST" if the user actually typed something
    if zipcode:
        # Update the result label's text
        label_result.config(text="STORE LIST")
    else:
        # Optional: Handle case where nothing was entered
        label_result.config(text="Please enter a zipcode.")

# --- main window ---
root = tk.Tk()
root.title("Store Finder")
root.geometry("300x200") # Set the window size (width x height)

# --- Create the widgets ---

# prompt user
label_prompt = tk.Label(root, text="Enter Zipcode:")

# text box
enter_zip = tk.Entry(root)

# search button
button_submit = tk.Button(root, text="Find Stores", command=show_store_list)

# display
label_result = tk.Label(root, text="", font=("Arial", 12, "bold"))

# --- Place the widgets on the window ---
# .pack() is the simplest way to add widgets in order, top-to-bottom.
# 'pady' adds a little vertical padding for spacing.
label_prompt.pack(pady=5)
enter_zip.pack(pady=5)
button_submit.pack(pady=10)
label_result.pack(pady=5)

# --- Start GUI ---
root.mainloop()