import cv2
import os
import preprocessing
import numpy as np
import tkinter as tk
from io import BytesIO
from picamera import PiCamera
from PIL import Image, ImageTk
from picamera.array import PiRGBArray
from tkinter import IntVar, ttk, filedialog

image_counter = 1
button_width = 15
camera_running = True  # Flag to control the camera feed


# Function to update the camera feed
def update_camera():
    if camera_running:
        frame = next(camera.capture_continuous(
            rawCapture, format="bgr", use_video_port=True))
        feed = frame.array

        # Convert image to grayscale
        grayscaled = cv2.cvtColor(feed, cv2.COLOR_BGR2GRAY)
        grayscaled = Image.fromarray(grayscaled)
        grayscaled = ImageTk.PhotoImage(grayscaled)

        # Update te camera preview with the grayscaled version
        cameraView.config(image=grayscaled)
        cameraView.image = grayscaled

        key = cv2.waitKey(1) & 0xFF
        rawCapture.truncate(0)
        if key == ord("q"):
            root.destroy()
            return

    root.after(1, update_camera)  # Schedule the next update


# Function to capture an image
def capture_image():
    global camera_running, image_counter
    directory = "/home/rpig3/docubase/env/bin/mainProg/temp_fldr"
    captureButton["state"] = "disable"

    # Pause camera feed
    camera_running = not camera_running

    # Set resolution for capturing image
    camera.resolution = (3280, 2464)
    frame = PiRGBArray(camera)
    camera.capture(frame, format="bgr")
    image = frame.array

    # Saving the unfiltered image
    image_path = os.path.join(directory, f"captured_image_{image_counter}.jpg")
    cv2.imwrite(image_path, cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    unfiltered_image = cv2.imread(image_path)

    # Preprocessing
    preprocesed_image = preprocessing.preprocessing(unfiltered_image)

    # Saving the preprocesed image
    preprocessed_path = os.path.join(
        directory, f"preprocessed_image_{image_counter}.jpg")
    cv2.imwrite(preprocessed_path, preprocessed_image)

    # Update the preview with the preprocessed image
    update_preview(preprocesed_path)

    # Show retake button
    retakeButton.grid(column=0, row=1, padx=(0, 5), pady=(0, 5))
    addButton.grid(column=1, row=1, padx=(5, 0), pady=(0, 5))
    finishButton.grid(column=0, row=2, pady=10)

    # Increment the image counter for the next capture
    image_counter += 1

    # Reset the resolution to the original value
    camera.resolution = (640, 480)

    rawCapture.truncate(0)  # Clear the camera array after capturing

    # Resume camera feed
    camera_running = not camera_running
    captureButton["state"] = "normal"


# Function to update the preview image
def update_preview(image_path):
    image = Image.open(image_path)
    image = image.resize((320, 240), resample=Image.LANCZOS)
    photo = ImageTk.PhotoImage(image)
    previewLabel.config(image=photo)
    previewLabel.image = photo


# Retake Button Function
def retake_button():
    global image_counter

    # Hide the buttons
    retakeButton.grid_forget()
    addButton.grid_forget()
    finishButton.grid_forget()

    # Reset the previewLabel
    previewLabel.config(image="")
    previewLabel.image = None

    image_counter -= 1


# Add Button Function
def add_button():
    global image_counter

    # Directory path
    output_directory = "/home/rpig3/docubase/env/bin/mainProg/scan_fldr"

    # Get the original image file path of the image in the preview
    original_image_path = f"/home/rpig3/docubase/env/bin/mainProg/temp_fldr/preprocessed_image_{image_counter-1}.jpg"

    # Save the image in the dedicated directory
    image_path = os.path.join(
        output_directory, f"scanned_image_{image_counter-1}.jpg")

    # Open the original image with PIL and save it to the new path
    pil_image = Image.open(original_image_path)
    pil_image.save(image_path)

    retakeButton.grid_forget()
    addButton.grid_forget()
    finishButton.grid_forget()

    # Reset the previewLabel
    previewLabel.config(image="")
    previewLabel.image = None


# Function to browse image to display in preview image frame
def browse_image():
    global img
    file_path = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select Image File",
                                           filetypes=(('JPG file', '*.jpg'), ('PNG file', '*.png'), ('All File', "*.*")))
    image = Image.open(file_path)
    image = image.resize((320, 240), resample=Image.LANCZOS)
    photo = ImageTk.PhotoImage(image)
    previewLabel.config(image=photo)
    previewLabel.image = photo


# Set up PiCamera
with PiCamera() as camera:
    camera.resolution = (640, 480)
    rawCapture = PiRGBArray(camera)

    # Create the main window
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

    # Start the Tkinter main loop
    update_camera()
    root.mainloop()
