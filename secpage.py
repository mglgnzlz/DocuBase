from tkinter import *
import sqlite3
import os
import webbrowser 
from tkinter import ttk
from PyPDF2 import PdfReader
from datetime import datetime
import subprocess




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

def extract_date_from_pdf(file_path):
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            
            # Metadata reading for Creation Date extraction
            metadata = pdf_reader.metadata
            creation_date = metadata.get('/CreationDate')
            
            if creation_date:
                #Remove bloat from metadata extracted + time conversion
                creation_date = creation_date.replace('D:', '')
                offset_str = creation_date[-6:].replace("'", "")
                date_str_without_offset = creation_date[:-6]

                date_obj = datetime.strptime(date_str_without_offset + offset_str, '%Y%m%d%H%M%S%z')
                return date_obj.strftime('%Y-%m-%d %H:%M:%S')
            else:
                print(f"No creation date found in metadata for {file_path}")
                return None
    except Exception as e:
        print(f"Error extracting date from {file_path}: {e}")
        return None


def update_database():
    conn = sqlite3.connect(r'C:\Users\Carl\Documents\SCHOOLWORKS\4Y1ST\DP1\DB_Database\g3db.db')
    cursor = conn.cursor()

    # PDF file path
    folder_path = r'C:\Users\Carl\Documents\SCHOOLWORKS\4Y1ST\DP1\DB_Database'

    # Clear table for new values
    cursor.execute("DELETE FROM pdf_files")

    # Populate table with entries
    for file_id, file_name in enumerate(os.listdir(folder_path), start=1):
        if file_name.endswith('.pdf'):
            file_path = os.path.join(folder_path, file_name)

            # Extract date from the PDF file
            file_date = extract_date_from_pdf(file_path)
            cursor.execute("INSERT INTO pdf_files (id, file_name, file_path, date) VALUES (?, ?, ?, ?)",
                           (file_id, file_name, file_path, file_date))
            
    conn.commit()
    conn.close()

def query_database():
    conn = sqlite3.connect(r'C:\Users\Carl\Documents\SCHOOLWORKS\4Y1ST\DP1\DB_Database\g3db.db')
    cursor = conn.cursor()

    # Retrieve values from SQLite DB
    cursor.execute("SELECT id, file_name, date FROM pdf_files")
    rows = cursor.fetchall()

    # Clear tree to populate for new files
    for item in tree.get_children():
        tree.delete(item)

    for row in rows:
        tree.insert("", "end", values=row)

    conn.close()

def sort_options_changed(*args):
    conn = sqlite3.connect(r'C:\Users\Carl\Documents\SCHOOLWORKS\4Y1ST\DP1\DB_Database\g3db.db')
    cursor = conn.cursor()
    selected_option = sort_combobox.get()

    

    if selected_option == "by Date (Ascending)":
        query = "SELECT * FROM pdf_files ORDER BY date ASC"
    elif selected_option == "by Date (Descending)":
        query = "SELECT * FROM pdf_files ORDER BY date DESC"
    elif selected_option == "by Name (Ascending)":
        query = "SELECT * FROM pdf_files ORDER BY file_name ASC"
    elif selected_option == "by Name (Descending)":
        query = "SELECT * FROM pdf_files ORDER BY file_name DESC"
    

    cursor.execute(query)
    sorted_data = cursor.fetchall()

    for item in tree.get_children():
        tree.delete(item)

    for i, row in enumerate(sorted_data, start=1):
        tree.insert("", "end", values=(row[0], row[1],row[3]))


def view_selected_pdf(event):
    # Get the selected item from the Treeview
    selected_item = tree.selection()
    if selected_item:

        # Debug line for doublechecking
        print(f"Selected item values: {tree.item(selected_item, 'values')}")
        file_path = tree.item(selected_item, 'values')[1] 

        try:
            # debug lie
            print(f"Selected PDF file: {file_path}")

            # Open the default PDF viewer on Windows
            subprocess.Popen(['start', '', file_path], shell=True)
        except Exception as e:
            print(f"Error opening PDF file: {e}")



def search_button_clicked():
    #TBC 
    query_database()

def update_button_clicked():
    update_database()
    query_database()

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
searchButton = ttk.Button(searchFrame, text="Search", command=search_button_clicked)
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

# Set default sorting option
sort_combobox.set(sort_options[0])
sort_combobox.bind("<<ComboboxSelected>>", sort_options_changed)

# Treeview (Table) with 3 columns 
columns = ("#", "Document Name", "Date")
tree = ttk.Treeview(root, columns=columns, show="headings")

# Set column headings
for col in columns:
    tree.heading(col, text=col)

# Place the Treeview in the grid
tree.grid(column=0, row=2, sticky=(N, S, E, W), padx=(20, 20), pady=(20, 20))
tree.bind('<ButtonRelease-1>', view_selected_pdf)

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
updateButton = ttk.Button(root, text="Update", command=update_button_clicked)
updateButton.grid(column=0, row=3, padx=(20, 20), pady=10, sticky=(N, S, E, W))

#Call the update_database function at startup
update_database()
query_database()

root.mainloop()