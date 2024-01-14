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
imageFrame.grid(column=0, row=0, rowspan=1, padx=10, pady=10, sticky=(N, S, W, E))

# Image box on the left side
imageLabel = ttk.Label(imageFrame, text="Camera Preview", width=40, anchor='center')
imageLabel.grid(column=0, row=0, padx=10, pady=10, sticky=(N, S, W, E))

# Frame for input fields
inputFrame = ttk.Frame(contentFrame, borderwidth=2, relief="solid")  # Add border
inputFrame.grid(column=1, row=0, padx=10, pady=10, sticky=(N, S, W, E))

# Labels and Entry fields on the right side
documentNameLabel = ttk.Label(inputFrame, text="Document Name:")
documentNameLabel.grid(column=0, row=0, padx=10, pady=(0, 2), sticky=W)

documentNameEntry = ttk.Entry(inputFrame)
documentNameEntry.grid(column=1, row=0, padx=10, pady=(0, 2), sticky=(W, E))

dateLabel = ttk.Label(inputFrame, text="Date:")
dateLabel.grid(column=0, row=1, padx=10, pady=(0, 2), sticky=W)

dateEntry = ttk.Entry(inputFrame)
dateEntry.grid(column=1, row=1, padx=10, pady=(0, 2), sticky=(W, E))

# Button to browse for an image
browseButton = ttk.Button(inputFrame, text="Browse Image", command=browseImage)
browseButton.grid(column=0, row=2, columnspan=2, pady=10, padx=10, sticky=(W, E))

# Column and Row configurations for resizing
contentFrame.columnconfigure(0, weight=1)  # Allow the first column (image frame) to resize
contentFrame.columnconfigure(1, weight=1)
contentFrame.rowconfigure(0, weight=1)

imageFrame.columnconfigure(0, weight=1)  # Allow the image frame to resize
imageFrame.rowconfigure(0, weight=1)

inputFrame.columnconfigure(0, weight=1)  # Allow the input frame to resize
inputFrame.columnconfigure(1, weight=1)
inputFrame.rowconfigure(0, weight=0)
inputFrame.rowconfigure(1, weight=0)
inputFrame.rowconfigure(2, weight=0)

root.columnconfigure(0, weight=1)  # Allow the entire window to resize
root.rowconfigure(0, weight=1)

# Checkbox under image frame
var1 = IntVar()
c1 = ttk.Checkbutton(contentFrame, text='First Page', variable=var1, onvalue=1, offvalue=0)
c1.grid(column=0, row=1, sticky=(E, S), padx=10, pady=10)

#Button width for All buttons
button_width = 10  # Set a common width for all buttons

#Capture Image Button
button4 = ttk.Button (contentFrame, text="Capture", width=button_width)
button4.grid(column=0, row=1, pady=10, padx=9, sticky=(W))

button5 = ttk.Button (contentFrame, text="Add", width=button_width)
button5.grid(column=0, row=1, pady=10, padx=10, sticky=(N))

#Buttons for content side
button1 = ttk.Button(contentFrame, text="Retake", width=button_width)
button1.grid(column=1, row=1, pady=10, padx=5, sticky=(N))

button2 = ttk.Button(contentFrame, text="Add", width=button_width)
button2.grid(column=1, row=1, pady=10, padx=9, sticky=(E))

button3 = ttk.Button(contentFrame, text="Finish", width=button_width)
button3.grid(column=1, row=1, pady=10, padx=10, sticky=(W))


root.mainloop()
