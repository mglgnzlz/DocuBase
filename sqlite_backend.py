import os
import sqlite3
from PyPDF2 import PdfReader
from datetime import datetime
import subprocess
from tkinter import Menu, simpledialog, messagebox

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
    conn = sqlite3.connect(r'C:\Users\danica\Docubase\DocuBase\g3db.db')
    cursor = conn.cursor()

    # PDF file path
    folder_path = r'C:\Users\danica\Docubase\DocuBase'

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
    
    conn = sqlite3.connect(r'C:\Users\danica\Docubase\DocuBase\g3db.db')
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

def sort_options_changed(sort_combobox, tree):
    conn = sqlite3.connect(r'C:\Users\danica\Docubase\DocuBase\g3db.db')
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

    # Clear the tree
    tree.delete(*tree.get_children())

    # Insert sorted data into the tree
    for row in sorted_data:
        tree.insert("", "end", values=(row[0], row[1], row[3]))

    conn.close()


#SEARCH BUTTON FUNCTION

def search_button_clicked(tree, search_entry):
    # Get the search keyword from the entry widget
    search_keyword = search_entry.get().lower()

    # Query the database for files containing the search keyword
    conn = sqlite3.connect(r'C:\Users\danica\Docubase\DocuBase\g3db.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, file_name, date FROM pdf_files WHERE LOWER(file_name) LIKE ?", ('%' + search_keyword + '%',))
    rows = cursor.fetchall()

    # Clear tree to populate for new search results
    for item in tree.get_children():
        tree.delete(item)

    # Populate the tree with the search results
    for row in rows:
        tree.insert("", "end", values=row)

    conn.close()

def update_button_clicked(tree):
    update_database()
    query_database(tree)
    
#For rename, view, and delete when right click

def show_context_menu(event, tree):
    # Identify the item that was clicked
    item_id = tree.identify_row(event.y)
    
    if item_id:
        # Display the context menu only if a valid item is clicked
        selected_item = tree.selection()
        if selected_item:
            context_menu = initialize_context_menu(tree)
            context_menu.post(event.x_root, event.y_root)
        
# Create the context menu
def initialize_context_menu(tree):
    context_menu = Menu(tree, tearoff=0)
    context_menu.add_command(label="View", command=lambda: view_selected_pdf(tree))
    context_menu.add_command(label="Rename", command=lambda: rename_selected_file(tree))
    context_menu.add_command(label="Delete", command=lambda: delete_selected_file(tree))
    return context_menu

#VIEW FILE
def view_selected_pdf(tree):
    selected_item = tree.selection()
    if selected_item:
        file_path = tree.item(selected_item, 'values')[1]
        try:
            subprocess.Popen(['start', '', file_path], shell=True)
        except Exception as e:
            print(f"Error opening PDF file: {e}")

#RENAMING FILE
def rename_selected_file(tree):
    selected_item = tree.selection()
    if selected_item:
        # Get the item ID and old file path
        item_id, old_file_path = tree.item(selected_item, 'values')[:2]

        # Get the current name from the tree
        current_name = tree.item(selected_item, 'values')[1]

        # Get the new file name using a simple dialog
        new_name = simpledialog.askstring("Rename File", "Enter a new name:", initialvalue=current_name)
        
        if new_name:
            try:
                # Update the tree with the new name
                tree.item(selected_item, values=(item_id, new_name, tree.item(selected_item, 'values')[2]))

                # Update the database with the new file name
                conn = sqlite3.connect(r'C:\Users\danica\Docubase\DocuBase\g3db.db')
                cursor = conn.cursor()
                cursor.execute("UPDATE pdf_files SET file_name = ? WHERE id = ?", (new_name, item_id))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Error renaming file: {e}")

#DELETION OF SELECTED FILE
def delete_selected_file(tree):
    selected_item = tree.selection()
    if selected_item:
        file_path = tree.item(selected_item, 'values')[1]

        # Display a confirmation dialog before deletion
        confirmation = messagebox.askyesno("Confirm Deletion", f"Do you want to delete the file:\n{file_path}?")
        
        if confirmation:
            try:
                # Delete the file
                os.remove(file_path)

                # Update the database by removing the corresponding entry
                conn = sqlite3.connect(r'C:\Users\danica\Docubase\DocuBase\g3db.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM pdf_files WHERE file_path = ?", (file_path,))
                conn.commit()
                conn.close()

                # Refresh the treeview to reflect the changes
                query_database(tree)
            except Exception as e:
                print(f"Error deleting file: {e}")