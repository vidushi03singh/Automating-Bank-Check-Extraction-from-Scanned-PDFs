import os
import io
import pdfplumber
from PIL import Image
import cv2
import re
import sqlite3
import csv
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

# Step 1: Parse PDF to extract images
def parse_pdf(file_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    with pdfplumber.open(file_path) as pdf:
        for page_number, page in enumerate(pdf.pages):
            image_regions = page.images
            if not image_regions:
                continue
            
            for img_index, image in enumerate(image_regions):
                if 'stream' in image:
                    base_image = image['stream']
                    image_bytes = base_image.get_data()
                    
                    # Open the image stream with Pillow
                    image_pil = Image.open(io.BytesIO(image_bytes))
                    image_path = os.path.join(output_folder, f"page_{page_number + 1}_image_{img_index + 1}.png")
                    image_pil.save(image_path)

# Step 2: Extract checks from images and resize them
def extract_checks(input_folder, output_folder, fixed_width, fixed_height):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for image_file in os.listdir(input_folder):
        image_path = os.path.join(input_folder, image_file)
        if image_file.lower().endswith(('png', 'jpg', 'jpeg')):
            try:
                image_pil = Image.open(image_path)
                resized_image = image_pil.resize((fixed_width, fixed_height), Image.Resampling.LANCZOS)
                output_image_path = os.path.join(output_folder, image_file)
                resized_image.save(output_image_path)
            except Exception as e:
                print(f"Error processing image {image_file}: {e}")

# Step 3: Extract regions of interest from check images
def extract_interest_regions(base_image_directory, regions_of_interest, regions_output_directory):
    if not os.path.exists(regions_output_directory):
        os.makedirs(regions_output_directory)
    
    for image_file in os.listdir(base_image_directory):
        image_path = os.path.join(base_image_directory, image_file)
        if image_file.lower().endswith(('png', 'jpg', 'jpeg')):
            image = cv2.imread(image_path)
            if image is not None:
                image_name = os.path.splitext(image_file)[0]
                output_page_dir = os.path.join(regions_output_directory, image_name)
                os.makedirs(output_page_dir, exist_ok=True)
                
                for field, (x0, y0, x1, y1) in regions_of_interest.items():
                    region_of_interest = image[y0:y1, x0:x1]
                    output_image_path = os.path.join(output_page_dir, f"{field}_region.png")
                    cv2.imwrite(output_image_path, region_of_interest)
                    print(f"Saved {field} region for {image_file} at {output_image_path}")

# Step 4: Extract text from cropped images using TrOCR
processor = TrOCRProcessor.from_pretrained('microsoft/trocr-large-stage1')
model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-large-stage1')

def validate_text(field, text):
    """Validates the extracted text based on the field type."""
    if field == 'date':
        # Normalize and validate date format
        text = re.sub(r'\s+', '', text)
        if re.match(r'\d{8}', text):
            return f"{text[:2]}/{text[2:4]}/{text[4:]}"
        elif re.match(r'\d{2}\d{2}\d{4}', text):
            return f"{text[:2]}/{text[2:4]}/{text[4:]}"
    elif field == 'payee' or field == 'name':
        # Accept and normalize any alphabetical text
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    elif field == 'amount_digits':
        # Normalize and validate amount format
        text = re.sub(r'[^\d,/-]', '', text)
        if re.match(r'[\d,]+/-', text):
            return text.replace(' ', '')
    elif field == 'account_number':
        # Normalize and validate account number
        text = re.sub(r'\s+', '', text)
        if re.match(r'[\d.]+', text):
            return text.replace(' ', '')
    return text

def extract_text_from_image(image_path):
    """Extracts text from a given image using the TrOCR model."""
    image = Image.open(image_path).convert("RGB")
    pixel_values = processor(image, return_tensors="pt").pixel_values  # Batch size 1
    generated_ids = model.generate(pixel_values)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return generated_text

def process_all_folders(base_dir):
    """Processes all image folders sequentially and extracts text from each image."""
    extracted_data = {}
    sorted_folders = sorted(os.listdir(base_dir), key=lambda x: int(re.search(r'\d+', x).group()))
    for page_folder in sorted_folders:
        page_folder_path = os.path.join(base_dir, page_folder)
        if os.path.isdir(page_folder_path):
            print(f"Processing folder: {page_folder}")
            extracted_data[page_folder] = {}
            for image_file in os.listdir(page_folder_path):
                image_path = os.path.join(page_folder_path, image_file)
                if image_file.lower().endswith(('png', 'jpg', 'jpeg')):
                    extracted_text = extract_text_from_image(image_path)
                    field_name = os.path.splitext(image_file)[0]
                    validated_text = validate_text(field_name, extracted_text)
                    extracted_data[page_folder][field_name] = validated_text
                    print(f"Text extracted for {field_name}: {validated_text}")
    return extracted_data

# Step 5: Initialize SQLite database
def initialize_database(database_path):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS checks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT,
                        payee TEXT,
                        name TEXT,
                        amount_digits TEXT,
                        account_number TEXT
                      )''')
    conn.commit()
    conn.close()

# Step 6: Store results in database
def store_results_in_db(results, database_path):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    
    # Map the keys from the extracted data to the database column names
    db_results = {
        'date': results.get('date_region', ''),
        'payee': results.get('payee_region', ''),
        'name': results.get('name_region', ''),
        'amount_digits': results.get('amount_digits_region', ''),
        'account_number': results.get('account_number_region', '')
    }

    # Adding print statements to debug
    print(f"Storing results: {db_results}")

    cursor.execute('''INSERT INTO checks (date, payee, name, amount_digits, account_number)
                      VALUES (?, ?, ?, ?, ?)''', 
                   (db_results['date'],
                    db_results['payee'],
                    db_results['name'],
                    db_results['amount_digits'],
                    db_results['account_number']))
    conn.commit()
    conn.close()

# Step 7: Search functionality
def search_checks(database_path, search_params):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    
    query = "SELECT * FROM checks WHERE "
    conditions = []
    values = []
    
    for field, value in search_params.items():
        conditions.append(f"{field} LIKE ?")
        values.append(f"%{value}%")
    
    query += " AND ".join(conditions)
    
    cursor.execute(query, values)
    rows = cursor.fetchall()
    conn.close()
    return rows

# Step 8: Update functionality
def update_check(database_path, check_id, update_fields):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    
    update_query = "UPDATE checks SET "
    update_values = []
    
    for field, value in update_fields.items():
        update_query += f"{field} = ?, "
        update_values.append(value)
    
    update_query = update_query.rstrip(", ")
    update_query += " WHERE id = ?"
    update_values.append(check_id)
    
    cursor.execute(update_query, update_values)
    conn.commit()
    conn.close()

# Step 9: Delete functionality
def delete_check(database_path, check_id):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM checks WHERE id = ?", (check_id,))
    conn.commit()
    conn.close()

# Step 10: Export functionality
def export_to_csv(database_path, csv_file_path):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM checks")
    rows = cursor.fetchall()
    
    headers = [description[0] for description in cursor.description]
    
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(headers)
        csvwriter.writerows(rows)
    
    conn.close()

# Step 11: Summary statistics
def get_summary_statistics(database_path):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*), SUM(CAST(REPLACE(amount_digits, ',', '') AS INTEGER)) FROM checks")
    count, total_amount = cursor.fetchone()
    
    conn.close()
    return {'total_checks': count, 'total_amount': total_amount}