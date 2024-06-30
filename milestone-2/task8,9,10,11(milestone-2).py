import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
import sqlite3
from PIL import Image, ImageTk

from transformers import TrOCRProcessor, VisionEncoderDecoderModel

# Import your backend functions
from backend import (
    parse_pdf,
    extract_checks,
    extract_interest_regions,
    process_all_folders,
    initialize_database,
    store_results_in_db,
    search_checks,
    update_check,
    delete_check,
    export_to_csv,
    get_summary_statistics
)

# Define the regions of interest for the checks
regions_of_interest = {
    'date': (754, 40, 970, 88),
    'payee': (70, 120, 760, 175),
    'name': (825, 440, 990, 475),
    'amount_digits': (735, 225, 970, 290),
    'account_number': (115, 300, 320, 335)
}

class CheckProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bank Check Processor")
        self.database_path = "checks.db"
        self.extracted_images_folder = "extracted_images"
        self.resized_checks_folder = "resized_images"
        self.cropped_images_folder = "cropped_images"
        self.csv_file_path = "checks_export.csv"

        self.create_widgets()
        initialize_database(self.database_path)

    def create_widgets(self):
        self.frame = ttk.Frame(self.root, padding="10 10 10 10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.pdf_label = ttk.Label(self.frame, text="Select PDF File:")
        self.pdf_label.grid(row=0, column=0, sticky=tk.W)
        
        self.pdf_entry = ttk.Entry(self.frame, width=50)
        self.pdf_entry.grid(row=0, column=1, sticky=tk.W)
        
        self.browse_button = ttk.Button(self.frame, text="Browse", command=self.browse_pdf)
        self.browse_button.grid(row=0, column=2, sticky=tk.W)

        self.process_button = ttk.Button(self.frame, text="Process PDF", command=self.process_pdf)
        self.process_button.grid(row=1, column=1, sticky=tk.W)
        
        self.results_tree = ttk.Treeview(self.frame, columns=("ID", "Date", "Payee", "Name", "Amount", "Account Number"), show="headings")
        self.results_tree.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        for col in self.results_tree["columns"]:
            self.results_tree.heading(col, text=col)
        
        self.search_label = ttk.Label(self.frame, text="Search Payee:")
        self.search_label.grid(row=3, column=0, sticky=tk.W)
        
        self.search_entry = ttk.Entry(self.frame, width=50)
        self.search_entry.grid(row=3, column=1, sticky=tk.W)
        
        self.search_button = ttk.Button(self.frame, text="Search", command=self.search_checks)
        self.search_button.grid(row=3, column=2, sticky=tk.W)
        
        self.update_button = ttk.Button(self.frame, text="Update", command=self.update_check)
        self.update_button.grid(row=4, column=1, sticky=tk.W)
        
        self.delete_button = ttk.Button(self.frame, text="Delete", command=self.delete_check)
        self.delete_button.grid(row=4, column=2, sticky=tk.W)
        
        self.export_button = ttk.Button(self.frame, text="Export to CSV", command=self.export_to_csv)
        self.export_button.grid(row=5, column=1, sticky=tk.W)
        
        self.summary_button = ttk.Button(self.frame, text="Summary Statistics", command=self.show_summary_statistics)
        self.summary_button.grid(row=5, column=2, sticky=tk.W)
        
    def browse_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.pdf_entry.delete(0, tk.END)
            self.pdf_entry.insert(0, file_path)

    def process_pdf(self):
        pdf_file_path = self.pdf_entry.get()
        if not os.path.exists(pdf_file_path):
            messagebox.showerror("Error", "PDF file not found!")
            return
        
        parse_pdf(pdf_file_path, self.extracted_images_folder)
        extract_checks(self.extracted_images_folder, self.resized_checks_folder, 1000, 600)
        extract_interest_regions(self.resized_checks_folder, regions_of_interest, self.cropped_images_folder)
        extracted_data = process_all_folders(self.cropped_images_folder)
        
        for page, fields in extracted_data.items():
            store_results_in_db(fields, self.database_path)
        
        messagebox.showinfo("Success", "PDF processed successfully!")

    def search_checks(self):
        search_term = self.search_entry.get()
        search_params = {'payee': search_term}
        results = search_checks(self.database_path, search_params)
        
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        for row in results:
            self.results_tree.insert("", "end", values=row)
    
    def update_check(self):
        selected_item = self.results_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No check selected!")
            return
        
        check_id = self.results_tree.item(selected_item, "values")[0]
        new_payee = simpledialog.askstring("Update Payee", "Enter new payee name:")
        if new_payee:
            update_fields = {'payee': new_payee}
            update_check(self.database_path, check_id, update_fields)
            self.search_checks()
    
    def delete_check(self):
        selected_item = self.results_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No check selected!")
            return
        
        check_id = self.results_tree.item(selected_item, "values")[0]
        delete_check(self.database_path, check_id)
        self.search_checks()

    def export_to_csv(self):
        export_to_csv(self.database_path, self.csv_file_path)
        messagebox.showinfo("Success", "Data exported to CSV successfully!")

    def show_summary_statistics(self):
        summary_stats = get_summary_statistics(self.database_path)
        messagebox.showinfo("Summary Statistics", f"Total Checks: {summary_stats['total_checks']}\nTotal Amount: {summary_stats['total_amount']}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CheckProcessorApp(root)
    root.mainloop()