## This task is about the Check Image Extraction: Implement the module to extract and save individual check images using OpenCV.

import fitz
import os
import cv2
import numpy as np

def extract_images_from_pdf(pdf_path, output_folder):
    """
    Extracts images from a PDF and saves them to the specified output folder using OpenCV.
    
    Args:
        pdf_path (str): The path to the PDF file.
        output_folder (str): The folder where the extracted images will be saved.
    """
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    document = fitz.open(pdf_path)
    
    image_counter = 1
    for page_number in range(len(document)):
        page = document.load_page(page_number)
        image_list = page.get_images(full=True)
        
        for image_index, img in enumerate(image_list):
            xref = img[0]
            base_image = document.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            # Convert image bytes to a numpy array
            image_np = np.frombuffer(image_bytes, np.uint8)
            # Decode the numpy array to an image
            image_cv = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
            
            # Define the output image path
            image_filename = os.path.join(output_folder, f'cheque_{image_counter}.{image_ext}')
            
            # Save the image using OpenCV
            cv2.imwrite(image_filename, image_cv)
            image_counter += 1
    
    print(f"Extracted images from {len(document)} pages in {pdf_path}")

if __name__ == "__main__":
    pdf_path = 'cheque.pdf'
    output_folder = 'task4-output'
    extract_images_from_pdf(pdf_path, output_folder)