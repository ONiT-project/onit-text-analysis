"""
This script creates a Marqo index of preprocessed and original OCR texts. Each page is indexed as a document that is split into 2 sentences long vectors.
The model used for sentence embedding is https://huggingface.co/flax-sentence-embeddings/all_datasets_v4_mpnet-base.

Code by Michela Vignoli. Parts of this code were developed with assistance from Simon König.
"""

from pprint import pprint
import csv
import marqo as mq

##
## Connect to Marqo
##

MARQO_URL = "http://10.103.251.104:8882"
marqoClient = mq.Client(url=MARQO_URL)
#pprint(marqoClient.get_indexes())

##
## Index settings
##

settings = {
    "textPreprocessing": {
        "splitLength": 2,
        "splitOverlap": 0,
        "splitMethod": "sentence",
    },
}

##
## Ask if index exists, if not create it
##

indexName = "onit-sonnini-DHd2025-clean"
print("Indexname: ", indexName)
current_indexes = [d["indexName"] for d in marqoClient.get_indexes()["results"]]
if indexName in current_indexes:
    print(f"Index already exists: {indexName} ")
    # Set indexName as the current index
    print(f"Defaulting to index connection. Index connected: {indexName} ")
else:  # Create a new index
    print(f"Index does not exist: {indexName} ")
    print(f"Creating index: {indexName} ")
    marqoClient.create_index(
        indexName,
        model="flax-sentence-embeddings/all_datasets_v4_mpnet-base",
        settings_dict=settings
    )

## List of models integrated in Marqo: https://docs.marqo.ai/latest/models/marqo/list-of-models/

pprint(marqoClient.get_indexes())

##
## Load dict of data
##


# Load list of dictionaries with each dictionary containing keys: text, barcode, page
# CSV path
csv_file = 'data/DHd_index-cleaned.csv'

# Read data from CSV file into a list of dictionaries
with open(csv_file, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    animal_descriptions = [row for row in reader]

# Function to clean text by replacing \n with spaces
def clean_text(text):
    return text.replace('\n', ' ').strip()

# Clean the 'text' field in each dictionary
for entry in animal_descriptions:
    entry['text_orig'] = clean_text(entry['text_orig'])
    entry['text_clean'] = clean_text(entry['text_clean'])
    entry['text_prep'] = clean_text(entry['text_prep'])

pprint(animal_descriptions[:3])

##
## Add documents to the index
##

print(f"Indexing data...")
# Define client_batch_size
client_batch_size = 128

# Indexing
marqoClient.index(indexName).add_documents(
    animal_descriptions,
    client_batch_size=client_batch_size,
    tensor_fields=["text_clean"],
)

print(f"Data has been indexed in {indexName}")