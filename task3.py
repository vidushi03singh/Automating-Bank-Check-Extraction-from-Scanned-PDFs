## This task is about Advanced PDF Parsing: Refine the script to accurately identify check regions within the PDF pages.

import fitz  # PyMuPDF
from pathlib import Path
import cv2
import numpy as np


def extract_pdf_images(pdf_filepath: Path, output_folder: Path):
    output_folder.mkdir(parents=True, exist_ok=True)

    with fitz.open(pdf_filepath) as pdf_doc:
        for page_num, page in enumerate(pdf_doc, start=1):
            image_data_list = page.get_images(full=True)
            print(f"Page {page_num} has {len(image_data_list)} images.")

            for image_index, image_info in enumerate(image_data_list, start=1):
                xref = image_info[0]
                base_image = pdf_doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_extension = base_image["ext"]

                image_filename = f"page_{page_num}_img{image_index}.{image_extension}"
                output_image_path = output_folder / image_filename

                with open(output_image_path, "wb") as image_file:
                    image_file.write(image_bytes)

                print(f"Saved image: {output_image_path}")

                # Process the saved image to identify check regions
                identify_check_regions(output_image_path)


def identify_check_regions(image_path: Path):
    # Load the image
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"Failed to load image: {image_path}")
        return

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to the image
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Use Canny edge detection
    edged = cv2.Canny(blurred, 50, 150)

    # Find contours in the edged image
    contours, _ = cv2.findContours(
        edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    check_regions = []

    for contour in contours:
        # Get the bounding box for each contour
        x, y, w, h = cv2.boundingRect(contour)

        # Check if the contour is likely a check region based on some criteria
        if w > 100 and h > 50:  # Example criteria: width > 100 pixels and height > 50 pixels
            check_regions.append((x, y, w, h))
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    if check_regions:
        print(
            f"Identified {len(check_regions)} check region(s) in {image_path}")
    else:
        print(f"No check regions identified in {image_path}")

    # Save the processed image with detected regions
    processed_image_path = image_path.stem + "_processed" + image_path.suffix
    cv2.imwrite(str(image_path.parent / processed_image_path), image)
    print(
        f"Processed image saved as: {image_path.parent / processed_image_path}")


if __name__ == "__main__":
    pdf_path = Path("cheque.pdf")
    output_folder = Path("task3-output")
    extract_pdf_images(pdf_path, output_folder)