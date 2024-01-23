from tkinter import *
import sqlite3
import os
import webbrowser 
from tkinter import ttk
from PyPDF2 import PdfReader
from datetime import datetime
import subprocess
from sqlite_backend import *




# Set the current working directory to the script's directory
script_directory = os.path.dirname(os.path.abspath(r'C:\Users\Carl\Documents\SCHOOLWORKS\4Y1ST\DP1\DB_Database'))
os.chdir(script_directory)

print("Current Working Directory:", os.getcwd())

# Path to the database file
database_path = os.path.join(script_directory, "g3db.db")
print("Database Path:", database_path)

try:
    # Create a connection to the SQLite database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    print("Connected to the database")

    # Continue with the rest of your code...
except Exception as e:
    print("Error:", e)
finally:
    # Close the database connection when the application is closed
    if conn:
        conn.close()
        print("Database connection closed")

root = Tk()
root.title("Document Form")

# Search Bar Frame
searchFrame = ttk.Frame(root, padding=(10, 10, 10, 10))
searchFrame.grid(column=0, row=0, rowspan=2, sticky=(N, S, E, W))

# Search Bar
searchLabel = ttk.Label(searchFrame, text="Search")
searchLabel.grid(column=0, row=0, padx=10, sticky=W)

searchEntry = ttk.Entry(searchFrame)
searchEntry.grid(column=1, row=(0), padx=0, pady=(0), sticky=(W, E))

# Search Button
searchButton = ttk.Button(searchFrame, text="Search", command=lambda: search_button_clicked(tree))
searchButton.grid(column=2, row=0, padx=(5, 0), pady=0, sticky=(W, E))


# Sort by Label
sortbyLabel = ttk.Label(searchFrame, text="Sort by")
sortbyLabel.grid(column=0, row=2, padx=10, sticky=W)

# Dropdown
# Sorting options
sort_options = ["by Date (Ascending)", "by Date (Descending)", "by Name (Ascending)", "by Name (Descending)"]  # Add your sorting options here

# Create a Combobox (drop-down menu) for sorting
sort_combobox = ttk.Combobox(searchFrame, values=sort_options, state="readonly")
sort_combobox.grid(column=1, row=2, padx=(0, 0), pady=(0), sticky=(W, E))


# Treeview (Table) with 3 columns 
columns = ("#", "Document Name", "Date")
tree = ttk.Treeview(root, columns=columns, show="headings")

# Set default sorting option
sort_combobox.set(sort_options[0])
sort_combobox.bind("<<ComboboxSelected>>", sort_options_changed(sort_combobox, tree))


# Set column headings
for col in columns:
    tree.heading(col, text=col)

# Place the Treeview in the grid
tree.grid(column=0, row=2, sticky=(N, S, E, W), padx=(20, 20), pady=(20, 20))
tree.bind('<ButtonRelease-1>', lambda event: view_selected_pdf(event, tree))

# Add a vertical scroll
scrollbar = ttk.Scrollbar(root, orient=VERTICAL, command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.grid(row=2, column=1, sticky='ns')

#Column and Row configurations for resizing
root.columnconfigure(0, weight=1) 
root.rowconfigure(0, weight=0)
root.rowconfigure(1, weight=0)
root.rowconfigure(2, weight=1) 

searchFrame.columnconfigure(0, weight=1)
searchFrame.columnconfigure(1, weight=1)
searchFrame.columnconfigure(2, weight=1)
searchFrame.columnconfigure(3, weight=1)
searchFrame.rowconfigure(0, weight=0)
searchFrame.rowconfigure(1, weight=0)

#Make only the checkbox columns resizable
searchFrame.columnconfigure(1, weight=1)
searchFrame.columnconfigure(2, weight=1)
searchFrame.columnconfigure(3, weight=1)

#Make each column of the table resizable
for col in columns:
    tree.column(col, anchor="center")
    tree.column(col, stretch=True)

#Add an "Update" button to trigger database update
updateButton = ttk.Button(root, text="Update", command=update_button_clicked(tree))
updateButton.grid(column=0, row=3, padx=(20, 20), pady=10, sticky=(N, S, E, W))

#Call the update_database function at startup
update_database()
query_database(tree)

root.mainloop()