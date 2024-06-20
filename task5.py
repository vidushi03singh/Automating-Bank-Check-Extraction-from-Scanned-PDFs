## This task is about Initial OCR Implementation: Write a basic OCR script to extract text from the check images using Tesseract.

import os
import pytesseract
from PIL import Image

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # This is the path for tesseract executable file. You need to change this path according to your tesseract installation

# Define the input and output directories
input_dir = 'dataset'
output_dir = 'task5-output'

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Loop through all images in the dataset directory
for image_name in os.listdir(input_dir):
    if image_name.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        # Open the image using PIL
        image_path = os.path.join(input_dir, image_name)
        image = Image.open(image_path)
        
        # Use Tesseract to extract text from the image
        extracted_text = pytesseract.image_to_string(image)
        
        # Define the output text file path
        text_file_name = os.path.splitext(image_name)[0] + '.txt'
        text_file_path = os.path.join(output_dir, text_file_name)
        
        # Write the extracted text to the output text file
        with open(text_file_path, 'w', encoding='utf-8') as text_file:
            text_file.write(extracted_text)
        
        print(f'Processed {image_name}, extracted text saved to {text_file_path}')