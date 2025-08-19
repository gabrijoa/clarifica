# clarifica/main.py

import os
import pymupdf
from . import extractor
from . import core
from . import generator

# --- CONFIGURATION ---
INPUT_FOLDER = "input_docs"
OUTPUT_FOLDER = "output_docs"
FILE_NAME = "puer_aeternus.pdf"
OUTPUT_FORMAT = "pdf"  # <-- CHANGE HERE: "pdf" or "md"

def main():
    """
    Main execution function that orchestrates the PDF processing workflow
    by processing the document page by page to ensure correct structure.
    """
    # 1. Setup paths
    input_file_path = os.path.join(INPUT_FOLDER, FILE_NAME)
    output_filename_base = os.path.splitext(FILE_NAME)[0]
    output_file_path = os.path.join(OUTPUT_FOLDER, f"{output_filename_base}.{OUTPUT_FORMAT}")
    image_output_folder = os.path.join(OUTPUT_FOLDER, "images")

    if not os.path.exists(input_file_path):
        print(f"ERROR: Input file not found at '{input_file_path}'")
        return
    
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    try:
        doc = pymupdf.open(input_file_path)
    except Exception as e:
        print(f"ERROR: Failed to open PDF file. Reason: {e}")
        return

    # --- Pre-Analysis Step: Determine body font size once for consistency ---
    print("--- Analyzing font sizes across document ---")
    all_text_blocks = extractor.extract_all_text_blocks(doc)
    body_font_size = core.safe_body_size(all_text_blocks)
    print(f"Identified body text font size: {body_font_size}")

    # --- Main Processing Loop: Page by Page ---
    final_structured_document = []
    saved_image_xrefs = set() # Track unique images across all pages

    print(f"--- Processing {len(doc)} pages ---")
    for page in doc:
        # 1. Extract text and images for the CURRENT page
        page_text_blocks = extractor.extract_text_blocks_from_page(page)
        page_image_blocks = extractor.extract_and_save_images_from_page(
            page, doc, image_output_folder, saved_image_xrefs
        )
        
        # 2. Combine and sort elements for THIS page
        page_elements = page_text_blocks + page_image_blocks
        page_elements.sort(key=lambda el: el.get('bbox', (0, 0, 0, 0))[1]) # Sort by vertical position

        # 3. Process the sorted elements of the page
        structured_page_content = core.process_page_elements(page_elements, body_font_size)
        
        # 4. Add the structured content of this page to the final document
        final_structured_document.extend(structured_page_content)

    doc.close()

    # 4. Generation Step
    print(f"--- Starting Generation (Format: {OUTPUT_FORMAT.upper()}) ---")
    if OUTPUT_FORMAT.lower() == "pdf":
        generator.generate_pdf(final_structured_document, output_file_path)
    else:
        generator.generate_markdown_file(final_structured_document, output_file_path)

if __name__ == "__main__":
    main()
