## This task is about the Basic PDF Parsing: Implement the module to extract text and images from a PDF file using PyMuPDF and PIL.


import os
import fitz  # PyMuPDF
from PIL import Image
import io

def parse_pdf(file_path):
    """
    Parses the PDF file to extract text and images, saving them into a specified output directory.

    Args:
        file_path (str): The path to the PDF file to be parsed.

    Returns:
        None
    """

    # Create output directory
    output_dir = "task2-output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_text = ""

    # Open the PDF file
    pdf_document = fitz.open(file_path)
    page_count = pdf_document.page_count
    output_text += f"Total pages: {page_count}\n"

    # Loop through each page in the PDF
    for page_num in range(page_count):
        page = pdf_document.load_page(page_num)
        output_text += f"\nProcessing page: {page_num + 1}\n"

        # Extract text from the page
        text = page.get_text()
        output_text += "Text found on page:\n"
        output_text += text + "\n"

        # Extract images from the page
        image_list = page.get_images(full=True)
        output_text += f"Found {len(image_list)} images on page\n"

        # Loop through each image in the page
        for img_index, img in enumerate(image_list, start=1):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]

            # Convert to PIL Image and save
            image = Image.open(io.BytesIO(image_bytes))
            image_filename = os.path.join(output_dir, f"page_{page_num + 1}_image_{img_index}.png")
            image.save(image_filename)
            output_text += f"Saved image: {image_filename}\n"

    pdf_document.close()

    # Save the extracted text to a file
    output_text_filename = os.path.join(output_dir, "basic-pdf-parsing-output.txt")
    with open(output_text_filename, "w") as output_file:
        output_file.write(output_text)

# Path to the PDF file
file_path = 'Python.pdf'
parse_pdf(file_path)