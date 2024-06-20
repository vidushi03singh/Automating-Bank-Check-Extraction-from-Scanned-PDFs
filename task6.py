## This task is about Data Parsing: Parse the OCR results to identify specific fields (e.g., payee, amount, name).

import os
import pytesseract
from PIL import Image
import re

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # This is the path for tesseract executable file. You need to change this path according to your tesseract installation

# Define the input and output directories
input_dir = 'dataset'
output_dir = 'task6-output'

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Function to parse the extracted text and identify specific fields
def parse_ocr_results(text):
    # Example regex patterns (adjust these according to the format of your checks)
    payee_pattern = re.compile(r'Pay(?:ee| to the order of):?\s*(.+)', re.IGNORECASE)
    amount_pattern = re.compile(r'Amount:\s*\$?([0-9,]+\.?[0-9]*)', re.IGNORECASE)
    name_pattern = re.compile(r'Name:\s*(.+)', re.IGNORECASE)

    payee = re.search(payee_pattern, text)
    amount = re.search(amount_pattern, text)
    name = re.search(name_pattern, text)

    return {
        'payee': payee.group(1) if payee else None,
        'amount': amount.group(1) if amount else None,
        'name': name.group(1) if name else None
    }

# Loop through all images in the dataset directory
for image_name in os.listdir(input_dir):
    if image_name.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        # Open the image using PIL
        image_path = os.path.join(input_dir, image_name)
        image = Image.open(image_path)
        
        # Use Tesseract to extract text from the image
        extracted_text = pytesseract.image_to_string(image)
        
        # Parse the extracted text to identify specific fields
        parsed_data = parse_ocr_results(extracted_text)
        
        # Define the output text file path
        text_file_name = os.path.splitext(image_name)[0] + '_parsed.txt'
        text_file_path = os.path.join(output_dir, text_file_name)
        
        # Write the parsed data to the output text file
        with open(text_file_path, 'w', encoding='utf-8') as text_file:
            for field, value in parsed_data.items():
                text_file.write(f'{field.capitalize()}: {value}\n')
        
        print(f'Processed {image_name}, parsed data saved to {text_file_path}')