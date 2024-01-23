import os
import sqlite3
from PyPDF2 import PdfReader
from datetime import datetime
import subprocess


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

def query_database(tree):
    
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

def sort_options_changed(sort_combobox, tree, *args):
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


def view_selected_pdf(event, tree):
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



def search_button_clicked(tree):
    #TBC 
    query_database(tree)

def update_button_clicked(tree):
    update_database()
    query_database(tree)