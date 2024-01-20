import cv2
import tkinter as tk
import os
import numpy as np
from io import BytesIO
from tkinter import IntVar, ttk, filedialog
from picamera.array import PiRGBArray
from picamera import PiCamera
from PIL import Image, ImageTk

image_counter = 1
button_width = 15


def order_points(pts):
    '''Rearrange coordinates to order:
       top-left, top-right, bottom-right, bottom-left'''
    rect = np.zeros((4, 2), dtype='float32')
    pts = np.array(pts)
    s = pts.sum(axis=1)
    # Top-left point will have the smallest sum.
    rect[0] = pts[np.argmin(s)]
    # Bottom-right point will have the largest sum.
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    # Top-right point will have the smallest difference.
    rect[1] = pts[np.argmin(diff)]
    # Bottom-left will have the largest difference.
    rect[3] = pts[np.argmax(diff)]
    # return the ordered coordinates
    return rect.astype('int').tolist()


# Function to update the camera feed
def update_camera():
    frame = next(camera.capture_continuous(
        rawCapture, format="bgr", use_video_port=True))
    image = frame.array

    # Convert OpenCV image to Tkinter PhotoImage
    img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img = Image.fromarray(img)
    img = ImageTk.PhotoImage(img)

    # Update the camera preview with the new image
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
    captureButton["state"] = "disable"
    # Capturing a single frame
    # Directory path
    directory = "/home/rpig3/docubase/env/bin/mainProg/temp_fldr"

    image_path = os.path.join(directory, f"captured_image_{image_counter}.jpg")

    highres_path = os.path.join(directory, f"highres_image_{image_counter}.jpg")

    frame = next(camera.capture_continuous(
        rawCapture, format="bgr", use_video_port=True))
    image = frame.array
    cv2.imwrite(image_path, cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    camera.resolution = (3280, 2464)
    camera.capture(highres_path)
    # Saving the unfiltered image
    # cv2.imwrite(image_path, cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
    # img = cv2.imread(image_path)

    # Preprocessing
    # preprocessed_img = preprocessing(img)

    # # Saving the preprocesed image
    # preprocessed_path = os.path.join(
    #     directory, f"preprocessed_image_{image_counter}.jpg")
    # cv2.imwrite(preprocessed_path, preprocessed_img)

    # Update the preview with the preprocessed image
    update_preview(image_path)

    # Show retake button
    retakeButton.grid(column=0, row=1, padx=(0, 5), pady=(0, 5))
    addButton.grid(column=1, row=1, padx=(5, 0), pady=(0, 5))
    finishButton.grid(column=0, row=2, pady=10)

    # Increment the image counter for the next capture
    image_counter += 1

    # Reset the rawCapture object for the next capture
    rawCapture.truncate(0)

    captureButton["state"] = "normal"


# Image Preprocessing Function
def preprocessing(img):
    # Scan for resize
    dim_limit = 1080
    max_dim = max(img.shape)
    if max_dim > dim_limit:
        resize_scale = dim_limit / max_dim
        img = cv2.resize(img, None, fx=resize_scale, fy=resize_scale)

    # Create a copy of resized original image for later use
    orig_img = img.copy()

    # Removing text from the document
    kernel = np.ones((7, 7), np.uint8)
    no_text_img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel, iterations=5)

    # Apply grayscaling
    grayed_img = cv2.cvtColor(no_text_img, cv2.COLOR_BGR2GRAY)

    # Apply blur
    blurred_img = cv2.GaussianBlur(grayed_img, (15, 15), 0)

    # Apply egde detection & dilation
    edged_img = cv2.Canny(blurred_img, 0, 200)
    edged_img = cv2.dilate(
        edged_img, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21)))

    # Finding contours for the detected edges.
    con = np.zeros_like(no_text_img)
    contours, hierarchy = cv2.findContours(
        edged_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Keeping only the largest detected contour.
        page = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
        contour_img = cv2.drawContours(con, page, -1, (0, 255, 255), 3)
        corners, destination_corners = find_corners(con, page)

        h, w = orig_img.shape[:2]
        # Getting the homography.
        homography, mask = cv2.findHomography(np.float32(corners), np.float32(destination_corners), method=cv2.RANSAC,
                                              ransacReprojThreshold=3.0)
        # Perspective transform using homography.
        print(type(homography))
        print(homography.shape)
        un_warped = cv2.warpPerspective(orig_img, np.float32(
            homography), (w, h), flags=cv2.INTER_LINEAR)
        # Crop
        transformed_img = un_warped[:destination_corners[2]
                                    [1], :destination_corners[2][0]]
        return transformed_img

    else:
        return img


def find_corners(con, page):
    # Detecting Edges through Contour approximation
    if len(page) == 0:
        return orig_img, None
    # Loop over the contours.
    for c in page:
        # Approximate the contour.
        epsilon = 0.02 * cv2.arcLength(c, True)
        corners = cv2.approxPolyDP(c, epsilon, True)
        # If our approximated contour has four points
        if len(corners) == 4:
            break
    cv2.drawContours(con, c, -1, (0, 255, 255), 3)
    cv2.drawContours(con, corners, -1, (0, 255, 0), 10)
    # Sorting the corners and converting them to desired shape.
    corners = sorted(np.concatenate(corners).tolist())
    # Rearranging the order of the corner points.
    corners = order_points(corners)

    # Displaying the corners.
    for index, c in enumerate(corners):
        character = chr(65 + index)
        cv2.putText(con, character, tuple(
            c), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1, cv2.LINE_AA)

    # Finding Destination Co-ordinates
    w1 = np.sqrt((corners[0][0] - corners[1][0]) ** 2 +
                 (corners[0][1] - corners[1][1]) ** 2)
    w2 = np.sqrt((corners[2][0] - corners[3][0]) ** 2 +
                 (corners[2][1] - corners[3][1]) ** 2)
    # Finding the maximum width.
    w = max(int(w1), int(w2))

    h1 = np.sqrt((corners[0][0] - corners[2][0]) ** 2 +
                 (corners[0][1] - corners[2][1]) ** 2)
    h2 = np.sqrt((corners[1][0] - corners[3][0]) ** 2 +
                 (corners[1][1] - corners[3][1]) ** 2)
    # Finding the maximum height.
    h = max(int(h1), int(h2))
    # Final destination co-ordinates.
    destination_corners = order_points(
        np.array([[0, 0], [w - 1, 0], [0, h - 1], [w - 1, h - 1]]))
    return corners, destination_corners


def unwrapping(orig_img, corners, destination_corners):
    h, w = orig_img.shape[:2]
    # Getting the homography.
    homography, mask = cv2.findHomography(np.float32(corners), np.float32(destination_corners), method=cv2.RANSAC,
                                          ransacReprojThreshold=3.0)
    # Perspective transform using homography.
    un_warped = cv2.warpPerspective(orig_img, np.float32(
        homography), (w, h), flags=cv2.INTER_LINEAR)
    # Crop
    transformed_img = un_warped[:destination_corners[2]
                                [1], :destination_corners[2][0]]
    return transformed_img


# Function to update the preview image
def update_preview(image_path):
    image = Image.open(image_path)
    image = image.resize((320, 240), resample=Image.LANCZOS)
    img = ImageTk.PhotoImage(image)
    previewLabel.config(image=img)
    previewLabel.image = img


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

# Run the camera update function in a separate thread
root.after(100, update_camera)  # Wait for 100 milliseconds before starting

# Start the Tkinter main loop
root.mainloop()

# Release resources
cv2.destroyAllWindows()
camera.close()
