"""
Simple Gradio app to preview the preliminary results for retrieving nature representations in imperfect OCR data extracted from 17-19 century German texts in the ONiT project.
Code by Michela Vignoli partially generated with Chat GPT3, GPT4 (free version), and Claude (free version).
"""

# Import packages
import gradio as gr
import pandas as pd
from difflib import SequenceMatcher
import re

# Import results
results_clean = pd.read_csv("data/retrieval_results/sonnini_cleaned/i_onit-sonnini-DHd2025-clean-q_Pferd, Pferde.csv").head(100)
results_prep = pd.read_csv("data/retrieval_results/sonnini_llm_corrected/i_onit-sonnini-DHd2025-prep-q_Pferd, Pferde.csv").head(100)
results_orig = pd.read_csv("data/retrieval_results/sonnini_original_ocr/i_onit-test-index-sonnini-q_Pferd-Pferde.csv").head(100)
annotations = pd.read_csv("data/annotations/DHd2025_referenceReports_annotations_preview_horses.csv")

# Drop 'text_prep' from results_orig
results_clean.drop(columns=['text_prep'], inplace=True)

# Modify the "document" column to remove "_page175.txt" and keep the "Z166069305_00175"
results_orig['document'] = results_orig['document'].str[:-12]

# Modify the "page" column to extract the numeric part and remove leading zeroes
results_orig['page'] = results_orig['page'].str.extract(r'(\d+)', expand=False).astype(int)

data_sources = {"Results Cleaned OCR": results_clean, "Results LLM Preprocessed OCR": results_prep, "Results Original OCR": results_orig, "Annotations": annotations}

# Pagination settings
R = 5  # Number of preview rows per page

def normalize_text(text):
    """Normalize text for better matching by removing extra whitespace and standardizing characters."""
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Could add more normalization steps here if needed
    return text

def find_best_match(needle, haystack):
    """Find the best matching position of needle in haystack using fuzzy matching."""
    matcher = SequenceMatcher(None, needle, haystack)
    matches = matcher.get_matching_blocks()
    
    # Find the best match that exceeds our threshold
    best_match = None
    best_match_ratio = 0.5  # Initialize the best match ratio with our minimum threshold
    
    for match in matches:
        i, j, n = match
        if n > 0:  # Only consider non-zero length matches
            subsequence = haystack[j:j+n]
            ratio = SequenceMatcher(None, needle, subsequence).ratio()
            if ratio > best_match_ratio:
                best_match = (j, j+n)
                best_match_ratio = ratio
    
    return best_match

def highlight_text(text, highlights):
    """
    Highlight specified text segments using fuzzy matching and HTML mark tags.
    
    Args:
        text (str): The original text to highlight
        highlights (str or list): Text segment(s) to highlight
    
    Returns:
        str: Text with highlights wrapped in <mark> tags
    """
    if not text or not highlights:
        return text
    
    # Ensure highlights is a list
    if isinstance(highlights, str):
        highlights = [highlights]
    
    # Remove empty or None highlights
    highlights = [h for h in highlights if h]
    if not highlights:
        return text
    
    # Sort highlights by length (longest first) to avoid nested highlights
    highlights = sorted(highlights, key=len, reverse=True)
    
    # Store positions to highlight
    positions_to_highlight = []
    
    # Find positions for each highlight
    for highlight in highlights:
        normalized_highlight = normalize_text(highlight)
        normalized_text = normalize_text(text)
        
        match = find_best_match(normalized_highlight, normalized_text)
        if match:
            start, end = match
            # Convert positions back to original text
            original_start = len(text[:start].rstrip())
            original_end = original_start + len(text[start:end].strip())
            positions_to_highlight.append((original_start, original_end))
    
    # Sort positions by start position
    positions_to_highlight.sort()
    
    # Apply highlights from end to start to avoid position shifting
    for start, end in reversed(positions_to_highlight):
        text = f"{text[:start]}<mark>{text[start:end]}</mark>{text[end:]}"
    
    return text

# Function to create preview rows
def preview_results(page, selected_data_source):
    data_source = data_sources[selected_data_source]
    start_idx = (page - 1) * R
    end_idx = min(start_idx + R, len(data_source))
    
    results = data_source.iloc[start_idx:end_idx]

    row_elements = []
    for idx, (_, row) in enumerate(results.iterrows(), start=start_idx + 1):
        highlighted_text = row['unpacked_highlights']
        # Highlight "Pferd" and "Pferde" using a span with a yellow background
        highlighted_text = re.sub(r'\b(Pferd\w*)\b', r"<span style='background-color: yellow; font-weight: bold;'>\1</span>", highlighted_text, flags=re.IGNORECASE)
        row_html = f"""
        <div style='border:1px solid #ddd; padding:10px; margin:5px 0; font-size: 18px;'>
            <b>{idx}. \'{row['document']}\'</b> - Score: {row['_score']} - Rank: {row['rank']}
            <br><i>{highlighted_text}</i>
        </div>
        """
        row_elements.append(row_html)

    return "".join(row_elements)

# Function to show details of a selected row
def show_details(document_name, selected_data_source):
    data_source = data_sources[selected_data_source]
    row = data_source[data_source["document"] == document_name]
    
    if row.empty:
        return "<p style='color:red;'>Document not found. Please select a valid document.</p>"

    row = row.iloc[0]  # Extract first matching row
    return f"""
    <div style="display: flex; justify-content: space-between; align-items: start;">
        <div style="width: 65%; font-size: 18px;">
            <h3>📄 Preview: {document_name}</h3>
            <p><b>Retrieved text chunk: </b><i>{row["unpacked_highlights"]}</i></p>
            <p><b>Text on page {row['page']}: </b>{highlight_text(row.get('text_prep') or row.get('text_clean') or row.get('text'), row["unpacked_highlights"])}</p>
            <p><a href="https://digital.onb.ac.at/OnbViewer/viewer.faces?doc=ABO_%2B{row['barcode']}&order={row['page']}&view=SINGLE" target="_blank">🔍 Open ÖNB Viewer</a></p>
        </div>
        <div style="width: 30%; text-align: right;">
            <img src="{row['iiif_link']}" alt="IIIF Image Preview" 
                 style="max-width: 100%; height: auto; border: 1px solid #ddd;">
        </div>
    </div>
    <div style="font-size: 18px;">
        <p><b>Source: </b>C. S. Sonnini's, ehemaligen Offiziers und Jngenieurs des französischen Seewesens <br>und Mitgliedes mehrerer gelehrten und litterarischen Gesellschaften, <br><i>Reisen in Ober= und Niederägypten</i>, Bd. 1. Leipzig/Gera: Wilh. Heinsius, 1800</p>
        <p><b>Citation link: <a href="http://data.onb.ac.at/rep/1058B194"target="_blank">http://data.onb.ac.at/rep/1058B194</a></p>
    </div>
    """

# Gradio Interface
with gr.Blocks() as demo:
    gr.Markdown("""
                ## 🔍 Preview Text Retrieval Results with Marqo Vector Database
                <div style="font-size: 18px;">
                <p><b>Instructions:</b> Browse through the retrieval results for the text prompt <i>"Pferd, Pferde"</i> by sliding the page slider (up to 100 first retrieval results can be inspected). 
                Select the data source: Choose between <i>Results Cleaned OCR, Results LLM Preprocessed OCR, Results Original OCR,</i> and our <i>Annotations</i> of text passages mentioning <i>horses and kindred animals</i> in the text. 
                To visualise details about the retrieved text chunk, copy and paste the document name (e.g. <i>Z166069305_430</i>) in the search bar below and click on the <i>Inspect</i> button. 
                Please note that pressing <i>Enter</i> does not work. 
                To inspect the page in the full book, click on <i>Open ONB Viewer</i> in the document details below.</p>
                </div>""")

    data_source_dropdown = gr.Dropdown(choices=list(data_sources.keys()), label="Select Data Source", value="Results Cleaned OCR")
    page_slider = gr.Slider(1, 1, step=1, label="Page", interactive=True)
    preview_output = gr.HTML()

    gr.Markdown("## 📝 Inspect Document Details")
    
    doc_name_input = gr.Textbox(label="Copy and paste document name to search bar (e.g. Z166069305_430):", interactive=True)
    inspect_button = gr.Button("Inspect")
    inspect_output = gr.HTML()

    # Function to update preview when data source changes
    def update_data_source(selected_data_source):
        max_page = (len(data_sources[selected_data_source]) // R) + 1
        page_slider.maximum = max_page  # Update the max page count dynamically
        return preview_results(1, selected_data_source), 1  # Reset slider to 1

    # Function to update preview when page slider changes
    def update_preview(page, selected_data_source):
        return preview_results(page, selected_data_source)

    # Function to update document details
    def update_details(doc_name, selected_data_source):
        return show_details(doc_name, selected_data_source)

    # Handle data source change
    data_source_dropdown.change(
        update_data_source,
        inputs=[data_source_dropdown], 
        outputs=[preview_output, page_slider]  # Update both preview and reset slider
    )
    # Handle page slider change
    page_slider.change(update_preview, inputs=[page_slider, data_source_dropdown], outputs=[preview_output])

    # Handle inspect button click
    inspect_button.click(update_details, inputs=[doc_name_input, data_source_dropdown], outputs=[inspect_output])

    # Initialize preview with default data source
    preview_output.value = update_data_source("Results Cleaned OCR")
    
    # Further information block at the end
    gr.Markdown("""
    ## 📚 Further Information
    <div style="font-size: 18px;">
        <p>This demo lets you explore our preliminary results for retrieving <i>nature</i> representations in imperfect OCR data extracted from 17-19 century German texts.
        This research was done in the <a href="https://onit.oeaw.ac.at/">Ottoman Nature in Travelogues (ONiT)</a> project and funded by the Austrian Science Fund (FWF: P 35245).
        The text retrieval was done with hybrid vector/lexical search (BM25) by using a <a href="https://docs.marqo.ai/">Marqo</a> 
        vector index. The texts were indexed as one page per document unit, and by splitting them in 2-sentence vectors and embedding them with 
        <a href="https://huggingface.co/flax-sentence-embeddings/all_datasets_v4_mpnet-base">flax-sentence-embeddings/all_datasets_v4_mpnet-base</a> model. 
        <i>Results Cleaned OCR</i> contain the retrieval results for the vectorized OCR texts that were cleaned by using regular expressions. 
        <i>Results LLM Preprocessed OCR</i> contain the retrieval results for the vectorized OCR texts that were automatically corrected with Llama3.1:70b. 
        <i>Results Original OCR</i> contain the retrieval results for the original OCR texts (without any preprocessing).</p>
        <p>For more information, contact <a href="mailto:michela.vignoli@ait.ac.at">michela(dot)vignoli(at)ait(dot)ac(dot)at</a>.</p>
    </div>
    """)

demo.launch()