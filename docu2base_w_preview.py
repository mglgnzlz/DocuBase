import cv2
import tkinter as tk
import os
import numpy as np
import glob
from io import BytesIO
from tkinter import IntVar, ttk, filedialog
from PIL import Image, ImageTk

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


def scan_image(img):
    # Resize image to workable size
    dim_limit = 1080
    max_dim = max(img.shape)
    if max_dim > dim_limit:
        resize_scale = dim_limit / max_dim
        img = cv2.resize(img, None, fx=resize_scale, fy=resize_scale)

    # Create a copy of resized original image for later use
    orig_img = img.copy()

    no_text_img = removing_text(img)
    grayed_img = grayscaling(no_text_img)
    blurred_img = blurring(grayed_img)
    edged_img = edge_detection(blurred_img)
    contour_img, corners, destination_corners = contours(edged_img, no_text_img)
    transformed_img = unwrapping(orig_img, corners, destination_corners)
     
    return no_text_img, grayed_img, blurred_img, edged_img, contour_img, transformed_img


def removing_text(img):
    # Removing text from the document
    kernel = np.ones((7, 7), np.uint8)
    no_text_img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel, iterations=5)
    return no_text_img

def grayscaling(no_text_img):
    # Convert to grayscale
    grayed_img = cv2.cvtColor(no_text_img, cv2.COLOR_BGR2GRAY)
    return grayed_img

def blurring(grayed_img):
    # Blur
    blurred_img = cv2.GaussianBlur(grayed_img, (11, 11), 0)
    return blurred_img

def edge_detection(blurred_img):
    # Egde Detection
    edged_img = cv2.Canny(blurred_img, 0, 200)
    edged_img = cv2.dilate(
        edged_img, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    return edged_img

def contours(edged_img, no_text_img):
    # Finding contours for the detected edges.
    con = np.zeros_like(no_text_img)
    contours, hierarchy = cv2.findContours(
        edged_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    # Keeping only the largest detected contour.
    page = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
    contour_img = cv2.drawContours(con, page, -1, (0, 255, 255), 3)
    corners, destination_corners = find_corners(con, page)
    
    return contour_img, corners, destination_corners

def find_corners(con, page):
    # Detecting Edges through Contour approximation
    if len(page) == 0:
        return orig_img
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
    transformed_img = un_warped[:destination_corners[2][1], :destination_corners[2][0]]
    return transformed_img


def convert_image():
    directory = "/home/rpig3/docubase/env/bin/mainProg"
    no_text_img_path = os.path.join(directory, "no_text_img.jpg")
    grayed_img_path = os.path.join(directory, "grayed_img.jpg")
    blurred_img_path = os.path.join(directory, "blurred_img.jpg")
    edged_img_path = os.path.join(directory, "edged_img.jpg")
    contoured_img_path = os.path.join(directory, "contoured_img.jpg")
    transformed_img_path = os.path.join(directory, "transformed_img.jpg")
    img = cv2.imread(
        "/home/rpig3/docubase/env/bin/mainProg/test_img.jpg")

    no_text_img, grayed_img, blurred_img, edged_img, contour_img, transformed_img = scan_image(img)

    # Save the no text image
    cv2.imwrite(no_text_img_path, no_text_img)
    no_text_preview(no_text_img_path)

    # Save the grayscaled image
    cv2.imwrite(grayed_img_path, grayed_img)
    gray_preview(grayed_img_path)

    # Save the blurred image
    cv2.imwrite(blurred_img_path, blurred_img)
    blur_preview(blurred_img_path)

    # Save the edged image
    cv2.imwrite(edged_img_path, edged_img)
    edge_preview(edged_img_path)

    # Save the contoured image
    cv2.imwrite(contoured_img_path, contour_img)
    contour_preview(contoured_img_path)

    # Save the transformed image
    cv2.imwrite(transformed_img_path, transformed_img)
    transform_preview(transformed_img_path)

    print("scanned")


# Function to update the preview label with the given image path
def no_text_preview(image_path):
    image = Image.open(image_path)
    resized_image = image.resize((192, 251), resample=Image.LANCZOS)
    img = ImageTk.PhotoImage(resized_image)
    noTextPreview.config(image=img)
    noTextPreview.image = img

def gray_preview(image_path):
    image = Image.open(image_path)
    resized_image = image.resize((192, 251), resample=Image.LANCZOS)
    img = ImageTk.PhotoImage(resized_image)
    grayedPreview.config(image=img)
    grayedPreview.image = img

def blur_preview(image_path):
    image = Image.open(image_path)
    resized_image = image.resize((192, 251), resample=Image.LANCZOS)
    img = ImageTk.PhotoImage(resized_image)
    blurredPreview.config(image=img)
    blurredPreview.image = img

def edge_preview(image_path):
    image = Image.open(image_path)
    resized_image = image.resize((192, 251), resample=Image.LANCZOS)
    img = ImageTk.PhotoImage(resized_image)
    edgedPreview.config(image=img)
    edgedPreview.image = img

def contour_preview(image_path):
    image = Image.open(image_path)
    resized_image = image.resize((192, 251), resample=Image.LANCZOS)
    img = ImageTk.PhotoImage(resized_image)
    contouredPreview.config(image=img)
    contouredPreview.image = img

def transform_preview(image_path):
    image = Image.open(image_path)
    resized_image = image.resize((192, 251), resample=Image.LANCZOS)
    img = ImageTk.PhotoImage(resized_image)
    transformedPreview.config(image=img)
    transformedPreview.image = img



# Function to load the image inside the imageView widget
def load_image():
    original_image = cv2.imread(
        "/home/rpig3/docubase/env/bin/mainProg/test_img.jpg")

    directory = "/home/rpig3/docubase/env/bin/mainProg"
    output_path = os.path.join(directory, "scanned_image.jpg")

    height = 500
    width = int(original_image.shape[1] * (height / original_image.shape[0]))
    resized_image = cv2.resize(original_image, (width, height))

    cv2.imwrite(output_path, resized_image)

    # Convert NumPy array to PIL Image
    pil_image = Image.fromarray(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB))

    # Convert the resized image to PhotoImage
    img = ImageTk.PhotoImage(pil_image)

    # Return the img
    return img


# Initialize the root widget
root = tk.Tk()
root.title("Document Form")

# Frame for the entire content
contentFrame = ttk.Frame(root, padding=(10, 10, 10, 10))
contentFrame.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))

imageFrame = ttk.LabelFrame(contentFrame, text="Camera Preview")
imageFrame.grid(column=0, row=0, padx=10, pady=10,
                sticky=(tk.N, tk.S, tk.E, tk.W))
imageView = ttk.Label(imageFrame)
imageView.grid(column=0, row=0, padx=10, pady=10,
               sticky=(tk.N, tk.S, tk.E, tk.W))

image = load_image()
imageView.configure(image=image)
imageView.image = image

# Convert Button
convertBFrame = ttk.Frame(imageFrame)
convertBFrame.grid(column=0, row=1, pady=(5, 10))
convertButton = ttk.Button(
    convertBFrame, text="Convert Image", width=button_width, command=convert_image)
convertButton.grid(column=0, row=0, columnspan=2, sticky=(tk.W, tk.E))

# Frame for right side contents (invisible)
rightFrame = ttk.Frame(contentFrame)
rightFrame.grid(column=1, row=0, padx=10, sticky=(tk.N, tk.S, tk.W, tk.E))

# Frame for image preview
previewFrame = ttk.LabelFrame(rightFrame, text="Image Preview")
previewFrame.grid(column=1, row=1, sticky=(tk.N, tk.S, tk.W, tk.E))

noTextPreview = ttk.Label(previewFrame)
noTextPreview.grid(column=0, row=0, padx=10, pady=10,
                  sticky=(tk.N, tk.S, tk.W, tk.E))
grayedPreview = ttk.Label(previewFrame)
grayedPreview.grid(column=1, row=0, padx=10, pady=10,
                  sticky=(tk.N, tk.S, tk.W, tk.E))
blurredPreview = ttk.Label(previewFrame)
blurredPreview.grid(column=2, row=0, padx=10, pady=10,
                  sticky=(tk.N, tk.S, tk.W, tk.E))
edgedPreview = ttk.Label(previewFrame)
edgedPreview.grid(column=0, row=1, padx=10, pady=10,
                  sticky=(tk.N, tk.S, tk.W, tk.E))
contouredPreview = ttk.Label(previewFrame)
contouredPreview.grid(column=1, row=1, padx=10, pady=10,
                  sticky=(tk.N, tk.S, tk.W, tk.E))
transformedPreview = ttk.Label(previewFrame)
transformedPreview.grid(column=2, row=1, padx=10, pady=10,
                  sticky=(tk.N, tk.S, tk.W, tk.E))

# Start the Tkinter main loop
root.mainloop()

# Release resources
cv2.destroyAllWindows()
camera.close()
