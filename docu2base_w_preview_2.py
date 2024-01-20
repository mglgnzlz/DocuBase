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

def order_points(pts):
	# initialzie a list of coordinates that will be ordered
	# such that the first entry in the list is the top-left,
	# the second entry is the top-right, the third is the
	# bottom-right, and the fourth is the bottom-left
	rect = np.zeros((4, 2), dtype = "float32")
	# the top-left point will have the smallest sum, whereas
	# the bottom-right point will have the largest sum
	s = pts.sum(axis = 1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]
	# now, compute the difference between the points, the
	# top-right point will have the smallest difference,
	# whereas the bottom-left will have the largest difference
	diff = np.diff(pts, axis = 1)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]
	# return the ordered coordinates
	return rect

def four_point_transform(image, pts):
	# obtain a consistent order of the points and unpack them
	# individually
	rect = order_points(pts)
	(tl, tr, br, bl) = rect
	# compute the width of the new image, which will be the
	# maximum distance between bottom-right and bottom-left
	# x-coordiates or the top-right and top-left x-coordinates
	widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
	widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	maxWidth = max(int(widthA), int(widthB))
	# compute the height of the new image, which will be the
	# maximum distance between the top-right and bottom-right
	# y-coordinates or the top-left and bottom-left y-coordinates
	heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
	maxHeight = max(int(heightA), int(heightB))
	# now that we have the dimensions of the new image, construct
	# the set of destination points to obtain a "birds eye view",
	# (i.e. top-down view) of the image, again specifying points
	# in the top-left, top-right, bottom-right, and bottom-left
	# order
	dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")
	# compute the perspective transform matrix and then apply it
	M = cv2.getPerspectiveTransform(rect, dst)
	warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
	# return the warped image
	return warped


def scan_image(img):
    # Resize image to workable size
    ratio = img.shape[0]/500
    # Create a copy of resized original image for later use
    orig_img = img.copy()
    img = imutils.resize(img, height=500)

    no_text_img = removing_text(img)
    grayed_img = grayscaling(img)
    blurred_img = blurring(grayed_img)
    edged_img = edge_detection(blurred_img)
    contour_img, screenCnt = contours(edged_img, img)
    transformed_img = unwrapping(orig_img, screenCnt, ratio)

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
    blurred_img = cv2.GaussianBlur(grayed_img, (5, 5), 0)
    return blurred_img


def edge_detection(blurred_img):
    # Egde Detection
    edged_img = cv2.Canny(blurred_img, 75, 200)
    return edged_img


def contours(edged_img, img):
    contour_img = cv2.findContours(
        edged_img.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contour_img = imutils.grab_contours(contour_img)
    contour_img = sorted(contour_img, key=cv2.contourArea, reverse=True)[:5]

    for c in contour_img:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        # if our approximated contour has four points, then we
        # can assume that we have found our screen
        if len(approx) == 4:
            screenCnt = approx
            break

    contour_img = cv2.drawContours(img, [screenCnt], -1, (0, 255, 0), 2)

    return contour_img, screenCnt


def unwrapping(orig_img, screenCnt, ratio):
    # apply the four point transform to obtain a top-down
    # view of the original image
    warped = four_point_transform(orig_img, screenCnt.reshape(4, 2) * ratio)
    # convert the warped image to grayscale, then threshold it
    # to give it that 'black and white' paper effect
    warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    T = threshold_local(warped, 11, offset = 10, method = "gaussian")
    transformed_img = (warped > T).astype("uint8") * 255
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
        "/home/rpig3/docubase/env/bin/mainProg/original_image.jpg")

    no_text_img, grayed_img, blurred_img, edged_img, contour_img, transformed_img = scan_image(
        img)

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
        "/home/rpig3/docubase/env/bin/mainProg/original_image.jpg")

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

