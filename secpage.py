from tkinter import *
import sqlite3
import os
import webbrowser 
from tkinter import ttk
from PyPDF2 import PdfReader
from datetime import datetime
import subprocess
from sqlite_backend import *
from sqlite_backend import (
    update_database,
    query_database,
    sort_options_changed,
    view_selected_pdf,
    search_button_clicked,
    delete_selected_file,
    rename_selected_file,
)

# Set the current working directory to the script's directory
script_directory = os.path.dirname(os.path.abspath(r'/home/rpig3/docubase/env/bin/mainProg/DocuBase'))
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

except Exception as e:
    print("Error:", e)
finally:
    # Close the database connection when the application is closed
    if conn:
        conn.close()
        print("Database connection closed")


def close_button(root):
    root.destroy()


def open_secpage_window():
    root = Tk()
    root.title("Database Page")
    root.attributes("-fullscreen", True)

    # Frame for the entire content
    # contentFrame = ttk.Frame(root, padding=(10, 10, 10, 10))

    # Search Bar Frame
    searchFrame = ttk.Frame(root, padding=(10, 10, 10, 10))
    searchFrame.grid(column=0, row=0, rowspan=2, sticky=("nsew"))

    # Search Bar
    searchLabel = ttk.Label(searchFrame, text="Search")
    searchLabel.grid(column=0, row=0, padx=10, sticky="w")

    searchEntry = ttk.Entry(searchFrame)
    searchEntry.grid(column=1, row=(0), padx=0, pady=(0), sticky=("we"))

    # Search Button
    searchButton = ttk.Button(searchFrame, text="Search", command=lambda: search_button_clicked(tree, searchEntry))
    searchButton.grid(column=2, row=0, padx=(5, 0), pady=0, sticky=("we"))

    # Sort by Label
    sortbyLabel = ttk.Label(searchFrame, text="Sort by")
    sortbyLabel.grid(column=0, row=2, padx=10, sticky="w")

    # Dropdown
    # Sorting options
    sort_options = ["by Date (Ascending)", "by Date (Descending)", "by Name (Ascending)", "by Name (Descending)"]  # Add your sorting options here

    # Create a Combobox (drop-down menu) for sorting
    sort_combobox = ttk.Combobox(searchFrame, values=sort_options, state="readonly")
    sort_combobox.grid(column=1, row=2, padx=(0, 0), pady=(0), sticky=("we"))

    # Treeview (Table) with 3 columns 
    columns = ("#", "Document Name", "Date")
    tree = ttk.Treeview(root, columns=columns, show="headings")

    # Set default sorting option
    sort_combobox.set(sort_options[0])
    sort_combobox.bind("<<ComboboxSelected>>", lambda event: sort_options_changed(sort_combobox, tree))

    # Set column headings
    for col in columns:
        tree.heading(col, text=col)

    # Place the Treeview in the grid
    tree.grid(column=0, row=2, sticky=("nsew"), padx=(20, 20), pady=(20, 20))
    tree.bind('<ButtonRelease-1>', lambda event: view_selected_pdf(tree))

    # Add a vertical scroll
    scrollbar = ttk.Scrollbar(root, orient=VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.grid(row=2, column=1, sticky='ns')
    
    #Make each column of the table resizable
    for col in columns:
        tree.column(col, anchor="center")
        tree.column(col, stretch=True)

    buttonFrame = ttk.Frame(root, padding=(10, 10, 10, 10))
    buttonFrame.grid(column=0, row=3, padx=20, pady=(0, 10), sticky=("nsew"))

    #Add an "Update" and "Back" button to trigger database update and close the page
    updateButton = ttk.Button(buttonFrame, text="Update", command =update_button_clicked(tree))
    updateButton.grid(column=0, row=0, padx=10, pady=(0, 10), sticky=("nsew"))

    closeButton = ttk.Button(buttonFrame, text="Close", command=lambda: close_button(root))
    closeButton.grid(column=1, row=0, padx=10, pady=(0,10), sticky=("nsew"))

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

    searchFrame.columnconfigure(1, weight=1)
    searchFrame.columnconfigure(2, weight=1)
    searchFrame.columnconfigure(3, weight=1)

    buttonFrame.columnconfigure(0, weight=1)
    buttonFrame.columnconfigure(1, weight=1)

    # Bind right-click event to show the context menu
    tree.bind("<Button-3>", lambda event: show_context_menu(event, tree))

    #Call the update_database function at startup
    update_database()
    query_database(tree)

    root.mainloop()
