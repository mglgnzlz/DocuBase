import cv2
import tkinter as tk
import os
from tkinter import IntVar, ttk, filedialog
from picamera.array import PiRGBArray
from picamera import PiCamera
from PIL import Image, ImageTk

# Function to update the camera feed
def update_camera():
        frame = next(camera.capture_continuous(rawCapture, format="bgr", use_video_port=True))
        image = frame.array

        # Convert OpenCV image to Tkinter PhotoImage
        img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img = ImageTk.PhotoImage(img)

        # Update the label with the new image
        cameraView.config(image=img)
        cameraView.image = img

        key = cv2.waitKey(1) & 0xFF
        rawCapture.truncate(0)

        if key == ord("q"):
            root.destroy()
            return

        root.after(1, update_camera)  # Schedule the next update


# Function to capture and save an image
def capture_image():
    # Capturing a single frame
    frame = next(camera.capture_continuous(rawCapture, format="bgr", use_video_port=True))
    image = frame.array
    
    # Saving
    cv2.imwrite("/home/rpig3/docubase/env/bin/mainProg/temp_fldr/captured_image.jpg", cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    # Reset the rawCapture object for the next capture
    rawCapture.truncate(0)


def browse_image():
    global img
    file_path = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select Image File",\
		filetypes=(('JPG file', '*.jpg'), ('PNG file', '*.png'), ('All File', "*.*")))
    image=Image.open(file_path)
    image = image.resize((300, 384), resample=Image.LANCZOS)
    img = ImageTk.PhotoImage(image)
    previewLabel.config(image=img)
    previewLabel.image = img

def convert_images_to_pdf(folder_path, output_pdf_path):
    images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    if not images:
        print("No images found in the selected folder.")
        return

    images.sort()  # Optional: Sort the images alphabetically

    img_list = [Image.open(os.path.join(folder_path, img)) for img in images]
    img_list[0].save(output_pdf_path, save_all=True, append_images=img_list[1:])


def on_done_button_click():
    initial_folder = r"C:\\Users\\danica\\OneDrive\\Desktop\\example"
    folder_path = filedialog.askdirectory(title="Select a folder with images", initialdir=initial_folder)
    
    if folder_path:
        output_folder = r"c:\\Users\\danica\\OneDrive\\Desktop\\done"  # Change this to the desired output folder
        output_pdf_path = os.path.join(output_folder, "output.pdf")
        
        convert_images_to_pdf(folder_path, output_pdf_path)
        print("Conversion completed successfully!")


# Initialize PiCamera
camera = PiCamera()
camera.resolution = (400, 512)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(400, 512))

# Initialize the root widget
root = tk.Tk()
root.title("Document Form")

# Frame for the entire content
contentFrame = ttk.Frame(root, padding=(10, 10, 10, 10))
contentFrame.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))

# Frame & Display the camera preview
cameraFrame = ttk.LabelFrame(contentFrame, text="Camera Preview")
cameraFrame.grid(column=0, row=0, padx=10, pady=10, sticky=(tk.N, tk.S, tk.E, tk.W))
cameraView = ttk.Label(cameraFrame)
cameraView.grid(column=0, row=0, padx=10, pady=10, sticky=(tk.N, tk.S, tk.E, tk.W))

# Capture Button
captureBFrame = ttk.Frame(cameraFrame, padding=(0, 0, 0, 10))
captureBFrame.grid(column=0, row=1)
captureButton = ttk.Button(captureBFrame, text="Capture Image", command=capture_image)
captureButton.grid(column=0, row=0, sticky=(tk.W, tk.E))

# Frame for right side contents (invisible)
rightFrame = ttk.Frame(contentFrame)
rightFrame.grid(column=1, row=0, padx=10, sticky=(tk.N, tk.S, tk.W, tk.E))

# Frame for input fields
inputFrame = ttk.LabelFrame(rightFrame, text="Input Fields")
inputFrame.grid(column=1, row=0, pady=10, sticky=(tk.N, tk.S, tk.W, tk.E))

# Labels and Entry fields
documentNameLabel = ttk.Label(inputFrame, text="Document Name:")
documentNameLabel.grid(column=0, row=0, padx=10, pady=(10, 2), sticky=tk.W)
documentNameEntry = ttk.Entry(inputFrame)
documentNameEntry.grid(column=1, row=0, padx=10, sticky=(tk.W, tk.E))
dateLabel = ttk.Label(inputFrame, text="Date:")
dateLabel.grid(column=0, row=1, padx=10, pady=(5, 2), sticky=tk.W)
dateEntry = ttk.Entry(inputFrame)
dateEntry.grid(column=1, row=1, padx=10, sticky=(tk.W, tk.E))

# Browse Button
browseButton = ttk.Button(inputFrame, text="Browse Image", command=browse_image)
browseButton.grid(column=0, row=2, columnspan=2, pady=10, padx=10, sticky=(tk.W, tk.E))

# Frame for image preview
previewFrame = ttk.LabelFrame(rightFrame, text="Image Preview")
previewFrame.grid(column=1, row=1, sticky=(tk.N, tk.S, tk.W, tk.E))
previewLabel = ttk.Label(previewFrame)
previewLabel.grid(column=0, row=0, padx=10, pady=10, sticky=(tk.N, tk.S, tk.W, tk.E))

# Column and Row configurations for resizing
# Allow the first column (image frame) to resize
contentFrame.columnconfigure(0, weight=1)
contentFrame.columnconfigure(1, weight=1)
contentFrame.rowconfigure(0, weight=1)

cameraFrame.columnconfigure(0, weight=1)  # Allow the image frame to resize
cameraFrame.rowconfigure(0, weight=1)

root.columnconfigure(0, weight=1)  # Allow the entire window to resize
root.rowconfigure(0, weight=1)

# Checkbox under image frame
var1 = IntVar()
c1 = ttk.Checkbutton(contentFrame, text='First Page', variable=var1, onvalue=1, offvalue=0)
c1.grid(column=0, row=1, sticky=(tk.E, tk.S), padx=10, pady=10)

# Buttons in one row following the content frame
button_width = 10  # Set a common width for all buttons

button1 = ttk.Button(contentFrame, text="Retake", width=button_width)
button1.grid(column=1, row=1, pady=10, padx=5, sticky=(tk.N))

button2 = ttk.Button(contentFrame, text="Add", width=button_width)
button2.grid(column=1, row=1, pady=10, padx=9, sticky=(tk.E))

button3 = ttk.Button(contentFrame, text="Finish", width=button_width)
button3.grid(column=1, row=1, pady=10, padx=10, sticky=(tk.W))

# Run the camera update function in a separate thread
root.after(100, update_camera)  # Wait for 100 milliseconds before starting

# Start the Tkinter main loop
root.mainloop()

# Release resources
cv2.destroyAllWindows()
camera.close()