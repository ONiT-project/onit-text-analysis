"""
This script creates a CSV with all data to be indexed on the Marqo server.

Code by Michela Vignoli. Parts of this code were developed with assistance from GPT-4 and GPT-3 (free version).
"""

import os
import csv
import chardet
from tqdm import tqdm

# Helper function to get all file paths with a specific extension in a folder
def collect_files(folder, extension=".txt"):
    file_paths = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(extension):
                file_paths.append(os.path.join(root, file))
    return file_paths

# Function to process files and extract their text
def process_file(file_path):
    try:
        # Detect encoding
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
            encoding = result['encoding']

        # Read the file
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

# Combine data from clean, orig, and prep folders
def combine_data(clean_files, orig_files, prep_files):
    combined_data = []

    # Index files by (barcode, page) for matching
    def index_files(files):
        indexed = {}
        for file in files:
            barcode = os.path.basename(os.path.dirname(file))[:10]
            page = os.path.basename(file)[:5]
            indexed[(barcode, page)] = file
        return indexed

    clean_index = index_files(clean_files)
    orig_index = index_files(orig_files)
    prep_index = index_files(prep_files)

    # Process files and combine data
    for key in tqdm(clean_index.keys(), desc="Combining data", unit="file"):
        clean_file = clean_index.get(key)
        orig_file = orig_index.get(key)
        prep_file = prep_index.get(key)

        # Extract text
        text_clean = process_file(clean_file) if clean_file else None
        text_orig = process_file(orig_file) if orig_file else None
        text_prep = process_file(prep_file) if prep_file else None

        # Add combined data row
        barcode, page = key
        page_url = page[:5].zfill(8)
        iiif_link = f"https://iiif.onb.ac.at/images/ABO/{barcode}/{page_url}/full/full/0/native.jpg"

        combined_data.append({
            "barcode": barcode,
            "page": page,
            "iiif_link": iiif_link,
            "text_clean": text_clean,
            "text_orig": text_orig,
            "text_prep": text_prep,
        })

    return combined_data

# Lists of folders to process
clean_folders = [
    'source/path/DHd 2025 dataset/Sonnini Z166069305/Z166069305_clean/',
]
orig_folders = [
    "source/path/02-texts/D19/Z166069305",
]
prep_folders = [
    'source/path/DHd 2025 dataset/Sonnini Z166069305/Z166069305_clean_preprocessed/',
]

# Collect file paths
clean_files = [file for folder in clean_folders for file in collect_files(folder)]
orig_files = [file for folder in orig_folders for file in collect_files(folder)]
prep_files = [file for folder in prep_folders for file in collect_files(folder)]

# Combine data from all folders
all_data = combine_data(clean_files, orig_files, prep_files)

# Specify the file path and create the directory if it does not exist
csv_file = 'output/path/DHd_index.csv'
os.makedirs(os.path.dirname(csv_file), exist_ok=True)

# Write data to CSV file
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=["barcode", "page", "iiif_link", "text_clean", "text_orig", "text_prep"])
    writer.writeheader()
    writer.writerows(all_data)

#### IMPORTANT ####
#### Data Cleaning Needed after storing the file ####

"""
# Clean data
# Specify columns to check and update
columns_to_check = ["text_clean", "text_prep"]

# Check for rows where any of the columns contain "status code" or "empty page"
rows_to_update = index_DHd[columns_to_check].applymap(lambda x: any(keyword in str(x) for keyword in ["status code", "empty page"])).any(axis=1)

# Replace content in the specified columns for the identified rows
index_DHd.loc[rows_to_update, columns_to_check] = "<empty page>

# Remove artifacts from the LLM generation process
index_DHd['text_prep'] = index_DHd['text_prep'].str.strip("Here is the corrected text:")

""""

print(f"Data from all folders has been written to {csv_file}")