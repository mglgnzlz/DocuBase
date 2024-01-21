import cv2
import numpy as np


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


# Image Preprocessing Function
def preprocessing(image):
    # Scan for resize
    dim_limit = 3280
    max_dim = max(image.shape)
    if max_dim > dim_limit:
        resize_scale = dim_limit / max_dim
        image = cv2.resize(image, None, fx=resize_scale, fy=resize_scale)

    # Create a copy of resized original image for later use
    orig_image = image.copy()

    # Removing text from the document
    kernel = np.ones((7, 7), np.uint8)
    no_text_image = cv2.morphologyEx(
        image, cv2.MORPH_CLOSE, kernel, iterations=5)

    # Apply grayscaling
    grayed_image = cv2.cvtColor(no_text_image, cv2.COLOR_BGR2GRAY)

    # Apply blur
    blurred_image = cv2.GaussianBlur(grayed_image, (15, 15), 0)

    # Apply egde detection & dilation
    edged_image = cv2.Canny(blurred_image, 0, 200)
    edged_image = cv2.dilate(
        edged_image, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21)))

    # Finding contours for the detected edges.
    con = np.zeros_like(no_text_image)
    contours, hierarchy = cv2.findContours(
        edged_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Keeping only the largest detected contour.
        page = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
        contour_image = cv2.drawContours(con, page, -1, (0, 255, 255), 3)
        corners, destination_corners = find_corners(con, page)

        h, w = orig_image.shape[:2]
        # Getting the homography.
        homography, mask = cv2.findHomography(np.float32(corners), np.float32(destination_corners), method=cv2.RANSAC,
                                              ransacReprojThreshold=3.0)
        # Perspective transform using homography.
        un_warped = cv2.warpPerspective(orig_image, np.float32(
            homography), (w, h), flags=cv2.INTER_LINEAR)
        # Crop
        transformed_image = un_warped[:destination_corners[2]
                                      [1], :destination_corners[2][0]]
        return transformed_image

    else:
        return image


def find_corners(con, page):
    # Detecting Edges through Contour approximation
    if len(page) == 0:
        return orig_image, None
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


def unwrapping(orig_image, corners, destination_corners):
    h, w = orig_image.shape[:2]
    # Getting the homography.
    homography, mask = cv2.findHomography(np.float32(corners), np.float32(destination_corners), method=cv2.RANSAC,
                                          ransacReprojThreshold=3.0)
    # Perspective transform using homography.
    un_warped = cv2.warpPerspective(orig_image, np.float32(
        homography), (w, h), flags=cv2.INTER_LINEAR)
    # Crop
    transformed_image = un_warped[:destination_corners[2]
                                  [1], :destination_corners[2][0]]
    return transformed_image
