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
def browse_image_button():
    global img
    file_path = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select Image File",
                                           filetypes=(('JPG file', '*.jpg'), ('PNG file', '*.png'), ('All File', "*.*")))
    image = Image.open(file_path)
    image = image.resize((320, 540), resample=Image.LANCZOS)
    photo = ImageTk.PhotoImage(image)
    previewLabel.config(image=photo)
    previewLabel.image = photo
