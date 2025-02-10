"""
This script parses through the cleaned texts and prompts Ollama to create transcriptions of the faulty OCR texts staying as close as possible to the original wording.
It was tested with German texts from the 17th, 18th, and 19th century.

Code by Michela Vignoli. Parts of this code were developed with assistance from GPT-4 and GPT-3 (free version).
"""

import json
import subprocess
import os
import time

def get_data(root_folder, extension='.txt'):
    data = []
    # Walk through all folders and files in the root directory
    for folder, _, files in os.walk(root_folder):
        for file in files:
            if file.endswith(extension):
                file_path = os.path.join(folder, file)
                filename = os.path.splitext(os.path.basename(file_path))[0]
                folder_path = os.path.join(f'preprocessed/{folder}_preprocessed')
                #print(f"Found file: {file_path}")
                
                # Read the file content with detected encoding
                with open(file_path, 'r', encoding="utf-8") as f:
                    text = f.read()
                    data.append({"path": folder_path, "text": text, "filename": filename})
    return data

def extract_corrected_text(raw_response):
    # Split the response by newline to handle multiple JSON objects
    lines = raw_response.strip().split('\n')
    response_segments = []
    
    # Process each line as a JSON object
    for line in lines:
        try:
            json_obj = json.loads(line)
            response_segment = json_obj.get('response', '')
            response_segments.append(response_segment)
        except json.JSONDecodeError:
            print(f"Skipping invalid JSON line: {line}")
    
    # Join all response segments into a single text
    full_text = ''.join(response_segments)
    return full_text

def correct_text_with_llm(text, retries=3):
    print('-------------------------')
    print('Processing LLM request...')
    prompt = "You are a historian expert in historical German texts. Correct the following faulty OCR texts generated from historical traveolgues printed from the 17-19th century. Remain as closely to the original, historical wording as possible while correcting all the errors from the faulty OCR. Output the corrected text by removing the unnecessary line breaks in the pages, where full sentences occur. Leave the line breaks in other pages. Only output the corrected text without further comments, explanations, or information. Omit Corrected text: before the actual text.\n\n" + text

    # Prepare the cURL command
    curl_command = [
        'curl',
        'http://your.ip:port/api/generate',
        '-d', json.dumps({
            "model": "llama3.1:70b",
            "prompt": prompt
        }),
        '-H', 'Content-Type: application/json'
    ]

    for attempt in range(retries):
        print(f"Attempt {attempt + 1} of {retries}: Processing LLM request...")
        result = subprocess.run(curl_command, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            print(f"Error: cURL command failed with error: {result.stderr}")
            time.sleep(2)  # Wait before retrying
            continue
        
        corrected_text = extract_corrected_text(result.stdout)
        print("Corrected text:", corrected_text)
        
        if corrected_text:
            return corrected_text
        
        print("Invalid response, retrying...")
        time.sleep(2)  # Wait before retrying

    print(f"Failed to get a valid response from the LLM API.")
    return None


def process_txt(root_folder):
    # Read text files from the root folder
    data = get_data(root_folder)
    
    # Process each file in the data list
    for item in data:
        text = item["text"]
        folder_path = item["path"]
        filename = item["filename"]
        
        # Define the output path for the corrected text file
        output_path = os.path.join(folder_path, f"{filename}_corrected.txt")
        
        # Create the necessary directories if they don't exist
        os.makedirs(folder_path, exist_ok=True)
        
        # Apply the LLM correction function
        corrected_text = correct_text_with_llm(text)
        
        # Determine the appropriate output path based on whether correction succeeded
        if corrected_text:
            # Save the corrected text into a .txt file
            with open(output_path, "w", encoding="utf-8") as file:
                file.write(corrected_text)
            print(f"Processed and corrected text saved to {output_path}")
        else:
            # Save the original text into a .txt file with a different name if correction failed
            output_path = os.path.join(folder_path, f"{filename}_FAILED.txt")
            with open(output_path, "w", encoding="utf-8") as file:
                file.write(text)
            print(f"Failed to correct text. Original text saved to {output_path}")

# Example usage
root_folder = 'source/folder/'
process_txt(root_folder)