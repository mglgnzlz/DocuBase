import os
import cv2
import time
import numpy as np
import preprocessed
import subprocess
import tkinter as tk
import secpage
from io import BytesIO
from picamera import PiCamera
from PIL import Image, ImageTk
from picamera.array import PiRGBArray
from tkinter import IntVar, ttk, filedialog, messagebox

image_counter = 1
button_width = 12
file_name = ""
camera_running = True  # Flag to control the camera feed

def shutdown_raspberry_pi():
    # Use subprocess to execute the shutdown command
    subprocess.run(["sudo", "shutdown", "-h", "now"])
    
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
def capture_image_button():
    global camera_running, image_counter, file_name
    directory = "/home/rpig3/docubase/env/bin/mainProg/temp_fldr"
    captureButton["state"] = "disable"

    start_time = time.time()

    # Pause camera feed
    camera_running = not camera_running

    # Set resolution for capturing image
    camera.rotation = 0
    camera.resolution = (1640, 1232)
    frame = PiRGBArray(camera)
    camera.capture(frame, format="bgr")
    image = frame.array

    # Saving the unfiltered image
    unfiltered_image_path = os.path.join(
        directory, f"captured_image_{image_counter}.jpg")
    cv2.imwrite(unfiltered_image_path, cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    unfiltered_image = cv2.imread(unfiltered_image_path)

    # Preprocessing and saving of preprocessed image
    preprocessed_image = preprocessed.preprocessing(unfiltered_image)
    preprocessed_image_path = os.path.join(
        directory, f"preprocessed_image_{image_counter}.jpg")
    cv2.imwrite(preprocessed_image_path, preprocessed_image)
    preprocessed_image = cv2.imread(preprocessed_image_path)

    # Deskewing of preprocesed image
    aligned_image = preprocessed.deskewing(preprocessed_image)
    aligned_image_path = os.path.join(
        directory, f"aligned_image_{image_counter}.jpg")
    cv2.imwrite(aligned_image_path, aligned_image)

    # Update the preview with the preprocessed image
    update_preview(aligned_image_path)

    # Show retake button
    retakeButton.grid(column=1, row=0, padx=(0, 10), pady=10)
    addButton.grid(column=1, row=1, padx=(0, 10), pady=10)
    finishButton.grid(column=1, row=2, padx=(0, 10), pady=10)

    # Increment the image counter for the next capture
    image_counter += 1

    # Reset the resolution to the original value
    camera.rotation = 90
    camera.resolution = (368, 480)

    rawCapture.truncate(0)  # Clear the camera array after capturing

    # OCR
    text = preprocessed.tesseract(aligned_image_path)

    # Reflecting the document name and date
    file_name = update_text_display(text)

    # Resume camera feed
    camera_running = not camera_running
    # captureButton["state"] = "normal"

    end_time = time.time()
    total_process_time = end_time - start_time
    print(f"Process time: {total_process_time} seconds")


# Function to update the preview image
def update_preview(image_path):
    image = Image.open(image_path)
    image = image.resize((420, 580), resample=Image.LANCZOS)
    photo = ImageTk.PhotoImage(image)
    previewLabel.config(image=photo)
    previewLabel.image = photo


# # Retake Button Function
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
    captureButton["state"] = "normal"
    dateEntry.delete(1.0, tk.END)   # Clear previous content
    documentNameEntry.delete(1.0, tk.END)  # Clear previous content


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
    
    captureButton["state"] = "normal"
    dateEntry.delete(1.0, tk.END)   # Clear previous content
    documentNameEntry.delete(1.0, tk.END)  # Clear previous content


# Finish Button Function
def finish_button():
    global file_name, image_counter
    response = messagebox.askyesno("Confirmation", "Do you want to proceed?")
    if response:
        add_button()
        scanned_directory_path = r"/home/rpig3/docubase/env/bin/mainProg/scan_fldr"

        if scanned_directory_path:
            # Change this to the desired output folder
            pdf_directory = "/home/rpig3/docubase/env/bin/mainProg/DocuBase"
            pdf_directory_path = os.path.join(
                pdf_directory, f"{file_name}.pdf")
            convert_images_to_pdf(scanned_directory_path, pdf_directory_path)
            messagebox.showinfo("", "Conversion completed successfully")
            image_counter = 1
    else:
        messagebox.showinfo("", "You clicked no!")
        return


# Browse Database Button Function
def browse_database_button():
    secpage.open_secpage_window()


# Conversion of images to PDF
def convert_images_to_pdf(scanned_directory_path, pdf_directory_path):
    images = [f for f in os.listdir(
        scanned_directory_path) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    images.sort()  # Optional: Sort the images alphabetically
    img_list = [Image.open(os.path.join(scanned_directory_path, img))
                for img in images]
    img_list[0].save(pdf_directory_path, save_all=True,
                     append_images=img_list[1:])


def update_text_display(text):
    global file_name, image_counter
    if image_counter == 2:
        dateEntry.delete(1.0, tk.END)  # Clear previous content
        dateEntry.insert(tk.END, text[:3])
        documentNameEntry.delete(1.0, tk.END)  # Clear previous content
        documentNameEntry.insert(tk.END, text[3:])
        date = "_".join(text[:3])
        document = "_".join(text[3:])
        file_name = document + "_" + date
        return file_name
    else:
        return file_name


# Set up PiCamera
with PiCamera() as camera:
    camera.rotation = 90
    camera.resolution = (368, 480)
    rawCapture = PiRGBArray(camera)

    # Create the main window
    root = tk.Tk()
    root.title("Document Scanner Form")
    root.attributes("-fullscreen", True)

    # Frame for the entire content
    contentFrame = ttk.Frame(root, padding=(10, 10, 10, 10))
    contentFrame.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))

    # Left frame (invisible)
    leftFrame = ttk.Frame(contentFrame)
    leftFrame.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.W, tk.E))

    # Frame & Display the camera preview (left side)
    cameraFrame = ttk.LabelFrame(leftFrame, text="Camera Preview")
    cameraFrame.grid(column=0, row=0, padx=10, pady=10,
                     sticky=(tk.N, tk.S, tk.E, tk.W))
    cameraView = ttk.Label(cameraFrame)
    cameraView.grid(column=0, row=0, padx=10, pady=10,
                    sticky=("nsew"))

    # Capture Button
    captureBFrame = ttk.Frame(cameraFrame)
    captureBFrame.grid(column=0, row=1, pady=(5, 10))
    captureButton = ttk.Button(
        captureBFrame, text="Capture Image", width=button_width, command=capture_image_button)
    captureButton.grid(column=0, row=0, columnspan=2, sticky=(tk.W, tk.E))

    # Frame for input fields
    inputFrame = ttk.LabelFrame(leftFrame, text=" ")
    inputFrame.grid(column=0, row=1, padx=5, pady=10,
                    sticky=(tk.N, tk.S, tk.W, tk.E))

    # Labels and Entry fields
    documentNameLabel = ttk.Label(inputFrame, text="Document Name:")
    documentNameLabel.grid(column=0, row=0, padx=10, pady=(10, 2), sticky=tk.W)
    documentNameEntry = tk.Text(inputFrame, height=1, width=30)
    documentNameEntry.grid(column=1, row=0, padx=10, sticky=(tk.W, tk.E))
    dateLabel = ttk.Label(inputFrame, text="Date:")
    dateLabel.grid(column=0, row=1, padx=10, pady=(5, 2), sticky=tk.W)
    dateEntry = tk.Text(inputFrame, height=1, width=30)
    dateEntry.grid(column=1, row=1, padx=10, sticky=(tk.W, tk.E))

    # Browse Databaes Button
    browseButton = ttk.Button(
        inputFrame, text="Browse Database", width=button_width, command=browse_database_button)
    browseButton.grid(column=0, row=2, columnspan=2,
                      pady=10, padx=10, sticky=(tk.W, tk.E))

    # Right frame (invisible)
    rightFrame = ttk.Frame(contentFrame)
    rightFrame.grid(column=1, row=0, sticky=(tk.N, tk.S, tk.W, tk.E))

    # Frame for image preview
    previewFrame = ttk.LabelFrame(rightFrame, text="Image Preview")
    previewFrame.grid(column=0, row=0, padx=10, pady=(10, 0),
                      sticky=(tk.N, tk.S, tk.W, tk.E))
    previewLabel = ttk.Label(previewFrame)
    previewLabel.grid(column=0, row=0, padx=10, pady=10,
                      sticky=(tk.N, tk.S, tk.W, tk.E))

    # Retake and Add Button and Frame
    buttonsFrame = ttk.Frame(previewFrame)
    buttonsFrame.grid(column=1, row=0)
    retakeButton = ttk.Button(buttonsFrame, text="Retake",
                              width=button_width, command=retake_button)
    addButton = ttk.Button(buttonsFrame, text="Add",
                           width=button_width, command=add_button)

    shutButton = ttk.Button(rightFrame, text="Shutdown", command=shutdown_raspberry_pi)
    shutButton.grid(column=0, row=1, padx=10, pady=(0, 12), sticky=("sew"))

    # Add confirmation pop up function
    finishButton = ttk.Button(
        buttonsFrame, width=button_width, text="Finish", command=finish_button)

    # Configure column weights for inputFrame
    inputFrame.columnconfigure(1, weight=1)
    # Configure row weights for rightFrame
    rightFrame.rowconfigure(1, weight=1)

    # Start the Tkinter main loop
    update_camera()
    root.mainloop()
