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
from skimage.filters import threshold_local

camera_running = True  # Flag to control the camera feed


# Function to update the camera feed
def update_camera():
    if camera_running:
        frame = next(camera.capture_continuous(
            rawCapture, format="bgr", use_video_port=True))
        feed = frame.array

        # Convert image to grayscale
        grayed_image = cv2.cvtColor(feed, cv2.COLOR_BGR2GRAY)

        # Thresholding
        T = threshold_local(grayed_image, 11, offset=10, method="gaussian")

        transformed_image = (grayed_image > T).astype("uint8") * 255

        final = Image.fromarray(transformed_image)
        final = ImageTk.PhotoImage(final)

        # Update te camera preview with the grayscaled version
        cameraView.config(image=final)
        cameraView.image = final

        key = cv2.waitKey(1) & 0xFF
        rawCapture.truncate(0)
        if key == ord("q"):
            root.destroy()
            return

    root.after(1, update_camera)  # Schedule the next update


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

    # Start the Tkinter main loop
    update_camera()
    root.mainloop()
