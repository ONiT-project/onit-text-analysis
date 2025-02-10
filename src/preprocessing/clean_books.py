"""
This script cleans the OCR files, so that we have uniform documents with the same pre-processing applied to each of
them. For every book, a new document is created so that the original file is always available for cross-checking etc.

Code adapted from Travelogues project, by Jan Rörden. Source: https://github.com/travelogues/scripts/blob/master/groundtruth/

"""

import os
import re
import string
import unicodedata
from tqdm import tqdm


# directories
books_original_dir = 'source/path/'
output_dir = 'output/path/'

# Ensure the cleaned directory exists
os.makedirs(output_dir, exist_ok=True)

# Function to remove accents and umlauts
def remove_accents(input_str):
    # Normalize to decompose accents
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    # Filter out diacritical marks
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

for fname in tqdm(sorted(os.listdir(books_original_dir))):
    # Save the current id for file naming later
    current_book_id = fname[:-4]

    # Process only .txt files
    if fname.endswith('.txt'):
        with open(os.path.join(books_original_dir, fname), 'r', encoding='utf-8') as f:
            cleaned_lines = []
            page_lines = []

            for line in f:
                # Replace long s and ß with normal s
                clean_line = re.sub(r'[ſß]', 's', line)

                # Remove accents and umlauts
                clean_line = remove_accents(clean_line)

                # Remove all non-word characters except whitespace and punctuation
                clean_line = re.sub(r'[^a-zA-Z0-9\s' + re.escape(string.punctuation) + ']', '', clean_line)

                # Convert to lowercase
                #clean_line = clean_line.lower()

                # Strip trailing spaces but keep line breaks
                clean_line = clean_line.rstrip()

                # Exclude lines based on criteria
                if len(clean_line) < 3 or clean_line.isdigit() or not re.search(r'[a-zA-Z]', clean_line):
                    continue  # Skip the line

                # Check for a new page indicated by a blank line
                if clean_line == "":
                    # Handle empty pages
                    if not page_lines or page_lines[0].startswith('statuscode') or page_lines[0].startswith('<html>'):
                        cleaned_lines.append("<empty page>")
                    else:
                        cleaned_lines.extend(page_lines)
                    page_lines = []
                else:
                    page_lines.append(clean_line)

            # Handle the last page if the file ends without a blank line
            if not page_lines or page_lines[0].startswith('statuscode') or page_lines[0].startswith('<html>'):
                cleaned_lines.append("<empty page>")
            else:
                cleaned_lines.extend(page_lines)

        # Save the cleaned text to a new file, retaining line breaks
        cleaned_file_path = os.path.join(output_dir, f"{current_book_id}_cleaned.txt")
        with open(cleaned_file_path, 'w', encoding='utf-8') as cleaned_file:
            cleaned_file.write('\n'.join(cleaned_lines))  # Write lines with original line breaks