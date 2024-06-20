## This task is about Initial OCR Implementation: Write a basic OCR script to extract text from the check images using Transformer Model.

## HuggignFace Transformers Library: https://huggingface.co/microsoft/trocr-base-handwritten

import os
from PIL import Image
import requests
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

# Load the pre-trained processor and model from HuggingFace
processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-handwritten')
model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-handwritten')

# Define the input and output directories
input_dir = 'dataset'
output_dir = 'task5-transformers-output'

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Function to extract text from an image using TrOCR
def extract_text_from_image(image_path):
    image = Image.open(image_path).convert("RGB")
    pixel_values = processor(images=image, return_tensors="pt").pixel_values
    generated_ids = model.generate(pixel_values)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return generated_text

# Loop through all images in the dataset directory
for image_name in os.listdir(input_dir):
    if image_name.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        # Open the image using PIL
        image_path = os.path.join(input_dir, image_name)
        
        # Extract text from the image using TrOCR
        extracted_text = extract_text_from_image(image_path)
        
        # Define the output text file path
        text_file_name = os.path.splitext(image_name)[0] + '.txt'
        text_file_path = os.path.join(output_dir, text_file_name)
        
        # Write the extracted text to the output text file
        with open(text_file_path, 'w', encoding='utf-8') as text_file:
            text_file.write(extracted_text)
        
        print(f'Processed {image_name}, extracted text saved to {text_file_path}')