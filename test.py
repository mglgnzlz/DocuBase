import cv2
import tkinter as tk
import os
import numpy as np
import imutils
from io import BytesIO
from tkinter import IntVar, ttk, filedialog
from PIL import Image, ImageTk
from skimage.filters import threshold_local

button_width = 15


def scan_image(img):
    # Create a copy of resized original image for later use
    orig_img = img.copy()
    # img = imutils.resize(img, height=2462)

    # 1st step: Inverting the image
    inverted_image = cv2.bitwise_not(img)

    # 2nd step: Grayscaling
    grayed_image = cv2.cvtColor(inverted_image, cv2.COLOR_BGR2GRAY)

    # 3rd step: Thresholding
    threshold_image = cv2.adaptiveThreshold(
        grayed_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 41, 11)
    # threshold_image = cv2.threshold(grayed_image, 0, 255, cv2.THRESH_BINARY)
    # T = threshold_local(grayed_image, 11, offset=10, method="gaussian")
    # threshold_image = (grayed_image > T).astype("uint8") * 255

    # 4th step: Noise Removal
    kernel = np.ones((1, 1), np.uint8)
    image = cv2.dilate(threshold_image, kernel, iterations=1)
    image = cv2.erode(image, kernel, iterations=1)
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    noise_removed_image = cv2.medianBlur(image, 3)
    
    # 5th step: Dilation (thicking the font) and Erosion (thinning the font) - No necessary
    # 6th step: Deskewing
    # 7th step: Removing borders
    contours, hierarchy = cv2.findContours(noise_removed_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cntsSorted = sorted(contours, key=lambda x: cv2.contourArea(x))
    cnt = cntsSorted[-1]
    x, y, w, h = cv2.boundingRect(cnt)
    cropped_image = image[y:y+h, x:x+w]


    return inverted_image, grayed_image, threshold_image, noise_removed_image, cropped_image


def getSkewAngle(cvImage) -> float:
    # Prep image, copy, convert to gray scale, blur, and threshold
    newImage = cvImage.copy()
    gray = cv2.cvtColor(newImage, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9, 9), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Apply dilate to merge text into meaningful lines/paragraphs.
    # Use larger kernel on X axis to merge characters into single line, cancelling out any spaces.
    # But use smaller kernel on Y axis to separate between different blocks of text
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
    dilate = cv2.dilate(thresh, kernel, iterations=2)

    # Find all contours
    contours, hierarchy = cv2.findContours(dilate, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key = cv2.contourArea, reverse = True)
    for c in contours:
        rect = cv2.boundingRect(c)
        x,y,w,h = rect
        cv2.rectangle(newImage,(x,y),(x+w,y+h),(0,255,0),2)

    # Find largest contour and surround in min area box
    largestContour = contours[0]
    print (len(contours))
    minAreaRect = cv2.minAreaRect(largestContour)
    cv2.imwrite("temp/boxes.jpg", newImage)
    # Determine the angle. Convert it to the value that was originally used to obtain skewed image
    angle = minAreaRect[-1]
    if angle < -45:
        angle = 90 + angle
    return -1.0 * angle

# Rotate the image around its center
def rotateImage(cvImage, angle: float):
    newImage = cvImage.copy()
    (h, w) = newImage.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    newImage = cv2.warpAffine(newImage, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return newImage

def convert_image():
    directory = "/home/rpig3/docubase/env/bin/mainProg"
    aligned_img_path = os.path.join(directory, "aligned_img.jpg")
    inverted_img_path = os.path.join(directory, "inverted_img.jpg")
    grayed_img_path = os.path.join(directory, "grayed_img.jpg")
    threshold_img_path = os.path.join(directory, "threshold_img.jpg")
    noise_removed_img_path = os.path.join(directory, "noise_removed_img.jpg")
    cropped_img_path = os.path.join(directory, "cropped_img.jpg")
    img = cv2.imread(
        "/home/rpig3/docubase/env/bin/mainProg/test_img.jpg")

    # Aligned the image
    angle = getSkewAngle(img)
    aligned_image = rotateImage(img, -1 * angle)
    cv2.imwrite(aligned_img_path, aligned_image)

    new = cv2.imread("/home/rpig3/docubase/env/bin/mainProg/aligned_img.jpg")
    inverted_img, grayed_img, threshold_img, noise_removed_img, cropped_img = scan_image(new)

    cv2.imwrite(inverted_img_path, inverted_img)
    first_preview(inverted_img_path)
    cv2.imwrite(grayed_img_path, grayed_img)
    second_preview(grayed_img_path)
    cv2.imwrite(threshold_img_path, threshold_img)
    third_preview(threshold_img_path)
    cv2.imwrite(noise_removed_img_path, noise_removed_img)
    fourth_preview(noise_removed_img_path)
    cv2.imwrite(cropped_img_path, cropped_img)
    fifth_preview(cropped_img_path)

    print("scanned")


# Function to update the preview label with the given image path
def first_preview(image_path):
    image = Image.open(image_path)
    resized_image = image.resize((192, 251), resample=Image.LANCZOS)
    img = ImageTk.PhotoImage(resized_image)
    invertedPreview.config(image=img)
    invertedPreview.image = img


def second_preview(image_path):
    image = Image.open(image_path)
    resized_image = image.resize((192, 251), resample=Image.LANCZOS)
    img = ImageTk.PhotoImage(resized_image)
    grayedPreview.config(image=img)
    grayedPreview.image = img


def third_preview(image_path):
    image = Image.open(image_path)
    resized_image = image.resize((192, 251), resample=Image.LANCZOS)
    img = ImageTk.PhotoImage(resized_image)
    thresholdPreview.config(image=img)
    thresholdPreview.image = img


def fourth_preview(image_path):
    image = Image.open(image_path)
    resized_image = image.resize((192, 251), resample=Image.LANCZOS)
    img = ImageTk.PhotoImage(resized_image)
    noiseRemovedPreview.config(image=img)
    noiseRemovedPreview.image = img


def fifth_preview(image_path):
    image = Image.open(image_path)
    resized_image = image.resize((192, 251), resample=Image.LANCZOS)
    img = ImageTk.PhotoImage(resized_image)
    croppedPreview.config(image=img)
    croppedPreview.image = img


# Function to load the image inside the imageView widget
def load_image():
    original_image = cv2.imread(
        "/home/rpig3/docubase/env/bin/mainProg/test_img.jpg")

    directory = "/home/rpig3/docubase/env/bin/mainProg"
    output_path = os.path.join(directory, "scanned_image.jpg")

    height = 616
    width = 820
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

invertedPreview = ttk.Label(previewFrame)
invertedPreview.grid(column=0, row=0, padx=10, pady=10,
                     sticky=(tk.N, tk.S, tk.W, tk.E))
grayedPreview = ttk.Label(previewFrame)
grayedPreview.grid(column=1, row=0, padx=10, pady=10,
                   sticky=(tk.N, tk.S, tk.W, tk.E))
thresholdPreview = ttk.Label(previewFrame)
thresholdPreview.grid(column=2, row=0, padx=10, pady=10,
                      sticky=(tk.N, tk.S, tk.W, tk.E))
noiseRemovedPreview = ttk.Label(previewFrame)
noiseRemovedPreview.grid(column=0, row=1, padx=10, pady=10,
                      sticky=(tk.N, tk.S, tk.W, tk.E))
croppedPreview = ttk.Label(previewFrame)
croppedPreview.grid(column=1, row=1, padx=10, pady=10,
                      sticky=(tk.N, tk.S, tk.W, tk.E))

# Start the Tkinter main loop
root.mainloop()

# Release resources
cv2.destroyAllWindows()
camera.close()
