import cv2
import tkinter as tk
import os
from io import BytesIO
from tkinter import IntVar, ttk, filedialog
from picamera.array import PiRGBArray
from picamera import PiCamera
from PIL import Image, ImageTk

image_counter = 1
button_width = 15

# Function to update the camera feed


def update_camera():
    frame = next(camera.capture_continuous(
        rawCapture, format="bgr", use_video_port=True))
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
    global image_counter

    # Capturing a single frame
    frame = next(camera.capture_continuous(
        rawCapture, format="bgr", use_video_port=True))
    image = frame.array

    # Directory path
    directory = "/home/rpig3/docubase/env/bin/mainProg/temp_fldr"

    # Saving the image with a numbered filename
    image_path = os.path.join(directory, f"captured_image_{image_counter}.jpg")
    cv2.imwrite(image_path, cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # Update the preview with the captured image
    update_preview(image_path)

    # Show retake button
    retakeButton.grid(column=0, row=1, padx=(0, 5), pady=(0, 5))
    addButton.grid(column=1, row=1, padx=(5, 0), pady=(0, 5))
    finishButton.grid(column=0, row=2, pady=10)

    # Increment the image counter for the next capture
    image_counter += 1

    # Reset the rawCapture object for the next capture
    rawCapture.truncate(0)


# Function to update the preview image
def update_preview(image_path):
    image = Image.open(image_path)
    image = image.resize((320, 240), resample=Image.LANCZOS)
    img = ImageTk.PhotoImage(image)
    previewLabel.config(image=img)
    previewLabel.image = img


# Retake Button Function
def retake_button():
    # Hide the buttons
    retakeButton.grid_forget()
    addButton.grid_forget()
    finishButton.grid_forget()

    # Reset the previewLabel
    previewLabel.config(image="")
    previewLabel.image = None


# Add Button Function
def add_button():
    global image_counter

    # Directory path
    output_directory = "/home/rpig3/docubase/env/bin/mainProg/scan_fldr"

    # Get the original image file path of the image in the preview
    original_image_path = f"/home/rpig3/docubase/env/bin/mainProg/temp_fldr/captured_image_{image_counter}.jpg"

    # Save the image in the dedicated directory
    image_path = os.path.join(
        output_directory, f"added_image_{image_counter-1}.jpg")

    # Open the original image with PIL and save it to the new path
    pil_image = Image.open(original_image_path)
    pil_image.save(image_path)

    retake_button()


# Function to browse image to display in preview image frame
def browse_image():
    global img
    file_path = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select Image File",
                                           filetypes=(('JPG file', '*.jpg'), ('PNG file', '*.png'), ('All File', "*.*")))
    image = Image.open(file_path)
    image = image.resize((320, 240), resample=Image.LANCZOS)
    img = ImageTk.PhotoImage(image)
    previewLabel.config(image=img)
    previewLabel.image = img


def convert_images_to_pdf(folder_path, output_pdf_path):
    images = [f for f in os.listdir(folder_path) if f.lower().endswith(
        ('.png', '.jpg', '.jpeg', '.gif'))]

    if not images:
        print("No images found in the selected folder.")
        return

    images.sort()  # Optional: Sort the images alphabetically

    img_list = [Image.open(os.path.join(folder_path, img)) for img in images]
    img_list[0].save(output_pdf_path, save_all=True,
                     append_images=img_list[1:])


def on_done_button_click():
    initial_folder = r"C:\\Users\\danica\\OneDrive\\Desktop\\example"
    folder_path = filedialog.askdirectory(
        title="Select a folder with images", initialdir=initial_folder)

    if folder_path:
        # Change this to the desired output folder
        output_folder = r"c:\\Users\\danica\\OneDrive\\Desktop\\done"
        output_pdf_path = os.path.join(output_folder, "output.pdf")

        convert_images_to_pdf(folder_path, output_pdf_path)
        print("Conversion completed successfully!")


# Initialize PiCamera
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(640, 480))

# Initialize the root widget
root = tk.Tk()
root.title("Document Form")

# Frame for the entire content
contentFrame = ttk.Frame(root, padding=(10, 10, 10, 10))
contentFrame.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))

# Frame & Display the camera preview (left side)
cameraFrame = ttk.LabelFrame(contentFrame, text="Camera Preview")
cameraFrame.grid(column=0, row=0, padx=10, pady=10,
                 sticky=(tk.N, tk.S, tk.E, tk.W))
cameraView = ttk.Label(cameraFrame)
cameraView.grid(column=0, row=0, padx=10, pady=10,
                sticky=(tk.N, tk.S, tk.E, tk.W))

# Capture Button
captureBFrame = ttk.Frame(cameraFrame)
captureBFrame.grid(column=0, row=1, pady=(5, 10))
captureButton = ttk.Button(
    captureBFrame, text="Capture Image", width=button_width, command=capture_image)
captureButton.grid(column=0, row=0, columnspan=2, sticky=(tk.W, tk.E))

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
browseButton = ttk.Button(
    inputFrame, text="Browse Image", width=button_width, command=browse_image)
browseButton.grid(column=0, row=2, columnspan=2,
                  pady=10, padx=10, sticky=(tk.W, tk.E))

# Frame for image preview
previewFrame = ttk.LabelFrame(rightFrame, text="Image Preview")
previewFrame.grid(column=1, row=1, sticky=(tk.N, tk.S, tk.W, tk.E))
previewLabel = ttk.Label(previewFrame)
previewLabel.grid(column=0, row=0, padx=10, pady=10,
                  sticky=(tk.N, tk.S, tk.W, tk.E))
finishButton = ttk.Button(previewFrame, text="Finish")

# Retake and Add Button and Frame
buttonsFrame = ttk.Frame(previewFrame)
buttonsFrame.grid(column=0, row=1)
retakeButton = ttk.Button(buttonsFrame, text="Retake",
                          width=button_width, command=retake_button)
addButton = ttk.Button(buttonsFrame, text="Add",
                       width=button_width, command=add_button)

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
# var1 = IntVar()
# c1 = ttk.Checkbutton(contentFrame, text='First Page',
#                      variable=var1, onvalue=1, offvalue=0)
# c1.grid(column=0, row=1, sticky=(tk.E, tk.S), padx=10, pady=10)

# Run the camera update function in a separate thread
root.after(100, update_camera)  # Wait for 100 milliseconds before starting

# Start the Tkinter main loop
root.mainloop()

# Release resources
cv2.destroyAllWindows()
camera.close()
