
import cv2
import tkinter as tk
import os
import argparse
import numpy as np
import imutils
import pytesseract
from io import BytesIO
from tkinter import IntVar, ttk, filedialog
from PIL import Image, ImageTk
from skimage.filters import threshold_local

button_width = 15

myconfig = r"--psm 6 --oem 3"

whitelist = ["jeepney", "carbon", "greenhouse"]


def extract_text(img):
    height, width, _ = img.shape
    boxes = pytesseract.image_to_boxes(img)
    extracted = pytesseract.image_to_string(img)

    whitelisted_words = [word for word in extracted.split() if word.lower() in whitelist]

    # Join the whitelisted words to form the final text
    final_text = ' '.join(whitelisted_words)

    for box in boxes.splitlines():
        box = box.split(" ")
        img = cv2.rectangle(img, (int(
            box[1]), height - int(box[2])), (int(box[3]), height - int(box[4])), (0, 255, 0), 2)

    # Resize the image before displaying
    height = 616
    width = 820
    resized_image = cv2.resize(img, (width, height))

    # print(extracted.encode('utf-8').decode('latin-1'))
    print(final_text)

    cv2.imshow("img", resized_image)
    cv2.waitKey(0)


def extract_image():
    img = cv2.imread(
        "/home/rpig3/docubase/env/bin/mainProg/scan_fldr/v3t_image.jpg")
    angle = getSkewAngle(img)
    img = rotateImage(img, -1 * angle)
    v1 = extract_text(img)

    print("scanned")


def getSkewAngle(cvImage) -> float:
    # Prep image, copy, convert to gray scale, blur, and threshold
    newImage = cvImage.copy()
    gray = cv2.cvtColor(newImage, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9, 9), 0)
    thresh = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Apply dilate to merge text into meaningful lines/paragraphs.
    # Use larger kernel on X axis to merge characters into single line, cancelling out any spaces.
    # But use smaller kernel on Y axis to separate between different blocks of text
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
    dilate = cv2.dilate(thresh, kernel, iterations=2)

    # Find all contours
    contours, hierarchy = cv2.findContours(
        dilate, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    for c in contours:
        rect = cv2.boundingRect(c)
        x, y, w, h = rect
        cv2.rectangle(newImage, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # Find largest contour and surround in min area box
    largestContour = contours[0]
    print(len(contours))
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
    newImage = cv2.warpAffine(
        newImage, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return newImage

# Function to load the image inside the imageView widget


def load_image():
    original_image = cv2.imread(
        "/home/rpig3/docubase/env/bin/mainProg/scan_fldr/v3t_image.jpg")

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
    convertBFrame, text="Extract Image", width=button_width, command=extract_image)
convertButton.grid(column=0, row=0, columnspan=2, sticky=(tk.W, tk.E))

# Start the Tkinter main loop
root.mainloop()

# Release resources
cv2.destroyAllWindows()
camera.close()
