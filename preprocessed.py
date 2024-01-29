import cv2
import imutils
import numpy as np
import pytesseract
from skimage.filters import threshold_local

# Whitelisted texts
date_whitelist = ["january", "febuary", "march", "april", "may", "june", "july", "august", "september", "october",
                  "november", "december", "21", "1,", "2,", "3,", "4,", "5,", "6,", "7,", "8,", "9,", "10,", "11,", "12,", "13,", "14,", "15,", "16,", "17,", "18,", "19," "20,", "21,", "22,", "23,", "24,", "25,", "26,", "27,", "28,", "29,", "30,", "31,", "2024"]
docu_whitelist = ["memorandum", "official", "receipt"]


def boundingBox(iamge):
    # Create a bounding box
    return


def preprocessing(image):

    # Direct transpose and flip the image
    rotated_image = cv2.transpose(image)
    rotated_image = cv2.flip(rotated_image, 1)

    # Grayscaling and Adaptive Thresholding combined
    grayed_thresholded = cv2.adaptiveThreshold(
        cv2.cvtColor(rotated_image, cv2.COLOR_BGR2GRAY),
        255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 41, 11
    )
    # Sharpening
    kernel = np.array([[-1, -1, -1], [-1, 9, -1],
                      [-1, -1, -1]], dtype=np.float32)
    sharpened_image = cv2.filter2D(grayed_thresholded, -1, kernel)

    return sharpened_image


def deskewing(image):
    angle = getSkewAngle(image)
    aligned_image = rotateImage(image, -1 * angle)
    aligned_image = aligned_image.copy()
    return image


def tesseract(image):
    # OCR process
    extract_text = pytesseract.image_to_string(image)

    # Process of whitelisting
    datelisted = [
        word for word in extract_text.split() if word.lower() in date_whitelist]
    doculisted = [
        word for word in extract_text.split() if word.lower() in docu_whitelist]

    # Join the whitelisted words to form the final text
    combined_list = datelisted + doculisted
    final_text = ' '.join(combined_list)

    with open("text_file.txt", "w+", encoding="utf-8") as f:
        f.write(final_text)

    return combined_list


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
    # print(len(contours))
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
