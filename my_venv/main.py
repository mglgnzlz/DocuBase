from tkinter import *
from tkinter import ttk, filedialog
from PIL import Image, ImageTk

def browseImage():
    filename = filedialog.askopenfilename()
    if filename:
        loadAndDisplayImage(filename)

def loadAndDisplayImage(filename):
    image = Image.open(filename)
    image = image.resize((400, 400), resample=Image.LANCZOS)  # Use Lanczos resampling
    photo = ImageTk.PhotoImage(image)
    imageLabel.config(image=photo)
    imageLabel.image = photo

root = Tk()
root.title("Document Form")

# Frame for the entire content
contentFrame = ttk.Frame(root, padding=(10, 10, 10, 10))
contentFrame.grid(column=0, row=0, sticky=(N, S, E, W))

# Frame for image display
imageFrame = ttk.Frame(contentFrame, borderwidth=2, relief="solid")  # Add border
imageFrame.grid(column=0, row=0, rowspan=5, padx=10, sticky=(N, S, W, E))

# Image box on the left side
imageLabel = ttk.Label(imageFrame, text="Image Preview", width=40, anchor='center')
imageLabel.grid(column=0, row=0, sticky=(N, S, W, E))  # No rowspan needed

# Frame for input fields
inputFrame = ttk.Frame(contentFrame, borderwidth=2, relief="solid")  # Add border
inputFrame.grid(column=1, row=0, sticky=(N, S, W, E))

# Labels and Entry fields on the right side
documentNameLabel = ttk.Label(inputFrame, text="Document Name:")
documentNameLabel.grid(column=0, row=0, sticky=W, padx=10, pady=(0, 2))  # Adjust pady

documentNameEntry = ttk.Entry(inputFrame)
documentNameEntry.grid(column=1, row=0, sticky=(W, E), padx=10, pady=(0, 2))  # Adjust pady

dateLabel = ttk.Label(inputFrame, text="Date:")
dateLabel.grid(column=0, row=1, sticky=W, padx=10, pady=(0, 2))  # Adjust pady

dateEntry = ttk.Entry(inputFrame)
dateEntry.grid(column=1, row=1, sticky=(W, E), padx=10, pady=(0, 2))  # Adjust pady

# Button to browse for an image
browseButton = ttk.Button(inputFrame, text="Browse Image", command=browseImage)
browseButton.grid(column=0, row=2, columnspan=2, pady=10, sticky=(W, E))  # Adjust row number and columnspan

# Column and Row configurations for resizing
contentFrame.columnconfigure(0, weight=0)  # Allow the first column (image frame) to resize
contentFrame.columnconfigure(1, weight=1)
contentFrame.rowconfigure(0, weight=1)
contentFrame.rowconfigure(5, weight=1)  # Adjust row number

imageFrame.columnconfigure(0, weight=1)  # Allow the image frame to resize
imageFrame.rowconfigure(0, weight=1)

inputFrame.columnconfigure(0, weight=1)  # Allow the input frame to resize
inputFrame.columnconfigure(1, weight=1)
inputFrame.rowconfigure(0, weight=0)
inputFrame.rowconfigure(1, weight=0)
inputFrame.rowconfigure(2, weight=0)

root.columnconfigure(0, weight=1)  # Allow the entire window to resize
root.rowconfigure(0, weight=1)

root.mainloop()
