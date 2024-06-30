import sqlite3
import csv
import pandas as pd
import json
from json2html import *
from fpdf import FPDF

def fetch_data_from_db(database_path):
    """Fetch all data from the database."""
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM checks")
    rows = cursor.fetchall()
    headers = [description[0] for description in cursor.description]
    conn.close()
    return headers, rows

def export_to_csv(database_path, file_path):
    headers, rows = fetch_data_from_db(database_path)
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(headers)
        csvwriter.writerows(rows)

def export_to_excel(database_path, file_path):
    headers, rows = fetch_data_from_db(database_path)
    df = pd.DataFrame(rows, columns=headers)
    df.to_excel(file_path, index=False, engine='xlsxwriter')

def export_to_json(database_path, file_path):
    headers, rows = fetch_data_from_db(database_path)
    data = [dict(zip(headers, row)) for row in rows]
    with open(file_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, ensure_ascii=False, indent=4)

def export_to_html(database_path, file_path):
    headers, rows = fetch_data_from_db(database_path)
    data = [dict(zip(headers, row)) for row in rows]
    html_data = json2html.convert(json=data)
    with open(file_path, 'w', encoding='utf-8') as htmlfile:
        htmlfile.write(html_data)

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Check Data', 0, 1, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(10)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

    def add_chapter(self, title, body):
        self.add_page()
        self.chapter_title(title)
        self.chapter_body(body)

def export_to_pdf(database_path, file_path):
    headers, rows = fetch_data_from_db(database_path)
    data = [dict(zip(headers, row)) for row in rows]
    
    pdf = PDF()
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    pdf.add_page()
    
    for record in data:
        body = '\n'.join([f'{key}: {value}' for key, value in record.items()])
        pdf.add_chapter('Check Details', body)
    
    pdf.output(file_path)

# Define paths and parameters
database_path = r"checks.db"
csv_file_path = r"checks_export.csv"
excel_file_path = r"checks_export.xlsx"
json_file_path = r"checks_export.json"
html_file_path = r"checks_export.html"
pdf_file_path = r"checks_export.pdf"

# Export data in various formats
export_to_csv(database_path, csv_file_path)
export_to_excel(database_path, excel_file_path)
export_to_json(database_path, json_file_path)
export_to_html(database_path, html_file_path)
export_to_pdf(database_path, pdf_file_path)