"""
This script matches the text annotations created on the original OCR files to the cleaned version of the text.
The annotations were created with Recogito https://recogito.pelagios.org/.

Code by Michela Vignoli. Parts of this code were developed with assistance from GPT-4 and GPT-3 (free version).
"""

## Import packages ##

import pandas as pd
import os
import re
from typing import Union


## Import annotations from Recogito ##

path_1 = "source/path/"
filename_1 = 'jiggvn0g5pgx34.csv'

# Function to reformat the labels
def reformat_labels(label_str):
    labels = str(label_str).split('|')  # Split the string by '|'
    reformatted = ', '.join([f"'{label}'" for label in labels])  # Enclose each label in ''
    return reformatted

df1 = pd.read_csv(os.path.join(path_1, filename_1))[["UUID", "FILE", "QUOTE_TRANSCRIPTION", "ANCHOR", "COMMENTS", "TAGS"]]

# Apply the function to the 'labels' column
df1['TAGS'] = df1['TAGS'].apply(reformat_labels)


## Extract page numbers from merged OCR text file ##

# Read the entire text file into a single string
with open('source/path/Z255430508_clean_merged.txt', 'r', encoding='utf-8') as file1:
    text_content1 = file1.read()


# Function to find a number in the preceding character sequence
def find_number_before_position(text: str, position: int, search_length: int = 10000) -> Union[str, str]:
    """
    Finds the last number following 'page' in the text preceding or succeeding the given position.

    Parameters:
    - text (str): The full text to search within.
    - position (int): The position in the text to search around.
    - search_length (int): The length of text to search before or after the position.

    Returns:
    - Union[str, str]: The last number found after 'page' in the preceding or succeeding text,
                        or a warning message "Warning: No matches found. Check!" if no match is found.
    """
    if not isinstance(text, str):
        raise ValueError("text must be a string")
    if not isinstance(position, int) or position < 0:
        raise ValueError("position must be a non-negative integer")
    if not isinstance(search_length, int) or search_length < 0:
        raise ValueError("search_length must be a non-negative integer")
    
    if position == 0:
        # Search after the position
        following_text = text[position:position + search_length]
        matches = re.findall(r'page(\d+)', following_text)
        if matches:
            return matches[0]  # Return the first match found
        else:
            return "Check!"
    else:
        # Search before the position
        start_position = max(0, position - search_length)
        preceding_text = text[start_position:position]
        matches = re.findall(r'page(\d+)', preceding_text)
        if matches:
            return matches[-1]  # Return the last match found
        else:
            return "Check!"

# Apply the function to each row in the DataFrames
df1['PAGE'] = pd.to_numeric(df1['ANCHOR'].str.extract(r'(\d+)')[0], errors='coerce').apply(lambda x: find_number_before_position(text_content1, x))


## Annotation analysis ##

# Split the labels by '|' and flatten the list of lists into a single list
all_labels = df1['TAGS'].str.split(', ').sum()

# Count the occurrences of each label
label_counts = pd.Series(all_labels).value_counts()

print(label_counts)

