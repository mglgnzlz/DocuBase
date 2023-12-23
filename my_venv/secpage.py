from tkinter import *
from tkinter import ttk

root = Tk()
root.title("Document Form")

# Search Bar Frame
searchFrame = ttk.Frame(root, padding=(10, 10, 10, 10))
searchFrame.grid(column=0, row=0, rowspan=2, sticky=(N, S, E, W))

# Search Bar
searchLabel = ttk.Label(searchFrame, text="Search")
searchLabel.grid(column=0, row=0, padx=10, sticky=W)

searchEntry = ttk.Entry(searchFrame)
searchEntry.grid(column=1, row=(0), padx=0, pady=(0), sticky=(W,E))

# Sort by Label
sortbyLabel = ttk.Label(searchFrame, text="Sort by")
sortbyLabel.grid(column=0, row=2, padx=10, sticky=W)

# Checkbox
var1 = IntVar()
c1 = ttk.Checkbutton(searchFrame, text='Date', variable=var1, onvalue=1, offvalue=0)
c1.grid(column=1, row=2, sticky=(W, E), padx=0, pady=10)

var2 = IntVar()
c2 = ttk.Checkbutton(searchFrame, text='Type', variable=var2, onvalue=1, offvalue=0)
c2.grid(column=1, row=2, sticky=(W, E), padx=75, pady=10)

var3 = IntVar()
c3 = ttk.Checkbutton(searchFrame, text='Name', variable=var3, onvalue=1, offvalue=0)
c3.grid(column=1, row=2, sticky=(W, E), padx=150, pady=10)

# Treeview (Table) with 5 columns
columns = ("#", "Document Name", "Date", "Type", "Download")
tree = ttk.Treeview(root, columns=columns, show="headings")


# Set column headings
for col in columns:
    tree.heading(col, text=col)
    

# Add some sample data
for i in range(10):
    tree.insert("", "end", values=(f"{i+1}", f"Value {i+2}", f"Value {i+3}", f"Value {i+4}", f"Value {i+5}"))

# Place the Treeview in the grid
tree.grid(column=0, row=2, sticky=(N, S, E, W), padx=(20, 20), pady=(20, 20))

# Add a vertical scrollbar
scrollbar = ttk.Scrollbar(root, orient=VERTICAL, command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.grid(row=2, column=1, sticky='ns')

# Column and Row configurations for resizing
root.columnconfigure(0, weight=1)  # Allow the entire window to resize
root.rowconfigure(0, weight=0)
root.rowconfigure(1, weight=0)
root.rowconfigure(2, weight=1)  # Make the row with the table resizable

searchFrame.columnconfigure(0, weight=1)
searchFrame.columnconfigure(1, weight=1)
searchFrame.columnconfigure(2, weight=1)
searchFrame.columnconfigure(3, weight=1)
searchFrame.rowconfigure(0, weight=0)
searchFrame.rowconfigure(1, weight=0)

# Make only the checkbox columns resizable
searchFrame.columnconfigure(1, weight=1)
searchFrame.columnconfigure(2, weight=1)
searchFrame.columnconfigure(3, weight=1)

# Make each column of the table resizable
for col in columns:
    tree.column(col, anchor="center")
    tree.column(col, stretch=True)

root.mainloop()
